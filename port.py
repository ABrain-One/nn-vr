import os, platform, shutil, sys
from os.path import expanduser, expandvars, join, basename, exists
from os import remove
from pathlib import Path

from ab.nn.api import check_nn, data
from ab.nn.util.Const import onnx_file, onnx_dir

verifier_dir = Path('unity_verifier')
asset_dir = verifier_dir / 'Assets'
model_verifier_dir = asset_dir / 'NN' / 'Models'
test_res_file = asset_dir / 'onnx_validation.txt'


def copy_nn_to_verify(onnx_file, unity_model_dir=model_verifier_dir):
    os.makedirs(unity_model_dir, exist_ok=True)
    dest_path = join(unity_model_dir, basename(onnx_file))
    shutil.copy2(onnx_file, dest_path)
    print(f"Model copied to the Unity Verifier: {dest_path}")
    return dest_path


def copy_nn_to_unity(onnx_file, unity_model_dir='unity_nn/Assets/NN/Models'):
    os.makedirs(unity_model_dir, exist_ok=True)
    dest_path = join(unity_model_dir, basename(onnx_file))
    shutil.copy2(onnx_file, dest_path)
    print(f"Model copied to the unity_nn project: {dest_path}")
    return dest_path


def check_onnx_log_messages():
    if not exists(test_res_file):
        print(f"Unity log file not found at: {test_res_file}")
        return False

    with open(test_res_file, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            print(line)
            return 'imported successfully!' in line


def train_save_nn(model_name, model_onnx_file):
    shutil.rmtree(onnx_dir, ignore_errors=True)
    df = data(nn=model_name)
    df_sorted = df.sort_values("duration")
    last_row = df_sorted.iloc[0]
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
        return False

    os.rename(onnx_file, model_onnx_file)


def verify_nn(nn_onnx_file, unity_version):
    shutil.rmtree(model_verifier_dir, ignore_errors=True)
    remove(test_res_file)
    copy_nn_to_verify(nn_onnx_file)
    unity_exe = f'"C:/Program Files/Unity/Hub/Editor/{unity_version}/Editor/Unity.exe"'
    build_dir = Path('./unity_verifier')
    return_code = os.system(
        f'{unity_exe} -quit -batchmode -executeMethod Builder.BuildWindows -logfile editor.log -projectPath {build_dir}')
    if return_code == 0:
        return check_onnx_log_messages()
    else:
        print(f'Verification is NOT successful. Returned code {return_code}')


def main():
    """
        Check if NN model correctly ported to Unity
        :return: True if model ported to virtual reality, otherwise False
        """
    if len(sys.argv) < 2:
        print("Usage: python port.py <model_name> <unity-version>")
        sys.exit(1)
    model_name = sys.argv[1]
    nn_onnx_file = onnx_dir / f'{model_name}.onnx'
    if not exists(nn_onnx_file):
        train_save_nn(model_name, nn_onnx_file)

    unity_ready = None
    if len(sys.argv) > 2:
        unity_version = sys.argv[2]
        unity_ready = verify_nn(nn_onnx_file, unity_version)

    if unity_ready:
        copy_nn_to_unity(nn_onnx_file)
    return unity_ready


if __name__ == "__main__":
    main()
