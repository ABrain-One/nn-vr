# tests/test_onnx_export.py
import numpy as np
import onnxruntime as ort
import pandas as pd

from onnx_exporter import export_onnx
from shape_utils import infer_in_out_shapes

def test_export_and_onnxruntime_executes(tmp_path):
    # Avoid coupling this test to upstream nn-dataset contents/order.
    # We use a known importable model that has a checkpoint in HF.
    row = pd.Series(
        {
            "nn": "ResNet",
            "dataset": "cifar-10",
            "prm": {"transform": "echo_256_flip"},
        }
    )
    out_path = tmp_path / "m.onnx"
    export_onnx(row, out_path, timeout_sec=180)

    sess = ort.InferenceSession(str(out_path), providers=["CPUExecutionProvider"])
    input_name = sess.get_inputs()[0].name
    # ORT shape may contain symbolic dims (None / "batch"), so we normalize them.
    ort_inp = sess.get_inputs()[0]
    shape = []
    for d in ort_inp.shape:
        if isinstance(d, int):
            shape.append(d)
        else:
            shape.append(1)  # default for dynamic/unknown dims

    x = np.random.randn(*shape).astype(np.float32)

    outputs = sess.run(None, {input_name: x})
    assert outputs is not None
    assert isinstance(outputs, list)
    assert len(outputs) >= 1
    assert outputs[0] is not None


def test_exported_input_shape_matches_inference(tmp_path):
    row = pd.Series(
        {
            "nn": "ResNet",
            "dataset": "cifar-10",
            "prm": {"transform": "echo_256_flip"},
        }
    )
    out_path = tmp_path / "shape.onnx"
    export_onnx(row, out_path, timeout_sec=180)

    (in_shape, _out_shape) = infer_in_out_shapes(dataset="cifar-10", transform_str="echo_256_flip")

    sess = ort.InferenceSession(str(out_path), providers=["CPUExecutionProvider"])
    ort_inp = sess.get_inputs()[0]
    norm = []
    for d in ort_inp.shape:
        norm.append(d if isinstance(d, int) else 1)

    assert tuple(norm) == in_shape