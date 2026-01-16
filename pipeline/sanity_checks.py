# VR + Barracuda checks

import os
import onnx
import onnxruntime as ort

MAX_OPSET = 11
MAX_MODEL_SIZE_MB = 100


class SanityCheckError(Exception):
    pass


def check_model_exists(path: str):
    if not os.path.isfile(path):
        raise SanityCheckError(f"Model file not found: {path}")


def check_model_size(path: str):
    size_mb = os.path.getsize(path) / (1024 * 1024)
    if size_mb > MAX_MODEL_SIZE_MB:
        raise SanityCheckError(
            f"Model too large for VR: {size_mb:.2f} MB > {MAX_MODEL_SIZE_MB} MB"
        )


def check_onnx_opset(path: str):
    model = onnx.load(path)

    if not model.opset_import:
        raise SanityCheckError("ONNX model has no opset information")

    opset = model.opset_import[0].version

    if opset > MAX_OPSET:
        raise SanityCheckError(
            f"Unsupported ONNX opset {opset} (Barracuda supports ≤ {MAX_OPSET})"
        )


def check_onnxruntime_load(path: str):
    try:
        ort.InferenceSession(path, providers=["CPUExecutionProvider"])
    except Exception as e:
        raise SanityCheckError(f"ONNXRuntime failed to load model: {e}")


def run_sanity_checks(path: str):
    """
    Raises SanityCheckError on failure.
    Returns True on success.
    """
    check_model_exists(path)
    check_model_size(path)
    check_onnx_opset(path)
    check_onnxruntime_load(path)

    return True
