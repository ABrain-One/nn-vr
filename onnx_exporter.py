"""Export ONNX via direct module import with validation and timeouts."""

from __future__ import annotations

import multiprocessing as mp
from pathlib import Path
import importlib

import onnx


def _row_to_job_dict(row) -> dict:
    d = row.to_dict()
    prm = d.get("prm")
    if prm is not None and hasattr(prm, "items"):
        d["prm"] = dict(prm)
    return d


def _export_worker(row_dict, dest_str, queue):
    try:
        import torch

        model_name = row_dict["nn"]
        dataset = row_dict.get("dataset", "cifar-10")
        print(f"EXPORTING: {model_name} for {dataset}")

        # 1. Safely import the module the same way nn-lite does
        try:
            module = importlib.import_module(f"ab.nn.nn.{model_name}")
        except ImportError as e:
            raise ImportError(f"Failed to import ab.nn.nn.{model_name}: {e}")

        if not hasattr(module, "Net"):
            raise RuntimeError(f"Module ab.nn.nn.{model_name} has no Net class")

        Net = module.Net

        # 2. Dynamically assign shapes based on the dataset
        if dataset == "mnist":
            in_shape = (1, 1, 28, 28)
            out_shape = (1, 10)
        elif dataset == "imagenette":
            in_shape = (1, 3, 160, 160) # Or whatever resolution imagenette uses in your pipeline
            out_shape = (1, 10)
        elif dataset == "cifar-100":
            in_shape = (1, 3, 32, 32)
            out_shape = (1, 100)
        else: # cifar-10, svhn
            in_shape = (1, 3, 32, 32)
            out_shape = (1, 10)

        device = torch.device("cpu")
        prm = row_dict.get("prm", {})

        # 3. Instantiate the model
        model = Net(in_shape, out_shape, prm, device)
        model.eval()

        dummy = torch.randn(in_shape)

        dest = Path(dest_str)
        dest.parent.mkdir(parents=True, exist_ok=True)

        # 4. Export to ONNX
        # Opset 14+ is recommended for modern PyTorch to avoid translation errors
        # torch.onnx.export(
        #     model,
        #     dummy,
        #     dest,
        #     opset_version=14, 
        #     input_names=["input"],
        #     output_names=["output"],
        #     # Dynamic axes allow Unity Barracuda to handle different batch sizes if needed later
        #     dynamic_axes={'input': {0: 'batch_size'}, 'output': {0: 'batch_size'}} 
        # )

        torch.onnx.export(
            model,
            dummy,
            dest,
            opset_version=14, 
            input_names=["input"],
            output_names=["output"]
            # dynamic_axes has been removed to prevent Dynamo crashes 
            # and ensure Barracuda compatibility
        )

        queue.put((True, None))

    except Exception as e:
        print(f"FAILED: {row_dict['nn']} - {repr(e)}")
        queue.put((False, repr(e)))


def export_onnx(row, out_path, *, timeout_sec=60):
    out_path = Path(out_path)
    row_dict = _row_to_job_dict(row)

    # Use 'spawn' context to ensure a clean slate for PyTorch and avoid CUDA/threading deadlocks
    ctx = mp.get_context("spawn")
    queue = ctx.Queue()
    
    proc = ctx.Process(target=_export_worker, args=(row_dict, str(out_path), queue))
    proc.start()
    proc.join(timeout=timeout_sec)

    if proc.is_alive():
        proc.terminate()
        proc.join(timeout=5)
        raise TimeoutError(f"ONNX export exceeded {timeout_sec}s limit; process killed.")

    if queue.empty():
        raise RuntimeError("Export worker exited without result (possible OOM or segfault)")

    ok, err = queue.get()

    if not ok:
        raise RuntimeError(err)

    if not out_path.exists():
        raise FileNotFoundError(f"Missing ONNX at {out_path}")

    # Validate the generated ONNX file
    onnx.checker.check_model(onnx.load(out_path))
    return out_path