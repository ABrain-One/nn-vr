import json
import time
import platform
import socket
from pathlib import Path

import psutil

from unity_runner import run_unity_benchmark


# --------------------------------------------------
# PATHS
# --------------------------------------------------

ONNX_DIR = Path("_work/onnx_temp")

BENCHMARK_JSON = Path("unity_benchmarks.json")


# --------------------------------------------------
# SYSTEM INFO
# --------------------------------------------------

WORKSTATION_NAME = socket.gethostname()

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


# --------------------------------------------------
# CORE FUNCTION
# --------------------------------------------------

def run_benchmarks(onnx_dir: Path = ONNX_DIR, benchmark_json: Path = BENCHMARK_JSON):
    """
    Iterate over all ONNX files in onnx_dir, run each through Unity
    Barracuda batchmode, and persist results to benchmark_json.

    Already-benchmarked models (valid=True) are skipped automatically,
    so this function is safe to call repeatedly for resume behaviour.
    """

    # Load existing results for resume (handles empty / corrupt file safely)
    benchmark_results = {}
    if benchmark_json.exists() and benchmark_json.stat().st_size > 0:
        try:
            with open(benchmark_json, "r") as f:
                benchmark_results = json.load(f)
        except json.JSONDecodeError:
            print(f"WARNING: {benchmark_json} is corrupt or empty — starting fresh.")

    onnx_files = sorted(onnx_dir.glob("*.onnx"))

    print(f"FOUND {len(onnx_files)} ONNX MODELS")

    for onnx_path in onnx_files:

        model_name = onnx_path.stem

        # --------------------------------------------------
        # SKIP ALREADY BENCHMARKED
        # --------------------------------------------------

        if (
            model_name in benchmark_results
            and benchmark_results[model_name].get("valid") is True
        ):
            print(f"SKIPPING {model_name} (already benchmarked)")
            continue

        print("\n" + "=" * 60)
        print(f"BENCHMARKING: {model_name}")
        print("=" * 60)

        try:

            benchmark_start = time.time()

            result = run_unity_benchmark(onnx_path)

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

            inference_time_ms = result.get("inference_time_ms", 0)

            duration_ns = int(inference_time_ms * 1_000_000)

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

            benchmark_results[model_name] = {

                "model_name": model_name,

                "device_type": WORKSTATION_NAME,

                "os_version": OS_VERSION,

                "python_version": PYTHON_VERSION,

                "valid": True,

                "emulator": False,

                "iterations": ITERATIONS,

                "duration": duration_ns,

                "unit": "Barracuda",

                # CPU timings — Barracuda exposes one timing value
                "cpu_duration": duration_ns,
                "cpu_min_duration": duration_ns,
                "cpu_max_duration": duration_ns,
                "cpu_std_dev": 0.0,

                # GPU timings — placeholder compatibility values
                "gpu_duration": duration_ns,
                "gpu_min_duration": duration_ns,
                "gpu_max_duration": duration_ns,
                "gpu_std_dev": 0.0,

                # NPU timings — desktop Barracuda has no NPU
                "npu_duration": 0,
                "npu_min_duration": 0,
                "npu_max_duration": 0,
                "npu_std_dev": 0.0,

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
                    "memory_info": {
                        "total_ram_gb": round(
                            TOTAL_RAM_KB / (1024 * 1024),
                            2
                        )
                    }
                }
            }

            print(f"SUCCESS: {model_name}")

        except Exception as e:

            print(f"FAILED: {model_name}")
            print(str(e))

            benchmark_results[model_name] = {

                "model_name": model_name,
                "device_type": WORKSTATION_NAME,
                "os_version": OS_VERSION,
                "valid": False,
                "emulator": False,
                "runtime": "Barracuda",
                "model_format": "onnx",
                "error": str(e),
                "device_analytics": {
                    "timestamp": time.time()
                }
            }

        # --------------------------------------------------
        # SAVE AFTER EVERY MODEL
        # --------------------------------------------------

        with open(benchmark_json, "w") as f:
            json.dump(benchmark_results, f, indent=2)

        print(f"SAVED: {benchmark_json}")

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