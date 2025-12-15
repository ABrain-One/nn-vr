import time
import json
import os
import platform
import psutil
import onnxruntime as ort
import numpy as np
from pathlib import Path

def get_device_info():
    """Collects system information similar to the target JSON format."""
    cpu_info = {
        "cpu_cores": psutil.cpu_count(logical=True),
        "processors": [], # Detailed per-core info is complex to get cross-platform in python without heavy deps, simplifying for now
        "arm_architecture": platform.machine() if "arm" in platform.machine().lower() else None
    }
    
    # Basic CPU info
    try:
        if platform.system() == "Windows":
            cpu_info["processors"] = [{"model": platform.processor()}]
        elif platform.system() == "Linux":
            # simplified reading of /proc/cpuinfo could go here, but keeping it simple for now
            pass
    except Exception:
        pass

    mem = psutil.virtual_memory()
    memory_info = {
        "total_ram_kb": f"{mem.total // 1024} kB",
        "free_ram_kb": f"{mem.free // 1024} kB",
        "available_ram_kb": f"{mem.available // 1024} kB",
        "cached_kb": "0 kB" # psutil doesn't always provide cached directly in a cross-platform way easily mapping to /proc/meminfo
    }

    return {
        "timestamp": time.time(),
        "memory_info": memory_info,
        "cpu_info": cpu_info
    }

def profile_model(onnx_path, device_name="PC_Host"):
    """
    Runs inference on the ONNX model and collects stats.
    Returns a dictionary matching the target JSON structure.
    """
    print(f"Profiling model: {onnx_path}")
    
    try:
        # Load model
        session = ort.InferenceSession(onnx_path)
        input_name = session.get_inputs()[0].name
        input_shape = session.get_inputs()[0].shape
        input_type = session.get_inputs()[0].type
        
        # Handle dynamic shapes (replace 'None' or strings with 1 or default size)
        fixed_shape = []
        for dim in input_shape:
            if isinstance(dim, str) or dim is None:
                fixed_shape.append(1)
            else:
                fixed_shape.append(dim)
        
        # Generate dummy input
        if "float" in input_type:
            dummy_input = np.random.random(fixed_shape).astype(np.float32)
        elif "int" in input_type:
            dummy_input = np.random.randint(0, 255, fixed_shape).astype(np.int32)
        else:
             # Fallback
            dummy_input = np.random.random(fixed_shape).astype(np.float32)

        # Warmup
        for _ in range(5):
            session.run(None, {input_name: dummy_input})

        # Measure inference time
        start_time = time.time()
        iterations = 10
        for _ in range(iterations):
            session.run(None, {input_name: dummy_input})
        end_time = time.time()
        
        avg_duration_ms = ((end_time - start_time) / iterations) * 1000
        
        # Collect device stats
        device_analytics = get_device_info()
        
        stats = {
            "model_name": Path(onnx_path).stem,
            "device_type": device_name,
            "os_version": f"{platform.system()} {platform.release()}",
            "valid": True,
            "emulator": False, # Running on host PC
            "error_message": None,
            "duration": int(avg_duration_ms), # Duration in ms
            "device_analytics": device_analytics
        }
        
        return stats

    except Exception as e:
        print(f"Profiling failed: {e}")
        return {
            "model_name": Path(onnx_path).stem,
            "device_type": device_name,
            "os_version": f"{platform.system()} {platform.release()}",
            "valid": False,
            "emulator": False,
            "error_message": str(e),
            "duration": 0,
            "device_analytics": get_device_info()
        }

def save_stats(stats, output_dir):
    """Saves the stats to a JSON file."""
    os.makedirs(output_dir, exist_ok=True)
    filename = f"{stats['device_type']}.json"
    output_path = os.path.join(output_dir, filename)
    
    with open(output_path, 'w') as f:
        json.dump(stats, f, indent=2)
    
    print(f"Stats saved to: {output_path}")
    return output_path

if __name__ == "__main__":
    # Test run
    import sys
    if len(sys.argv) > 1:
        profile_model(sys.argv[1])
    else:
        print("Usage: python profiler.py <path_to_onnx_model>")
