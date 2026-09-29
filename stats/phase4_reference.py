#!/usr/bin/env python3
"""
phase4_reference.py
Computes Unity overhead by comparing Unity latency with LEMUR standalone PyTorch latency.
"""
import pandas as pd
import json
import os
from pathlib import Path
import numpy as np

REPO = Path(__file__).resolve().parent.parent
STATS_DIR = REPO / "stats"
LEMUR_RUN_DIR = REPO / "nn-dataset" / "ab" / "nn" / "stat" / "run" / "pt" / "fp32"
NS_TO_MS = 1 / 1_000_000

def load_lemur_inference(model_name: str) -> dict | None:
    """Load LEMUR standalone PyTorch inference timings."""
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
    print("PHASE 4: UNITY OVERHEAD VS LEMUR STANDALONE")
    print("=" * 70)
    
    real_gpu_csv = STATS_DIR / "aggregated_real_gpu_stats.csv"
    if not real_gpu_csv.exists():
        print("Missing real GPU CSV")
        return
        
    df_real = pd.read_csv(real_gpu_csv)
    
    records = []
    
    print("Extracting LEMUR standalone timings...")
    for idx, row in df_real.iterrows():
        model_name = row['model_name']
        lemur_data = load_lemur_inference(model_name)
        if lemur_data:
            lemur_cpu_ms = lemur_data["cpu_duration"] * NS_TO_MS
            lemur_gpu_ms = lemur_data["gpu_duration"] * NS_TO_MS
            
            records.append({
                "model_name": model_name,
                "unity_cpu_ms": row["cpu_mean_ms"],
                "unity_gpu_ms": row["gpu_mean_ms"],
                "lemur_cpu_ms": lemur_cpu_ms,
                "lemur_gpu_ms": lemur_gpu_ms,
                "cpu_overhead_multiplier": row["cpu_mean_ms"] / lemur_cpu_ms if lemur_cpu_ms > 0 else np.nan,
                "gpu_overhead_multiplier": row["gpu_mean_ms"] / lemur_gpu_ms if lemur_gpu_ms > 0 else np.nan
            })
            
    df_overhead = pd.DataFrame(records)
    print(f"Matched {len(df_overhead)} models with LEMUR reference data.")
    
    if len(df_overhead) > 0:
        cpu_mean_mult = df_overhead["cpu_overhead_multiplier"].mean()
        gpu_mean_mult = df_overhead["gpu_overhead_multiplier"].mean()
        
        print(f"\nCPU Overhead Multiplier: {cpu_mean_mult:.2f}x (Unity CPU is {cpu_mean_mult:.2f}x slower than Standalone CPU)")
        print(f"GPU Overhead Multiplier: {gpu_mean_mult:.2f}x (Unity GPU is {gpu_mean_mult:.2f}x slower than Standalone GPU)")
        
        out_csv = STATS_DIR / "unity_overhead.csv"
        df_overhead.to_csv(out_csv, index=False)
        print(f"\nSaved overhead data to {out_csv.relative_to(REPO)}")

if __name__ == "__main__":
    main()
