import json
import glob
import os
import pandas as pd
from collections import defaultdict

def main():
    print("Aggregating Unity Successful Runs...")
    # 1. Aggregate Successful Runs
    unity_files = glob.glob("out/nn/stat/*/onnx/fp32/*/*.json")
    
    # Store lists of metrics per model
    model_stats = defaultdict(lambda: {
        'cpu_durations': [],
        'gpu_durations': [],
        'model_size_mb': [],
        'status': 'success',
        'error_msg': None
    })
    
    for f in unity_files:
        try:
            with open(f, 'r') as fp:
                data = json.load(fp)
            m_name = data.get("model_name")
            if not m_name:
                continue
            
            # Unity stats (in nanoseconds, converting to ms)
            if "cpu_duration" in data and data["cpu_duration"] is not None:
                model_stats[m_name]['cpu_durations'].append(data["cpu_duration"] / 1e6)
            if "gpu_duration" in data and data["gpu_duration"] is not None:
                model_stats[m_name]['gpu_durations'].append(data["gpu_duration"] / 1e6)
            if "model_size_mb" in data and data["model_size_mb"] is not None:
                model_stats[m_name]['model_size_mb'].append(data["model_size_mb"])
        except Exception as e:
            print(f"Error reading {f}: {e}")

    # 2. Add Failed Benchmarks
    print("Aggregating Unity Failed Benchmarks...")
    failed_benchmarks = glob.glob("out/nn/stat/*/failed_benchmarks/*.json")
    for f in failed_benchmarks:
        try:
            with open(f, 'r') as fp:
                data = json.load(fp)
            m_name = data.get("model_name")
            if m_name:
                # Only mark as failed if it hasn't succeeded
                if not model_stats[m_name]['cpu_durations'] and not model_stats[m_name]['gpu_durations']:
                    model_stats[m_name]['status'] = 'failed_benchmark'
                    model_stats[m_name]['error_msg'] = data.get("error_message", "Unknown")
        except: pass

    # 3. Add Failed Exports
    print("Aggregating Failed Exports...")
    failed_exports = glob.glob("out/nn/stat/failed_exports/*.json")
    for f in failed_exports:
        try:
            with open(f, 'r') as fp:
                data = json.load(fp)
            m_name = data.get("model_name")
            if m_name:
                # Only mark as failed if it hasn't succeeded
                if not model_stats[m_name]['cpu_durations'] and not model_stats[m_name]['gpu_durations']:
                    model_stats[m_name]['status'] = 'failed_export'
                    err = data.get("traceback", "")
                    model_stats[m_name]['error_msg'] = err.split('\n')[-2] if '\n' in err else err
        except: pass

    # 4. Merge with Workstation Structural Data
    print("Merging with Workstation Data from nn-dataset...")
    final_rows = []
    
    for m_name, stats in model_stats.items():
        row = {
            'model_name': m_name,
            'status': stats['status'],
            'error_msg': stats['error_msg']
        }
        
        # Calculate means for successes
        if stats['cpu_durations']:
            row['unity_cpu_duration_mean'] = sum(stats['cpu_durations']) / len(stats['cpu_durations'])
        if stats['gpu_durations']:
            row['unity_gpu_duration_mean'] = sum(stats['gpu_durations']) / len(stats['gpu_durations'])
        if stats['model_size_mb']:
            row['model_size_mb'] = sum(stats['model_size_mb']) / len(stats['model_size_mb'])

        # Find workstation JSON
        ws_matches = glob.glob(f"nn-dataset/ab/nn/stat/nn/{m_name}*.json")
        
        # Exact match logic if multiple exist
        ws_file = None
        if len(ws_matches) == 1:
            ws_file = ws_matches[0]
        elif len(ws_matches) > 1:
            exact_match = f"nn-dataset/ab/nn/stat/nn/{m_name}.json"
            if exact_match in ws_matches:
                ws_file = exact_match
            else:
                ws_file = ws_matches[0]
                
        if ws_file:
            try:
                with open(ws_file, 'r') as fp:
                    ws_data = json.load(fp)
                
                # Extract structural parameters
                row['total_layers'] = ws_data.get('total_layers')
                row['total_params'] = ws_data.get('total_params')
                row['flops'] = ws_data.get('flops')
                row['has_attention'] = ws_data.get('has_attention')
                row['has_residual_connections'] = ws_data.get('has_residual_connections')
                row['is_resnet_like'] = ws_data.get('is_resnet_like')
                row['is_vgg_like'] = ws_data.get('is_vgg_like')
                row['is_transformer_like'] = ws_data.get('is_transformer_like')
                row['is_mobilenet_like'] = ws_data.get('is_mobilenet_like')
                
                meta = ws_data.get('meta', {})
                if 'conv_info' in meta:
                    row['conv_count'] = meta['conv_info'].get('count', 0)
                if 'linear_info' in meta:
                    row['linear_count'] = meta['linear_info'].get('count', 0)
                
            except Exception as e:
                print(f"Error reading workstation JSON {ws_file}: {e}")
        else:
            print(f"Warning: No workstation JSON found for {m_name}")
            
        final_rows.append(row)

    # Save to DataFrame and CSV
    df = pd.DataFrame(final_rows)
    print(f"Aggregated {len(df)} models.")
    df.to_csv("aggregated_unity_stats.csv", index=False)
    print("Saved to aggregated_unity_stats.csv")

if __name__ == "__main__":
    main()
