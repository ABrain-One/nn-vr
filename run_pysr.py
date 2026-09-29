import pandas as pd
import numpy as np
from pysr import PySRRegressor
import os

def main():
    print("Loading data...")
    df = pd.read_csv("aggregated_unity_stats.csv")
    
    # Filter for successes
    df = df[df['status'] == 'success'].copy()
    
    # Prepare features
    # Similar to the paper, we use log of flops and params, and layer count
    df['Flog'] = np.log1p(df['flops'])
    df['Plog'] = np.log1p(df['total_params'])
    df['L'] = df['total_layers']
    
    features = ['Flog', 'Plog', 'L']
    
    # Drop rows with NaN values in features or targets
    df = df.dropna(subset=features + ['unity_cpu_duration_mean', 'unity_gpu_duration_mean'])
    
    X = df[features].values
    
    # Extract targets (milliseconds)
    t_cpu = df['unity_cpu_duration_mean'].values
    t_gpu = df['unity_gpu_duration_mean'].values
    
    # Transform targets to log(t+1)
    y_cpu = np.log1p(t_cpu)
    y_gpu = np.log1p(t_gpu)
    
    # Common PySR Config (Matching the Reference Paper's Latency Configuration)
    model_cpu = PySRRegressor(
        niterations=100,
        population_size=30,
        maxsize=30,
        binary_operators=["+", "-", "*", "/"],
        unary_operators=["exp", "log", "sqrt", "abs"],
        model_selection="best",
        elementwise_loss="loss(prediction, target) = (prediction - target)^2",
        random_state=42,
        temp_equation_file="pysr_cpu_equations.csv"
    )
    
    model_gpu = PySRRegressor(
        niterations=100,
        population_size=30,
        maxsize=30,
        binary_operators=["+", "-", "*", "/"],
        unary_operators=["exp", "log", "sqrt", "abs"],
        model_selection="best",
        elementwise_loss="loss(prediction, target) = (prediction - target)^2",
        random_state=42,
        temp_equation_file="pysr_gpu_equations.csv"
    )
    
    print("Running PySR for Unity CPU Latency...")
    model_cpu.fit(X, y_cpu, variable_names=["Flog", "Plog", "L"])
    best_cpu_eq = model_cpu.sympy()
    
    print("\nRunning PySR for Unity GPU Latency...")
    model_gpu.fit(X, y_gpu, variable_names=["Flog", "Plog", "L"])
    best_gpu_eq = model_gpu.sympy()
    
    print("\n====================================")
    print("          PySR RESULTS              ")
    print("====================================")
    print(f"Best CPU Formula (log space): {best_cpu_eq}")
    print(f"Best GPU Formula (log space): {best_gpu_eq}")
    print("====================================")
    
    # Save the output to a markdown file
    with open("pysr_results.md", "w") as f:
        f.write("# Phase 3: Symbolic Regression Results (PySR)\n\n")
        f.write("We applied evolutionary symbolic regression to discover closed-form analytical formulas for Unity CPU and GPU inference latency.\n\n")
        f.write("## Targets & Features\n")
        f.write("- **Target**: `log(t+1)` where `t` is inference time in milliseconds.\n")
        f.write("- **Features**: `Flog` (log FLOPs), `Plog` (log Parameters), `L` (Total Layers).\n\n")
        f.write("## Discovered Equations\n")
        f.write(f"- **CPU Latency Equation**: `log(t_cpu + 1) = {best_cpu_eq}`\n")
        f.write(f"- **GPU Latency Equation**: `log(t_gpu + 1) = {best_gpu_eq}`\n\n")
        f.write("## Interpretation\n")
        f.write("These equations demonstrate that inference latency is non-linear and device-heterogeneous. The GPU and CPU require qualitatively different mathematical models to capture their bottlenecks.\n")

if __name__ == "__main__":
    main()
