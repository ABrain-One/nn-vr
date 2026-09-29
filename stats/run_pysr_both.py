import pandas as pd
import numpy as np
from pysr import PySRRegressor
import os
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

def run_pysr_for_dataset(df, target_cpu_col, target_gpu_col, output_md, title):
    # Filter for successes if status exists
    if 'status' in df.columns:
        df = df[df['status'] == 'success'].copy()
        
    # Prepare features
    df['Flog'] = np.log1p(df['flops'])
    df['Plog'] = np.log1p(df['total_params'])
    df['L'] = df['total_layers']
    
    features = ['Flog', 'Plog', 'L']
    
    df = df.dropna(subset=features + [target_cpu_col, target_gpu_col])
    
    X = df[features].values
    
    # Extract targets (milliseconds)
    t_cpu = df[target_cpu_col].values
    t_gpu = df[target_gpu_col].values
    
    y_cpu = np.log1p(t_cpu)
    y_gpu = np.log1p(t_gpu)
    
    model_cpu = PySRRegressor(
        niterations=50,
        population_size=30,
        maxsize=20,
        binary_operators=["+", "-", "*", "/"],
        unary_operators=["exp", "log", "sqrt", "abs"],
        model_selection="best",
        elementwise_loss="loss(prediction, target) = (prediction - target)^2",
        random_state=42,
        temp_equation_file=f"pysr_{title.replace(' ', '_')}_cpu.csv"
    )
    
    model_gpu = PySRRegressor(
        niterations=50,
        population_size=30,
        maxsize=20,
        binary_operators=["+", "-", "*", "/"],
        unary_operators=["exp", "log", "sqrt", "abs"],
        model_selection="best",
        elementwise_loss="loss(prediction, target) = (prediction - target)^2",
        random_state=42,
        temp_equation_file=f"pysr_{title.replace(' ', '_')}_gpu.csv"
    )
    
    print(f"Running PySR for {title} CPU Latency...")
    model_cpu.fit(X, y_cpu, variable_names=["Flog", "Plog", "L"])
    best_cpu_eq = model_cpu.sympy()
    
    print(f"Running PySR for {title} GPU Latency...")
    model_gpu.fit(X, y_gpu, variable_names=["Flog", "Plog", "L"])
    best_gpu_eq = model_gpu.sympy()
    
    print(f"\n====================================")
    print(f"          PySR RESULTS: {title}     ")
    print(f"====================================")
    print(f"Best CPU Formula (log space): {best_cpu_eq}")
    print(f"Best GPU Formula (log space): {best_gpu_eq}")
    
    # Save the output
    out_path = REPO / "stats" / output_md
    with open(out_path, "w") as f:
        f.write(f"# Symbolic Regression Results ({title})\n\n")
        f.write(f"- **CPU Latency Equation**: `log(t_cpu + 1) = {best_cpu_eq}`\n")
        f.write(f"- **GPU Latency Equation**: `log(t_gpu + 1) = {best_gpu_eq}`\n\n")

def main():
    print("Loading datasets...")
    llvmpipe_csv = REPO / "aggregated_unity_stats.csv"
    real_gpu_csv = REPO / "stats" / "aggregated_real_gpu_stats.csv"
    
    df_llvm = pd.read_csv(llvmpipe_csv)
    df_real = pd.read_csv(real_gpu_csv)
    
    # Llvmpipe
    run_pysr_for_dataset(
        df_llvm, 
        "unity_cpu_duration_mean", 
        "unity_gpu_duration_mean", 
        "pysr_results_llvmpipe.md", 
        "Llvmpipe"
    )
    
    # Real GPU
    run_pysr_for_dataset(
        df_real, 
        "cpu_mean_ms", 
        "gpu_mean_ms", 
        "pysr_results_real_gpu.md", 
        "Real GPU"
    )

if __name__ == "__main__":
    main()
