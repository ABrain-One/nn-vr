"""Append-only JSON lines logging for benchmark runs."""

from __future__ import annotations

import json
from pathlib import Path


def log(entry: dict, path: str | Path = "results.jsonl") -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
