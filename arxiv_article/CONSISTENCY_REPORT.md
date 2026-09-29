# Consistency report

The revised manuscript uses the following source-of-truth artifacts.

| Claim | Value | Source | Status |
|---|---:|---|---|
| Model population | 1,762 | `stats/export_stats.json` | Consistent |
| Successful ONNX exports | 1,732 (98.3%) | `stats/export_stats.json` | Consistent |
| ONNX export failures | 30 (1.7%) | `stats/export_stats.json` | Consistent |
| Successful Unity executions | 814 (46.2%) | `report/evidence_summary.md`; `stats/aggregated_real_gpu_stats.csv` | Consistent |
| RTX campaign passes | 813, 812, 814, 811, 814, 812 | `stats/real_gpu_versions.json` | Consistent |
| Models with six/five RTX timing records | 806 / 8 | `stats/aggregated_real_gpu_stats.csv`; `report/evidence_summary.md` | Consistent |
| CPU/GPU-window CV mean, median, p95 | 25.6/8.8/121.3%; 29.3/5.4/180.2% | `stats/aggregated_real_gpu_stats.csv`; `report/evidence_summary.md` | Consistent |
| RTX CPU/GPU timing-window means | 17.6583 / 0.2137 ms | `stats/real_gpu_timing_summary.json` | Consistent |
| GPU-window lower count | 777/814 (95.5%) | `stats/real_gpu_timing_summary.json` | Consistent |
| Complexity correlations | FLOPs 0.1729/0.2453; parameters 0.1112/0.4253; layers 0.1462/0.4934 | `stats/real_gpu_timing_summary.json` | Consistent |
| Unity/workstation matched rows | 814 | `stats/unity_overhead.csv` | Consistent |
| Unity/workstation CPU/GPU ratio medians | 1.296 / 0.244 | `stats/unity_overhead.csv`; `report/evidence_summary.md` | Consistent; interpreted as per-model-ratio medians |
| llvmpipe campaign denominators | 1,732 each | `stats/generate_stats.py`; regenerated `stats/cpu_gpu_emulated_versions.json` | Corrected |

## Timing semantics audit

`NNVRBenchmark/Assets/Editor/BenchmarkCLI.cs` starts the timer before `worker.Execute(input)`, calls `worker.PeekOutput()`, stops the timer, and only then disposes the output. Vendored Barracuda 3.0.2 source documents `PeekOutput()` as non-blocking (`Barracuda.cs`) and calls `PrepareCacheForAccess(blocking:false)` in `GenericWorker.cs`. `BarracudaBackendsFactory.cs` maps CSharpBurst to `BurstCPUOps`; the latter schedules Burst jobs. The manuscript therefore calls both outputs backend timing windows and does not claim completed inference.

## llvmpipe denominator audit

Versions 1--5 previously counted 1,733 records because they include `rag-0941355086027897acb251dc222fd9f2`; that name is absent from canonical `out/nn/stat/run/onnx/fp32/all_models.json` and present in `stats/export_stats.json` as an export failure. Version 6 contains only the canonical 1,732. The aggregation now filters all llvmpipe versions to the canonical successful-export population.
