import json
import os
import glob
import statistics
from pathlib import Path
from collections import defaultdict

stat_dir = Path("out/nn/stat")

# 1. Analyze Variance across 5 versions
benchmark_stats = defaultdict(lambda: {"cpu_avg": [], "gpu_avg": []})

for i in range(1, 6):
    v_dir = stat_dir / f"version{i}" / "onnx" / "fp32"
    if v_dir.exists():
        for file_path in v_dir.glob("*/linux_guest*.json"):
            model_name = file_path.parent.name.split("_acc_")[-1]
            try:
                with open(file_path, "r") as f:
                    data = json.load(f)
                    if data.get("success"):
                        benchmark_stats[model_name]["cpu_avg"].append(data["cpu"]["avg_ms"])
                        benchmark_stats[model_name]["gpu_avg"].append(data["gpu"]["avg_ms"])
            except:
                pass

valid_models = 0
cpu_variances = []
gpu_variances = []

for model, stats in benchmark_stats.items():
    if len(stats["cpu_avg"]) == 5:
        valid_models += 1
        cpu_cv = (statistics.stdev(stats["cpu_avg"]) / statistics.mean(stats["cpu_avg"])) * 100 if statistics.mean(stats["cpu_avg"]) > 0 else 0
        gpu_cv = (statistics.stdev(stats["gpu_avg"]) / statistics.mean(stats["gpu_avg"])) * 100 if statistics.mean(stats["gpu_avg"]) > 0 else 0
        cpu_variances.append(cpu_cv)
        gpu_variances.append(gpu_cv)

print("=== VARIANCE ANALYSIS ACROSS 5 VERSIONS ===")
print(f"Models with 5 successful runs: {valid_models}")
if valid_models > 0:
    print(f"Average CPU Latency Coefficient of Variation (CV): {statistics.mean(cpu_variances):.2f}%")
    print(f"Max CPU Latency CV: {max(cpu_variances):.2f}%")
    print(f"Average GPU Latency Coefficient of Variation (CV): {statistics.mean(gpu_variances):.2f}%")
    print(f"Max GPU Latency CV: {max(gpu_variances):.2f}%")
print("")

# 2. Analyze Failed Exports
failed_exports_dir = stat_dir / "failed_exports"
export_errors = defaultdict(int)
export_layer_stats = {"Conv": [], "Linear": [], "Activation": [], "BatchNorm": [], "Pooling": []}
total_failed_exports = 0

if failed_exports_dir.exists():
    for file_path in failed_exports_dir.glob("*.json"):
        total_failed_exports += 1
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
                err_msg = data.get("error_message", "").split("\n")[-1] if data.get("error_message") else "Unknown"
                # Simplify error message
                if "Unsupported ONNX opset version" in err_msg:
                    err_msg = "Unsupported ONNX opset version"
                elif "RuntimeError:" in err_msg:
                    err_msg = err_msg.split("RuntimeError:")[1][:100]
                elif "AssertionError:" in err_msg:
                    err_msg = err_msg.split("AssertionError:")[1][:100]
                export_errors[err_msg.strip()] += 1
                
                arch = data.get("architecture", {})
                for k in export_layer_stats.keys():
                    if arch.get(k) is not None:
                        export_layer_stats[k].append(arch.get(k))
        except:
            pass

print("=== FAILED EXPORT ANALYSIS ===")
print(f"Total Failed Exports: {total_failed_exports}")
if total_failed_exports > 0:
    print("Top Error Causes:")
    for k, v in sorted(export_errors.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  - {v} times: {k}")
    print("\nAverage Architecture of Failed Models:")
    for k, v in export_layer_stats.items():
        if v:
            print(f"  - {k} layers: {statistics.mean(v):.1f} (max: {max(v)})")
print("")

# 3. Analyze Failed Benchmarks
benchmark_errors = defaultdict(int)
total_failed_benchmarks = 0

for i in range(1, 6):
    fail_dir = stat_dir / f"version{i}" / "failed_benchmarks"
    if fail_dir.exists():
        for file_path in fail_dir.glob("*.json"):
            total_failed_benchmarks += 1
            try:
                with open(file_path, "r") as f:
                    data = json.load(f)
                    err_msg = data.get("error_summary", "Unknown Error")
                    if "ComputePrecompiled" in err_msg:
                        err_msg = "ComputePrecompiled exception"
                    benchmark_errors[err_msg.strip()] += 1
            except:
                pass

print("=== FAILED BENCHMARK ANALYSIS ===")
print(f"Total Failed Benchmarks (across all versions): {total_failed_benchmarks}")
if total_failed_benchmarks > 0:
    print("Top Error Causes:")
    for k, v in sorted(benchmark_errors.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  - {v} times: {k}")

