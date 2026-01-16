import os
import json
import shutil
from typing import Dict


class ModelFetchError(Exception):
    pass


CACHE_ROOT = os.path.join(".cache", "nn-dataset")


def _ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


def _import_nn_api():
    # Force UTF-8 to avoid nn-dataset Windows encoding bug
    # os.environ["PYTHONUTF8"] = "1"
    try:
        import ab.nn.api as api
        return api.data
    except ImportError as e:
        raise ModelFetchError(
            "nn-dataset API not installed or failed to initialize.\n"
            "Try reinstalling with:\n"
            "pip install --no-cache-dir git+https://github.com/ABrain-One/nn-dataset "
            "--upgrade --force"
        ) from e


def fetch_model(model_record: Dict) -> str:
    """
    Fetch ONNX model artifact for a given nn-dataset model record.

    Args:
        model_record: metadata dict returned by model_selector.py

    Returns:
        Absolute path to local ONNX file
    """

    model_name = model_record.get("nn")
    if not model_name:
        raise ModelFetchError("Invalid model record: missing 'nn' field")

    model_dir = os.path.join(CACHE_ROOT, model_name)
    model_path = os.path.join(model_dir, "model.onnx")
    metadata_path = os.path.join(model_dir, "metadata.json")

    _ensure_dir(model_dir)

    # If already cached, reuse
    if os.path.isfile(model_path):
        return os.path.abspath(model_path)

    # Fetch via nn-dataset API
    get_model = _import_nn_api()

    try:
        model_info = get_model(model_name)
    except Exception as e:
        raise ModelFetchError(
            f"Failed to fetch model '{model_name}' from nn-dataset: {e}"
        ) from e

    # Resolve ONNX artifact
    onnx_path = model_info.get("onnx")
    if not onnx_path or not os.path.isfile(onnx_path):
        raise ModelFetchError(
            f"ONNX artifact not available for model '{model_name}'"
        )

    # Copy ONNX to cache
    shutil.copyfile(onnx_path, model_path)

    # Save metadata snapshot (for traceability)
    with open(metadata_path, "w") as f:
        json.dump(model_record, f, indent=2)

    return os.path.abspath(model_path)
