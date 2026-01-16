from sanity_checks import run_sanity_checks

if __name__ == "__main__":
    model_path = "D:/CV-PROJECT/nn-vr/unity_nn/Assets/Models/efficientnet-lite4-11.onnx"
    
    print(f"Running sanity checks on: {model_path}")
    try:
        run_sanity_checks(model_path)
        print("✓ All sanity checks passed!")
    except Exception as e:
        print(f"✗ Sanity check failed: {e}")
