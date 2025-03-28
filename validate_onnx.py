import os
import sys
import torch
import shutil
import platform
from ab.nn.api import check_nn, data


def get_unity_log_path():
    if platform.system() == "Windows":
        return os.path.expandvars(r"%USERPROFILE%\AppData\Local\Unity\Editor\Editor.log")
    elif platform.system() == "Darwin":
        return os.path.expanduser("~/Library/Logs/Unity/Editor.log")
    else:
        raise RuntimeError("Unsupported OS")


def copy_model_to_unity(onnx_file, unity_model_dir="Barracuda-Image-Classification/Assets/NN/Models"):
    os.makedirs(unity_model_dir, exist_ok=True)
    dest_path = os.path.join(unity_model_dir, os.path.basename(onnx_file))
    shutil.copy2(onnx_file, dest_path)
    print(f"Model copied to Unity: {dest_path}")
    return dest_path


def check_onnx_log_messages():
    log_path = get_unity_log_path()
    if not os.path.exists(log_path):
        print(f"Unity log file not found at: {log_path}")
        return

    success_message = "Model loaded and worker created successfully."
    error_prefix = "Failed to load ONNX model:"

    found_success = False
    found_error = False
    error_detail = None

    with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if success_message in line:
                found_success = True
            elif error_prefix in line:
                found_error = True
                error_detail = line.strip()

    print("\n=== ONNX Loader Status ===")
    if found_success:
        print("Success: ONNX model loaded and worker created.")
    if found_error:
        print("Error detected:", error_detail)
    if not found_success and not found_error:
        print("No ONNX loader messages found in the log.")


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_onnx.py <model_name>")
        sys.exit(1)

    model_name = sys.argv[1]

    df = data(nn=model_name)
    df_sorted = df.sort_values("epoch")
    last_row = df_sorted.iloc[-1]

    prm = last_row["prm"]
    prm["epoch"] = 50
    prm["device"] = "cuda" if torch.cuda.is_available() else "cpu"

    check_nn(
        nn_code=last_row["nn_code"],
        task=last_row["task"],
        dataset=last_row["dataset"],
        metric=last_row["metric"],
        prm=prm,
        save_to_db=False,
        export_onnx=True
    )

    onnx_path = f" ./onnx/{model_name}.onnx"

    if not os.path.exists(onnx_path):
        print("File not found:", onnx_path)
        sys.exit(1)

    copy_model_to_unity(onnx_path)
    check_onnx_log_messages()


if __name__ == "__main__":
    main()
