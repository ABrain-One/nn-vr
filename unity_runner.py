import json
import shutil
import subprocess
import time
import traceback
from pathlib import Path


UNITY_EXE = Path(
    r"C:\Program Files\Unity\Hub\Editor\2022.3.62f3\Editor\Unity.exe"
).resolve()

UNITY_PROJECT = Path(
    r"D:\nn-vr\NNVRBenchmark"
).resolve()

UNITY_MODELS_DIR = (
    UNITY_PROJECT / "Assets" / "Models"
).resolve()

UNITY_RESULTS_DIR = (
    UNITY_PROJECT / "Assets" / "Results"
).resolve()


def run_unity_benchmark(onnx_path: Path):
    """
    Copy ONNX into Unity project and run benchmark.
    """
    try:
        onnx_path = Path(onnx_path)
        onnx_path = onnx_path.resolve()

        if not onnx_path.exists():
            raise FileNotFoundError(onnx_path)

        # --------------------------------------------------
        # CLEAR OLD MODELS
        # --------------------------------------------------
        for f in UNITY_MODELS_DIR.glob("*"):
            try:
                if not f.is_file():
                    continue
                # Skip Unity meta files
                if f.suffix == ".meta":
                    continue
                f.unlink()

            except Exception as e:
                print(f"WARNING: Could not delete {f}")
                print(str(e))
            
        time.sleep(0.5)

        # --------------------------------------------------
        # COPY NEW MODEL
        # --------------------------------------------------

        target_onnx = UNITY_MODELS_DIR / "model.onnx"

        shutil.copy2(
            onnx_path,
            target_onnx
        )

        # --------------------------------------------------
        # COPY EXTERNAL WEIGHTS FILE IF PRESENT
        # --------------------------------------------------

        data_file = onnx_path.with_suffix(".onnx.data")

        if data_file.exists():

            target_data = UNITY_MODELS_DIR / "model.onnx.data"
            shutil.copy2(
                data_file,
                target_data
            )
    
        # --------------------------------------------------
        # CLEAR OLD JSON RESULTS
        # --------------------------------------------------
        for f in UNITY_RESULTS_DIR.glob("*_results.json"):
            try:
                f.unlink()
            except Exception as e:
                print(f"WARNING: Could not delete old result {f}: {e}")
                raise

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
            text=True,
            timeout=300
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

    except Exception as e:
        print("\nFULL TRACEBACK:")
        traceback.print_exc()
        raise