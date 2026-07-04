import time
import platform
from pathlib import Path
import json

import psutil

from ab.vr.unity_runner import (
    get_device_type,
    is_model_benchmarked,
    run_unity_benchmark,
    save_model_record,
)


# --------------------------------------------------
# PATHS
# --------------------------------------------------

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
ONNX_DIR = ROOT_DIR / "_work" / "onnx_temp"


# --------------------------------------------------
# SYSTEM INFO
# --------------------------------------------------

DEVICE_TYPE = get_device_type()

OS_VERSION = platform.platform()

PYTHON_VERSION = platform.python_version()

TOTAL_RAM_KB = int(
    psutil.virtual_memory().total / 1024
)

FREE_RAM_KB = int(
    psutil.virtual_memory().free / 1024
)

AVAILABLE_RAM_KB = int(
    psutil.virtual_memory().available / 1024
)

CPU_CORES = psutil.cpu_count(logical=True)

CPU_NAME = platform.processor()

UNITY_VERSION = "2022.3.62f3"

ITERATIONS = 20

def classify_failure(error: str):

    error = error.lower()

    if "3221225477" in error:
        return "unity_native_crash"

    if "timeout" in error:
        return "timeout"

    if "no unity results json found" in error:
        return "missing_results"

    if "unsupported" in error:
        return "unsupported_operator"

    return "unknown"

# --------------------------------------------------
# CORE FUNCTION
# --------------------------------------------------

def run_benchmarks(onnx_dir: Path = ONNX_DIR, models: list[str] = None):
    """
    Iterate over all ONNX files in onnx_dir, run each through Unity
    Barracuda batchmode, and persist one JSON per model under
    out/nn/stat/run/onnx/fp32/img-classification_cifar-10_acc_{model}/.

    Already-benchmarked models (valid=True) are skipped automatically,
    so this function is safe to call repeatedly for resume behaviour.
    """

    benchmark_results = {}

    onnx_files = sorted(onnx_dir.glob("*.onnx"))
    if models:
        models_set = set(models)
        onnx_files = [f for f in onnx_files if f.stem in models_set]
    # lets only benchmark the first 5 models
    # onnx_files = sorted(onnx_dir.glob("*.onnx"))[:500]

    print(f"FOUND {len(onnx_files)} ONNX MODELS")

    for onnx_path in onnx_files:

        model_name = onnx_path.stem

        # --------------------------------------------------
        # SKIP ALREADY BENCHMARKED
        # --------------------------------------------------

        if is_model_benchmarked(model_name, device_type=DEVICE_TYPE):
            print(f"SKIPPING {model_name} (already benchmarked)")
            continue

        print("\n" + "=" * 60)
        print(f"BENCHMARKING: {model_name}")
        print("=" * 60)

        try:

            benchmark_start = time.time()

            result = run_unity_benchmark(onnx_path)
            print("\nRAW UNITY RESULT:")
            print(json.dumps(result, indent=2))

            if not result.get("success", False):
                raise RuntimeError(
                    result.get("error", "Unity benchmark failed")
                )

            benchmark_duration_sec = round(
                time.time() - benchmark_start,
                2
            )

            # --------------------------------------------------
            # MODEL SIZE
            # --------------------------------------------------

            model_size_mb = round(
                onnx_path.stat().st_size / (1024 * 1024),
                2
            )

            # --------------------------------------------------
            # TIMING CONVERSION
            # Unity returns milliseconds → convert to nanoseconds
            # --------------------------------------------------

            cpu_stats = result.get("cpu", {})
            gpu_stats = result.get("gpu", {})

            cpu_avg_ms = cpu_stats.get("avg_ms", 0)
            cpu_min_ms = cpu_stats.get("min_ms", 0)
            cpu_max_ms = cpu_stats.get("max_ms", 0)
            cpu_std_ms = cpu_stats.get("std_dev_ms", 0)

            gpu_avg_ms = gpu_stats.get("avg_ms", 0)
            gpu_min_ms = gpu_stats.get("min_ms", 0)
            gpu_max_ms = gpu_stats.get("max_ms", 0)
            gpu_std_ms = gpu_stats.get("std_dev_ms", 0)

            cpu_duration_ns = int(cpu_avg_ms * 1_000_000)
            cpu_min_ns = int(cpu_min_ms * 1_000_000)
            cpu_max_ns = int(cpu_max_ms * 1_000_000)

            gpu_duration_ns = int(gpu_avg_ms * 1_000_000)
            gpu_min_ns = int(gpu_min_ms * 1_000_000)
            gpu_max_ns = int(gpu_max_ms * 1_000_000)

            # --------------------------------------------------
            # INPUT SHAPE
            # --------------------------------------------------

            input_shape = result.get("input_shape", [0, 0, 0, 0])

            while len(input_shape) < 4:
                input_shape.append(0)

            # --------------------------------------------------
            # OUTPUT SHAPE
            # --------------------------------------------------

            output_shape = result.get("output_shape", [0, 0, 0, 0])

            while len(output_shape) < 4:
                output_shape.append(0)

            # --------------------------------------------------
            # SAVE SUCCESS RESULT
            # --------------------------------------------------

            record = {

                "model_name": model_name,

                "device_type": DEVICE_TYPE,

                "os_version": OS_VERSION,

                "python_version": PYTHON_VERSION,

                "valid": True,

                "emulator": False,

                "iterations": ITERATIONS,

                "duration": gpu_duration_ns,

                "unit": "gpu",

                # CPU timings — Barracuda exposes one timing value
                "cpu_duration": cpu_duration_ns,
                "cpu_min_duration": cpu_min_ns,
                "cpu_max_duration": cpu_max_ns,
                "cpu_std_dev": cpu_std_ms,

                # GPU timings — placeholder compatibility values
                "gpu_duration": gpu_duration_ns,
                "gpu_min_duration": gpu_min_ns,
                "gpu_max_duration": gpu_max_ns,
                "gpu_std_dev": gpu_std_ms,

                # NPU timings — desktop Barracuda has no NPU
                "npu_duration": None,
                "npu_min_duration": None,
                "npu_max_duration": None,
                "npu_std_dev": None,
                "npu_backend": "unsupported",

                # Memory
                "total_ram_kb": TOTAL_RAM_KB,
                "free_ram_kb": FREE_RAM_KB,
                "available_ram_kb": AVAILABLE_RAM_KB,
                "cached_kb": 0,

                # Input dimensions
                "in_dim_0": input_shape[0],
                "in_dim_1": input_shape[1],
                "in_dim_2": input_shape[2],
                "in_dim_3": input_shape[3],

                # Output dimensions
                "out_dim_0": output_shape[0],
                "out_dim_1": output_shape[1],
                "out_dim_2": output_shape[2],
                "out_dim_3": output_shape[3],

                # Metadata
                "model_size_mb": model_size_mb,
                "runtime": "Barracuda",
                "model_format": "onnx",
                "backend": result.get("backend", "ComputePrecompiled"),
                "unity_version": UNITY_VERSION,
                "benchmark_duration_sec": benchmark_duration_sec,

                "device_analytics": {
                    "timestamp": time.time(),
                    "cpu_info": {
                        "cpu_cores": CPU_CORES,
                        "processor": CPU_NAME
                    },
                    "gpu_info": {
                        "gpu_name": result.get("gpu_name", ""),
                        "gpu_api": result.get("gpu_api", "")
                    },
                    "memory_info": {
                        "total_ram_gb": round(
                            TOTAL_RAM_KB / (1024 * 1024),
                            2
                        )
                    }
                }
            }

            out_path = save_model_record(record)
            benchmark_results[model_name] = record
            print(f"SUCCESS: {model_name}")
            print(f"SAVED: {out_path}")

        except Exception as e:

            print(f"FAILED: {model_name}")
            print(str(e))

            record = {

                "model_name": model_name,
                "device_type": DEVICE_TYPE,
                "os_version": OS_VERSION,
                "valid": False,
                "emulator": False,
                "runtime": "Barracuda",
                "model_format": "onnx",
                "error": str(e),
                "failure_type": classify_failure(str(e)),
                "device_analytics": {
                    "timestamp": time.time()
                }
            }

            out_path = save_model_record(record)
            benchmark_results[model_name] = record
            print(f"SAVED: {out_path}")

    # --------------------------------------------------
    # FINAL SUMMARY
    # --------------------------------------------------

    success_count = sum(
        1 for x in benchmark_results.values()
        if x.get("valid") is True
    )

    failure_count = sum(
        1 for x in benchmark_results.values()
        if x.get("valid") is False
    )

    print("\n" + "=" * 60)
    print("BENCHMARK COMPLETE")
    print("=" * 60)
    print(f"SUCCESS: {success_count}")
    print(f"FAILED : {failure_count}")

    return benchmark_results


# --------------------------------------------------
# STANDALONE ENTRY POINT
# --------------------------------------------------

if __name__ == "__main__":
    run_benchmarks()