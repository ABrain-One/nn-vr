# Artifact source inventory

Inventory timestamp (UTC): 2026-11-15T22:12:10.478472+00:00

Inventory was collected read-only before copying inputs. No existing file was changed. Sizes are bytes except explicitly labeled directory groups. Paths are repository relative.

## Repositories

### nn-vr
- Branch: `main`; HEAD: `d103cd388e57f7ae6070bd3fb3c9d0c678337b9f`.
- Remote: https://github.com/ABrain-One/nn-vr.git
- Working-tree status at inventory:
```text
?? ARTICLE_V3_ARXIV_PACKAGING_PLAN.md
?? ARTICLE_V3_CLAIM_MATRIX.md
?? ARTICLE_V3_FIGURE_TABLE_PLAN.md
?? ARTICLE_V3_FORENSIC_AUDIT.md
?? ARTICLE_V3_RELATED_WORK_PLAN.md
?? ARTICLE_V3_STRUCTURE_PLAN.md
?? REFERENCE_PAPER_LESSONS.md
?? arxiv_article_v3/
?? arxiv_article_v3_1/
?? arxiv_article_v3_2/
?? practicum_report_official_template/
```

### nn-dataset
- Branch: `main`; HEAD: `fa7c741fbb372cb4360296ac5f508253c67a8633`.
- Remote: https://github.com/ABrain-One/nn-dataset.git
- Working-tree status at inventory:
```text
(clean)
```

### nn-vr-experiment-b
- Branch: `experiment-b-inference-engine`; HEAD: `642e8cd42277dbfbaad19a5fe4acaca4dd7fbe59`.
- Remote: https://github.com/ABrain-One/nn-vr.git
- Working-tree status at inventory:
```text
M NNVRBenchmark/Assets/Editor/BenchmarkCLI.cs
 M NNVRBenchmark/Assets/Scripts/BenchmarkRunner.cs
 M NNVRBenchmark/Packages/manifest.json
 M NNVRBenchmark/Packages/packages-lock.json
 M NNVRBenchmark/ProjectSettings/EditorBuildSettings.asset
 M NNVRBenchmark/ProjectSettings/ProjectSettings.asset
 M NNVRBenchmark/ProjectSettings/ProjectVersion.txt
?? EXPERIMENT_B_PROTOCOL.md
?? NNVRBenchmark/NNVRBenchmark.slnx
?? NNVRBenchmark/ProjectSettings/MultiplayerManager.asset
?? NNVRBenchmark/ProjectSettings/PhysicsCoreProjectSettings2D.asset
?? NNVRBenchmark/ProjectSettings/ProjectAuditorSettings.asset
?? ab/vr/experiment_b.py
?? ab/vr/inference_engine_runner.py
```

Both repositories contain root MIT license notices. nn-dataset also has dependency/model-specific notices in doc/licenses; those model sources are not copied. The nn-vr .gitignore excludes analysis/, nn-dataset/, out/, models/, environments, caches, and build products. Those exclusions do not make retained evidence expendable.

| Repository | Relative source | Bytes | Needed | Safe to release | Copied to | Purpose / exclusion reason |
|---|---|---:|---|---|---|---|
| nn-vr | analysis/experiment_ab/EXPERIMENT_AB_COMPARISON_REPORT.md | 9966 | False | not packaged | None | Not used by a V3.2 output, redundant working report/plot, or generated cache. |
| nn-vr | analysis/experiment_ab/EXPERIMENT_AB_CONSISTENCY_REPORT.md | 1501 | False | not packaged | None | Not used by a V3.2 output, redundant working report/plot, or generated cache. |
| nn-vr | analysis/experiment_ab/FIGURE_TABLE_RECOMMENDATIONS.md | 1784 | False | not packaged | None | Not used by a V3.2 output, redundant working report/plot, or generated cache. |
| nn-vr | analysis/experiment_ab/REPORT_FEEDBACK_RECONCILIATION.md | 4707 | False | not packaged | None | Not used by a V3.2 output, redundant working report/plot, or generated cache. |
| nn-vr | analysis/experiment_ab/__pycache__/analyze_experiment_ab.cpython-310.pyc | 52763 | False | not packaged | None | Not used by a V3.2 output, redundant working report/plot, or generated cache. |
| nn-vr | analysis/experiment_ab/analyze_experiment_ab.py | 60489 | True | yes after path audit | provenance/analysis_source/analyze_experiment_ab.py.txt | Selected paper claim evidence or source provenance. |
| nn-vr | analysis/experiment_ab/architecture_comparison.csv | 1549 | True | yes after path audit | architecture/architecture_comparison.csv | Selected paper claim evidence or source provenance. |
| nn-vr | analysis/experiment_ab/campaign_audit.csv | 2033 | True | yes after path audit | campaign_audit/campaign_audit.csv | Selected paper claim evidence or source provenance. |
| nn-vr | analysis/experiment_ab/compatibility_transition.csv | 96129 | True | yes after path audit | compatibility/compatibility_transition.csv | Selected paper claim evidence or source provenance. |
| nn-vr | analysis/experiment_ab/complexity_correlations.csv | 1098 | True | yes after path audit | complexity/complexity_correlations.csv | Selected paper claim evidence or source provenance. |
| nn-vr | analysis/experiment_ab/cpu_gpu_architecture.csv | 959 | False | not packaged | None | Not used by a V3.2 output, redundant working report/plot, or generated cache. |
| nn-vr | analysis/experiment_ab/cpu_gpu_behavior.csv | 225082 | False | not packaged | None | Not used by a V3.2 output, redundant working report/plot, or generated cache. |
| nn-vr | analysis/experiment_ab/cpu_gpu_complexity_correlations.csv | 575 | False | not packaged | None | Not used by a V3.2 output, redundant working report/plot, or generated cache. |
| nn-vr | analysis/experiment_ab/cpu_gpu_extremes.csv | 8261 | False | not packaged | None | Not used by a V3.2 output, redundant working report/plot, or generated cache. |
| nn-vr | analysis/experiment_ab/export_contract_audit.csv | 543 | True | yes after path audit | campaign_audit/export_contract_audit.csv | Selected paper claim evidence or source provenance. |
| nn-vr | analysis/experiment_ab/failure_category_summary.csv | 1038 | True | yes after path audit | failures/failure_category_summary.csv | Selected paper claim evidence or source provenance. |
| nn-vr | analysis/experiment_ab/failure_message_summary.csv | 1917 | True | yes after path audit | failures/failure_message_summary.csv | Selected paper claim evidence or source provenance. |
| nn-vr | analysis/experiment_ab/nn_dataset_comparison/NN_DATASET_COMPARISON_REPORT.md | 4015 | False | not packaged | None | Not used by a V3.2 output, redundant working report/plot, or generated cache. |
| nn-vr | analysis/experiment_ab/nn_dataset_comparison/SOURCE_SELECTION.md | 3526 | True | yes after path audit | pt_context/SOURCE_SELECTION.md | Selected paper claim evidence or source provenance. |
| nn-vr | analysis/experiment_ab/nn_dataset_comparison/__pycache__/compare_nn_dataset.cpython-310.pyc | 27146 | False | not packaged | None | Not used by a V3.2 output, redundant working report/plot, or generated cache. |
| nn-vr | analysis/experiment_ab/nn_dataset_comparison/compare_nn_dataset.py | 29475 | True | yes after path audit | provenance/analysis_source/compare_nn_dataset.py.txt | Selected paper claim evidence or source provenance. |
| nn-vr | analysis/experiment_ab/nn_dataset_comparison/comparison_summary.json | 14518 | True | yes after path audit | pt_context/comparison_summary.json | Selected paper claim evidence or source provenance. |
| nn-vr | analysis/experiment_ab/nn_dataset_comparison/matched_pt_a_b.csv | 446439 | True | yes after path audit | pt_context/matched_pt_a_b.csv | Selected paper claim evidence or source provenance. |
| nn-vr | analysis/experiment_ab/nn_dataset_comparison/model_overlap.csv | 808416 | True | yes after path audit | pt_context/model_overlap.csv | Selected paper claim evidence or source provenance. |
| nn-vr | analysis/experiment_ab/nn_dataset_comparison/pt_unity_scatter.pdf | 89568 | False | not packaged | None | Not used by a V3.2 output, redundant working report/plot, or generated cache. |
| nn-vr | analysis/experiment_ab/nn_dataset_comparison/pt_unity_scatter.png | 470586 | False | not packaged | None | Not used by a V3.2 output, redundant working report/plot, or generated cache. |
| nn-vr | analysis/experiment_ab/paired_latency_comparison.csv | 197998 | True | yes after path audit | timing/paired_latency_comparison.csv | Selected paper claim evidence or source provenance. |
| nn-vr | analysis/experiment_ab/per_model_comparison.csv | 401838 | True | yes after path audit | analysis/inputs/per_model_comparison.csv | Selected paper claim evidence or source provenance. |
| nn-vr | analysis/experiment_ab/per_model_reproducibility.csv | 273147 | True | yes after path audit | reproducibility/per_model_reproducibility.csv | Selected paper claim evidence or source provenance. |
| nn-vr | analysis/experiment_ab/post_export_runtime_transition.csv | 64673 | True | yes after path audit | compatibility/post_export_runtime_transition.csv | Selected paper claim evidence or source provenance. |
| nn-vr | analysis/experiment_ab/reproducibility_summary.csv | 1533 | True | yes after path audit | reproducibility/reproducibility_summary.csv | Selected paper claim evidence or source provenance. |
| nn-vr | analysis/experiment_ab/runtime_latency_summary.csv | 1106 | True | yes after path audit | timing/runtime_latency_summary.csv | Selected paper claim evidence or source provenance. |
| nn-vr | analysis/experiment_ab/statistical_tests.json | 1074 | True | yes after path audit | analysis/inputs/statistical_tests.json | Selected paper claim evidence or source provenance. |
| nn-vr | analysis/experiment_ab/summary.json | 48681 | True | yes after path audit | analysis/inputs/summary.json | Selected paper claim evidence or source provenance. |
| nn-vr | analysis/experiment_ab/timing_reproducibility_outliers.csv | 18058 | True | yes after path audit | reproducibility/timing_reproducibility_outliers.csv | Selected paper claim evidence or source provenance. |
| nn-vr | analysis/experiment_ab/transition_failure_evidence.csv | 229291 | True | yes after path audit | failures/transition_failure_evidence.csv | Selected paper claim evidence or source provenance. |
| nn-vr | ARTICLE_V3_CLAIM_MATRIX.md | 7712 | True | yes; license/ownership notes apply | provenance/manuscript/CLAIM_MATRIX.md | Scientific provenance, official license notice, or audited producer source. |
| nn-vr | arxiv_article_v3_2/audit/ARTICLE_V3_2_CONSISTENCY_REPORT.md | 2333 | True | yes; license/ownership notes apply | provenance/manuscript/V3_2_CONSISTENCY_REPORT.md | Scientific provenance, official license notice, or audited producer source. |
| nn-vr | arxiv_article_v3_2/figures/figures.tex | 10202 | True | yes; license/ownership notes apply | provenance/manuscript/figures.tex | Scientific provenance, official license notice, or audited producer source. |
| nn-vr | arxiv_article_v3_2/sections/results.tex | 10781 | True | yes; license/ownership notes apply | provenance/manuscript/results.tex | Scientific provenance, official license notice, or audited producer source. |
| nn-vr | arxiv_article_v3_2/sections/appendix.tex | 5488 | True | yes; license/ownership notes apply | provenance/manuscript/appendix.tex | Scientific provenance, official license notice, or audited producer source. |
| nn-vr | arxiv_article_v3_2/sections/experimental_setup.tex | 6425 | True | yes; license/ownership notes apply | provenance/manuscript/experimental_setup.tex | Scientific provenance, official license notice, or audited producer source. |
| nn-vr | arxiv_article_v3_2/sections/study_design.tex | 10713 | True | yes; license/ownership notes apply | provenance/manuscript/study_design.tex | Scientific provenance, official license notice, or audited producer source. |
| nn-vr | LICENSE | 1111 | True | yes; license/ownership notes apply | provenance/licenses/nn-vr-LICENSE | Scientific provenance, official license notice, or audited producer source. |
| nn-dataset | nn-dataset/LICENSE | 1106 | True | yes; license/ownership notes apply | provenance/licenses/nn-dataset-LICENSE | Scientific provenance, official license notice, or audited producer source. |
| nn-dataset | nn-dataset/ab/nn/util/Inference.py | 12842 | True | yes; license/ownership notes apply | provenance/analysis_source/Inference.py.txt | Scientific provenance, official license notice, or audited producer source. |
| nn-vr | NNVRBenchmark/Assets/Editor/BenchmarkCLI.cs | 8887 | True | yes; license/ownership notes apply | provenance/runtime_source/Experiment_B_BenchmarkCLI.cs.txt | Scientific provenance, official license notice, or audited producer source. |
| nn-vr | ab/vr/onnx_exporter.py | 5348 | True | yes; license/ownership notes apply | provenance/runtime_source/onnx_exporter.py.txt | Scientific provenance, official license notice, or audited producer source. |
| nn-vr | aggregated_unity_stats.csv | 961735 | True | selected columns only | provenance/historical_status.csv | Only identity/status columns retained; historical timings and free-text errors excluded. |
| nn-vr / nn-dataset | out/, nn-dataset/ab/nn/stat/, sibling B out/ | many records; not copied | underlying provenance only | raw host/path/log fields require separate review | None | Derived per-model tables suffice for summary reproduction; complete raw archives out of scope. |
| nn-vr / nn-dataset | models/, _work/, Library/, .venv/, .git/, caches, weights, ONNX and Unity builds | not packaged | False | no public redistribution in this candidate | None | Not required; third-party content, credentials/config risk, build products, or caches. |
| nn-vr | arxiv_article_v3_2/build/, finalized manuscript PDF and ZIP; practicum bundles | 1150684 | False | not packaged | None | Frozen manuscript is an authority checked by hashes; only necessary source evidence is copied. |
| nn-vr | arxiv_article_v3_1/figures/generate_paired_latency_figure.py | 1813 | True | Author-owned plotting source; license approval noted | provenance/analysis_source/generate_paired_latency_figure.py.txt | Original Figure 5 renderer inspected before adaptation; provenance only. |
