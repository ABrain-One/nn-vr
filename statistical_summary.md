# Statistical Summary

> **Note**: Inference timing stats (CPU/GPU ms) are derived from llvmpipe
> (software-emulated GPU) runs. Real GPU timings will be added once those
> benchmark runs complete.

## Dataset & Export

| Total Models | Export Passed | Export Failed |
|---|---|---|
| 1766 | 1733 | 33 |

## Benchmark Results — CPU + Software-emulated GPU (llvmpipe)

*Pass = `valid: true` in benchmark record. Fail = no valid success across all retries.*

| Version  | Passed | Failed |
|----------|-------:|-------:|
| version1 |    714 |   1019 |
| version2 |    169 |   1564 |
| version3 |    169 |   1564 |
| version4 |    401 |   1332 |
| version5 |    814 |    919 |
| version6 |    813 |    919 |

## Inference Performance (Unity / llvmpipe, v5 — most complete run)

- **CPU Inference**: 17.61 ms ± 5.02 (95% CI)
- **GPU Inference (llvmpipe)**: 221.02 ms ± 32.99 (95% CI)
- **Average CPU/GPU Diversity Ratio**: 0.20x ± 0.10

## Mathematical Correlations (llvmpipe data)

- **CPU Time vs FLOPs**: R = 0.171
- **GPU Time vs FLOPs**: R = 0.412
- **CPU Time vs Params**: R = 0.118
- **GPU Time vs Params**: R = 0.538

## Symbolic Regression (PySR) — Discovered Equations

- **CPU Latency**: `log(t_cpu + 1) = log(0.158 × L)` (L = total layers)
- **GPU Latency**: `log(t_gpu + 1) = exp(P_log × 0.108)` (P_log = log parameters)

## Architectural Failure Rates (llvmpipe benchmarks)

| Architecture Flag        | Failed / Total  | Failure Rate |
|--------------------------|-----------------|--------------|
| `is_resnet_like`         | 325 / 630       | 51.6 %       |
| `is_vgg_like`            | 6 / 18          | 33.3 %       |
| `is_transformer_like`    | 108 / 146       | 74.0 %       |
| `has_attention`          | 9 / 10          | 90.0 %       |
| `has_residual_connections` | 56 / 110      | 50.9 %       |

---
*Auto-counts kept in `stats/`. Re-run `python stats/generate_stats.py` to refresh.*
