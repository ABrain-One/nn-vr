#!/usr/bin/env python3
"""
NN-VR: End-to-end ONNX pipeline — from HuggingFace model fetch to Unity inference.

Stages
------
1. ONNX Export   — fetch architectures + weights from HF, export to ONNX, evaluate
                   CIFAR-10 accuracy.  (process_models.py)
2. Unity Bench   — run each ONNX through Unity Barracuda batchmode, persist timing
                   + shape results under out/nn/stat/run/onnx/fp32/ (per-model JSON).
                   (benchmark_models.py)

Usage
-----
Full pipeline (export then benchmark):
    python main.py

Export only (no Unity):
    python main.py --skip-device

Benchmark only (skip export, use existing ONNX files in _work/onnx_temp/):
    python main.py --benchmark-only

Resume export where it stopped, then benchmark:
    python main.py                   # state file keeps track automatically

Force re-export everything then benchmark:
    python main.py --force

Specific models only:
    python main.py ResNet,VGG --benchmark-only
    python main.py ResNet,VGG --skip-device
"""

import argparse
import sys


def main():
    ap = argparse.ArgumentParser(
        description="NN-VR end-to-end pipeline: HF fetch -> ONNX export -> Unity benchmark",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # ── Positional (optional) ────────────────────────────────────────────────
    ap.add_argument(
        "models",
        nargs="?",
        default=None,
        help="Comma-separated model names to process (default: all)",
    )

    # ── Stage control ────────────────────────────────────────────────────────
    stage = ap.add_mutually_exclusive_group()
    stage.add_argument(
        "--skip-device",
        action="store_true",
        help="Export ONNX + evaluate accuracy only; skip Unity benchmarking",
    )
    stage.add_argument(
        "--benchmark-only",
        action="store_true",
        help="Skip ONNX export; run Unity benchmarking on existing _work/onnx_temp/*.onnx files",
    )
    
    # ── Storage options ──────────────────────────────────────────────────────
    ap.add_argument(
        "--low-storage",
        action="store_true",
        help="Interleave ONNX export and benchmarking, deleting each ONNX file after it's benchmarked.",
    )

    # ── Export options ───────────────────────────────────────────────────────
    ap.add_argument("--limit", type=int, default=None, help="Max models to export")
    ap.add_argument("--dataset", default="cifar-10")
    ap.add_argument("--export-timeout", type=float, default=120.0)
    ap.add_argument("--android-runs", type=int, default=20)
    ap.add_argument("--force", action="store_true", help="Reset export state, reprocess all")
    ap.add_argument("--push-hf", action="store_true", help="Upload results to HuggingFace Hub")

    args = ap.parse_args()

    # ── Pre-Cleanup / Benchmark Leftovers (Low Storage Mode) ─────────────────
    if getattr(args, "low_storage", False) and not args.skip_device and not args.benchmark_only:
        from pathlib import Path
        onnx_temp = Path("_work/onnx_temp")
        if onnx_temp.exists() and any(onnx_temp.glob("*.onnx")):
            print("Found leftover ONNX files. Benchmarking and cleaning them up before resuming export...")
            from ab.vr.benchmark_models import run_benchmarks
            models_list = [m.strip() for m in args.models.split(",")] if args.models else None
            run_benchmarks(models=models_list)
            for f in onnx_temp.glob("*.onnx"):
                try:
                    f.unlink()
                except Exception:
                    pass

    # ── Stage 1: ONNX Export ─────────────────────────────────────────────────
    if not args.benchmark_only:
        # Forward all relevant flags to process_models.main() by rebuilding sys.argv
        # so its own argparse parser sees the right arguments.
        export_argv = [sys.argv[0]]
        if args.models:
            export_argv.append(args.models)
        # Always pass --skip-device to process_models: Stage 1 is ONNX export only.
        # Unity benchmarking is handled exclusively by Stage 2 (benchmark_models.py).
        export_argv.append("--skip-device")
        
        # Interleave Unity benchmark to save disk space
        if getattr(args, "low_storage", False) and not args.skip_device:
            export_argv.append("--unity-benchmark")
            
        if args.force:
            export_argv.append("--force")
        if args.push_hf:
            export_argv.append("--push-hf")
        if args.limit:
            export_argv += ["--limit", str(args.limit)]
        if args.dataset != "cifar-10":
            export_argv += ["--dataset", args.dataset]
        if args.export_timeout != 120.0:
            export_argv += ["--export-timeout", str(args.export_timeout)]
        if args.android_runs != 20:
            export_argv += ["--android-runs", str(args.android_runs)]

        # Temporarily replace sys.argv so process_models.main() parses correctly
        original_argv = sys.argv
        sys.argv = export_argv

        from ab.vr.process_models import main as export_main
        export_main()

        sys.argv = original_argv

    # ── Stage 2: Unity Benchmark ─────────────────────────────────────────────
    if not args.skip_device:
        from ab.vr.benchmark_models import run_benchmarks
        models_list = [m.strip() for m in args.models.split(",")] if args.models else None
        run_benchmarks(models=models_list)
        
        # Cleanup
        if getattr(args, "low_storage", False):
            from pathlib import Path
            onnx_temp = Path("_work/onnx_temp")
            if onnx_temp.exists():
                for f in onnx_temp.glob("*.onnx"):
                    try:
                        f.unlink()
                    except Exception:
                        pass


if __name__ == "__main__":
    main()
