from pathlib import Path
from unity_runner import run_unity_benchmark

result = run_unity_benchmark(
    Path(r"_work/onnx_temp/AirNet.onnx")
)

print(result)
