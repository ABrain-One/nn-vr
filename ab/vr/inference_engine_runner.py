"""Unity 6 / Inference Engine invocation isolated to Experiment B."""

from __future__ import annotations

import json
import os
import platform
import re
import shutil
import signal
import socket
import subprocess
import time
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent.parent
UNITY_EXE = Path("/home/syedalihaider/Unity/Hub/Editor/6000.6.5f1/Unity")
UNITY_PROJECT = ROOT_DIR / "NNVRBenchmark"
UNITY_MODELS_DIR = UNITY_PROJECT / "Assets" / "Models"
UNITY_RESULTS_DIR = UNITY_PROJECT / "Assets" / "Results"


def get_device_type() -> str:
    """Use the same Linux hostname result-key convention as Experiment A."""
    if platform.system() != "Windows":
        return socket.gethostname()
    return socket.gethostname()


def _clear_model_assets() -> None:
    # Unity creates a .meta file next to every copied ONNX asset. Remove only
    # the known transient model and its metadata, never arbitrary project data.
    for filename in (
        "model.onnx", "model.onnx.meta", "model.onnx.data", "model.onnx.data.meta",
        "model_input_shape.json", "model_input_shape.json.meta",
    ):
        (UNITY_MODELS_DIR / filename).unlink(missing_ok=True)


def run_unity_benchmark(onnx_path: Path, input_shape: tuple[int, ...], timeout_sec: float = 300.0) -> dict:
    """Copy one temporary ONNX artifact into B's Unity project and benchmark it."""
    if not UNITY_EXE.is_file():
        raise FileNotFoundError(f"Unity 6 executable not found: {UNITY_EXE}")
    onnx_path = onnx_path.resolve()
    if not onnx_path.is_file():
        raise FileNotFoundError(onnx_path)

    UNITY_MODELS_DIR.mkdir(parents=True, exist_ok=True)
    UNITY_RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    _clear_model_assets()
    target_onnx = UNITY_MODELS_DIR / "model.onnx"
    shutil.copy2(onnx_path, target_onnx)
    (UNITY_MODELS_DIR / "model_input_shape.json").write_text(
        json.dumps({"shape": list(input_shape)}) + "\n", encoding="utf-8"
    )
    data_file = onnx_path.with_suffix(".onnx.data")
    if data_file.is_file():
        shutil.copy2(data_file, UNITY_MODELS_DIR / "model.onnx.data")

    for old_result in UNITY_RESULTS_DIR.glob("*_results.json"):
        old_result.unlink()

    command = [
        str(UNITY_EXE),
        "-batchmode",
        "-force-vulkan",
        "-projectPath", str(UNITY_PROJECT),
        "-executeMethod", "BenchmarkCLI.RunBenchmark",
        "-quit",
    ]
    print("RUNNING UNITY 6 INFERENCE ENGINE BENCHMARK...", flush=True)
    print(" ".join(command), flush=True)
    environment = os.environ.copy()
    environment["VK_ICD_FILENAMES"] = "/usr/share/vulkan/icd.d/nvidia_icd.json"
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=environment,
        start_new_session=(platform.system() != "Windows"),
    )
    try:
        stdout, stderr = process.communicate(timeout=timeout_sec)
    except subprocess.TimeoutExpired as exc:
        if platform.system() != "Windows":
            try:
                os.killpg(process.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
        else:
            process.terminate()
        try:
            stdout, stderr = process.communicate(timeout=15)
        except subprocess.TimeoutExpired:
            if platform.system() != "Windows":
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
            else:
                process.kill()
            stdout, stderr = process.communicate()
        raise RuntimeError(
            f"Unity 6 benchmark timed out after {timeout_sec:g} seconds; its process group was terminated"
        ) from exc

    if stdout:
        print("UNITY STDOUT:\n" + stdout, flush=True)
    if stderr:
        print("UNITY STDERR:\n" + stderr, flush=True)
    if process.returncode != 0:
        raise RuntimeError(f"Unity 6 exited with code {process.returncode}")

    json_files = list(UNITY_RESULTS_DIR.glob("*_results.json"))
    if not json_files:
        raise RuntimeError("No Unity 6 results JSON found.")
    result_file = max(json_files, key=lambda path: path.stat().st_mtime)
    try:
        return json.loads(result_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Invalid Unity 6 result JSON: {result_file}") from exc
