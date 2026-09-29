#!/usr/bin/env python3
"""Recompute the numerical claims in report/main.tex from committed artifacts.

This script uses only the Python standard library. Run it from the repository
root with: python stats/reproduce_article_claims.py
"""

from __future__ import annotations

import csv
import json
import math
import statistics
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
REPORT = ROOT / "report" / "evidence_summary.md"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def finite_float(value: str | None) -> float | None:
    try:
        result = float(value)  # type: ignore[arg-type]
        return result if math.isfinite(result) else None
    except (TypeError, ValueError):
        return None


def percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    index = (len(ordered) - 1) * fraction
    low, high = math.floor(index), math.ceil(index)
    if low == high:
        return ordered[low]
    return ordered[low] + (ordered[high] - ordered[low]) * (index - low)


def fmt_percent(value: float) -> str:
    return f"{value * 100:.1f}%"


def pearson(values_a: list[float], values_b: list[float]) -> float:
    mean_a, mean_b = statistics.mean(values_a), statistics.mean(values_b)
    numerator = sum((a - mean_a) * (b - mean_b) for a, b in zip(values_a, values_b))
    denominator = math.sqrt(
        sum((a - mean_a) ** 2 for a in values_a)
        * sum((b - mean_b) ** 2 for b in values_b)
    )
    return numerator / denominator


def average_ranks(values: list[float]) -> list[float]:
    order = sorted(range(len(values)), key=values.__getitem__)
    ranks = [0.0] * len(values)
    start = 0
    while start < len(order):
        end = start
        while end + 1 < len(order) and values[order[end + 1]] == values[order[start]]:
            end += 1
        rank = (start + end + 2) / 2
        for position in range(start, end + 1):
            ranks[order[position]] = rank
        start = end + 1
    return ranks


def main() -> None:
    export = json.loads((ROOT / "stats" / "export_stats.json").read_text())
    versions = json.loads((ROOT / "stats" / "real_gpu_versions.json").read_text())
    timing = json.loads((ROOT / "stats" / "real_gpu_timing_summary.json").read_text())
    real = read_csv(ROOT / "stats" / "aggregated_real_gpu_stats.csv")
    unity = read_csv(ROOT / "aggregated_unity_stats.csv")
    workstation = read_csv(ROOT / "stats" / "unity_overhead.csv")

    total = export["total_models"]
    exported = export["export_passed"]
    successful = len(real)
    gpu_passes = [versions["versions"][f"version{i}"]["benchmark_passed"] for i in range(1, 7)]

    cpu_cv = [finite_float(row["cpu_cv"]) for row in real]
    gpu_cv = [finite_float(row["gpu_cv"]) for row in real]
    cpu_cv = [x for x in cpu_cv if x is not None]
    gpu_cv = [x for x in gpu_cv if x is not None]
    version_counts: dict[str, int] = {}
    for row in real:
        version_counts[row["num_versions"]] = version_counts.get(row["num_versions"], 0) + 1

    cpu_faster = [
        row for row in real
        if finite_float(row["cpu_mean_ms"]) is not None
        and finite_float(row["gpu_mean_ms"]) is not None
        and float(row["cpu_mean_ms"]) < float(row["gpu_mean_ms"])
    ]
    gpu_faster = successful - len(cpu_faster)

    def med(rows: list[dict[str, str]], column: str) -> float:
        values = [finite_float(row[column]) for row in rows]
        values = [x for x in values if x is not None]
        return statistics.median(values)

    family_rows = []
    labels = [
        ("has_attention", "Has attention"),
        ("is_transformer_like", "Transformer-like"),
        ("has_residual_connections", "Residual connections"),
        ("is_resnet_like", "ResNet-like"),
        ("is_vgg_like", "VGG-like"),
        ("is_mobilenet_like", "MobileNet-like"),
    ]
    for column, label in labels:
        members = [row for row in unity if row.get(column) in {"1", "1.0"}]
        passes = sum(row.get("status") == "success" for row in members)
        family_rows.append((label, len(members), passes, len(members) - passes))

    llvmpipe_success = [row for row in unity if row.get("status") == "success"]
    llvmpipe_cpu = [finite_float(row.get("unity_cpu_duration_mean")) for row in llvmpipe_success]
    llvmpipe_gpu = [finite_float(row.get("unity_gpu_duration_mean")) for row in llvmpipe_success]
    llvmpipe_cpu = [x for x in llvmpipe_cpu if x is not None]
    llvmpipe_gpu = [x for x in llvmpipe_gpu if x is not None]

    workstation_summary = {}
    for backend in ("cpu", "gpu"):
        unity_values = [float(row[f"unity_{backend}_ms"]) for row in workstation]
        reference_values = [float(row[f"lemur_{backend}_ms"]) for row in workstation]
        ratios = [float(row[f"{backend}_overhead_multiplier"]) for row in workstation]
        workstation_summary[backend] = {
            "unity_median": statistics.median(unity_values),
            "reference_median": statistics.median(reference_values),
            "ratio_median": statistics.median(ratios),
            "ratio_geomean": math.exp(statistics.mean([math.log(x) for x in ratios if x > 0])),
            "ratio_q1": percentile(ratios, .25),
            "ratio_q3": percentile(ratios, .75),
            "ratio_above_one": sum(x > 1 for x in ratios) / len(ratios),
            "spearman": pearson(average_ranks(unity_values), average_ranks(reference_values)),
        }

    correlations = timing["correlations"]
    lines = [
        "# Evidence Summary for `report/main.tex`",
        "",
        "Generated by `python stats/reproduce_article_claims.py`. The script reads the committed aggregate artifacts and does not modify source measurements.",
        "",
        "## Compatibility",
        "",
        f"- Population: **{total}** models.",
        f"- ONNX export: **{exported}/{total}** ({fmt_percent(exported / total)}).",
        f"- End-to-end execution-successful models: **{successful}/{total}** ({fmt_percent(successful / total)}).",
        f"- Exported but Unity-benchmark unsuccessful: **{exported - successful}/{total}** ({fmt_percent((exported - successful) / total)}).",
        "",
        "| Flag | Total | Successful | Failed | Failure rate |",
        "|---|---:|---:|---:|---:|",
    ]
    for label, count, passed, failed in family_rows:
        lines.append(f"| {label} | {count} | {passed} | {failed} | {fmt_percent(failed / count)} |")

    lines.extend([
        "",
        "## RTX 4090/Vulkan reproducibility",
        "",
        f"- Per-campaign successful-model counts: **{', '.join(map(str, gpu_passes))}** (range {min(gpu_passes)}--{max(gpu_passes)}).",
        f"- Timing-record coverage: **{version_counts.get('6', 0)}** models in all six campaigns and **{version_counts.get('5', 0)}** in five campaigns.",
        f"- CPU across-campaign CV: mean **{fmt_percent(statistics.mean(cpu_cv))}**, median **{fmt_percent(statistics.median(cpu_cv))}**, p95 **{fmt_percent(percentile(cpu_cv, .95))}**.",
        f"- GPU dispatch-window CV: mean **{fmt_percent(statistics.mean(gpu_cv))}**, median **{fmt_percent(statistics.median(gpu_cv))}**, p95 **{fmt_percent(percentile(gpu_cv, .95))}**.",
        "",
        "## Recorded runtime observations",
        "",
        f"- CPU campaign-mean average: **{timing['cpu_mean_ms']:.4f} ms**; GPU dispatch-window average: **{timing['gpu_mean_ms']:.4f} ms**.",
        f"- GPU dispatch window lower than CPU mean for **{gpu_faster}/{successful}** models ({fmt_percent(gpu_faster / successful)}).",
        f"- CPU-faster subset median parameters/layers: **{med(cpu_faster, 'total_params'):,.0f} / {med(cpu_faster, 'total_layers'):,.0f}**; remaining models: **{med([r for r in real if r not in cpu_faster], 'total_params'):,.0f} / {med([r for r in real if r not in cpu_faster], 'total_layers'):,.0f}**.",
        f"- llvmpipe aggregate mean CPU/GPU windows: **{statistics.mean(llvmpipe_cpu):.2f} / {statistics.mean(llvmpipe_gpu):.2f} ms**.",
        "- Interpretation boundary: the Unity code stops the timer after `PeekOutput()` and before output disposal, with no explicit output read/download in the timed interval. These are dispatch-window observations, not validated synchronized end-to-end GPU latencies.",
        "",
        "## Correlations with RTX recorded values",
        "",
        "| Feature | CPU Pearson r | GPU-window Pearson r |",
        "|---|---:|---:|",
    ])
    for feature in ("FLOPs", "Params", "Layers"):
        lines.append(f"| {feature} | {correlations[feature]['cpu']:.4f} | {correlations[feature]['gpu']:.4f} |")
    lines.extend([
        "",
        "## Observational workstation comparison",
        "",
        f"- Matched rows in `stats/unity_overhead.csv`: **{len(workstation)}**.",
        "- These ratios are descriptive only: the artifact does not establish equal input geometry, timing synchronization, preprocessing, or system load between the Unity and workstation collections.",
        "",
        "| Backend | Unity median (ms) | Workstation median (ms) | Ratio median | Ratio geometric mean | Ratio IQR | Spearman rank agreement |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ])
    for backend, label in (("cpu", "CPU"), ("gpu", "GPU window")):
        item = workstation_summary[backend]
        lines.append(
            f"| {label} | {item['unity_median']:.4f} | {item['reference_median']:.4f} | "
            f"{item['ratio_median']:.3f} | {item['ratio_geomean']:.3f} | "
            f"{item['ratio_q1']:.3f}--{item['ratio_q3']:.3f} | {item['spearman']:.3f} |"
        )
    lines.extend([
        "",
        f"- CPU ratio greater than one (Unity recorded slower): **{fmt_percent(workstation_summary['cpu']['ratio_above_one'])}** of matched models.",
        f"- GPU-window ratio greater than one: **{fmt_percent(workstation_summary['gpu']['ratio_above_one'])}** of matched models; this is not an end-to-end GPU speed claim because the Unity numerator is an unsynchronized dispatch window.",
        "",
        "## Traceability",
        "",
        "- Export counts: `stats/export_stats.json`.",
        "- Campaign counts: `stats/real_gpu_versions.json`.",
        "- Per-model campaign aggregates and CVs: `stats/aggregated_real_gpu_stats.csv`.",
        "- Family flags/outcomes: `aggregated_unity_stats.csv`.",
        "- Means and correlations: `stats/real_gpu_timing_summary.json`.",
        "- Matched Unity/workstation comparison: `stats/unity_overhead.csv`.",
        "- Benchmark timing implementation: `NNVRBenchmark/Assets/Editor/BenchmarkCLI.cs`.",
        "",
    ])
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {REPORT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
