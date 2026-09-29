#!/usr/bin/env python3
"""
generate_stats.py — Regenerate all benchmark statistics files.

Run from the nn-vr project root:
    python stats/generate_stats.py

Output files (written to stats/):
    cpu_gpu_emulated_versions.json  — 6 llvmpipe/CPU benchmark run counts
    real_gpu_versions.json          — 6 real GPU benchmark run counts
    export_stats.json               — ONNX export pass/fail counts
    run_history.md                  — Human-readable version history table

Pass/fail counting logic:
    A model is PASSED in a version if ANY result JSON in onnx/fp32/ for that
    model has "valid": true.
    A model is FAILED  if it has no valid==true record anywhere in that version
    (it may still have a valid==false record in onnx/fp32/ or an entry in
    failed_benchmarks/ — both represent unsuccessful attempts).
    This means retry-successes are correctly reflected: only models that never
    succeeded across all retries within a version are counted as failed.
"""

import json
from pathlib import Path

# ── Roots ────────────────────────────────────────────────────────────────────
REPO_ROOT     = Path(__file__).resolve().parent.parent
STAT_ROOT     = REPO_ROOT / "out" / "nn" / "stat"
LLVMPIPE_DIR  = STAT_ROOT / "run_llvmpipe_old"          # version1 … version6
GPU_DIR       = STAT_ROOT / "real_gpu_versions"          # version1 … version6 (GPU)
EXPORTS_DIR   = STAT_ROOT / "failed_exports"             # ONNX export failure records
ALL_MODELS_FILE = STAT_ROOT / "run" / "onnx" / "fp32" / "all_models.json"  # export accuracy map
STATS_DIR     = REPO_ROOT / "stats"
STATS_DIR.mkdir(exist_ok=True)


# ── Core helper ──────────────────────────────────────────────────────────────

def count_version(version_dir: Path, allowed_models: set[str] | None = None) -> dict:
    """
    Count genuinely passed and genuinely failed models for one version.

    Rules:
      - Scan every *.json under onnx/fp32/ (recursively).
      - A model is 'passed' if it has at least one record with valid==true.
      - A model is 'failed' if it exists in the data (onnx/fp32 or
        failed_benchmarks) but has NO valid==true record.
    """
    onnx_fp32 = version_dir / "onnx" / "fp32"
    failed_dir = version_dir / "failed_benchmarks"

    # Collect per-model validity: model_name → True if ever succeeded
    model_valid: dict = {}

    # Walk onnx/fp32 results (both valid=True and valid=False land here)
    if onnx_fp32.exists():
        for json_file in onnx_fp32.rglob("*.json"):
            try:
                data = json.loads(json_file.read_text(encoding="utf-8"))
            except Exception:
                continue
            name = data.get("model_name")
            if not name:
                continue
            was_valid = data.get("valid") is True
            # Once a model passes, it stays passed (max over retries)
            model_valid[name] = model_valid.get(name, False) or was_valid

    # Also collect model names that only appear in failed_benchmarks
    # (they won't appear in onnx/fp32 if they crashed before any result was saved)
    if failed_dir.exists():
        for json_file in failed_dir.glob("*.json"):
            try:
                data = json.loads(json_file.read_text(encoding="utf-8"))
            except Exception:
                continue
            name = data.get("model_name") or json_file.stem
            if name and name not in model_valid:
                model_valid[name] = False

    # Historical llvmpipe directories contain one stale record for a model that
    # later appears in failed_exports/. Restricting to the canonical successful-
    # export set prevents that pre-export artifact from changing a benchmark
    # denominator. No raw result is deleted.
    if allowed_models is not None:
        model_valid = {
            name: valid for name, valid in model_valid.items()
            if name in allowed_models
        }

    passed = sum(1 for v in model_valid.values() if v)
    failed = sum(1 for v in model_valid.values() if not v)
    return {"benchmark_passed": passed, "benchmark_failed": failed}


def collect_versions(
    base_dir: Path, num_versions: int = 6, allowed_models: set[str] | None = None
) -> dict:
    """Build per-version stats dict for versions 1..num_versions."""
    versions = {}
    for i in range(1, num_versions + 1):
        v_name = f"version{i}"
        v_dir = base_dir / v_name
        if v_dir.exists():
            versions[v_name] = count_version(v_dir, allowed_models)
        else:
            versions[v_name] = {"benchmark_passed": 0, "benchmark_failed": 0}
    return versions


# ── 1. CPU / Software-emulated GPU (llvmpipe) ────────────────────────────────

def write_llvmpipe_stats():
    # all_models.json is the canonical population that actually completed ONNX
    # export (1,732 models). Earlier llvmpipe folders contain one stale result
    # for rag-0941355086027897acb251dc222fd9f2, which is an export failure.
    all_models = json.loads(ALL_MODELS_FILE.read_text(encoding="utf-8"))
    versions = collect_versions(LLVMPIPE_DIR, allowed_models=set(all_models))
    out = {
        "hardware": "CPU + Software-emulated GPU (Mesa llvmpipe, -force-vulkan)",
        "note": "6 independent benchmark runs restricted to the 1,732 canonical ONNX-export-successful models.",
        "versions": versions,
    }
    path = STATS_DIR / "cpu_gpu_emulated_versions.json"
    path.write_text(json.dumps(out, indent=2))
    print(f"Written: {path.relative_to(REPO_ROOT)}")
    return versions


# ── 2. Real GPU benchmark versions ───────────────────────────────────────────

def write_real_gpu_stats():
    versions = collect_versions(GPU_DIR)
    out = {
        "hardware": "Actual GPU (NVIDIA, Vulkan, -force-vulkan, VK_ICD_FILENAMES=nvidia_icd.json)",
        "note": "6 independent benchmark runs on the same ONNX exports.",
        "versions": versions,
    }
    path = STATS_DIR / "real_gpu_versions.json"
    path.write_text(json.dumps(out, indent=2))
    print(f"Written: {path.relative_to(REPO_ROOT)}")
    return versions


# ── 3. ONNX Export stats ─────────────────────────────────────────────────────

def write_export_stats():
    """
    Export pass = models in all_models.json (the accuracy map written by the
    export stage for every successfully exported model).
    Export fail = one JSON per model in failed_exports/ (written by process_models.py
    for every model that crashed during ONNX export).
    """
    # Export passed: all_models.json is the canonical list of successfully exported models
    export_passed = 0
    if ALL_MODELS_FILE.exists():
        try:
            all_models = json.loads(ALL_MODELS_FILE.read_text(encoding="utf-8"))
            export_passed = len(all_models)
        except Exception as e:
            print(f"  WARNING: could not read all_models.json: {e}")

    # Export failed: live failed_exports/ directory
    failed_models = []
    if EXPORTS_DIR.exists():
        for json_file in sorted(EXPORTS_DIR.glob("*.json")):
            try:
                data = json.loads(json_file.read_text(encoding="utf-8"))
                name = data.get("model_name") or json_file.stem
            except Exception:
                name = json_file.stem
            failed_models.append(name)

    export_failed = len(failed_models)
    total = export_passed + export_failed

    out = {
        "total_models": total,
        "export_passed": export_passed,
        "export_failed": export_failed,
        "failed_models": sorted(failed_models),
    }
    path = STATS_DIR / "export_stats.json"
    path.write_text(json.dumps(out, indent=2))
    print(f"Written: {path.relative_to(REPO_ROOT)}")
    return out


# ── 4. Run history table ──────────────────────────────────────────────────────

def write_run_history(llvmpipe_versions: dict, gpu_versions: dict, export_info: dict):
    lines = [
        "# Benchmark Run History",
        "",
        "Tracks every benchmark run across both hardware environments.",
        "Pass/fail counts reflect **unique model outcomes** — a model that initially",
        "failed but succeeded on retry is counted as **passed only**.",
        "",
        "## ONNX Export",
        "",
        "| Total Models | Export Passed | Export Failed |",
        "|---|---|---|",
        f"| {export_info['total_models']} | {export_info['export_passed']} | {export_info['export_failed']} |",
        "",
        "## CPU + Software-emulated GPU Runs (Mesa llvmpipe)",
        "",
        "| Version  | Architecture                   | Benchmark Passed | Benchmark Failed | Notes                              |",
        "|----------|--------------------------------|-----------------:|-----------------:|------------------------------------|",
    ]

    notes_llvmpipe = {
        "version1": "First run — higher failure rate (v1 baseline)",
        "version2": "Reduced failures after retry tuning",
        "version3": "Stable",
        "version4": "Stable",
        "version5": "Stable",
        "version6": "Extended run",
    }

    for v_name, counts in llvmpipe_versions.items():
        passed = counts["benchmark_passed"]
        failed = counts["benchmark_failed"]
        note   = notes_llvmpipe.get(v_name, "")
        lines.append(
            f"| {v_name:<8} | CPU + llvmpipe (Software GPU)  | {passed:>16} | {failed:>16} | {note:<34} |"
        )

    lines += [
        "",
        "## Actual GPU Runs (NVIDIA Vulkan)",
        "",
        "| Version  | Architecture                   | Benchmark Passed | Benchmark Failed | Notes                              |",
        "|----------|--------------------------------|-----------------:|-----------------:|------------------------------------|",
    ]

    for v_name, counts in gpu_versions.items():
        passed = counts["benchmark_passed"]
        failed = counts["benchmark_failed"]
        status = "Pending" if (passed == 0 and failed == 0) else ""
        lines.append(
            f"| {v_name:<8} | NVIDIA GPU (Vulkan)            | {passed:>16} | {failed:>16} | {status:<34} |"
        )

    lines += [
        "",
        "---",
        "_Auto-generated by `stats/generate_stats.py`. Re-run after each benchmark version to refresh._",
    ]

    path = STATS_DIR / "run_history.md"
    path.write_text("\n".join(lines) + "\n")
    print(f"Written: {path.relative_to(REPO_ROOT)}")


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    print("Generating stats...\n")

    print("── CPU/llvmpipe versions ──────────────────")
    llvmpipe_versions = write_llvmpipe_stats()

    print("\n── Real GPU versions ──────────────────────")
    gpu_versions = write_real_gpu_stats()

    print("\n── ONNX export stats ──────────────────────")
    export_info = write_export_stats()

    print("\n── Run history table ──────────────────────")
    write_run_history(llvmpipe_versions, gpu_versions, export_info)

    print("\nAll stats files written to stats/")


if __name__ == "__main__":
    main()
