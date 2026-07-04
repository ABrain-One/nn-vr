import json
import platform
import re
import shutil
import socket
import subprocess
import time
import traceback
from pathlib import Path


# --------------------------------------------------
# BENCHMARK OUTPUT LAYOUT (matches nn-dataset stat/run)
# --------------------------------------------------

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
OUTPUT_ROOT = ROOT_DIR / "out" / "nn" / "stat" / "run" / "onnx" / "fp32"
CONFIG_PREFIX = "img-classification_cifar-10_acc"


def sanitize_filename(s: str) -> str:
    return "".join(c if (c.isalnum() or c in ("-", "_")) else "_" for c in s)


def get_device_type() -> str:
    """Human-readable device label (prefers product + CPU over hostname)."""
    if platform.system() != "Windows":
        return socket.gethostname()
    try:
        ps = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                "$cs = Get-CimInstance Win32_ComputerSystem; "
                "$cpu = (Get-CimInstance Win32_Processor | Select-Object -First 1).Name; "
                "Write-Output $cs.Manufacturer; Write-Output $cs.Model; Write-Output $cpu",
            ],
            capture_output=True,
            text=True,
            timeout=15,
            check=True,
        )
        lines = [ln.strip() for ln in ps.stdout.strip().splitlines() if ln.strip()]
        if len(lines) >= 3:
            _manufacturer, model, cpu = lines[0], lines[1], lines[2]
            cpu_match = re.search(r"i7-(\d+\w*)", cpu, re.I)
            if "omen" in model.lower() and cpu_match:
                return f"HP Omen 16 i7-{cpu_match.group(1)}"
            return f"{lines[0]} {model}".strip()
    except Exception:
        pass
    return socket.gethostname()


def device_result_filename(device_type: str | None = None) -> str:
    device_type = device_type or get_device_type()
    os_prefix = "windows" if platform.system() == "Windows" else "linux"
    return f"{os_prefix}_{sanitize_filename(device_type)}.json"


def model_result_path(model_name: str, device_type: str | None = None) -> Path:
    device_type = device_type or get_device_type()
    folder = OUTPUT_ROOT / f"{CONFIG_PREFIX}_{model_name}"
    return folder / device_result_filename(device_type)


def save_model_record(record: dict, model_name: str | None = None) -> Path:
    model_name = model_name or record.get("model_name")
    if not model_name:
        raise ValueError("model_name is required to save a benchmark record")
    device_type = record.get("device_type") or get_device_type()
    record["device_type"] = device_type
    path = model_result_path(model_name, device_type)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(record, f, indent=2)
        f.write("\n")
    return path


def load_model_record(model_name: str, device_type: str | None = None) -> dict | None:
    path = model_result_path(model_name, device_type)
    if not path.exists() or path.stat().st_size == 0:
        return None
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return None


def is_model_benchmarked(model_name: str, device_type: str | None = None) -> bool:
    record = load_model_record(model_name, device_type)
    return bool(record and record.get("valid") is True)


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
        
        time.sleep(1.5)
    
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