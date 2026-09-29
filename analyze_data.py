import pandas as pd
import numpy as np
import scipy.stats as stats
import json

def mean_confidence_interval(data, confidence=0.95):
    a = 1.0 * np.array(data)
    n = len(a)
    if n == 0:
        return 0, 0
    m, se = np.mean(a), stats.sem(a)
    h = se * stats.t.ppf((1 + confidence) / 2., n-1)
    return m, h

def main():
    df = pd.read_csv("aggregated_unity_stats.csv")
    
    # 1. Successful vs Failed
    total = len(df)
    successful = df[df['status'] == 'success']
    failed_benchmarks = df[df['status'] == 'failed_benchmark']
    failed_exports = df[df['status'] == 'failed_export']
    
    print(f"Total Models: {total}")
    print(f"Success: {len(successful)} ({len(successful)/total*100:.1f}%)")
    print(f"Failed Benchmarks: {len(failed_benchmarks)} ({len(failed_benchmarks)/total*100:.1f}%)")
    print(f"Failed Exports: {len(failed_exports)} ({len(failed_exports)/total*100:.1f}%)")
    print("-" * 40)
    
    # 2. Mean Inference & Confidence Intervals
    cpu_times = successful['unity_cpu_duration_mean'].dropna()
    gpu_times = successful['unity_gpu_duration_mean'].dropna()
    
    cpu_m, cpu_h = mean_confidence_interval(cpu_times)
    gpu_m, gpu_h = mean_confidence_interval(gpu_times)
    
    print(f"Unity CPU Inference: {cpu_m:.2f} ms +/- {cpu_h:.2f} (95% CI)")
    print(f"Unity GPU Inference: {gpu_m:.2f} ms +/- {gpu_h:.2f} (95% CI)")
    print("-" * 40)
    
    # 3. Diversity Ratio (CPU vs GPU Time)
    # Ratio = CPU time / GPU time for each model
    ratios = (successful['unity_cpu_duration_mean'] / successful['unity_gpu_duration_mean']).dropna()
    # clean inf or zero
    ratios = ratios[np.isfinite(ratios)]
    ratio_m, ratio_h = mean_confidence_interval(ratios)
    
    print(f"Average CPU/GPU Time Ratio: {ratio_m:.2f}x +/- {ratio_h:.2f}")
    print(f"Max CPU/GPU Ratio: {ratios.max():.2f}x")
    print(f"Min CPU/GPU Ratio: {ratios.min():.2f}x")
    print("-" * 40)
    
    # 4. Failures by Architecture Type
    print("Failures by Architectural Characteristics:")
    for arch in ['is_resnet_like', 'is_vgg_like', 'is_transformer_like', 'has_attention', 'has_residual_connections']:
        arch_df = df[df[arch] == 1.0]
        if len(arch_df) == 0:
            continue
        arch_success = len(arch_df[arch_df['status'] == 'success'])
        arch_fail = len(arch_df) - arch_success
        fail_rate = arch_fail / len(arch_df) * 100
        print(f"  - {arch}: {arch_fail}/{len(arch_df)} failed ({fail_rate:.1f}%)")
    print("-" * 40)
    
    # 5. Correlation of Inference Time with FLOPs/Params
    # Pearson correlation
    corr_cpu_flops = successful['unity_cpu_duration_mean'].corr(successful['flops'])
    corr_gpu_flops = successful['unity_gpu_duration_mean'].corr(successful['flops'])
    
    corr_cpu_params = successful['unity_cpu_duration_mean'].corr(successful['total_params'])
    corr_gpu_params = successful['unity_gpu_duration_mean'].corr(successful['total_params'])
    
    print("Correlations (Pearson R):")
    print(f"  CPU Time vs FLOPs: {corr_cpu_flops:.3f}")
    print(f"  GPU Time vs FLOPs: {corr_gpu_flops:.3f}")
    print(f"  CPU Time vs Params: {corr_cpu_params:.3f}")
    print(f"  GPU Time vs Params: {corr_gpu_params:.3f}")

    # Write output to markdown artifact for Phase 2!
    with open("statistical_summary.md", "w") as f:
        f.write("# Phase 2: Statistical & Architectural Analysis\n\n")
        f.write(f"## Dataset Overview\n")
        f.write(f"- Total Models: {total}\n")
        f.write(f"- Success: {len(successful)} ({len(successful)/total*100:.1f}%)\n")
        f.write(f"- Failed Benchmarks: {len(failed_benchmarks)} ({len(failed_benchmarks)/total*100:.1f}%)\n")
        f.write(f"- Failed Exports: {len(failed_exports)} ({len(failed_exports)/total*100:.1f}%)\n\n")
        
        f.write("## Inference Performance (Unity)\n")
        f.write(f"- **CPU Inference**: {cpu_m:.2f} ms ± {cpu_h:.2f} (95% CI)\n")
        f.write(f"- **GPU Inference**: {gpu_m:.2f} ms ± {gpu_h:.2f} (95% CI)\n")
        f.write(f"- **Average CPU/GPU Diversity Ratio**: {ratio_m:.2f}x ± {ratio_h:.2f}\n\n")
        
        f.write("## Architectural Bottlenecks & Failures\n")
        for arch in ['is_resnet_like', 'is_vgg_like', 'is_transformer_like', 'has_attention', 'has_residual_connections']:
            arch_df = df[df[arch] == 1.0]
            if len(arch_df) == 0: continue
            arch_success = len(arch_df[arch_df['status'] == 'success'])
            arch_fail = len(arch_df) - arch_success
            fail_rate = arch_fail / len(arch_df) * 100
            f.write(f"- **{arch}**: {arch_fail}/{len(arch_df)} failed ({fail_rate:.1f}%)\n")
            
        f.write("\n## Mathematical Correlations\n")
        f.write(f"- **CPU Time vs FLOPs**: $R = {corr_cpu_flops:.3f}$\n")
        f.write(f"- **GPU Time vs FLOPs**: $R = {corr_gpu_flops:.3f}$\n")
        f.write(f"- **CPU Time vs Params**: $R = {corr_cpu_params:.3f}$\n")
        f.write(f"- **GPU Time vs Params**: $R = {corr_gpu_params:.3f}$\n")
        

if __name__ == "__main__":
    main()
