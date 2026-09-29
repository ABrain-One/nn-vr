#!/usr/bin/env python3
"""
phase2_analysis.py
Computes remaining Phase 2 items:
1. Overlap analysis between llvmpipe and real GPU pass/fail sets.
2. Architectural failure rates for real GPU.
3. Llvmpipe distortion factors.
"""
import pandas as pd
import json
import os
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
STATS_DIR = REPO / "stats"

def main():
    print("=" * 70)
    print("PHASE 2 ANALYSIS")
    print("=" * 70)
    
    llvmpipe_csv = REPO / "aggregated_unity_stats.csv"
    real_gpu_csv = STATS_DIR / "aggregated_real_gpu_stats.csv"
    
    if not llvmpipe_csv.exists() or not real_gpu_csv.exists():
        print("Missing CSV files!")
        return

    df_llvm = pd.read_csv(llvmpipe_csv)
    df_real = pd.read_csv(real_gpu_csv)
    
    # 1. Overlap Analysis
    llvm_success = set(df_llvm[df_llvm["status"] == "success"]["model_name"])
    real_success = set(df_real["model_name"])
    
    print(f"Llvmpipe successful models: {len(llvm_success)}")
    print(f"Real GPU successful models: {len(real_success)}")
    
    both = llvm_success.intersection(real_success)
    only_llvm = llvm_success - real_success
    only_real = real_success - llvm_success
    
    print(f"Models successful in BOTH: {len(both)}")
    print(f"Models successful in Llvmpipe ONLY: {len(only_llvm)}")
    print(f"Models successful in Real GPU ONLY: {len(only_real)}")
    
    # 2. Distortion Factors
    print("\n" + "=" * 70)
    print("LLVMPIPE DISTORTION FACTORS")
    print("=" * 70)
    
    # Merge on model_name
    df_both = pd.merge(
        df_llvm[df_llvm["status"] == "success"][["model_name", "unity_cpu_duration_mean", "unity_gpu_duration_mean"]],
        df_real[["model_name", "cpu_mean_ms", "gpu_mean_ms"]],
        on="model_name",
        how="inner"
    )
    
    # Distortion = llvmpipe GPU latency / real GPU latency
    df_both["distortion"] = df_both["unity_gpu_duration_mean"] / df_both["gpu_mean_ms"]
    
    mean_dist = df_both["distortion"].mean()
    median_dist = df_both["distortion"].median()
    min_dist = df_both["distortion"].min()
    max_dist = df_both["distortion"].max()
    
    print(f"Evaluated {len(df_both)} models for distortion")
    print(f"Mean distortion: {mean_dist:.2f}x (llvmpipe is {mean_dist:.2f}x slower than real GPU)")
    print(f"Median distortion: {median_dist:.2f}x")
    print(f"Min distortion: {min_dist:.2f}x")
    print(f"Max distortion: {max_dist:.2f}x")
    
    # 3. Architectural Failure Rates (Real GPU)
    print("\n" + "=" * 70)
    print("ARCHITECTURAL FAILURE RATES (Real GPU)")
    print("=" * 70)
    
    # We need the total list of exported models to compute failure rates.
    # We can get it from export_stats.json or by looking at the full list of models in nn-dataset.
    # The llvmpipe CSV has the full list of exported models (1762 rows, 1732 exported successfully).
    exported_models = df_llvm[df_llvm["error_msg"] != "Export Failed"]
    print(f"Total exported models: {len(exported_models)}")
    
    # Let's map architectures
    arch_families = [
        ("has_attention", "Attention"),
        ("is_transformer_like", "Transformer"),
        ("is_resnet_like", "ResNet"),
        ("is_vgg_like", "VGG"),
        ("is_mobilenet_like", "MobileNet")
    ]
    
    for col, name in arch_families:
        # Number of exported models of this family
        family_total = len(exported_models[exported_models[col] == 1])
        if family_total == 0:
            continue
            
        # Number of successful models in real GPU of this family
        # df_real has these columns as well
        family_success = len(df_real[df_real[col] == 1])
        
        failure_rate = (1 - (family_success / family_total)) * 100
        print(f"{name:15} | Total: {family_total:4} | Success: {family_success:4} | Fail Rate: {failure_rate:5.1f}%")

if __name__ == "__main__":
    main()
