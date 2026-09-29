#!/usr/bin/env python3
"""
aggregate_real_gpu_stats.py — Aggregate per-model CPU+GPU timings from real GPU runs.

Reads JSON files from out/nn/stat/real_gpu_versions/version{1-6}/onnx/fp32/
and produces:
  1. stats/aggregated_real_gpu_stats.csv — per-model aggregated timings
  2. stats/real_gpu_timing_summary.json — overall statistics
  
Duration units in source JSON: NANOSECONDS (Unity ms × 1,000,000)
Output CSV: MILLISECONDS (ns / 1,000,000)

Also joins with nn-dataset architectural metadata for correlation analysis.
"""
import json
import os
import csv
import sys
from pathlib import Path
from collections import defaultdict
import numpy as np
import scipy.stats as stats

REPO = Path(__file__).resolve().parent.parent
GPU_DIR = REPO / "out" / "nn" / "stat" / "real_gpu_versions"
LLVMPIPE_DIR = REPO / "out" / "nn" / "stat" / "run_llvmpipe_old"
NN_STAT_DIR = REPO / "nn-dataset" / "ab" / "nn" / "stat" / "nn"
LEMUR_RUN_DIR = REPO / "nn-dataset" / "ab" / "nn" / "stat" / "run" / "pt" / "fp32"
STATS_DIR = REPO / "stats"
STATS_DIR.mkdir(exist_ok=True)

NS_TO_MS = 1 / 1_000_000  # nanoseconds to milliseconds


def mean_ci(data, confidence=0.95):
    """Return (mean, half-width of CI)."""
    a = np.array(data, dtype=float)
    n = len(a)
    if n < 2:
        return float(np.mean(a)), 0.0
    m = float(np.mean(a))
    se = float(stats.sem(a))
    h = se * stats.t.ppf((1 + confidence) / 2.0, n - 1)
    return m, h


def collect_timings_for_version(version_dir: Path) -> dict:
    """Walk all JSON files in a version dir, return {model_name: record}."""
    onnx_dir = version_dir / "onnx" / "fp32"
    if not onnx_dir.exists():
        return {}

    results = {}
    for model_dir in onnx_dir.iterdir():
        if not model_dir.is_dir():
            continue
        for jf in model_dir.iterdir():
            if not jf.name.endswith(".json"):
                continue
            try:
                data = json.loads(jf.read_text(encoding="utf-8"))
            except Exception:
                continue
            if data.get("valid") is not True:
                continue
            name = data.get("model_name")
            if not name:
                continue
            cpu_dur = data.get("cpu_duration")
            gpu_dur = data.get("gpu_duration")
            if cpu_dur is None or gpu_dur is None:
                continue
            results[name] = {
                "cpu_ns": cpu_dur,
                "gpu_ns": gpu_dur,
                "cpu_ms": cpu_dur * NS_TO_MS,
                "gpu_ms": gpu_dur * NS_TO_MS,
                "cpu_min_ns": data.get("cpu_min_duration"),
                "cpu_max_ns": data.get("cpu_max_duration"),
                "gpu_min_ns": data.get("gpu_min_duration"),
                "gpu_max_ns": data.get("gpu_max_duration"),
                "cpu_std_ms": data.get("cpu_std_dev", 0),
                "gpu_std_ms": data.get("gpu_std_dev", 0),
            }
    return results


def load_nn_metadata(model_name: str) -> dict | None:
    """Load architectural metadata from nn-dataset/ab/nn/stat/nn/."""
    # Try exact match first
    for suffix in ["", ".json"]:
        path = NN_STAT_DIR / f"{model_name}{suffix}"
        if path.exists():
            try:
                return json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                pass
    return None


def load_lemur_inference(model_name: str) -> dict | None:
    """Load LEMUR standalone PyTorch inference timings."""
    # The LEMUR run directories use the format:
    # img-classification_cifar-10_acc_{model_name}/Linux_MS-7E27.json
    # We need to search across datasets
    for dataset_prefix in [
        "img-classification_cifar-10_acc",
        "img-classification_cifar-100_acc",
        "img-classification_imagenette_acc",
    ]:
        dir_name = f"{dataset_prefix}_{model_name}"
        model_dir = LEMUR_RUN_DIR / dir_name
        if model_dir.exists():
            for jf in model_dir.iterdir():
                if jf.name.endswith(".json"):
                    try:
                        data = json.loads(jf.read_text(encoding="utf-8"))
                        if data.get("valid") and data.get("cpu_duration"):
                            return data
                    except Exception:
                        pass
    return None


def main():
    print("=" * 70)
    print("AGGREGATING REAL GPU BENCHMARK DATA")
    print("=" * 70)

    # ── Step 1: Collect timings from all 6 versions ──────────────────────
    version_data = {}
    for i in range(1, 7):
        vdir = GPU_DIR / f"version{i}"
        print(f"\nScanning version{i}...")
        timings = collect_timings_for_version(vdir)
        version_data[f"version{i}"] = timings
        print(f"  Found {len(timings)} valid models with CPU+GPU timings")

    # ── Step 2: Aggregate across versions (mean of means) ────────────────
    all_models = set()
    for v_data in version_data.values():
        all_models.update(v_data.keys())
    
    print(f"\nTotal unique models across all versions: {len(all_models)}")

    aggregated = {}
    for model_name in sorted(all_models):
        cpu_values = []
        gpu_values = []
        for v_name, v_data in version_data.items():
            if model_name in v_data:
                cpu_values.append(v_data[model_name]["cpu_ms"])
                gpu_values.append(v_data[model_name]["gpu_ms"])
        
        if not cpu_values:
            continue
        
        cpu_mean, cpu_ci = mean_ci(cpu_values)
        gpu_mean, gpu_ci = mean_ci(gpu_values)
        
        aggregated[model_name] = {
            "cpu_mean_ms": cpu_mean,
            "cpu_ci_ms": cpu_ci,
            "gpu_mean_ms": gpu_mean,
            "gpu_ci_ms": gpu_ci,
            "num_versions": len(cpu_values),
            "cpu_cv": float(np.std(cpu_values) / np.mean(cpu_values)) if np.mean(cpu_values) > 0 else 0,
            "gpu_cv": float(np.std(gpu_values) / np.mean(gpu_values)) if np.mean(gpu_values) > 0 else 0,
        }

    print(f"Aggregated {len(aggregated)} models with timing data")

    # ── Step 3: Join with nn-dataset metadata ────────────────────────────
    print("\nJoining with nn-dataset metadata...")
    metadata_hits = 0
    for model_name, agg in aggregated.items():
        meta = load_nn_metadata(model_name)
        if meta:
            metadata_hits += 1
            agg["total_layers"] = meta.get("total_layers")
            agg["total_params"] = meta.get("total_params")
            agg["flops"] = meta.get("flops")
            agg["has_attention"] = meta.get("has_attention")
            agg["has_residual_connections"] = meta.get("has_residual_connections")
            agg["is_resnet_like"] = meta.get("is_resnet_like")
            agg["is_vgg_like"] = meta.get("is_vgg_like")
            agg["is_transformer_like"] = meta.get("is_transformer_like")
            agg["is_mobilenet_like"] = meta.get("is_mobilenet_like")
            agg["model_size_mb"] = meta.get("model_size_mb")
    print(f"  Metadata found for {metadata_hits}/{len(aggregated)} models")

    # ── Step 4: Write CSV ────────────────────────────────────────────────
    csv_path = STATS_DIR / "aggregated_real_gpu_stats.csv"
    fieldnames = [
        "model_name", "cpu_mean_ms", "cpu_ci_ms", "gpu_mean_ms", "gpu_ci_ms",
        "num_versions", "cpu_cv", "gpu_cv",
        "total_layers", "total_params", "flops", "model_size_mb",
        "has_attention", "has_residual_connections",
        "is_resnet_like", "is_vgg_like", "is_transformer_like", "is_mobilenet_like",
    ]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for name in sorted(aggregated.keys()):
            row = {"model_name": name, **aggregated[name]}
            writer.writerow(row)
    print(f"\nWritten: {csv_path.relative_to(REPO)}")

    # ── Step 5: Compute overall statistics ───────────────────────────────
    print("\n" + "=" * 70)
    print("REAL GPU TIMING SUMMARY")
    print("=" * 70)

    all_cpu = [a["cpu_mean_ms"] for a in aggregated.values()]
    all_gpu = [a["gpu_mean_ms"] for a in aggregated.values()]
    
    cpu_overall_mean, cpu_overall_ci = mean_ci(all_cpu)
    gpu_overall_mean, gpu_overall_ci = mean_ci(all_gpu)
    
    ratios = [a["cpu_mean_ms"] / a["gpu_mean_ms"] for a in aggregated.values() if a["gpu_mean_ms"] > 0]
    ratio_mean, ratio_ci = mean_ci(ratios)
    
    gpu_faster = sum(1 for r in ratios if r > 1.0)
    cpu_faster = sum(1 for r in ratios if r < 1.0)
    
    summary = {
        "hardware": "Actual GPU (NVIDIA, Vulkan, -force-vulkan, VK_ICD_FILENAMES=nvidia_icd.json)",
        "total_models_with_timings": len(aggregated),
        "cpu_mean_ms": round(cpu_overall_mean, 4),
        "cpu_ci_ms": round(cpu_overall_ci, 4),
        "gpu_mean_ms": round(gpu_overall_mean, 4),
        "gpu_ci_ms": round(gpu_overall_ci, 4),
        "cpu_gpu_ratio_mean": round(ratio_mean, 4),
        "cpu_gpu_ratio_ci": round(ratio_ci, 4),
        "gpu_faster_count": gpu_faster,
        "cpu_faster_count": cpu_faster,
        "gpu_faster_pct": round(gpu_faster / len(ratios) * 100, 1) if ratios else 0,
        "cpu_faster_pct": round(cpu_faster / len(ratios) * 100, 1) if ratios else 0,
        "duration_unit": "milliseconds",
        "source_unit": "nanoseconds (Unity ms × 1,000,000)",
    }
    
    print(f"Models with timing data: {summary['total_models_with_timings']}")
    print(f"CPU mean: {summary['cpu_mean_ms']:.4f} ± {summary['cpu_ci_ms']:.4f} ms")
    print(f"GPU mean: {summary['gpu_mean_ms']:.4f} ± {summary['gpu_ci_ms']:.4f} ms")
    print(f"CPU/GPU ratio: {summary['cpu_gpu_ratio_mean']:.4f} ± {summary['cpu_gpu_ratio_ci']:.4f}")
    print(f"GPU faster: {summary['gpu_faster_count']}/{len(ratios)} ({summary['gpu_faster_pct']:.1f}%)")
    print(f"CPU faster: {summary['cpu_faster_count']}/{len(ratios)} ({summary['cpu_faster_pct']:.1f}%)")
    
    summary_path = STATS_DIR / "real_gpu_timing_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2))
    print(f"\nWritten: {summary_path.relative_to(REPO)}")

    # ── Step 6: Correlation analysis ─────────────────────────────────────
    print("\n" + "=" * 70)
    print("CORRELATION ANALYSIS (Real GPU)")
    print("=" * 70)
    
    models_with_meta = [a for a in aggregated.values() if a.get("flops") is not None]
    if models_with_meta:
        cpu_t = np.array([m["cpu_mean_ms"] for m in models_with_meta])
        gpu_t = np.array([m["gpu_mean_ms"] for m in models_with_meta])
        flops = np.array([m["flops"] for m in models_with_meta])
        params = np.array([m["total_params"] for m in models_with_meta])
        layers = np.array([m["total_layers"] for m in models_with_meta])
        
        from scipy.stats import pearsonr
        
        correlations = {}
        for feat_name, feat_vals in [("FLOPs", flops), ("Params", params), ("Layers", layers)]:
            mask = np.isfinite(feat_vals) & (feat_vals > 0)
            if mask.sum() > 2:
                r_cpu, _ = pearsonr(cpu_t[mask], feat_vals[mask])
                r_gpu, _ = pearsonr(gpu_t[mask], feat_vals[mask])
                correlations[feat_name] = {"cpu": round(r_cpu, 4), "gpu": round(r_gpu, 4)}
                print(f"  CPU Time vs {feat_name}: R = {r_cpu:.4f}")
                print(f"  GPU Time vs {feat_name}: R = {r_gpu:.4f}")
        
        summary["correlations"] = correlations
        summary["models_with_metadata"] = len(models_with_meta)
        summary_path.write_text(json.dumps(summary, indent=2))
    else:
        print("  No models with metadata found for correlation analysis")

    print("\n✅ Done!")


if __name__ == "__main__":
    main()
