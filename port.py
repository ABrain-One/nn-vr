import os
import shutil
import sys
from os.path import join, basename, exists, getsize
from pathlib import Path
import onnx
import build_and_deploy
from vr_processor import VRProcessor

# Add nn-dataset to sys.path to allow importing ab
sys.path.append(os.path.join(os.path.dirname(__file__), 'nn-dataset'))
try:
    from ab.nn.api import check_nn, data
    from ab.nn.util.Const import onnx_file, onnx_dir
except ImportError:
    print("Warning: Could not import ab.nn.api. Running in standalone mode?")
    onnx_dir = Path("onnx_models")
    onnx_file = onnx_dir / "temp_model.onnx"


# These variables tell the script where Unity should pick up the ONNX model:
# 📄 unity_nn/Assets/onnx_validation.txt ← Unity writes validation result here
UNITY_PROJECT_DIR = Path('unity_nn')
ASSET_DIR = UNITY_PROJECT_DIR / 'Assets'
RESOURCES_DIR = ASSET_DIR / 'Resources'
TEST_RES_FILE = ASSET_DIR / 'onnx_validation.txt'


def check_vr_readiness(onnx_path):
    """
    Checks if the model is suitable for VR/Android deployment.
    """
    print(f"🔍 Checking VR readiness for: {onnx_path}")
    
    # 1. Size Check
    size_mb = getsize(onnx_path) / (1024 * 1024)
    print(f"   Size: {size_mb:.2f} MB")
    
    if size_mb > 2000:
        print("   ⚠️  WARNING: Model is larger than 2GB. Android APK limits might be exceeded.")
        # Note: We already handle external data splitting in other scripts, but good to warn.
        
    # 2. Basic ONNX Validity
    try:
        model = onnx.load(onnx_path)
        onnx.checker.check_model(model)
        print("   ✅ ONNX Structure is valid.")
    except Exception as e:
        print(f"   ❌ Invalid ONNX model: {e}")
        return False

    return True


def copy_nn_to_unity(onnx_file_path):
    """
    Copies ONNX model to unity_nn/Assets/Resources for inference.
    """
    os.makedirs(RESOURCES_DIR, exist_ok=True)
    dest_path = join(RESOURCES_DIR, basename(onnx_file_path))
    
    print(f"📂 Copying model to Unity Project: {dest_path}")
    shutil.copy2(onnx_file_path, dest_path)
    
    # Check for external data
    src_dir = os.path.dirname(onnx_file_path)
    external_data_filename = "nn.onnx.data"
    src_data_file = os.path.join(src_dir, external_data_filename)
    
    if exists(src_data_file):
        dest_data_path = join(os.path.dirname(dest_path), external_data_filename)
        shutil.copy2(src_data_file, dest_data_path)
        print(f"   + External data copied: {dest_data_path}")

    return dest_path


def train_save_nn(model_name, model_onnx_file):
    """
    Fetches/Trains model from nn-dataset and saves as ONNX.
    """
    shutil.rmtree(onnx_dir, ignore_errors=True)
    df = data(nn=model_name)
    if df.empty:
        print(f"No data found for model: {model_name}")
        return False
    
    if "duration" not in df.columns:
        df_sorted = df
    else:
        df_sorted = df.sort_values("duration")
        
    last_row = df_sorted.iloc[0]
    prm = last_row["prm"]
    prm["epoch"] = 0
    
    try:
        check_nn(nn_code=last_row["nn_code"],
                 task=last_row["task"],
                 dataset=last_row["dataset"],
                 metric=last_row["metric"],
                 prm=prm,
                 prefix=model_name,
                 save_to_db=False,
                 export_onnx=True,
                 epoch_limit_minutes=5 * 60)
    except Exception as e:
        print(f"Warning: Training/Export encountered an error: {e}")
        if exists(onnx_file):
            print("ONNX file was created successfully, proceeding...")
        else:
            raise e

    if not exists(onnx_file):
        print("File not found:", onnx_file)
        return False

    os.rename(onnx_file, model_onnx_file)
    return True


def main():
    if len(sys.argv) < 2:
        print("Usage: python port.py <model_name> [unity-version]")
        sys.exit(1)
        
    model_name = sys.argv[1]
    nn_onnx_file = onnx_dir / f'{model_name}.onnx'
    
    # 1. Fetch/Train Model
    if not exists(nn_onnx_file):
        print(f"🔨 Generating ONNX for {model_name}...")
        success = train_save_nn(model_name, nn_onnx_file)
        if not success:
            print(f"❌ Failed to generate model: {model_name}")
            sys.exit(1)
            
    # 2. VR Readiness Check
    if not check_vr_readiness(nn_onnx_file):
        print("❌ Model failed VR readiness check.")
        sys.exit(1)

    # 3. Import to Unity
    print("🔄 Importing to Unity...")
    copy_nn_to_unity(nn_onnx_file)
    
    # 4. Build APK (Optional - handled by build_and_deploy)
    # If the user wants to force a build every time, uncomment below:
    # unity_exe = build_and_deploy.find_unity_executable()
    # if unity_exe:
    #     build_and_deploy.build_android(unity_exe, str(UNITY_PROJECT_DIR))
    
    # Check if we should deploy/run
    print("🚀 Initiating VR Processing...")
    vr_proc = VRProcessor()
    vr_proc.process_model(str(nn_onnx_file), model_name)


if __name__ == "__main__":
    main()
