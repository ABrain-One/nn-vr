#!/usr/bin/env python3
"""
Linear pipeline: nn-dataset row → ONNX → headset → Barracuda → JSON log.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

from logger import log
from model_loader import load_models
from onnx_exporter import export_onnx
from vr_runner import (
    DEFAULT_PACKAGE,
    device_ready,
    fetch_results,
    push_model,
    run_benchmark,
    wait_for_done,
)


def _file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    p = argparse.ArgumentParser(description="NN-VR ONNX → Barracuda benchmark pipeline")
    p.add_argument("--limit", type=int, default=None, help="Max rows from nn-dataset")
    p.add_argument("--nn", type=str, default=None, help="Filter by model name")
    p.add_argument(
        "--export-timeout",
        type=float,
        default=60.0,
        help="Kill ONNX export subprocess after this many seconds",
    )
    p.add_argument(
        "--skip-device",
        action="store_true",
        help="Only export ONNX; do not use ADB",
    )
    p.add_argument(
        "--package",
        type=str,
        default=DEFAULT_PACKAGE,
        help="Android applicationId for am start",
    )
    p.add_argument(
        "--log-file",
        type=str,
        default="results.jsonl",
        help="Append-only JSON lines benchmark log",
    )
    p.add_argument(
        "--models-dir",
        type=str,
        default="models",
        help="Directory for exported .onnx files",
    )
    args = p.parse_args()

    df = load_models(limit=args.limit, nn=args.nn)
    if df.empty:
        print("No models matched.", file=sys.stderr)
        sys.exit(1)

    models_dir = Path(args.models_dir)
    models_dir.mkdir(parents=True, exist_ok=True)

    if not args.skip_device and not device_ready():
        print("No ADB device; use --skip-device to export ONNX only.", file=sys.stderr)
        sys.exit(1)

    df = df[df["task"] == "img-classification"]
    df = df[df["dataset"].isin(["cifar-10","mnist","svhn","imagenette"])]

    for _, row in df.iterrows():
        if row["task"] != "img-classification":
            continue

        if row["dataset"] not in ["cifar-10", "cifar-100", "mnist", "svhn", "imagenette"]:
            continue
        # name = row["nn"]
        # onnx_path = models_dir / f"{name}.onnx"
        name = row["nn"]
        uid = row["id"] if "id" in row else _
        onnx_path = models_dir / f"{name}_{uid}.onnx"
        entry: dict = {"model": name, "status": "failed"}

        try:
            print("EXPORTING:", name)
            if onnx_path.exists():
                print("ALREADY EXISTS:", name)
                continue
            export_onnx(row, onnx_path, timeout_sec=args.export_timeout)
            entry["onnx_path"] = str(onnx_path.resolve())

            if args.skip_device:
                entry["status"] = "exported"
                log(entry, args.log_file)
                continue

            h = _file_sha256(onnx_path)
            push_model(onnx_path, name)
            run_benchmark(name, h, package=args.package)
            if not wait_for_done(name):
                entry["error"] = "logcat completion timeout"
                log(entry, args.log_file)
                continue

            bench = fetch_results()
            entry["status"] = "success"
            entry["benchmark"] = bench
            entry["model_hash"] = h
            log(entry, args.log_file)

        except Exception as e:
            entry["error"] = repr(e)
            log(entry, args.log_file)


if __name__ == "__main__":
    main()
    # from model_loader import load_models

    # df = load_models(limit=None)
    # print(df["task"].value_counts())
    # print(df["dataset"].value_counts())
    # main()
