import sys
import subprocess
import time
from pathlib import Path

def run_model(model_name):
    print(f"\n{'='*50}")
    print(f"🚀 Processing Model: {model_name}")
    print(f"{'='*50}")
    
    start_time = time.time()
    try:
        # Call port.py as a subprocess
        result = subprocess.run(
            [sys.executable, 'port.py', model_name],
            capture_output=False, # Let output stream to console
            text=True
        )
        
        duration = time.time() - start_time
        if result.returncode == 0:
            print(f"\n✅ {model_name} completed successfully in {duration:.2f}s")
            return True
        else:
            print(f"\n❌ {model_name} failed with exit code {result.returncode}")
            return False
            
    except Exception as e:
        print(f"\n❌ Error running {model_name}: {e}")
        return False

def main():
    # Default list of models to test if none provided
    models = ["AirNet", "ResNet50", "MobileNetV2"]
    
    # If arguments provided, use those
    if len(sys.argv) > 1:
        models = sys.argv[1:]
        
    print(f"Batch processing {len(models)} models: {', '.join(models)}")
    
    results = {}
    for model in models:
        success = run_model(model)
        results[model] = "Success" if success else "Failed"
        
    print(f"\n{'='*50}")
    print("📊 Batch Processing Summary")
    print(f"{'='*50}")
    for model, status in results.items():
        icon = "✅" if status == "Success" else "❌"
        print(f"{icon} {model}: {status}")

if __name__ == "__main__":
    main()
