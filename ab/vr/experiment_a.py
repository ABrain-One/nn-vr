#!/usr/bin/env python3
"""Experiment A: low-storage, completion-aware Barracuda benchmark runner.

This intentionally reuses the established model lookup, ONNX exporter and ONNX
accuracy validator, but gives Experiment A its own state, log and result tree.
It must be run by the physical-hardware operator; it does not launch campaigns
on its own.
"""

from __future__ import annotations

import argparse
import json
import logging
import platform
import time
import traceback
from pathlib import Path

from scripts.shape_utils import infer_image_resolution


ROOT_DIR = Path(__file__).resolve().parent.parent.parent
EXPERIMENT_ROOT = ROOT_DIR / "out" / "nn" / "stat"
WORK_DIR = ROOT_DIR / "_work"
CONFIG_PREFIX = "img-classification_cifar-10_acc"
TIMING_PROTOCOL = "completion_aware_v1"
UNITY_VERSION = "2022.3.62f3"
BARRACUDA_VERSION = "3.0.2"
CPU_BACKEND = "CSharpBurst"
GPU_BACKEND = "ComputePrecompiled"
WARMUPS = 5
ITERATIONS = 20


def get_input_size(transform_str: str) -> int:
    """Same model-specific resolution rule used by process_models.py."""
    return infer_image_resolution(transform_str) or 32


def atomic_json(path: Path, value: dict) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def sanitize_filename(value: str) -> str:
    return "".join(char if (char.isalnum() or char in ("-", "_")) else "_" for char in value)


def result_path(campaign_dir: Path, model_name: str, device_type: str) -> Path:
    os_prefix = "windows" if platform.system() == "Windows" else "linux"
    filename = f"{os_prefix}_{sanitize_filename(device_type)}.json"
    return campaign_dir / "onnx" / "fp32" / f"{CONFIG_PREFIX}_{model_name}" / filename


def is_completed(campaign_dir: Path, model_name: str) -> bool:
    from ab.vr.unity_runner import get_device_type

    path = result_path(campaign_dir, model_name, get_device_type())
    if not path.exists():
        return False
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
        # Match the established pipeline's default resume semantics: both a
        # completed success and a classified completed failure are retained
        # within this campaign.  --rerun remains the explicit retry path.
        return record.get("stages", {}).get("cleanup") in {"success", "failed"}
    except (OSError, json.JSONDecodeError):
        return False


def cleanup_temporary_artifacts(onnx_path: Path) -> None:
    """Remove only per-model transient artifacts, never permanent results."""
    for path in (onnx_path, onnx_path.with_suffix(".onnx.data")):
        try:
            path.unlink(missing_ok=True)
        except OSError as exc:
            raise RuntimeError(f"temporary cleanup failed for {path}: {exc}") from exc


def classify_failure(stage: str, error: Exception | str) -> str:
    text = str(error).lower()
    if stage == "acquisition":
        return "model_acquisition_or_loading_failure"
    if stage == "export":
        return "onnx_export_failure"
    if stage == "validation":
        return "onnx_validation_failure"
    if "requires the physical nvidia rtx 4090" in text or "requires vulkan" in text:
        return "infrastructure_or_unintended_gpu_failure"
    if "timeout" in text or "timed out" in text:
        return "timeout_or_infrastructure_failure"
    if "material" in text or "readback" in text or "toreadonlyarray" in text:
        return "output_materialization_or_completion_failure"
    if "csharburst" in text:
        return "cpu_execution_failure"
    if "computeprecompiled" in text:
        return "gpu_execution_failure"
    return "unity_barracuda_load_or_execution_failure"


def run_model(campaign_dirs: list[Path], work_dir: Path, model_name: str, row, logger: logging.Logger) -> None:
    """Export and validate once, then benchmark that ONNX in every requested campaign.

    Campaigns are repeat measurements.  Keeping the transient ONNX alive for
    this inner loop makes those repetitions comparable and avoids a needless
    download/export cycle between them.
    """
    import onnx
    from ab.vr.onnx_exporter import export_onnx
    from ab.vr.onnx_validator import eval_onnx_accuracy
    from ab.vr.unity_runner import get_device_type, run_unity_benchmark
    import psutil

    def new_record(campaign_dir: Path) -> dict:
        return {
            "experiment": "Experiment A",
            "campaign": campaign_dir.name,
            "timing_protocol": TIMING_PROTOCOL,
            "model_name": model_name,
            "valid": False,
            "stages": {"acquisition": "not_started", "export": "not_started", "validation": "not_started", "unity": "not_started", "cleanup": "not_started"},
            "environment": {"unity_version_expected": UNITY_VERSION, "barracuda_version_expected": BARRACUDA_VERSION, "cpu_backend_expected": CPU_BACKEND, "gpu_backend_expected": GPU_BACKEND},
        }

    records = {campaign_dir: new_record(campaign_dir) for campaign_dir in campaign_dirs}
    onnx_path = work_dir / "onnx_temp" / f"{model_name}.onnx"
    start = time.time()
    stage = "acquisition"
    try:
        for record in records.values():
            record["stages"][stage] = "success"
        prm = row.get("prm", {})
        if isinstance(prm, str):
            import ast
            prm = ast.literal_eval(prm)
        target_h = get_input_size(prm.get("transform", ""))
        export_configuration = {
            "population_configuration_source": "process_models._discover_models_from_arch_hf(dataset='cifar-10')",
            "dataset": row.get("dataset", ""),
            "checkpoint_source": "NN-Dataset/checkpoints-epoch-50",
            "precision": "fp32",
            "opset_version": 12,
            "onnx_ir_version": 7,
            "exporter": "torch.onnx.export(dynamo=False)",
            "dynamic_axes": {"input": {"0": "batch_size"}, "output": {"0": "batch_size"}},
            "input_shape_source": "existing model-specific infer_in_out_shapes",
            "target_height": target_h,
        }
        for record in records.values():
            record["export_configuration"] = export_configuration

        stage = "export"
        export_onnx(row, onnx_path, timeout_sec=120.0)
        for record in records.values():
            record["stages"][stage] = "success"
            record["onnx_size_mb"] = round(onnx_path.stat().st_size / (1024 * 1024), 2)
        exported_model = onnx.load(onnx_path)
        exported_opsets = [entry.version for entry in exported_model.opset_import if entry.domain in ("", "ai.onnx")]
        onnx_exported = {
            "main_opsets": exported_opsets,
            "ir_version": exported_model.ir_version,
        }
        for record in records.values():
            record["onnx_exported"] = onnx_exported
        if exported_opsets != [12] or exported_model.ir_version != 7:
            raise RuntimeError(
                f"exported ONNX violates the frozen Barracuda contract: opsets={exported_opsets}, IR={exported_model.ir_version}"
            )

        stage = "validation"
        onnx_accuracy = eval_onnx_accuracy(onnx_path, target_h, work_dir / "data")
        for record in records.values():
            record["onnx_accuracy"] = onnx_accuracy
            record["stages"][stage] = "success"

        # A Unity invocation is deliberately repeated for each campaign, but
        # all six use the exact same downloaded/exported/validated ONNX file.
        campaign_items = list(records.items())
        for campaign_index, (campaign_dir, record) in enumerate(campaign_items):
            stage = "unity"
            try:
                unity = run_unity_benchmark(onnx_path)
                if not unity.get("success"):
                    raise RuntimeError(unity.get("error", "Unity returned success=false"))
                if unity.get("timing_protocol") != TIMING_PROTOCOL:
                    raise RuntimeError("Unity result does not identify completion_aware_v1 timing")
                if unity.get("backend_cpu") != CPU_BACKEND or unity.get("backend_gpu") != GPU_BACKEND:
                    raise RuntimeError(f"unexpected backends: {unity.get('backend_cpu')}, {unity.get('backend_gpu')}")
                if unity.get("gpu_api") != "Vulkan" or "RTX 4090" not in unity.get("gpu_name", "") or "nvidia" not in unity.get("gpu_name", "").lower():
                    raise RuntimeError(f"unexpected GPU environment: {unity.get('gpu_name')} / {unity.get('gpu_api')}")
                for backend in ("cpu", "gpu"):
                    stats = unity.get(backend) or {}
                    if stats.get("warmup_iterations") != WARMUPS or stats.get("measured_iterations") != ITERATIONS or len(stats.get("samples_ms") or []) != ITERATIONS:
                        raise RuntimeError(f"{backend} iteration evidence is incomplete")
                    if stats.get("completion_operation") != "Tensor.ToReadOnlyArray()":
                        raise RuntimeError(f"{backend} did not report the blocking materialization operation")
                record["unity"] = unity
                cpu = unity["cpu"]
                gpu = unity["gpu"]
                # Retain the familiar legacy-statistics fields alongside the complete
                # Unity evidence so downstream readers can discover these records by
                # the standard campaign layout without mistaking their timing protocol.
                record.update({
            "iterations": ITERATIONS,
            "duration": int(gpu["avg_ms"] * 1_000_000),
            "unit": "gpu",
            "cpu_duration": int(cpu["avg_ms"] * 1_000_000),
            "cpu_min_duration": int(cpu["min_ms"] * 1_000_000),
            "cpu_max_duration": int(cpu["max_ms"] * 1_000_000),
            "cpu_std_dev": cpu["std_dev_ms"],
            "gpu_duration": int(gpu["avg_ms"] * 1_000_000),
            "gpu_min_duration": int(gpu["min_ms"] * 1_000_000),
            "gpu_max_duration": int(gpu["max_ms"] * 1_000_000),
            "gpu_std_dev": gpu["std_dev_ms"],
            "runtime": "Barracuda",
            "model_format": "onnx",
            "backend": GPU_BACKEND,
            "unity_version": unity["unity_version"],
            "input_shape": unity["input_shape"],
            "output_shape": unity["output_shape"],
                })
                record["stages"][stage] = "success"
                record["valid"] = True
            except Exception as exc:
                record["failure_type"] = classify_failure(stage, exc)
                record["error"] = str(exc)
                record["traceback"] = traceback.format_exc()
                record["stages"][stage] = "failed"
                logger.exception("%s failed during Unity for %s", model_name, campaign_dir.name)
                # A 300-second timeout is not a timing sample.  Repeating the
                # same hung invocation five more times against the identical
                # ONNX only burns server time and can leave Unity helpers
                # behind.  Preserve the evidence from the actual attempt and
                # mark the remaining repetitions as deliberately unmeasured.
                if record["failure_type"] == "timeout_or_infrastructure_failure":
                    for skipped_campaign_dir, skipped_record in campaign_items[campaign_index + 1:]:
                        skipped_record["failure_type"] = "not_run_after_unity_timeout"
                        skipped_record["error"] = (
                            f"Not independently measured: {campaign_dir.name} timed out after 300 seconds "
                            "with the same shared ONNX artifact."
                        )
                        skipped_record["timeout_source_campaign"] = campaign_dir.name
                        skipped_record["stages"]["unity"] = "not_run_after_timeout"
                        skipped_record["execution_status"] = "not_independently_measured"
                    break
    except Exception as exc:
        for record in records.values():
            record["failure_type"] = classify_failure(stage, exc)
            record["error"] = str(exc)
            record["traceback"] = traceback.format_exc()
            record["stages"][stage] = "failed"
        logger.exception("%s failed during %s", model_name, stage)
    finally:
        try:
            cleanup_temporary_artifacts(onnx_path)
            for record in records.values():
                record["stages"]["cleanup"] = "success"
        except Exception as cleanup_exc:
            for record in records.values():
                record["stages"]["cleanup"] = "failed"
                record["cleanup_error"] = str(cleanup_exc)
                record["valid"] = False
        device_type = get_device_type()
        for campaign_dir, record in records.items():
            record["benchmark_duration_sec"] = round(time.time() - start, 2)
            record["host"] = {"device_type": device_type, "os_version": platform.platform(), "python_version": platform.python_version(), "cpu": platform.processor(), "logical_cpu_count": psutil.cpu_count(logical=True)}
            output = result_path(campaign_dir, model_name, device_type)
            output.parent.mkdir(parents=True, exist_ok=True)
            atomic_json(output, record)
            failure_output = campaign_dir / "failed_benchmarks" / f"{model_name}.json"
            if record["valid"]:
                failure_output.unlink(missing_ok=True)
            else:
                failure_output.parent.mkdir(parents=True, exist_ok=True)
                atomic_json(failure_output, record)


def main() -> None:
    parser = argparse.ArgumentParser(description="Experiment A low-storage completion-aware Barracuda benchmark")
    parser.add_argument("models", nargs="?", help="Comma-separated model identifiers")
    parser.add_argument("--all", action="store_true", help="Run the established complete architecture/checkpoint population")
    parser.add_argument("--rerun", action="store_true", help="Re-run named models even when this campaign already has valid records")
    parser.add_argument("--campaign", help="One Experiment A namespace, e.g. barracuda_completion_aware_v1")
    parser.add_argument("--all-versions", action="store_true", help="For each model, reuse one export across all six repeat campaigns")
    args = parser.parse_args()
    allowed_campaigns = {"barracuda_completion_aware_validation", *(f"barracuda_completion_aware_v{i}" for i in range(1, 7))}
    if args.all_versions and args.campaign:
        parser.error("use --all-versions without --campaign")
    if not args.all_versions and not args.campaign:
        parser.error("provide --campaign or --all-versions")
    if args.campaign and args.campaign not in allowed_campaigns:
        parser.error("campaign must be barracuda_completion_aware_validation or barracuda_completion_aware_v1 through barracuda_completion_aware_v6")
    if args.all and args.models:
        parser.error("use either a model list or --all, not both")
    # Use exactly the established full-population discovery configuration for
    # both validation and campaigns.  Named validation must not select a
    # different per-dataset metadata row than --all would select.
    from ab.vr.process_models import _discover_models_from_arch_hf
    model_configs = _discover_models_from_arch_hf(dataset="cifar-10")
    if args.all:
        models = list(model_configs.keys())
    else:
        models = [name.strip() for name in (args.models or "").split(",") if name.strip()]
    if not models:
        parser.error("provide a model list or --all")
    unknown = [name for name in models if name not in model_configs]
    if unknown:
        parser.error(f"model(s) absent from the established architecture/checkpoint population: {', '.join(unknown)}")

    campaign_names = [f"barracuda_completion_aware_v{i}" for i in range(1, 7)] if args.all_versions else [args.campaign]
    campaign_dirs = [EXPERIMENT_ROOT / name for name in campaign_names]
    # Preserve the repository's established low-storage work location.  The
    # campaign directory contains permanent benchmark records only.
    work_dir = WORK_DIR
    (work_dir / "onnx_temp").mkdir(parents=True, exist_ok=True)
    for campaign_dir in campaign_dirs:
        campaign_dir.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("experiment_a")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    logger.addHandler(logging.FileHandler(EXPERIMENT_ROOT / "experiment_a_all_versions.log" if args.all_versions else campaign_dirs[0] / "experiment_a.log", encoding="utf-8"))
    logger.addHandler(logging.StreamHandler())
    for campaign_dir in campaign_dirs:
        atomic_json(campaign_dir / "manifest.json", {"experiment": "Experiment A", "campaign": campaign_dir.name, "timing_protocol": TIMING_PROTOCOL, "population_configuration_source": "process_models._discover_models_from_arch_hf(dataset='cifar-10')", "models_requested": models, "unity_version": UNITY_VERSION, "barracuda_version": BARRACUDA_VERSION, "cpu_backend": CPU_BACKEND, "gpu_backend": GPU_BACKEND, "warmup_iterations": WARMUPS, "measured_iterations": ITERATIONS, "shared_export_across_versions": args.all_versions})
    for name in models:
        pending_campaign_dirs = campaign_dirs if args.rerun else [campaign_dir for campaign_dir in campaign_dirs if not is_completed(campaign_dir, name)]
        if not pending_campaign_dirs:
            logger.info("Skipping completed model %s in all requested campaigns", name)
            continue
        logger.info("Processing model %s in %s", name, ", ".join(campaign_dir.name for campaign_dir in pending_campaign_dirs))
        run_model(pending_campaign_dirs, work_dir, name, model_configs[name], logger)


if __name__ == "__main__":
    main()
