#!/usr/bin/env python3
import pandas as pd
import math
import os

def main():
    df = pd.read_csv("stats/aggregated_real_gpu_stats.csv")
    
    # Sort by model name
    df = df.sort_values(by="model_name").reset_index(drop=True)
    
    latex_file = "report/appendix_tables.tex"
    
    with open(latex_file, "w") as f:
        f.write("\\appendix\n")
        f.write("\\section{Complete Empirical Benchmarking Results}\n")
        f.write("This appendix contains the complete empirical inference latency results for all 814 successfully benchmarked models on the NVIDIA RTX 4090 hardware environment. \\\\ \\vspace{1cm}\n\n")
        
        # We will create multiple tables, 40 models per page to span ~20 pages
        batch_size = 50
        num_batches = math.ceil(len(df) / batch_size)
        
        for i in range(num_batches):
            batch = df.iloc[i*batch_size : (i+1)*batch_size]
            
            f.write("\\begin{table*}[h!]\n")
            f.write("\\centering\n")
            f.write("\\fontsize{7}{9}\\selectfont\n")
            f.write("\\begin{tabular}{lrrrrrr}\n")
            f.write("\\toprule\n")
            f.write("\\textbf{Model Name} & \\textbf{Params} & \\textbf{FLOPs} & \\textbf{Layers} & \\textbf{CPU Mean (ms)} & \\textbf{GPU Mean (ms)} & \\textbf{GPU Faster Factor} \\\\\n")
            f.write("\\midrule\n")
            
            for _, row in batch.iterrows():
                # Escape underscores in model names
                name = str(row['model_name']).replace("_", "\\_")
                
                params = f"{row['total_params']:,.0f}" if pd.notna(row['total_params']) else "-"
                flops = f"{row['flops']:,.0f}" if pd.notna(row['flops']) else "-"
                layers = str(int(row['total_layers'])) if pd.notna(row['total_layers']) else "-"
                
                cpu = f"{row['cpu_mean_ms']:.2f}"
                gpu = f"{row['gpu_mean_ms']:.2f}"
                
                ratio = "-"
                if row['gpu_mean_ms'] > 0:
                    r = row['cpu_mean_ms'] / row['gpu_mean_ms']
                    ratio = f"{r:.1f}$\\times$"
                
                f.write(f"{name} & {params} & {flops} & {layers} & {cpu} & {gpu} & {ratio} \\\\\n")
                
            f.write("\\bottomrule\n")
            f.write("\\end{tabular}\n")
            f.write(f"\\caption{{Complete Empirical Benchmarking Results (Part {i+1} of {num_batches})}}\n")
            f.write("\\end{table*}\n\n")
            f.write("\\clearpage\n\n")
            
if __name__ == "__main__":
    main()
