import json
import shutil
import subprocess
import time
from pathlib import Path


UNITY_EXE = Path(
    r"C:\Program Files\Unity\Hub\Editor\2022.3.62f3\Editor\Unity.exe"
)

UNITY_PROJECT = Path(
    r"D:\nn-vr\NNVRBenchmark\NNVRBenchmark"
)

UNITY_MODELS_DIR = UNITY_PROJECT / "Assets" / "Models"

UNITY_RESULTS_DIR = UNITY_PROJECT / "Assets" / "Results"


def run_unity_benchmark(onnx_path: Path):
    """
    Copy ONNX into Unity project and run benchmark.
    """

    onnx_path = Path(onnx_path)

    if not onnx_path.exists():
        raise FileNotFoundError(onnx_path)

    # --------------------------------------------------
    # CLEAR OLD MODELS
    # --------------------------------------------------
    for f in UNITY_MODELS_DIR.glob("*"):
        try:
            if f.is_file():
                f.unlink()
        except Exception as e:
            print(f"WARNING: Could not delete {f}: {e}")

    # --------------------------------------------------
    # COPY NEW MODEL
    # --------------------------------------------------

    target_onnx = UNITY_MODELS_DIR / onnx_path.name

    shutil.copy2(onnx_path, target_onnx)

    # --------------------------------------------------
    # COPY EXTERNAL WEIGHTS FILE IF PRESENT
    # --------------------------------------------------
    data_file = onnx_path.with_suffix(".onnx.data")

    if data_file.exists():
        shutil.copy2(
            data_file,
            UNITY_MODELS_DIR / data_file.name
        )

    # --------------------------------------------------
    # CLEAR OLD JSON RESULTS
    # --------------------------------------------------
    for f in UNITY_RESULTS_DIR.glob("*_results.json"):
        try:
            f.unlink()
        except Exception as e:
            print(f"WARNING: Could not delete old result {f}: {e}")

    # --------------------------------------------------
    # RUN UNITY
    # --------------------------------------------------

    cmd = [
        str(UNITY_EXE),
        "-batchmode",
        "-projectPath",
        str(UNITY_PROJECT),
        "-executeMethod",
        "BenchmarkCLI.RunBenchmark",
        "-quit"
    ]

    print("RUNNING UNITY BENCHMARK...")
    print(" ".join(cmd))

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )

    print("UNITY STDOUT:")
    print(result.stdout)

    if result.stderr:
        print("UNITY STDERR:")
        print(result.stderr)

    if result.returncode != 0:
        print(result.stderr)
        raise RuntimeError(
            f"Unity failed with code {result.returncode}"
        )

    # --------------------------------------------------
    # WAIT FOR JSON
    # --------------------------------------------------

    json_files = list(
        UNITY_RESULTS_DIR.glob("*_results.json")
    )

    if not json_files:
        raise RuntimeError(
            "No Unity results JSON found."
        )

    latest = max(
        json_files,
        key=lambda p: p.stat().st_mtime
    )

    with open(latest, "r") as f:
        benchmark = json.load(f)

    return benchmark