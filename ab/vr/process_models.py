#!/usr/bin/env python3
"""
Continuous ONNX model pipeline for VR inference benchmarking.

Exports PyTorch models to ONNX and benchmarks them on an Android emulator/device
using ONNX Runtime's perf test CLI tool (no Android app required).

Usage:
    python process_models.py                        # Process all models
    python process_models.py ResNet,MoE             # Specific models only
    python process_models.py --limit 5              # First 5 models
    python process_models.py --skip-device          # Export ONNX only
    python process_models.py --force                # Reset state, reprocess all
    python process_models.py --android-runs 50      # 50 benchmark iterations
"""

import sys
import os
import argparse
import json
import re
import subprocess
import time
import gc
import logging
import traceback
from pathlib import Path

from ab.vr.model_loader import load_models
from ab.vr.onnx_exporter import export_onnx
from scripts.shape_utils import infer_image_resolution
import importlib
import pkgutil

# ── Configuration ────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent
STAT_DIR = SCRIPT_DIR / "out" / "nn" / "stat" / "run" / "onnx" / "fp32"
WORK_DIR = SCRIPT_DIR / "_work"
STATE_FILE = WORK_DIR / "processing_state.json"
ONNX_TEMP = WORK_DIR / "onnx_temp"

DEVICE_TMP = "/data/local/tmp"
ORT_PERF = f"{DEVICE_TMP}/onnxruntime_perf_test"

DEFAULT_RUNS = 20
RESTART_EVERY = 50
COOLDOWN = 2
EXPORT_TIMEOUT = 120.0
MAX_PARAM_MB = 500

for _d in [STAT_DIR, WORK_DIR, ONNX_TEMP]:
    _d.mkdir(parents=True, exist_ok=True)

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(WORK_DIR / "processing.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


# ── ADB helpers ──────────────────────────────────────────────────────────────
def _wait_for_device():
    """Block until an ADB device comes back online."""
    logger.info("⏳ Waiting for device reconnection...")
    while True:
        r = subprocess.run(["adb", "get-state"], capture_output=True, text=True)
        if "device" in r.stdout:
            logger.info("✅ Device reconnected")
            time.sleep(5)
            return
        time.sleep(10)


def adb_shell(cmd: str) -> str:
    """Run an ``adb shell`` command; auto-retry on device-lost."""
    while True:
        r = subprocess.run(["adb", "shell", cmd], capture_output=True, text=True)
        if r.returncode != 0 and ("device not found" in r.stderr or "lost" in r.stderr):
            _wait_for_device()
            continue
        return r.stdout.strip()


def adb_getprop(key: str) -> str:
    out = adb_shell(f"getprop {key}")
    return out.splitlines()[-1] if out else ""


def device_ready(timeout: int = 10) -> bool:
    try:
        r = subprocess.run(["adb", "devices"], capture_output=True, text=True, timeout=timeout)
        lines = [l for l in r.stdout.splitlines()[1:] if l.strip()]
        return any("\tdevice" in l for l in lines)
    except Exception:
        return False


def is_emulator_device() -> bool:
    try:
        r = subprocess.run(["adb", "devices"], capture_output=True, text=True, timeout=10)
        return any("emulator-" in l for l in r.stdout.splitlines())
    except Exception:
        return False


# ── Emulator management ─────────────────────────────────────────────────────
def get_available_avds() -> list:
    try:
        r = subprocess.run(["emulator", "-list-avds"], capture_output=True, text=True, timeout=10)
        return [a.strip() for a in r.stdout.splitlines() if a.strip()] if r.returncode == 0 else []
    except Exception:
        return []


def ensure_emulator_running() -> bool:
    """Start an emulator if no device is connected."""
    if device_ready():
        logger.info("✅ Device already connected")
        return True

    avds = get_available_avds()
    if not avds:
        logger.error("❌ No AVDs found. Create one in Android Studio first.")
        return False

    target = avds[0]
    logger.info(f"🚀 Starting emulator: {target}")
    subprocess.Popen(
        ["emulator", "-avd", target, "-no-audio", "-no-window"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    # Wait for device to appear (3 min)
    for _ in range(36):
        time.sleep(5)
        if device_ready():
            # Wait for full boot (2 min)
            for _ in range(24):
                if adb_shell("getprop sys.boot_completed") == "1":
                    logger.info("✅ Emulator fully booted")
                    return True
                time.sleep(5)
            break

    logger.error("❌ Emulator boot timeout")
    return False


# ── Device analytics ─────────────────────────────────────────────────────────
def get_android_memory() -> dict:
    mem = {}
    raw = adb_shell("cat /proc/meminfo")
    mapping = {
        "MemTotal": "total_ram_kb",
        "MemFree": "free_ram_kb",
        "MemAvailable": "available_ram_kb",
        "Cached": "cached_kb",
    }
    for line in raw.splitlines():
        parts = line.split(":")
        if len(parts) == 2:
            k = parts[0].strip()
            if k in mapping:
                try:
                    mem[mapping[k]] = int(parts[1].strip().split()[0])
                except (ValueError, IndexError):
                    pass
    return mem


def get_device_analytics() -> dict:
    raw = adb_shell("cat /proc/cpuinfo")
    processors, current = [], {}
    meta = {
        "hardware": "", "features": "",
        "cpu implementer": "", "cpu architecture": "",
        "cpu variant": "", "cpu part": "", "cpu revision": "",
    }
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            if current:
                processors.append(current)
                current = {}
            continue
        if ":" in line:
            k, v = line.split(":", 1)
            k, v = k.strip().lower(), v.strip()
            if k == "processor" and v.isdigit():
                current["processor"] = v
            elif k in meta:
                meta[k] = v
                current[k] = v
            else:
                current[k] = v
    if current:
        processors.append(current)

    soc = adb_getprop("ro.soc.model") or adb_getprop("ro.board.platform")
    return {
        "timestamp": time.time(),
        "cpu_info": {
            "cpu_cores": len([p for p in processors if "processor" in p]),
            "processors": processors[:4],
            "arm_architecture": {
                "hardware": meta["hardware"] or soc,
                "features": meta["features"],
                "cpu_implementer": meta["cpu implementer"],
                "cpu_architecture": meta["cpu architecture"],
                "cpu_variant": meta["cpu variant"],
                "cpu_part": meta["cpu part"],
                "cpu_revision": meta["cpu revision"],
            },
        },
    }


# ── Benchmark ────────────────────────────────────────────────────────────────
def check_benchmark_tool() -> bool:
    """Return True if onnxruntime_perf_test exists on the device."""
    out = adb_shell(f"ls {ORT_PERF}")
    return "No such file" not in out and out != ""


def run_bench(model_path: str, runs: int, use_nnapi: bool = False) -> dict:
    """Run ONNX Runtime perf test on device and parse timing output.

    Expected output contains lines like:
        Average inference time cost: 12.345 ms
        Total inference time cost: 246.9 ms
        Min inference time cost: 10.2 ms
        Max inference time cost: 15.1 ms
    Values are converted to microseconds (µs) to match the reference format.
    """
    ep = "-e nnapi" if use_nnapi else ""
    cmd = f"{ORT_PERF} -m {model_path} -r {runs} {ep}"
    out = adb_shell(cmd)

    if not out or "error" in out.lower() or "fail" in out.lower():
        return {"avg": float("inf"), "min": 0, "max": 0, "std": 0,
                "status": "failed", "error": (out or "empty output")[:300]}

    res = {"avg": 0.0, "min": 0.0, "max": 0.0, "std": 0.0, "status": "ok"}
    for pattern, key in [
        (r"(?:average|avg|mean)[^\d]*([\d.]+)", "avg"),
        (r"(?:min|minimum)[^\d]*([\d.]+)", "min"),
        (r"(?:max|maximum)[^\d]*([\d.]+)", "max"),
        (r"(?:std|stddev|deviation)[^\d]*([\d.]+)", "std"),
    ]:
        m = re.search(pattern, out, re.IGNORECASE)
        if m:
            # Convert ms → µs (×1000) to match reference project format
            res[key] = float(m.group(1)) * 1000.0

    if res["avg"] == 0.0:
        # Try total / runs fallback
        m = re.search(r"total[^\d]*([\d.]+)", out, re.IGNORECASE)
        if m and runs > 0:
            res["avg"] = float(m.group(1)) * 1000.0 / runs

    if res["avg"] == 0.0:
        res["status"] = "failed"
        res["error"] = "Could not parse benchmark output"

    return res


# ── Helpers ──────────────────────────────────────────────────────────────────
def get_input_size(transform_str: str) -> int:
    """Extract image resolution from transform string, e.g. 'echo_128' → 128."""
    return infer_image_resolution(transform_str) or 32


def save_state(state: dict):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def _discover_models_from_arch_hf(
    *,
    limit: int | None = None,
    dataset: str = "cifar-10",
) -> dict:
    """
    Reference-repo-style discovery:
    - enumerate importable `ab.nn.nn.*` modules (architectures available locally)
    - intersect with HF checkpoints available in `NN-Dataset/checkpoints-epoch-50` (files `*.pth`)
    - use HF `all_models.json` as metadata source for `prm` (transform, etc.)
    Returns: name -> pandas.Series-like row (supports .get/.copy/.to_dict via export path)
    """
    try:
        import pandas as pd
        from huggingface_hub import hf_hub_download, list_repo_files
        import json as _json
    except Exception as e:
        raise RuntimeError(f"Missing deps for HF/arch discovery: {e}")

    # 1) Discover importable architectures
    try:
        import ab.nn.nn as ab_nn_nn
    except Exception as e:
        raise RuntimeError(f"Could not import ab.nn.nn package: {e}")

    arch_mods = set()
    for m in pkgutil.iter_modules(getattr(ab_nn_nn, "__path__", [])):
        if not m.ispkg:
            arch_mods.add(m.name)

    # 2) Discover checkpoints on HF
    hf_repo = "NN-Dataset/checkpoints-epoch-50"
    hf_files = list_repo_files(hf_repo)
    ckpt_stems = {Path(p).stem for p in hf_files if p.endswith(".pth")}

    # 3) Load metadata (prm/transform)
    meta_path = hf_hub_download(
        repo_id=hf_repo,
        filename="all_models.json",
        cache_dir=str(WORK_DIR / "temp"),
    )
    model_db = _json.load(open(meta_path, "r"))

    # 4) Intersection
    names = sorted(arch_mods.intersection(ckpt_stems))
    if limit is not None:
        names = names[: int(limit)]

    out: dict = {}
    for name in names:
        entry = model_db.get(name, {}) or {}
        prm = (entry.get("prm", {}) or {}) if isinstance(entry, dict) else {}
        out[name] = pd.Series(
            {
                "nn": name,
                "task": "img-classification",
                "dataset": dataset,
                "accuracy": float(entry.get("accuracy", 0.0) or 0.0) if isinstance(entry, dict) else 0.0,
                "prm": prm,
            }
        )

    return out


# ── Main pipeline ────────────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser(description="ONNX model pipeline for VR inference benchmarking")
    ap.add_argument("models", nargs="?", default=None, help="Comma-separated model names")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--android-runs", type=int, default=DEFAULT_RUNS)
    ap.add_argument("--skip-device", action="store_true", help="Export ONNX only")
    ap.add_argument("--force", action="store_true", help="Reset state")
    ap.add_argument("--dataset", default="cifar-10")
    ap.add_argument("--export-timeout", type=float, default=EXPORT_TIMEOUT)
    ap.add_argument("--push-hf", action="store_true", help="Push to HuggingFace Hub")
    args = ap.parse_args()

    # ── State & JSON tracking ────────────────────────────────────────────
    if args.force and STATE_FILE.exists():
        STATE_FILE.unlink()
    state = json.load(open(STATE_FILE)) if STATE_FILE.exists() else {"processed": [], "failed": []}
    
    # Track results globally
    all_models_json = STAT_DIR / "all_models.json"
    skipped_models_json = STAT_DIR / "skipped_models.json"
    results = json.load(open(all_models_json)) if all_models_json.exists() else {}
    skipped = json.load(open(skipped_models_json)) if skipped_models_json.exists() else {}

    # ── Discover models ──────────────────────────────────────────────────
    model_configs = {}  # name → row dict
    if args.models:
        # Specific models requested: look them up via load_models() for metadata,
        # then fall back to HF discovery if the DB has no entry.
        model_names = [m.strip() for m in args.models.split(",")]
        for name in model_names:
            df = load_models(nn=name)
            df = df[df["task"] == "img-classification"]
            if not df.empty:
                best = df.loc[df["accuracy"].idxmax()].copy()
                best["nn"] = name
                model_configs[name] = best
            else:
                logger.warning(f"⚠️  No DB config for {name}; will try HF arch discovery")
        # Fill any missing names via HF arch discovery
        missing = [n for n in model_names if n not in model_configs]
        if missing:
            hf_configs = _discover_models_from_arch_hf(dataset=args.dataset)
            for n in missing:
                if n in hf_configs:
                    model_configs[n] = hf_configs[n]
                else:
                    logger.warning(f"⚠️  {n} not found in HF checkpoints either, skipping")
        model_names = list(model_configs.keys())
    else:
        # Default: mirror the reference repo — enumerate ALL importable arch modules
        # that have a matching .pth on HF. This yields ~1740 models, not ~45.
        # ab.nn.api.data() is intentionally NOT used here as the primary path because
        # it collapses UUID-variant model names (e.g. AirNet-626c3eb9-...) into a
        # single base name via split("-")[0], reducing 1740 models down to ~27.
        logger.info("Discovering models via arch+HF intersection (reference repo style)...")
        model_configs = _discover_models_from_arch_hf(limit=args.limit, dataset=args.dataset)
        model_names = list(model_configs.keys())
        logger.info(f"Found {len(model_names)} models to process")

    remaining = [m for m in model_names if m not in state["processed"] and m not in state["failed"]]
    if not remaining:
        logger.info("✅ All models already processed!")
        return

    logger.info(f"📋 {len(remaining)} models to process")

    # ── Device setup ─────────────────────────────────────────────────────
    device_name = "local"
    os_ver = ""
    emu = False
    has_bench = False

    if not args.skip_device:
        if not ensure_emulator_running():
            logger.error("❌ No device available. Use --skip-device for export-only.")
            return
        emu = is_emulator_device()
        device_name = (adb_getprop("ro.product.model") or "unknown").replace(" ", "_")
        os_ver = f"{adb_getprop('ro.build.version.release')} | {adb_getprop('ro.build.id')}"

        has_bench = check_benchmark_tool()
        if not has_bench:
            # logger.warning(f"⚠️  Benchmark tool not found at {ORT_PERF}")
            # logger.warning("   Build ONNX Runtime for Android, then:")
            # logger.warning(f"     adb push onnxruntime_perf_test {DEVICE_TMP}/")
            # logger.warning(f"     adb shell chmod +x {ORT_PERF}")
            # logger.warning("   Continuing in export-only mode.")
            # args.skip_device = True
            raise RuntimeError(
                "onnxruntime_perf_test not found on device. "
                "You MUST install it before running pipeline."
            )

    # ── Process loop ─────────────────────────────────────────────────────
    session_count = 0
    for idx, name in enumerate(remaining, 1):
        time.sleep(COOLDOWN)

        if session_count >= RESTART_EVERY:
            logger.info("🔄 Restarting process for memory cleanup...")
            save_state(state)
            time.sleep(5)
            os.execv(sys.executable, [sys.executable] + sys.argv)

        logger.info(f"\n{'='*55}")
        logger.info(f"  [{idx}/{len(remaining)}] {name}")
        logger.info(f"{'='*55}")

        try:
            row = model_configs[name]
            prm = row.get("prm", {})
            if isinstance(prm, str):
                import ast
                prm = ast.literal_eval(prm)

            transform = prm.get("transform", "")
            target_h = get_input_size(transform)
            task = row.get("task", "img-classification")
            dataset = row.get("dataset", args.dataset)
            accuracy = float(row.get("accuracy", 0))

            # ── 1. Export ONNX ───────────────────────────────────────────
            onnx_file = ONNX_TEMP / f"{name}.onnx"
            if not onnx_file.exists():
                logger.info(f"   Exporting ONNX ({target_h}x{target_h})...")
                row_copy = row.copy()
                row_copy["nn"] = name
                export_onnx(row_copy, onnx_file, timeout_sec=args.export_timeout)
                logger.info(f"   ✅ Exported: {onnx_file.name}")
            else:
                logger.info(f"   ⏭️  ONNX already exists")

            # ── 1.5 Evaluate ONNX Accuracy ─────────────────────────────────
            acc = 0.0
            if name not in results or "accuracy" not in results[name]:
                try:
                    from ab.vr.onnx_validator import eval_onnx_accuracy
                    logger.info(f"   Evaluating ONNX accuracy...")
                    data_root = WORK_DIR / "data"
                    data_root.mkdir(parents=True, exist_ok=True)
                    acc = eval_onnx_accuracy(onnx_file, target_h, data_root)
                    logger.info(f"   🎯 Accuracy: {acc:.4f}")
                except Exception as e:
                    logger.warning(f"   ⚠️  Could not evaluate accuracy: {e}")
            else:
                acc = results[name]["accuracy"]
                logger.info(f"   🎯 Cached Accuracy: {acc:.4f}")

            results[name] = {
                "accuracy": acc,
                "transform": transform
            }
            with open(all_models_json, "w") as f:
                json.dump(results, f, indent=2)

            if args.skip_device:
                state["processed"].append(name)
                save_state(state)
                session_count += 1
                gc.collect()
                continue

            # ── 2. Push to device ────────────────────────────────────────
            dev_path = f"{DEVICE_TMP}/{name}.onnx"
            logger.info(f"   📤 Pushing to device...")
            for attempt in range(3):
                r = subprocess.run(
                    ["adb", "push", str(onnx_file), dev_path],
                    capture_output=True, text=True,
                )
                if r.returncode == 0:
                    break
                logger.warning(f"   ⚠️  Push attempt {attempt+1} failed, retrying...")
                time.sleep(3)
            else:
                raise RuntimeError(f"Failed to push {name} after 3 attempts")

            # ── 3. Benchmark (CPU + NNAPI) ───────────────────────────────
            logger.info(f"   🎯 Benchmarking CPU ({args.android_runs} runs)...")
            cpu = run_bench(dev_path, args.android_runs, use_nnapi=False)

            logger.info(f"   🎯 Benchmarking NNAPI ({args.android_runs} runs)...")
            nnapi = run_bench(dev_path, args.android_runs, use_nnapi=True)

            # Clean up device
            adb_shell(f"rm {dev_path}")

            # Pick best backend
            opts = {}
            if cpu["status"] == "ok":
                opts["CPU"] = cpu["avg"]
            if nnapi["status"] == "ok":
                opts["NNAPI"] = nnapi["avg"]
            winner = min(opts, key=opts.get) if opts else "Failed"

            # ── 4. Collect analytics & save report ───────────────────────
            mem = get_android_memory()
            analytics = get_device_analytics()

            report = {
                "model_name": name,
                "device_type": device_name.replace("_", " "),
                "os_version": os_ver,
                "valid": winner != "Failed",
                "emulator": emu,
                "iterations": args.android_runs,
                "duration": int(opts[winner]) if winner != "Failed" else 0,
                "unit": winner,
                "cpu_duration": int(cpu["avg"]) if cpu["avg"] != float("inf") else 0,
                "cpu_min_duration": int(cpu["min"]),
                "cpu_max_duration": int(cpu["max"]),
                "cpu_std_dev": cpu.get("std", 0),
                "nnapi_duration": int(nnapi["avg"]) if nnapi["avg"] != float("inf") else 0,
                "nnapi_min_duration": int(nnapi["min"]),
                "nnapi_max_duration": int(nnapi["max"]),
                "nnapi_std_dev": nnapi.get("std", 0),
                **mem,
                "in_dim_0": 1, "in_dim_1": 3,
                "in_dim_2": target_h, "in_dim_3": target_h,
                "accuracy": acc,
                "device_analytics": analytics,
            }
            if nnapi["status"] == "failed":
                report["nnapi_error"] = nnapi.get("error", "")

            # Save: out/nn/stat/run/onnx/fp32/{task}_{dataset}_acc_{model}/android_{device}.json
            folder = STAT_DIR / f"{task}_{dataset}_acc_{name}"
            folder.mkdir(parents=True, exist_ok=True)
            report_path = folder / f"android_{device_name}.json"
            with open(report_path, "w") as f:
                json.dump(report, f, indent=2)

            logger.info(f"   ✅ Done — best: {winner} = {report['duration']} µs")
            logger.info(f"   📁 {report_path}")

            state["processed"].append(name)
            save_state(state)
            session_count += 1
            gc.collect()

        except Exception as e:
            logger.error(f"   ❌ Failed: {e}")
            logger.debug(traceback.format_exc())
            state["failed"].append(name)
            save_state(state)
            skipped[name] = str(e)
            with open(skipped_models_json, "w") as f:
                json.dump(skipped, f, indent=2)

    # ── Upload to HuggingFace ────────────────────────────────────────────
    if args.push_hf:
        try:
            from huggingface_hub import create_repo, upload_folder
            logger.info("☁️ Uploading to HuggingFace Hub...")
            hf_repo = "NN-Dataset/onnx"
            create_repo(hf_repo, repo_type="model", exist_ok=True)
            upload_folder(
                folder_path=str(ONNX_TEMP),
                repo_id=hf_repo,
                repo_type="model",
            )
            # Also upload the JSONs
            upload_folder(
                folder_path=str(STAT_DIR),
                repo_id=hf_repo,
                repo_type="model",
            )
            logger.info("✅ Upload complete")
        except Exception as e:
            logger.error(f"❌ HF Upload failed: {e}")

    # ── Summary ──────────────────────────────────────────────────────────
    ok, fail = len(state["processed"]), len(state["failed"])
    logger.info(f"\n{'='*55}")
    logger.info(f"  SUMMARY: ✅ {ok} succeeded, ❌ {fail} failed")
    logger.info(f"{'='*55}")
    if state["failed"]:
        logger.info(f"  Failed: {', '.join(state['failed'])}")
        logger.info("  Re-run to retry failed models.")
    logger.info(f"  Reports: {STAT_DIR.resolve()}")


if __name__ == "__main__":
    main()
