#!/usr/bin/env python3
"""Experiment B primary protocol: Unity 6 Inference Engine, frozen ONNX contract.

This module never writes Experiment A campaigns.  The primary B protocol is a
same-export-contract comparison (ONNX opset 12, IR 7, dynamo=False) because A's
low-storage workflow correctly removed its transient ONNX artifacts.  A later
newer-opset protocol must use a separate module and campaign namespace.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import platform
import time
import traceback
from pathlib import Path

from scripts.shape_utils import infer_image_resolution, infer_in_out_shapes


ROOT_DIR = Path(__file__).resolve().parent.parent.parent
EXPERIMENT_ROOT = ROOT_DIR / "out" / "nn" / "stat"
WORK_DIR = ROOT_DIR / "_work"
CONFIG_PREFIX = "img-classification_cifar-10_acc"
EXPERIMENT_NAME = "Experiment B primary: same-export-contract Unity Inference Engine"
TIMING_PROTOCOL = "completion_aware_inference_engine_v1"
UNITY_VERSION = "6000.6.5f1"
INFERENCE_ENGINE_PACKAGE = "com.unity.ai.inference@2.6.1"
CPU_BACKEND = "CPU"
GPU_BACKEND = "GPUCompute"
WARMUPS = 5
ITERATIONS = 20
PRIMARY_PREFIX = "inference_engine_opset12_completion_aware"


def get_input_size(transform_str: str) -> int:
    return infer_image_resolution(transform_str) or 32


def atomic_json(path: Path, value: dict) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def sanitize_filename(value: str) -> str:
    return "".join(char if (char.isalnum() or char in ("-", "_")) else "_" for char in value)


def result_path(campaign_dir: Path, model_name: str, device_type: str) -> Path:
    os_prefix = "windows" if platform.system() == "Windows" else "linux"
    return campaign_dir / "onnx" / "fp32" / f"{CONFIG_PREFIX}_{model_name}" / f"{os_prefix}_{sanitize_filename(device_type)}.json"


def is_completed(campaign_dir: Path, model_name: str) -> bool:
    from ab.vr.inference_engine_runner import get_device_type

    path = result_path(campaign_dir, model_name, get_device_type())
    try:
        return json.loads(path.read_text(encoding="utf-8")).get("stages", {}).get("cleanup") in {"success", "failed"}
    except (OSError, json.JSONDecodeError):
        return False


def cleanup_temporary_artifacts(onnx_path: Path) -> None:
    for path in (onnx_path, onnx_path.with_suffix(".onnx.data")):
        path.unlink(missing_ok=True)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


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
    if "downloadtoarray" in text or "material" in text or "readback" in text:
        return "output_materialization_or_completion_failure"
    if "gpucompute" in text:
        return "gpu_execution_failure"
    if "backendtype.cpu" in text or "cpu" in text:
        return "cpu_execution_failure"
    if "modelasset" in text or "inference" in text or "onnx" in text:
        return "unity_inference_engine_load_or_execution_failure"
    return "unity_inference_engine_load_or_execution_failure"


def run_model(campaign_dirs: list[Path], work_dir: Path, model_name: str, row, logger: logging.Logger) -> None:
    """Export/validate once and run the exact artifact in all requested B repeats."""
    import ast
    import psutil
    import onnx
    from ab.vr.inference_engine_runner import get_device_type, run_unity_benchmark
    from ab.vr.onnx_exporter import export_onnx
    from ab.vr.onnx_validator import eval_onnx_accuracy

    def record_for(campaign_dir: Path) -> dict:
        return {
            "experiment": EXPERIMENT_NAME,
            "comparison_role": "primary_same_export_contract_runtime_comparison",
            "campaign": campaign_dir.name,
            "timing_protocol": TIMING_PROTOCOL,
            "model_name": model_name,
            "valid": False,
            "stages": {stage: "not_started" for stage in ("acquisition", "export", "validation", "unity", "cleanup")},
            "environment": {
                "unity_version_expected": UNITY_VERSION,
                "runtime_expected": "Unity Inference Engine",
                "inference_engine_package_expected": INFERENCE_ENGINE_PACKAGE,
                "cpu_backend_expected": CPU_BACKEND,
                "gpu_backend_expected": GPU_BACKEND,
            },
            "artifact_provenance": "deterministic Experiment A export contract re-created because A low-storage cleanup removed transient ONNX files",
        }

    records = {campaign: record_for(campaign) for campaign in campaign_dirs}
    onnx_path = work_dir / "onnx_temp" / f"{model_name}.onnx"
    started = time.time()
    stage = "acquisition"
    try:
        for record in records.values():
            record["stages"][stage] = "success"
        prm = row.get("prm", {})
        if isinstance(prm, str):
            prm = ast.literal_eval(prm)
        target_h = get_input_size(prm.get("transform", ""))
        input_shape, _ = infer_in_out_shapes(
            dataset=row.get("dataset", "cifar-10"), transform_str=prm.get("transform", "")
        )
        export_configuration = {
            "comparison_control": "same exporter/opset/IR contract as Experiment A; runtime is the intended changed factor",
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
        exported_model = onnx.load(onnx_path)
        main_opsets = [entry.version for entry in exported_model.opset_import if entry.domain in ("", "ai.onnx")]
        onnx_metadata = {"main_opsets": main_opsets, "ir_version": exported_model.ir_version, "sha256": sha256(onnx_path)}
        if main_opsets != [12] or exported_model.ir_version != 7:
            raise RuntimeError(f"exported ONNX violates B primary contract: opsets={main_opsets}, IR={exported_model.ir_version}")
        for record in records.values():
            record["stages"][stage] = "success"
            record["onnx_size_mb"] = round(onnx_path.stat().st_size / (1024 * 1024), 2)
            record["onnx_exported"] = onnx_metadata

        stage = "validation"
        accuracy = eval_onnx_accuracy(onnx_path, target_h, work_dir / "data")
        for record in records.values():
            record["onnx_accuracy"] = accuracy
            record["stages"][stage] = "success"

        campaign_items = list(records.items())
        for index, (campaign_dir, record) in enumerate(campaign_items):
            stage = "unity"
            try:
                unity = run_unity_benchmark(onnx_path, input_shape)
                if not unity.get("success"):
                    raise RuntimeError(unity.get("error", "Unity returned success=false"))
                if unity.get("timing_protocol") != TIMING_PROTOCOL:
                    raise RuntimeError("Unity result did not identify the B completion-aware timing protocol")
                if unity.get("runtime") != "Unity Inference Engine" or unity.get("inference_engine_package") != INFERENCE_ENGINE_PACKAGE:
                    raise RuntimeError("Unity result identifies an unexpected runtime or package")
                if unity.get("backend_cpu") != CPU_BACKEND or unity.get("backend_gpu") != GPU_BACKEND:
                    raise RuntimeError(f"unexpected B backends: {unity.get('backend_cpu')}, {unity.get('backend_gpu')}")
                if unity.get("gpu_api") != "Vulkan" or "RTX 4090" not in unity.get("gpu_name", "") or "nvidia" not in unity.get("gpu_name", "").lower():
                    raise RuntimeError(f"unexpected GPU environment: {unity.get('gpu_name')} / {unity.get('gpu_api')}")
                for backend in ("cpu", "gpu"):
                    stats = unity.get(backend) or {}
                    if stats.get("warmup_iterations") != WARMUPS or stats.get("measured_iterations") != ITERATIONS or len(stats.get("samples_ms") or []) != ITERATIONS:
                        raise RuntimeError(f"{backend} iteration evidence is incomplete")
                    if stats.get("completion_operation") != "Tensor<float>.DownloadToArray()":
                        raise RuntimeError(f"{backend} did not report blocking output materialization")
                record["unity"] = unity
                cpu, gpu = unity["cpu"], unity["gpu"]
                record.update({
                    "iterations": ITERATIONS, "duration": int(gpu["avg_ms"] * 1_000_000), "unit": "gpu",
                    "cpu_duration": int(cpu["avg_ms"] * 1_000_000), "cpu_min_duration": int(cpu["min_ms"] * 1_000_000), "cpu_max_duration": int(cpu["max_ms"] * 1_000_000), "cpu_std_dev": cpu["std_dev_ms"],
                    "gpu_duration": int(gpu["avg_ms"] * 1_000_000), "gpu_min_duration": int(gpu["min_ms"] * 1_000_000), "gpu_max_duration": int(gpu["max_ms"] * 1_000_000), "gpu_std_dev": gpu["std_dev_ms"],
                    "runtime": "Unity Inference Engine", "model_format": "onnx", "backend": GPU_BACKEND,
                    "unity_version": unity["unity_version"], "input_shape": unity["input_shape"], "output_shape": unity["output_shape"],
                })
                record["stages"][stage] = "success"
                record["valid"] = True
            except Exception as exc:
                record.update({"failure_type": classify_failure(stage, exc), "error": str(exc), "traceback": traceback.format_exc()})
                record["stages"][stage] = "failed"
                logger.exception("%s failed during B Unity benchmark for %s", model_name, campaign_dir.name)
                if record["failure_type"] == "timeout_or_infrastructure_failure":
                    for skipped_dir, skipped in campaign_items[index + 1:]:
                        skipped.update({"failure_type": "not_run_after_unity_timeout", "error": f"Not independently measured: {campaign_dir.name} timed out with the same shared ONNX artifact.", "timeout_source_campaign": campaign_dir.name, "execution_status": "not_independently_measured"})
                        skipped["stages"]["unity"] = "not_run_after_timeout"
                    break
    except Exception as exc:
        for record in records.values():
            record.update({"failure_type": classify_failure(stage, exc), "error": str(exc), "traceback": traceback.format_exc()})
            record["stages"][stage] = "failed"
        logger.exception("%s failed during B %s", model_name, stage)
    finally:
        try:
            cleanup_temporary_artifacts(onnx_path)
            for record in records.values():
                record["stages"]["cleanup"] = "success"
        except OSError as exc:
            for record in records.values():
                record["stages"]["cleanup"] = "failed"
                record["cleanup_error"] = str(exc)
                record["valid"] = False
        device_type = get_device_type()
        for campaign_dir, record in records.items():
            record["benchmark_duration_sec"] = round(time.time() - started, 2)
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
    parser = argparse.ArgumentParser(description="Experiment B primary Unity Inference Engine comparison (opset 12 / IR 7)")
    parser.add_argument("models", nargs="?", help="Comma-separated model identifiers")
    parser.add_argument("--all", action="store_true", help="Run the established complete architecture/checkpoint population")
    parser.add_argument("--rerun", action="store_true", help="Re-run named models even when a record exists")
    parser.add_argument("--campaign", help=f"One primary B campaign, e.g. {PRIMARY_PREFIX}_v1")
    parser.add_argument("--all-versions", action="store_true", help="Reuse one export across all six primary B repeat campaigns")
    args = parser.parse_args()
    allowed_campaigns = {f"{PRIMARY_PREFIX}_validation", *(f"{PRIMARY_PREFIX}_v{i}" for i in range(1, 7))}
    if args.all_versions and args.campaign:
        parser.error("use --all-versions without --campaign")
    if not args.all_versions and not args.campaign:
        parser.error("provide --campaign or --all-versions")
    if args.campaign and args.campaign not in allowed_campaigns:
        parser.error(f"campaign must be {PRIMARY_PREFIX}_validation or {PRIMARY_PREFIX}_v1 through _v6")
    if args.all and args.models:
        parser.error("use either a model list or --all, not both")

    from ab.vr.process_models import _discover_models_from_arch_hf
    model_configs = _discover_models_from_arch_hf(dataset="cifar-10")
    models = list(model_configs) if args.all else [name.strip() for name in (args.models or "").split(",") if name.strip()]
    if not models:
        parser.error("provide a model list or --all")
    unknown = [name for name in models if name not in model_configs]
    if unknown:
        parser.error(f"model(s) absent from the established architecture/checkpoint population: {', '.join(unknown)}")

    campaign_names = [f"{PRIMARY_PREFIX}_v{i}" for i in range(1, 7)] if args.all_versions else [args.campaign]
    campaign_dirs = [EXPERIMENT_ROOT / name for name in campaign_names]
    (WORK_DIR / "onnx_temp").mkdir(parents=True, exist_ok=True)
    for campaign_dir in campaign_dirs:
        campaign_dir.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("experiment_b")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    logger.addHandler(logging.FileHandler(EXPERIMENT_ROOT / "experiment_b_opset12_all_versions.log" if args.all_versions else campaign_dirs[0] / "experiment_b.log", encoding="utf-8"))
    logger.addHandler(logging.StreamHandler())
    for campaign_dir in campaign_dirs:
        atomic_json(campaign_dir / "manifest.json", {
            "experiment": EXPERIMENT_NAME, "comparison_role": "primary_same_export_contract_runtime_comparison", "campaign": campaign_dir.name,
            "timing_protocol": TIMING_PROTOCOL, "population_configuration_source": "process_models._discover_models_from_arch_hf(dataset='cifar-10')",
            "models_requested": models, "unity_version": UNITY_VERSION, "runtime": "Unity Inference Engine", "inference_engine_package": INFERENCE_ENGINE_PACKAGE,
            "onnx_opset_version": 12, "onnx_ir_version": 7, "exporter": "torch.onnx.export(dynamo=False)",
            "cpu_backend": CPU_BACKEND, "gpu_backend": GPU_BACKEND, "warmup_iterations": WARMUPS, "measured_iterations": ITERATIONS,
            "shared_export_across_versions": args.all_versions,
            "artifact_provenance": "A's transient ONNX artifacts were deleted by low-storage cleanup; B recreates and metadata-verifies the exact export contract before all B repeats.",
            "secondary_newer_opset_experiment": "not part of this namespace or script",
        })
    for name in models:
        pending = campaign_dirs if args.rerun else [campaign for campaign in campaign_dirs if not is_completed(campaign, name)]
        if not pending:
            logger.info("Skipping completed model %s in all requested B campaigns", name)
            continue
        logger.info("Processing model %s in %s", name, ", ".join(campaign.name for campaign in pending))
        run_model(pending, WORK_DIR, name, model_configs[name], logger)


if __name__ == "__main__":
    main()
