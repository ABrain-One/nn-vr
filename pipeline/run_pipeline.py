# pipeline/run_pipeline.py

from pipeline.model_selector import select_models
from pipeline.model_fetcher import fetch_model
from pipeline.sanity_checks import run_sanity_checks

def main():
    # 1. Select models (metadata only)
    models = select_models(
        mode="one",
        names=["AirNet"]
    )

    # 2. Loop over selected models
    for model_record in models:
        print(f"[INFO] Selected model: {model_record['nn']}")

        # 3. Fetch ONNX artifact
        local_onnx_path = fetch_model(model_record)
        print(f"[INFO] ONNX cached at: {local_onnx_path}")

        # 4. Run sanity checks
        run_sanity_checks(local_onnx_path)
        print("[INFO] Sanity checks passed")

        # 5. (Later) run on VR
        # vr_processor.run(local_onnx_path)

if __name__ == "__main__":
    main()
