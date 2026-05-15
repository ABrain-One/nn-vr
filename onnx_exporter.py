"""Export ONNX via direct module import with validation, memory limits, and strict timeouts."""

from __future__ import annotations

import multiprocessing as mp
import os
import sys
from pathlib import Path
import importlib

import onnx

from shape_utils import infer_in_out_shapes


def _row_to_job_dict(row) -> dict:
    d = row.to_dict()
    prm = d.get("prm")
    if prm is not None and hasattr(prm, "items"):
        d["prm"] = dict(prm)
    return d


def _export_worker(row_dict, dest_str, queue):
    # Fix Windows cp1252 crash when PyTorch prints Unicode (e.g. emojis)
    os.environ["PYTHONIOENCODING"] = "utf-8"
    if sys.stdout.encoding != "utf-8":
        sys.stdout = open(sys.stdout.fileno(), mode="w", encoding="utf-8", errors="replace", closefd=False)
        sys.stderr = open(sys.stderr.fileno(), mode="w", encoding="utf-8", errors="replace", closefd=False)
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

        # 2. Dynamically assign shapes based on the dataset and transform
        prm = row_dict.get("prm", {})
        transform_str = prm.get("transform", "")

        in_shape, out_shape = infer_in_out_shapes(dataset=dataset, transform_str=transform_str)

        device = torch.device("cpu")

        # 3. Instantiate the model
        model = Net(in_shape, out_shape, prm, device)
        
        # 3.5 Load pre-trained weights from HuggingFace
        try:
            # pyrefly: ignore [missing-import]
            from huggingface_hub import hf_hub_download
            temp_dir = str(Path(dest_str).parent.parent / "temp")
            pth = hf_hub_download("NN-Dataset/checkpoints-epoch-50", f"{model_name}.pth", cache_dir=temp_dir)
            ckpt = torch.load(pth, map_location="cpu", weights_only=False)
            model.load_state_dict(
                ckpt["state_dict"] if isinstance(ckpt, dict) and "state_dict" in ckpt else ckpt,
                strict=False
            )
            print(f"Loaded weights for {model_name} from HuggingFace")
        except Exception as e:
            # print(f"Warning: Could not load weights for {model_name}: {e}")
            raise RuntimeError(f"FAILED to load weights for {model_name}: {e}")

        model.eval()

        dummy = torch.randn(in_shape)

        dest = Path(dest_str)
        dest.parent.mkdir(parents=True, exist_ok=True)

        # 4. Export to ONNX
        # Barracuda 3.x officially supports up to opset 12. Opset 14+ has new math operations
        # that will cause the VR headset to silently crash.
        torch.onnx.export(
            model,
            dummy,
            dest,
            opset_version=12, 
            input_names=["input"],
            output_names=["output"],
            # Dynamic axes allow Unity Barracuda to handle different batch sizes if needed later
            dynamic_axes={'input': {0: 'batch_size'}, 'output': {0: 'batch_size'}} 
        )

        # Downgrade ONNX IR version for Barracuda compatibility
        model_onnx = onnx.load(dest)
        model_onnx.ir_version = 7
        onnx.save(model_onnx, dest)

        queue.put((True, None))

    except Exception as e:
        try:
            print(f"FAILED: {row_dict['nn']} - {repr(e)}")
        except UnicodeEncodeError:
            pass
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