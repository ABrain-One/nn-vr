"""ADB: push ONNX, launch Unity benchmark, pull JSON results."""

from __future__ import annotations

import json
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any

# Match BarracudaRunner: shared storage paths on device
REMOTE_MODEL_DIR = "/sdcard/nn_models"
REMOTE_RESULTS_FILE = "/sdcard/nn_results/output.json"
DEFAULT_PACKAGE = "com.DefaultCompany.Test"


def _adb() -> list[str]:
    exe = shutil.which("adb")
    if not exe:
        raise FileNotFoundError(
            "adb not found; install Android platform-tools and add to PATH"
        )
    return [exe]


def device_ready(timeout_sec: float = 5.0) -> bool:
    try:
        subprocess.run(
            _adb() + ["wait-for-device"],
            check=True,
            timeout=timeout_sec,
            capture_output=True,
        )
        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        return False


def ensure_remote_dirs(timeout_sec: float = 30.0) -> None:
    subprocess.run(
        _adb()
        + [
            "shell",
            "mkdir",
            "-p",
            REMOTE_MODEL_DIR,
            str(Path(REMOTE_RESULTS_FILE).parent),
        ],
        check=True,
        timeout=timeout_sec,
        capture_output=True,
    )


def push_model(
    local_path: str | Path,
    model_name: str,
    *,
    timeout_sec: float = 120.0,
) -> None:
    """Push ``local_path`` to ``/sdcard/nn_models/{model_name}.onnx`` (+ optional external data)."""
    local_path = Path(local_path)
    if not model_name.endswith(".onnx"):
        remote = f"{REMOTE_MODEL_DIR}/{model_name}.onnx"
    else:
        remote = f"{REMOTE_MODEL_DIR}/{model_name}"

    ensure_remote_dirs()
    subprocess.run(
        _adb() + ["push", str(local_path), remote],
        check=True,
        timeout=timeout_sec,
        capture_output=True,
        text=True,
    )

    data_file = local_path.parent / "nn.onnx.data"
    if data_file.exists():
        subprocess.run(
            _adb() + ["push", str(data_file), f"{REMOTE_MODEL_DIR}/nn.onnx.data"],
            check=True,
            timeout=timeout_sec,
            capture_output=True,
            text=True,
        )


def run_benchmark(
    model_name: str,
    model_hash: str = "",
    *,
    package: str = DEFAULT_PACKAGE,
    timeout_sec: float = 30.0,
) -> None:
    subprocess.run(
        _adb() + ["shell", "am", "force-stop", package],
        timeout=timeout_sec,
        capture_output=True,
    )
    subprocess.run(
        _adb()
        + [
            "shell",
            "am",
            "start",
            "-n",
            f"{package}/com.unity3d.player.UnityPlayerActivity",
            "--es",
            "model_name",
            model_name,
            "--es",
            "model_hash",
            model_hash,
        ],
        check=True,
        timeout=timeout_sec,
        capture_output=True,
        text=True,
    )


def wait_for_done(
    model_name: str,
    *,
    log_timeout_sec: float = 120.0,
) -> bool:
    """Return True if logcat contains ``DONE {model_name}`` within timeout."""
    subprocess.run(_adb() + ["logcat", "-c"], capture_output=True, timeout=10)
    proc = subprocess.Popen(
        _adb() + ["logcat", "-s", "Unity"],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    assert proc.stdout is not None
    end = time.time() + log_timeout_sec
    try:
        while time.time() < end:
            line = proc.stdout.readline()
            if not line:
                time.sleep(0.05)
                continue
            if f"DONE {model_name}" in line:
                return True
        return False
    finally:
        proc.terminate()
        proc.wait(timeout=5)


def fetch_results(
    local_path: str | Path = "results/output.json",
    *,
    timeout_sec: float = 60.0,
) -> dict[str, Any] | None:
    local_path = Path(local_path)
    local_path.parent.mkdir(parents=True, exist_ok=True)
    r = subprocess.run(
        _adb() + ["pull", REMOTE_RESULTS_FILE, str(local_path)],
        capture_output=True,
        text=True,
        timeout=timeout_sec,
    )
    if r.returncode != 0 or not local_path.is_file():
        return None
    with open(local_path, encoding="utf-8") as f:
        return json.load(f)
