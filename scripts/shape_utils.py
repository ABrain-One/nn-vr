from __future__ import annotations

import re
from typing import Optional, Tuple


def infer_image_resolution(transform_str: str) -> Optional[int]:
    """
    Infer a square image resolution from a transform identifier string.

    Examples:
      - "echo_128" -> 128
      - "norm_299_flip" -> 299

    Returns None if no resolution can be inferred.
    """
    if not transform_str:
        return None

    # 1. Look for explicit resolution patterns like echo_128 or norm_299
    m = re.search(r"(?:echo|norm)_(\d+)", transform_str)
    if m:
        return int(m.group(1))

    # 2. Check for standard neural network resolution numbers
    # This prevents extracting random augmentation parameters like "CenterCrop_22" or "v1"
    standard_res = re.search(r"\b(64|96|128|160|192|224|256|288|299|331|384|512)\b", transform_str)
    if standard_res:
        return int(standard_res.group(1))

    return None


def infer_in_out_shapes(
    *,
    dataset: str,
    transform_str: str = "",
) -> Tuple[Tuple[int, int, int, int], Tuple[int, ...]]:
    """
    Infer (in_shape, out_shape) for a model given dataset name and transform string.
    Mirrors the logic previously duplicated across process_models + onnx_exporter.
    """
    res = infer_image_resolution(transform_str)

    if res is not None:
        in_shape = (1, 3, res, res)
    else:
        if dataset == "mnist":
            in_shape = (1, 1, 28, 28)
        elif dataset == "imagenette":
            in_shape = (1, 3, 160, 160)
        elif dataset == "cifar-100":
            in_shape = (1, 3, 32, 32)
        else:  # cifar-10, svhn, unknown
            in_shape = (1, 3, 32, 32)

    if dataset == "cifar-100":
        out_shape = (100,)
    else:
        out_shape = (10,)

    return in_shape, out_shape

