#!/usr/bin/env python3
"""
migrate_benchmarks.py
---------------------
One-shot migration: splits the old monolithic unity_benchmarks.json into the
new per-model directory layout so that the resume logic in benchmark_models.py
recognises previously-benchmarked models and skips them correctly.

Target layout (written by unity_runner.save_model_record):
  out/nn/stat/run/onnx/fp32/
    img-classification_cifar-10_acc_{ModelName}/
      windows_{device_sanitized}.json

Run once from the project root:
  python migrate_benchmarks.py

Already-migrated files are never overwritten.
"""

import json
import sys
from pathlib import Path

# Import helpers from the updated unity_runner so the paths are always in sync.
from unity_runner import (
    OUTPUT_ROOT,
    CONFIG_PREFIX,
    sanitize_filename,
)

OLD_FILE = Path(__file__).resolve().parent / "unity_benchmarks.json"


def main() -> None:
    if not OLD_FILE.exists():
        print(f"ERROR: {OLD_FILE} not found – nothing to migrate.")
        sys.exit(1)

    print(f"Reading {OLD_FILE} …")
    data: dict = json.loads(OLD_FILE.read_text(encoding="utf-8"))
    print(f"Found {len(data)} model records.\n")

    migrated = 0
    skipped  = 0
    errors   = 0

    for model_name, record in data.items():
        try:
            device_type: str = record.get("device_type") or "unknown"
            # All existing records were produced on Windows.
            os_prefix = "windows"
            safe_device = sanitize_filename(device_type)
            filename    = f"{os_prefix}_{safe_device}.json"

            folder   = OUTPUT_ROOT / f"{CONFIG_PREFIX}_{model_name}"
            out_path = folder / filename

            if out_path.exists():
                print(f"  SKIP  (already exists) : {out_path.relative_to(OUTPUT_ROOT)}")
                skipped += 1
                continue

            folder.mkdir(parents=True, exist_ok=True)
            with open(out_path, "w", encoding="utf-8") as fh:
                json.dump(record, fh, indent=2)
                fh.write("\n")
            print(f"  OK    {model_name:50s} > {filename}")
            migrated += 1

        except Exception as exc:
            print(f"  ERROR {model_name}: {exc}")
            errors += 1

    print(f"\n{'='*60}")
    print(f"Migration complete.")
    print(f"  Migrated : {migrated}")
    print(f"  Skipped  : {skipped}  (files already present – not overwritten)")
    print(f"  Errors   : {errors}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
