#!/usr/bin/env python3
"""
Sanity-check ONNX export shape inference consistency.

This script compares:
- process_models.get_input_size(transform_str)
- onnx_exporter export-worker regex logic (replicated here)
then exports ONNX for a small sample and validates the ORT input shape.
"""

from __future__ import annotations

import sys
import re
from pathlib import Path

import onnxruntime as ort
import pandas as pd
import importlib

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from onnx_exporter import export_onnx
from process_models import get_input_size
from onnx_validator import eval_onnx_accuracy


def exporter_in_shape(dataset: str, transform_str: str) -> tuple[int, int, int, int]:
    # Replicate onnx_exporter._export_worker parsing exactly
    size_match = (
        re.search(r"_(\d+)", transform_str)
        or re.search(r"complex_(\d+)", transform_str)
        or re.search(r"echo_(\d+)", transform_str)
        or re.search(r"norm_(\d+)", transform_str)
    )
    if not size_match:
        size_match = re.search(r"(\d+)", transform_str)

    if size_match:
        res = int(size_match.group(1))
        return (1, 3, res, res)

    if dataset == "mnist":
        return (1, 1, 28, 28)
    if dataset == "imagenette":
        return (1, 3, 160, 160)
    if dataset == "cifar-100":
        return (1, 3, 32, 32)
    return (1, 3, 32, 32)


def _norm_shape(shape) -> list[int]:
    out: list[int] = []
    for d in shape:
        out.append(d if isinstance(d, int) else 1)
    return out


def _is_importable_ab_model(nn: str) -> bool:
    try:
        importlib.import_module(f"ab.nn.nn.{nn}")
        return True
    except Exception:
        return False


def main():
    root = ROOT
    out_dir = root / "_work" / "sanity_onnx"
    out_dir.mkdir(parents=True, exist_ok=True)

    # Try nn-dataset first (as process_models does). If it's empty / doesn't include
    # img-classification/cifar-10 in this environment, fall back to HF metadata.
    rows: list[pd.Series] = []
    try:
        from model_loader import load_models  # optional dependency path

        d = load_models(limit=20000)
        if d is not None and not d.empty:
            if "task" in d.columns:
                d = d[d["task"] == "img-classification"]
            if "dataset" in d.columns:
                d = d[d["dataset"] == "cifar-10"]
            if d is not None and not d.empty:
                # Keep best-per-base like process_models
                d = d.copy()
                d["nn_base"] = d["nn"].apply(lambda x: str(x).split("-")[0])
                for nn_base, group in d.groupby("nn_base"):
                    best = group.loc[group["accuracy"].idxmax()].copy()
                    best["nn"] = nn_base
                    rows.append(best)
    except Exception:
        rows = []

    if not rows:
        print("[WARN] nn-dataset did not return img-classification/cifar-10 rows; falling back to HF all_models.json")
        from huggingface_hub import hf_hub_download
        import json

        work_dir = root / "_work" / "sanity_onnx"
        work_dir.mkdir(parents=True, exist_ok=True)
        meta_path = hf_hub_download(
            repo_id="NN-Dataset/checkpoints-epoch-50",
            filename="all_models.json",
            local_dir=str(work_dir),
        )
        model_db = json.load(open(meta_path, "r"))

        # Create "rows" compatible with export_onnx (expects .to_dict()).
        for name, entry in model_db.items():
            prm = (entry or {}).get("prm", {}) or {}
            rows.append(
                pd.Series(
                    {
                        "nn": str(name).split("-")[0],
                        "task": "img-classification",
                        "dataset": "cifar-10",
                        "accuracy": float((entry or {}).get("accuracy", 0.0) or 0.0),
                        "prm": prm,
                    }
                )
            )

    # Choose up to 10 unique base models, preferring "interesting" transforms
    picked: list[pd.Series] = []
    seen = set()
    for r in rows:
        nn = str(r.get("nn", "")).split("-")[0]
        if not nn or nn in seen:
            continue
        if not _is_importable_ab_model(nn):
            continue
        prm = r.get("prm", {}) or {}
        t = str(prm.get("transform", "") or "")
        interesting = len(re.findall(r"\d+", t)) >= 2 or any(k in t.lower() for k in ["complex", "echo", "norm"])
        if interesting:
            r2 = r.copy()
            r2["nn"] = nn
            picked.append(r2)
            seen.add(nn)
        if len(picked) >= 7:
            break

    if len(picked) < 10:
        for r in rows:
            nn = str(r.get("nn", "")).split("-")[0]
            if not nn or nn in seen:
                continue
            if not _is_importable_ab_model(nn):
                continue
            r2 = r.copy()
            r2["nn"] = nn
            picked.append(r2)
            seen.add(nn)
            if len(picked) >= 10:
                break

    print("model | transform | target_h(process_models) | target_h(exporter) | onnx_input | acc")
    print("-" * 120)

    data_root = root / "_work" / "data"
    data_root.mkdir(parents=True, exist_ok=True)

    for row in picked:
        nn = row["nn"]
        prm = row.get("prm", {}) or {}
        transform = str(prm.get("transform", "") or "")
        dataset = str(row.get("dataset", "cifar-10") or "cifar-10")

        th_proc = get_input_size(transform)
        in_shape = exporter_in_shape(dataset, transform)
        th_exp = in_shape[-1]

        onnx_path = out_dir / f"{nn}.onnx"
        export_onnx(row, onnx_path, timeout_sec=180)

        sess = ort.InferenceSession(str(onnx_path), providers=["CPUExecutionProvider"])
        ort_inp = sess.get_inputs()[0]
        ort_shape = _norm_shape(ort_inp.shape)

        # Shape assertion: exported ONNX must match exporter-inferred shape
        if ort_shape != list(in_shape):
            raise AssertionError(f"{nn}: ORT input {ort_inp.shape} -> {ort_shape} != expected {in_shape}")

        acc = eval_onnx_accuracy(onnx_path, th_exp, data_root)

        print(f"{nn} | {transform} | {th_proc} | {th_exp} | {tuple(ort_shape)} | {acc:.4f}")


if __name__ == "__main__":
    main()

