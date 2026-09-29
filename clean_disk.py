import os, glob, shutil

print("Cleaning ONNX models...")
for f in glob.glob("out/nn/stat/version*/onnx/fp32/*/*.onnx"):
    try:
        os.remove(f)
    except: pass

print("Cleaning temp files...")
try:
    shutil.rmtree("/tmp/opt-clean-test", ignore_errors=True)
    shutil.rmtree("/tmp/stash_extract", ignore_errors=True)
    shutil.rmtree("/tmp/xet-test", ignore_errors=True)
    shutil.rmtree("/tmp/xet-final", ignore_errors=True)
    shutil.rmtree("/tmp/xet-auto-test", ignore_errors=True)
    shutil.rmtree("/tmp/train-sh-test", ignore_errors=True)
except: pass

print("Done cleaning.")
