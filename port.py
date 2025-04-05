import os
import platform
import shutil
import sys
from os.path import expanduser, expandvars, join, basename, exists

from ab.nn.api import check_nn, data
from ab.nn.util.Const import onnx_file


def get_unity_log_path():
    if platform.system() == "Windows":
        return expandvars(r"%USERPROFILE%\AppData\Local\Unity\Editor\Editor.log")
    elif platform.system() == "Darwin":
        return expanduser("~/Library/Logs/Unity/Editor.log")
    else:
        raise RuntimeError("Unsupported OS")


def copy_model_to_unity(onnx_file, unity_model_dir="unity_nn/Assets/NN/Models"):
    os.makedirs(unity_model_dir, exist_ok=True)
    dest_path = join(unity_model_dir, basename(onnx_file))
    shutil.copy2(onnx_file, dest_path)
    print(f"Model copied to Unity: {dest_path}")
    return dest_path


def check_onnx_log_messages():
    log_path = get_unity_log_path()
    if not exists(log_path):
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
        print("Usage: python port.py <model_name>")
        sys.exit(1)

    model_name = sys.argv[1]

    df = data(nn=model_name)
    df_sorted = df.sort_values("epoch")
    last_row = df_sorted.iloc[-1]

    prm = last_row["prm"]
    prm["epoch"] = 1

    check_nn(nn_code=last_row["nn_code"],
             task=last_row["task"],
             dataset=last_row["dataset"],
             metric=last_row["metric"],
             prm=prm,
             prefix=model_name,
             save_to_db=False,
             export_onnx=True,
             epoch_duration_limit_sec=5 * 60 * 60)

    if not exists(onnx_file):
        print("File not found:", onnx_file)
        sys.exit(1)

    copy_model_to_unity(onnx_file)
    check_onnx_log_messages()


if __name__ == "__main__":
    main()
