import shutil
import sys
import os

onnx_file = sys.argv[1]
unity_path = "../UnityProject/Assets/NN/Models"

shutil.copy(onnx_file, os.path.join(unity_path, os.path.basename(onnx_file)))

print(f"ONNX model copied to Unity project: {unity_path}")
