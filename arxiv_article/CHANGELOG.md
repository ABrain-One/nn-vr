# Manuscript revision changelog

## Scientific corrections

- Reclassified all Unity measurements as **backend timing windows**: wall-clock time from `worker.Execute()` through non-blocking `worker.PeekOutput()`.
- Removed the unsupported assertion that CSharpBurst timing is synchronous completed-inference latency. Barracuda 3.0.2 maps CSharpBurst to `BurstCPUOps`, which schedules Burst jobs; no completion or output materialization occurs in the timed interval.
- Propagated this correction through the abstract, methodology, results, workstation comparison, deployment guidance, limitations, conclusion, appendix, and timing figure.
- Renamed architecture percentages to **post-export non-completion**. Their denominators are flag-specific successful ONNX exports, not all flagged models in the original population.
- Added Wilson 95% intervals for the six subgroup non-completion proportions and stated the overlap/non-causality limitation.

## Numerical and artifact corrections

- Traced the llvmpipe 1,733-row totals to a stale result for `rag-0941355086027897acb251dc222fd9f2`, which is listed in `stats/export_stats.json` as an ONNX export failure.
- Updated `stats/generate_stats.py` to restrict llvmpipe aggregation to the canonical 1,732 successful ONNX exports without deleting raw records.
- Regenerated `stats/cpu_gpu_emulated_versions.json` and `stats/run_history.md`. Corrected llvmpipe failed counts are 1,018; 1,563; 1,563; 1,331; 918; and 919.
- Re-ran `stats/reproduce_article_claims.py`.

## Structure and writing

- Reorganized top-level manuscript sections to Introduction; Related Work and Background; Methodology; Experiments; Results and Discussion; Conclusion; References; and Appendix.
- Kept RQ1--RQ6 as result/discussion subsections rather than independent top-level sections.
- Made the ratio interpretation explicit: the median of per-model Unity/workstation ratios is not the ratio of population medians.

## Bibliography and reproducibility

- Replaced placeholder metadata for `ABrain.NN-Dataset` and `ABrain.LEMUR2` with the citations supplied by the local NN-Dataset repository.
- Removed unused placeholder `ABrain.*` records.
- Recorded exact Unity, Barracuda, CPU, RAM, OS, Python, GPU, driver, and CUDA values where present in local project files or benchmark metadata.
- Added a `\date{}` command and retained the portable Overleaf layout because no local CVPR style file is available.
