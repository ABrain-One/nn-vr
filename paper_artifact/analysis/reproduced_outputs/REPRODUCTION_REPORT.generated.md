# Generated reproduction report

This file is intentionally regenerated. The top-level REPRODUCTION_REPORT.md remains the frozen reference report. Generated output bytes are not the cross-version scientific acceptance criterion.

Command: `python analysis/scripts/reproduce_paper_results.py` then `python analysis/scripts/verify_canonical_results.py`.

Environment: Python 3.10.12; NumPy 2.2.6; SciPy 1.15.3.

Checks: 347; PASS: 347; FAIL: 0; supporting-source integrity failures: 0.

All values are recomputed from packaged retained inputs. Summary aggregation checks do not establish raw sample completeness or numerical parity of Unity outputs. Source-semantic checks are static checks only. No canonical file is rewritten.

| ID | Field | Expected | Reproduced | Status | Supporting inputs |
|---|---|---|---|---|---|
| C001 | p1.n | 1762 | 1762 | PASS | compatibility/compatibility_transition.csv; analysis/inputs/per_model_comparison.csv |
| C002 | p1.a_success | 1067 | 1067 | PASS | compatibility/compatibility_transition.csv; analysis/inputs/per_model_comparison.csv |
| C003 | p1.b_success | 1177 | 1177 | PASS | compatibility/compatibility_transition.csv; analysis/inputs/per_model_comparison.csv |
| C004 | p1.pp | 1061 | 1061 | PASS | compatibility/compatibility_transition.csv; analysis/inputs/per_model_comparison.csv |
| C005 | p1.fp | 116 | 116 | PASS | compatibility/compatibility_transition.csv; analysis/inputs/per_model_comparison.csv |
| C006 | p1.pf | 6 | 6 | PASS | compatibility/compatibility_transition.csv; analysis/inputs/per_model_comparison.csv |
| C007 | p1.ff | 579 | 579 | PASS | compatibility/compatibility_transition.csv; analysis/inputs/per_model_comparison.csv |
| C008 | p1.a_rate_percent | 60.56 | 60.55618615209988 | PASS | compatibility/compatibility_transition.csv; analysis/inputs/per_model_comparison.csv |
| C009 | p1.b_rate_percent | 66.8 | 66.79909194097617 | PASS | compatibility/compatibility_transition.csv; analysis/inputs/per_model_comparison.csv |
| C010 | p1.net_gain | 110 | 110 | PASS | compatibility/compatibility_transition.csv; analysis/inputs/per_model_comparison.csv |
| C011 | p1.change_pp | 6.24 | 6.242905788876277 | PASS | compatibility/compatibility_transition.csv; analysis/inputs/per_model_comparison.csv |
| C012 | p1.mcnemar_p | 1.6e-27 | 1.6018659814207945e-27 | PASS | compatibility/compatibility_transition.csv; analysis/inputs/per_model_comparison.csv |
| C013 | p2.n | 1186 | 1186 | PASS | compatibility/post_export_runtime_transition.csv; analysis/inputs/per_model_comparison.csv |
| C014 | p2.a_success | 1064 | 1064 | PASS | compatibility/post_export_runtime_transition.csv; analysis/inputs/per_model_comparison.csv |
| C015 | p2.b_success | 1177 | 1177 | PASS | compatibility/post_export_runtime_transition.csv; analysis/inputs/per_model_comparison.csv |
| C016 | p2.pp | 1061 | 1061 | PASS | compatibility/post_export_runtime_transition.csv; analysis/inputs/per_model_comparison.csv |
| C017 | p2.fp | 116 | 116 | PASS | compatibility/post_export_runtime_transition.csv; analysis/inputs/per_model_comparison.csv |
| C018 | p2.pf | 3 | 3 | PASS | compatibility/post_export_runtime_transition.csv; analysis/inputs/per_model_comparison.csv |
| C019 | p2.ff | 6 | 6 | PASS | compatibility/post_export_runtime_transition.csv; analysis/inputs/per_model_comparison.csv |
| C020 | p2.a_rate_percent | 89.71 | 89.7133220910624 | PASS | compatibility/post_export_runtime_transition.csv; analysis/inputs/per_model_comparison.csv |
| C021 | p2.b_rate_percent | 99.24 | 99.24114671163575 | PASS | compatibility/post_export_runtime_transition.csv; analysis/inputs/per_model_comparison.csv |
| C022 | p2.net_gain | 113 | 113 | PASS | compatibility/post_export_runtime_transition.csv; analysis/inputs/per_model_comparison.csv |
| C023 | p2.change_pp | 9.53 | 9.527824620573355 | PASS | compatibility/post_export_runtime_transition.csv; analysis/inputs/per_model_comparison.csv |
| C024 | p2.mcnemar_p | 8.45e-31 | 8.454832455859965e-31 | PASS | compatibility/post_export_runtime_transition.csv; analysis/inputs/per_model_comparison.csv |
| C025 | eligibility.a | 1191 | 1191 | PASS | analysis/inputs/per_model_comparison.csv |
| C026 | eligibility.b | 1186 | 1186 | PASS | analysis/inputs/per_model_comparison.csv |
| C027 | eligibility.common | 1186 | 1186 | PASS | analysis/inputs/per_model_comparison.csv |
| C028 | eligibility.a_only | 5 | 5 | PASS | analysis/inputs/per_model_comparison.csv |
| C029 | eligibility.b_only | 0 | 0 | PASS | analysis/inputs/per_model_comparison.csv |
| C030 | compatibility.a.union | 1074 | 1074 | PASS | analysis/inputs/per_model_comparison.csv |
| C031 | compatibility.b.union | 1181 | 1181 | PASS | analysis/inputs/per_model_comparison.csv |
| C032 | timing.n | 1061 | 1061 | PASS | timing/paired_latency_comparison.csv; analysis/inputs/per_model_comparison.csv |
| C033 | timing.cpu.a_median_ms | 5.4707 | 5.470723191897075 | PASS | timing/paired_latency_comparison.csv; analysis/inputs/per_model_comparison.csv |
| C034 | timing.cpu.b_median_ms | 0.478 | 0.4780383333333334 | PASS | timing/paired_latency_comparison.csv; analysis/inputs/per_model_comparison.csv |
| C035 | timing.cpu.difference_ms | -4.8325 | -4.832524188550313 | PASS | timing/paired_latency_comparison.csv; analysis/inputs/per_model_comparison.csv |
| C036 | timing.cpu.ratio | 0.078 | 0.07823162800035334 | PASS | timing/paired_latency_comparison.csv; analysis/inputs/per_model_comparison.csv |
| C037 | timing.cpu.b_faster | 1061 | 1061 | PASS | timing/paired_latency_comparison.csv; analysis/inputs/per_model_comparison.csv |
| C038 | timing.cpu.b_faster_percent | 100.0 | 100.0 | PASS | timing/paired_latency_comparison.csv; analysis/inputs/per_model_comparison.csv |
| C039 | timing.cpu.wilcoxon_p | 3.75e-175 | 3.754886588745924e-175 | PASS | timing/paired_latency_comparison.csv; analysis/inputs/per_model_comparison.csv |
| C040 | timing.cpu.rank_biserial | -1.0 | -1.0 | PASS | timing/paired_latency_comparison.csv; analysis/inputs/per_model_comparison.csv |
| C041 | timing.gpu.a_median_ms | 2.9733 | 2.9732850790023804 | PASS | timing/paired_latency_comparison.csv; analysis/inputs/per_model_comparison.csv |
| C042 | timing.gpu.b_median_ms | 2.8315 | 2.8315083333333333 | PASS | timing/paired_latency_comparison.csv; analysis/inputs/per_model_comparison.csv |
| C043 | timing.gpu.difference_ms | -0.0944 | -0.09440464787801117 | PASS | timing/paired_latency_comparison.csv; analysis/inputs/per_model_comparison.csv |
| C044 | timing.gpu.ratio | 0.982 | 0.9823430670797145 | PASS | timing/paired_latency_comparison.csv; analysis/inputs/per_model_comparison.csv |
| C045 | timing.gpu.b_faster | 604 | 604 | PASS | timing/paired_latency_comparison.csv; analysis/inputs/per_model_comparison.csv |
| C046 | timing.gpu.b_faster_percent | 56.92742695570217 | 56.92742695570217 | PASS | timing/paired_latency_comparison.csv; analysis/inputs/per_model_comparison.csv |
| C047 | timing.gpu.wilcoxon_p | 4.49e-06 | 4.486913347549354e-06 | PASS | timing/paired_latency_comparison.csv; analysis/inputs/per_model_comparison.csv |
| C048 | timing.gpu.rank_biserial | -0.163 | -0.16258513181786716 | PASS | timing/paired_latency_comparison.csv; analysis/inputs/per_model_comparison.csv |
| C049 | architecture.has_attention.n | 2 | 2 | PASS | analysis/inputs/per_model_comparison.csv; architecture/architecture_comparison.csv |
| C050 | architecture.has_attention.a_success | 2 | 2 | PASS | analysis/inputs/per_model_comparison.csv; architecture/architecture_comparison.csv |
| C051 | architecture.has_attention.b_success | 2 | 2 | PASS | analysis/inputs/per_model_comparison.csv; architecture/architecture_comparison.csv |
| C052 | architecture.has_attention.a_percent | 100.0 | 100.0 | PASS | analysis/inputs/per_model_comparison.csv; architecture/architecture_comparison.csv |
| C053 | architecture.has_attention.b_percent | 100.0 | 100.0 | PASS | analysis/inputs/per_model_comparison.csv; architecture/architecture_comparison.csv |
| C054 | architecture.has_attention.a_wilson_low_percent | 34.2380227506653 | 34.2380227506653 | PASS | analysis/inputs/per_model_comparison.csv; architecture/architecture_comparison.csv |
| C055 | architecture.has_attention.a_wilson_high_percent | 100.0 | 100.0 | PASS | analysis/inputs/per_model_comparison.csv; architecture/architecture_comparison.csv |
| C056 | architecture.has_attention.b_wilson_low_percent | 34.2380227506653 | 34.2380227506653 | PASS | analysis/inputs/per_model_comparison.csv; architecture/architecture_comparison.csv |
| C057 | architecture.has_attention.b_wilson_high_percent | 100.0 | 100.0 | PASS | analysis/inputs/per_model_comparison.csv; architecture/architecture_comparison.csv |
| C058 | architecture.has_attention.change_pp | 0.0 | 0.0 | PASS | analysis/inputs/per_model_comparison.csv; architecture/architecture_comparison.csv |
| C059 | architecture.has_attention.recoveries | 0 | 0 | PASS | analysis/inputs/per_model_comparison.csv; architecture/architecture_comparison.csv |
| C060 | architecture.has_attention.regressions | 0 | 0 | PASS | analysis/inputs/per_model_comparison.csv; architecture/architecture_comparison.csv |
| C061 | architecture.is_transformer_like.n | 122 | 122 | PASS | analysis/inputs/per_model_comparison.csv; architecture/architecture_comparison.csv |
| C062 | architecture.is_transformer_like.a_success | 73 | 73 | PASS | analysis/inputs/per_model_comparison.csv; architecture/architecture_comparison.csv |
| C063 | architecture.is_transformer_like.b_success | 119 | 119 | PASS | analysis/inputs/per_model_comparison.csv; architecture/architecture_comparison.csv |
| C064 | architecture.is_transformer_like.a_percent | 59.83606557377049 | 59.83606557377049 | PASS | analysis/inputs/per_model_comparison.csv; architecture/architecture_comparison.csv |
| C065 | architecture.is_transformer_like.b_percent | 97.54098360655738 | 97.54098360655738 | PASS | analysis/inputs/per_model_comparison.csv; architecture/architecture_comparison.csv |
| C066 | architecture.is_transformer_like.a_wilson_low_percent | 50.965379378579456 | 50.965379378579456 | PASS | analysis/inputs/per_model_comparison.csv; architecture/architecture_comparison.csv |
| C067 | architecture.is_transformer_like.a_wilson_high_percent | 68.10623678425965 | 68.10623678425965 | PASS | analysis/inputs/per_model_comparison.csv; architecture/architecture_comparison.csv |
| C068 | architecture.is_transformer_like.b_wilson_low_percent | 93.019240156411 | 93.019240156411 | PASS | analysis/inputs/per_model_comparison.csv; architecture/architecture_comparison.csv |
| C069 | architecture.is_transformer_like.b_wilson_high_percent | 99.16023796397793 | 99.16023796397793 | PASS | analysis/inputs/per_model_comparison.csv; architecture/architecture_comparison.csv |
| C070 | architecture.is_transformer_like.change_pp | 37.704918032786885 | 37.704918032786885 | PASS | analysis/inputs/per_model_comparison.csv; architecture/architecture_comparison.csv |
| C071 | architecture.is_transformer_like.recoveries | 47 | 47 | PASS | analysis/inputs/per_model_comparison.csv; architecture/architecture_comparison.csv |
| C072 | architecture.is_transformer_like.regressions | 1 | 1 | PASS | analysis/inputs/per_model_comparison.csv; architecture/architecture_comparison.csv |
| C073 | architecture.has_residual_connections.n | 103 | 103 | PASS | analysis/inputs/per_model_comparison.csv; architecture/architecture_comparison.csv |
| C074 | architecture.has_residual_connections.a_success | 72 | 72 | PASS | analysis/inputs/per_model_comparison.csv; architecture/architecture_comparison.csv |
| C075 | architecture.has_residual_connections.b_success | 102 | 102 | PASS | analysis/inputs/per_model_comparison.csv; architecture/architecture_comparison.csv |
| C076 | architecture.has_residual_connections.a_percent | 69.90291262135922 | 69.90291262135922 | PASS | analysis/inputs/per_model_comparison.csv; architecture/architecture_comparison.csv |
| C077 | architecture.has_residual_connections.b_percent | 99.02912621359224 | 99.02912621359224 | PASS | analysis/inputs/per_model_comparison.csv; architecture/architecture_comparison.csv |
| C078 | architecture.has_residual_connections.a_wilson_low_percent | 60.46054631486112 | 60.46054631486112 | PASS | analysis/inputs/per_model_comparison.csv; architecture/architecture_comparison.csv |
| C079 | architecture.has_residual_connections.a_wilson_high_percent | 77.91407010516357 | 77.91407010516357 | PASS | analysis/inputs/per_model_comparison.csv; architecture/architecture_comparison.csv |
| C080 | architecture.has_residual_connections.b_wilson_low_percent | 94.70418081674632 | 94.70418081674632 | PASS | analysis/inputs/per_model_comparison.csv; architecture/architecture_comparison.csv |
| C081 | architecture.has_residual_connections.b_wilson_high_percent | 99.82841085209499 | 99.82841085209499 | PASS | analysis/inputs/per_model_comparison.csv; architecture/architecture_comparison.csv |
| C082 | architecture.has_residual_connections.change_pp | 29.12621359223301 | 29.12621359223301 | PASS | analysis/inputs/per_model_comparison.csv; architecture/architecture_comparison.csv |
| C083 | architecture.has_residual_connections.recoveries | 30 | 30 | PASS | analysis/inputs/per_model_comparison.csv; architecture/architecture_comparison.csv |
| C084 | architecture.has_residual_connections.regressions | 0 | 0 | PASS | analysis/inputs/per_model_comparison.csv; architecture/architecture_comparison.csv |
| C085 | architecture.is_resnet_like.n | 409 | 409 | PASS | analysis/inputs/per_model_comparison.csv; architecture/architecture_comparison.csv |
| C086 | architecture.is_resnet_like.a_success | 383 | 383 | PASS | analysis/inputs/per_model_comparison.csv; architecture/architecture_comparison.csv |
| C087 | architecture.is_resnet_like.b_success | 408 | 408 | PASS | analysis/inputs/per_model_comparison.csv; architecture/architecture_comparison.csv |
| C088 | architecture.is_resnet_like.a_percent | 93.64303178484109 | 93.64303178484107 | PASS | analysis/inputs/per_model_comparison.csv; architecture/architecture_comparison.csv |
| C089 | architecture.is_resnet_like.b_percent | 99.75550122249389 | 99.75550122249389 | PASS | analysis/inputs/per_model_comparison.csv; architecture/architecture_comparison.csv |
| C090 | architecture.is_resnet_like.a_wilson_low_percent | 90.84863122608097 | 90.84863122608097 | PASS | analysis/inputs/per_model_comparison.csv; architecture/architecture_comparison.csv |
| C091 | architecture.is_resnet_like.a_wilson_high_percent | 95.62524206653636 | 95.62524206653636 | PASS | analysis/inputs/per_model_comparison.csv; architecture/architecture_comparison.csv |
| C092 | architecture.is_resnet_like.b_wilson_low_percent | 98.62823311223912 | 98.62823311223912 | PASS | analysis/inputs/per_model_comparison.csv; architecture/architecture_comparison.csv |
| C093 | architecture.is_resnet_like.b_wilson_high_percent | 99.9568269160389 | 99.9568269160389 | PASS | analysis/inputs/per_model_comparison.csv; architecture/architecture_comparison.csv |
| C094 | architecture.is_resnet_like.change_pp | 6.112469437652812 | 6.112469437652812 | PASS | analysis/inputs/per_model_comparison.csv; architecture/architecture_comparison.csv |
| C095 | architecture.is_resnet_like.recoveries | 25 | 25 | PASS | analysis/inputs/per_model_comparison.csv; architecture/architecture_comparison.csv |
| C096 | architecture.is_resnet_like.regressions | 0 | 0 | PASS | analysis/inputs/per_model_comparison.csv; architecture/architecture_comparison.csv |
| C097 | architecture.is_vgg_like.n | 16 | 16 | PASS | analysis/inputs/per_model_comparison.csv; architecture/architecture_comparison.csv |
| C098 | architecture.is_vgg_like.a_success | 10 | 10 | PASS | analysis/inputs/per_model_comparison.csv; architecture/architecture_comparison.csv |
| C099 | architecture.is_vgg_like.b_success | 16 | 16 | PASS | analysis/inputs/per_model_comparison.csv; architecture/architecture_comparison.csv |
| C100 | architecture.is_vgg_like.a_percent | 62.5 | 62.5 | PASS | analysis/inputs/per_model_comparison.csv; architecture/architecture_comparison.csv |
| C101 | architecture.is_vgg_like.b_percent | 100.0 | 100.0 | PASS | analysis/inputs/per_model_comparison.csv; architecture/architecture_comparison.csv |
| C102 | architecture.is_vgg_like.a_wilson_low_percent | 38.64104054550271 | 38.64104054550271 | PASS | analysis/inputs/per_model_comparison.csv; architecture/architecture_comparison.csv |
| C103 | architecture.is_vgg_like.a_wilson_high_percent | 81.51876744113636 | 81.51876744113636 | PASS | analysis/inputs/per_model_comparison.csv; architecture/architecture_comparison.csv |
| C104 | architecture.is_vgg_like.b_wilson_low_percent | 80.63923194655636 | 80.63923194655636 | PASS | analysis/inputs/per_model_comparison.csv; architecture/architecture_comparison.csv |
| C105 | architecture.is_vgg_like.b_wilson_high_percent | 100.00000000000003 | 100.00000000000003 | PASS | analysis/inputs/per_model_comparison.csv; architecture/architecture_comparison.csv |
| C106 | architecture.is_vgg_like.change_pp | 37.5 | 37.5 | PASS | analysis/inputs/per_model_comparison.csv; architecture/architecture_comparison.csv |
| C107 | architecture.is_vgg_like.recoveries | 6 | 6 | PASS | analysis/inputs/per_model_comparison.csv; architecture/architecture_comparison.csv |
| C108 | architecture.is_vgg_like.regressions | 0 | 0 | PASS | analysis/inputs/per_model_comparison.csv; architecture/architecture_comparison.csv |
| C109 | architecture.is_mobilenet_like.n | 73 | 73 | PASS | analysis/inputs/per_model_comparison.csv; architecture/architecture_comparison.csv |
| C110 | architecture.is_mobilenet_like.a_success | 59 | 59 | PASS | analysis/inputs/per_model_comparison.csv; architecture/architecture_comparison.csv |
| C111 | architecture.is_mobilenet_like.b_success | 73 | 73 | PASS | analysis/inputs/per_model_comparison.csv; architecture/architecture_comparison.csv |
| C112 | architecture.is_mobilenet_like.a_percent | 80.82191780821918 | 80.82191780821918 | PASS | analysis/inputs/per_model_comparison.csv; architecture/architecture_comparison.csv |
| C113 | architecture.is_mobilenet_like.b_percent | 100.0 | 100.0 | PASS | analysis/inputs/per_model_comparison.csv; architecture/architecture_comparison.csv |
| C114 | architecture.is_mobilenet_like.a_wilson_low_percent | 70.34449738686679 | 70.34449738686679 | PASS | analysis/inputs/per_model_comparison.csv; architecture/architecture_comparison.csv |
| C115 | architecture.is_mobilenet_like.a_wilson_high_percent | 88.2176391090128 | 88.2176391090128 | PASS | analysis/inputs/per_model_comparison.csv; architecture/architecture_comparison.csv |
| C116 | architecture.is_mobilenet_like.b_wilson_low_percent | 95.00079920442688 | 95.00079920442688 | PASS | analysis/inputs/per_model_comparison.csv; architecture/architecture_comparison.csv |
| C117 | architecture.is_mobilenet_like.b_wilson_high_percent | 99.99999999999997 | 99.99999999999997 | PASS | analysis/inputs/per_model_comparison.csv; architecture/architecture_comparison.csv |
| C118 | architecture.is_mobilenet_like.change_pp | 19.17808219178082 | 19.17808219178082 | PASS | analysis/inputs/per_model_comparison.csv; architecture/architecture_comparison.csv |
| C119 | architecture.is_mobilenet_like.recoveries | 14 | 14 | PASS | analysis/inputs/per_model_comparison.csv; architecture/architecture_comparison.csv |
| C120 | architecture.is_mobilenet_like.regressions | 0 | 0 | PASS | analysis/inputs/per_model_comparison.csv; architecture/architecture_comparison.csv |
| C121 | repro.A.cpu.n | 1071 | 1071 | PASS | reproducibility/per_model_reproducibility.csv; analysis/inputs/per_model_comparison.csv; reproducibility/reproducibility_summary.csv |
| C122 | repro.A.cpu.median_percent | 12.58 | 12.578321433007325 | PASS | reproducibility/per_model_reproducibility.csv; analysis/inputs/per_model_comparison.csv; reproducibility/reproducibility_summary.csv |
| C123 | repro.A.cpu.p95_percent | 88.08 | 88.07889864616119 | PASS | reproducibility/per_model_reproducibility.csv; analysis/inputs/per_model_comparison.csv; reproducibility/reproducibility_summary.csv |
| C124 | repro.A.gpu.n | 1071 | 1071 | PASS | reproducibility/per_model_reproducibility.csv; analysis/inputs/per_model_comparison.csv; reproducibility/reproducibility_summary.csv |
| C125 | repro.A.gpu.median_percent | 9.79 | 9.793728668002432 | PASS | reproducibility/per_model_reproducibility.csv; analysis/inputs/per_model_comparison.csv; reproducibility/reproducibility_summary.csv |
| C126 | repro.A.gpu.p95_percent | 77.51 | 77.50666947928053 | PASS | reproducibility/per_model_reproducibility.csv; analysis/inputs/per_model_comparison.csv; reproducibility/reproducibility_summary.csv |
| C127 | repro.A.success_runs.0 | 688 | 688 | PASS | reproducibility/per_model_reproducibility.csv; analysis/inputs/per_model_comparison.csv; reproducibility/reproducibility_summary.csv |
| C128 | repro.A.success_runs.1 | 3 | 3 | PASS | reproducibility/per_model_reproducibility.csv; analysis/inputs/per_model_comparison.csv; reproducibility/reproducibility_summary.csv |
| C129 | repro.A.success_runs.2 | 1 | 1 | PASS | reproducibility/per_model_reproducibility.csv; analysis/inputs/per_model_comparison.csv; reproducibility/reproducibility_summary.csv |
| C130 | repro.A.success_runs.3 | 2 | 2 | PASS | reproducibility/per_model_reproducibility.csv; analysis/inputs/per_model_comparison.csv; reproducibility/reproducibility_summary.csv |
| C131 | repro.A.success_runs.4 | 0 | 0 | PASS | reproducibility/per_model_reproducibility.csv; analysis/inputs/per_model_comparison.csv; reproducibility/reproducibility_summary.csv |
| C132 | repro.A.success_runs.5 | 1 | 1 | PASS | reproducibility/per_model_reproducibility.csv; analysis/inputs/per_model_comparison.csv; reproducibility/reproducibility_summary.csv |
| C133 | repro.A.success_runs.6 | 1067 | 1067 | PASS | reproducibility/per_model_reproducibility.csv; analysis/inputs/per_model_comparison.csv; reproducibility/reproducibility_summary.csv |
| C134 | repro.B.cpu.n | 1181 | 1181 | PASS | reproducibility/per_model_reproducibility.csv; analysis/inputs/per_model_comparison.csv; reproducibility/reproducibility_summary.csv |
| C135 | repro.B.cpu.median_percent | 2.48 | 2.484854282076675 | PASS | reproducibility/per_model_reproducibility.csv; analysis/inputs/per_model_comparison.csv; reproducibility/reproducibility_summary.csv |
| C136 | repro.B.cpu.p95_percent | 29.56 | 29.560235170283043 | PASS | reproducibility/per_model_reproducibility.csv; analysis/inputs/per_model_comparison.csv; reproducibility/reproducibility_summary.csv |
| C137 | repro.B.gpu.n | 1181 | 1181 | PASS | reproducibility/per_model_reproducibility.csv; analysis/inputs/per_model_comparison.csv; reproducibility/reproducibility_summary.csv |
| C138 | repro.B.gpu.median_percent | 4.4 | 4.404944378492772 | PASS | reproducibility/per_model_reproducibility.csv; analysis/inputs/per_model_comparison.csv; reproducibility/reproducibility_summary.csv |
| C139 | repro.B.gpu.p95_percent | 54.14 | 54.144824899202824 | PASS | reproducibility/per_model_reproducibility.csv; analysis/inputs/per_model_comparison.csv; reproducibility/reproducibility_summary.csv |
| C140 | repro.B.success_runs.0 | 581 | 581 | PASS | reproducibility/per_model_reproducibility.csv; analysis/inputs/per_model_comparison.csv; reproducibility/reproducibility_summary.csv |
| C141 | repro.B.success_runs.1 | 0 | 0 | PASS | reproducibility/per_model_reproducibility.csv; analysis/inputs/per_model_comparison.csv; reproducibility/reproducibility_summary.csv |
| C142 | repro.B.success_runs.2 | 0 | 0 | PASS | reproducibility/per_model_reproducibility.csv; analysis/inputs/per_model_comparison.csv; reproducibility/reproducibility_summary.csv |
| C143 | repro.B.success_runs.3 | 0 | 0 | PASS | reproducibility/per_model_reproducibility.csv; analysis/inputs/per_model_comparison.csv; reproducibility/reproducibility_summary.csv |
| C144 | repro.B.success_runs.4 | 0 | 0 | PASS | reproducibility/per_model_reproducibility.csv; analysis/inputs/per_model_comparison.csv; reproducibility/reproducibility_summary.csv |
| C145 | repro.B.success_runs.5 | 4 | 4 | PASS | reproducibility/per_model_reproducibility.csv; analysis/inputs/per_model_comparison.csv; reproducibility/reproducibility_summary.csv |
| C146 | repro.B.success_runs.6 | 1177 | 1177 | PASS | reproducibility/per_model_reproducibility.csv; analysis/inputs/per_model_comparison.csv; reproducibility/reproducibility_summary.csv |
| C147 | campaign.A1.records | 1762 | 1762 | PASS | campaign_audit/campaign_audit.csv |
| C148 | campaign.A1.valid_completed_benchmarks | 1074 | 1074 | PASS | campaign_audit/campaign_audit.csv |
| C149 | campaign.A1.export_success | 1195 | 1195 | PASS | campaign_audit/campaign_audit.csv |
| C150 | campaign.A1.export_failure | 567 | 567 | PASS | campaign_audit/campaign_audit.csv |
| C151 | campaign.A1.validation_failure | 4 | 4 | PASS | campaign_audit/campaign_audit.csv |
| C152 | campaign.A1.failure_runtime_load_execution | 106 | 106 | PASS | campaign_audit/campaign_audit.csv |
| C153 | campaign.A1.failure_timeout | 11 | 11 | PASS | campaign_audit/campaign_audit.csv |
| C154 | campaign.A1.missing_results | 0 | 0 | PASS | campaign_audit/campaign_audit.csv |
| C155 | campaign.A1.unexpected_results | 0 | 0 | PASS | campaign_audit/campaign_audit.csv |
| C156 | campaign.A1.corrupt_or_incomplete_files | 0 | 0 | PASS | campaign_audit/campaign_audit.csv |
| C157 | campaign.A1.duplicate_results | 0 | 0 | PASS | campaign_audit/campaign_audit.csv |
| C158 | campaign.A1.cleanup_failure | 0 | 0 | PASS | campaign_audit/campaign_audit.csv |
| C159 | campaign.A1.accounting_reconciles | True | True | PASS | campaign_audit/campaign_audit.csv |
| C160 | campaign.A2.records | 1762 | 1762 | PASS | campaign_audit/campaign_audit.csv |
| C161 | campaign.A2.valid_completed_benchmarks | 1071 | 1071 | PASS | campaign_audit/campaign_audit.csv |
| C162 | campaign.A2.export_success | 1195 | 1195 | PASS | campaign_audit/campaign_audit.csv |
| C163 | campaign.A2.export_failure | 567 | 567 | PASS | campaign_audit/campaign_audit.csv |
| C164 | campaign.A2.validation_failure | 4 | 4 | PASS | campaign_audit/campaign_audit.csv |
| C165 | campaign.A2.failure_runtime_load_execution | 106 | 106 | PASS | campaign_audit/campaign_audit.csv |
| C166 | campaign.A2.failure_timeout | 14 | 14 | PASS | campaign_audit/campaign_audit.csv |
| C167 | campaign.A2.missing_results | 0 | 0 | PASS | campaign_audit/campaign_audit.csv |
| C168 | campaign.A2.unexpected_results | 0 | 0 | PASS | campaign_audit/campaign_audit.csv |
| C169 | campaign.A2.corrupt_or_incomplete_files | 0 | 0 | PASS | campaign_audit/campaign_audit.csv |
| C170 | campaign.A2.duplicate_results | 0 | 0 | PASS | campaign_audit/campaign_audit.csv |
| C171 | campaign.A2.cleanup_failure | 0 | 0 | PASS | campaign_audit/campaign_audit.csv |
| C172 | campaign.A2.accounting_reconciles | True | True | PASS | campaign_audit/campaign_audit.csv |
| C173 | campaign.A3.records | 1762 | 1762 | PASS | campaign_audit/campaign_audit.csv |
| C174 | campaign.A3.valid_completed_benchmarks | 1070 | 1070 | PASS | campaign_audit/campaign_audit.csv |
| C175 | campaign.A3.export_success | 1195 | 1195 | PASS | campaign_audit/campaign_audit.csv |
| C176 | campaign.A3.export_failure | 567 | 567 | PASS | campaign_audit/campaign_audit.csv |
| C177 | campaign.A3.validation_failure | 4 | 4 | PASS | campaign_audit/campaign_audit.csv |
| C178 | campaign.A3.failure_runtime_load_execution | 106 | 106 | PASS | campaign_audit/campaign_audit.csv |
| C179 | campaign.A3.failure_timeout | 15 | 15 | PASS | campaign_audit/campaign_audit.csv |
| C180 | campaign.A3.missing_results | 0 | 0 | PASS | campaign_audit/campaign_audit.csv |
| C181 | campaign.A3.unexpected_results | 0 | 0 | PASS | campaign_audit/campaign_audit.csv |
| C182 | campaign.A3.corrupt_or_incomplete_files | 0 | 0 | PASS | campaign_audit/campaign_audit.csv |
| C183 | campaign.A3.duplicate_results | 0 | 0 | PASS | campaign_audit/campaign_audit.csv |
| C184 | campaign.A3.cleanup_failure | 0 | 0 | PASS | campaign_audit/campaign_audit.csv |
| C185 | campaign.A3.accounting_reconciles | True | True | PASS | campaign_audit/campaign_audit.csv |
| C186 | campaign.A4.records | 1762 | 1762 | PASS | campaign_audit/campaign_audit.csv |
| C187 | campaign.A4.valid_completed_benchmarks | 1068 | 1068 | PASS | campaign_audit/campaign_audit.csv |
| C188 | campaign.A4.export_success | 1195 | 1195 | PASS | campaign_audit/campaign_audit.csv |
| C189 | campaign.A4.export_failure | 567 | 567 | PASS | campaign_audit/campaign_audit.csv |
| C190 | campaign.A4.validation_failure | 4 | 4 | PASS | campaign_audit/campaign_audit.csv |
| C191 | campaign.A4.failure_runtime_load_execution | 106 | 106 | PASS | campaign_audit/campaign_audit.csv |
| C192 | campaign.A4.failure_timeout | 17 | 17 | PASS | campaign_audit/campaign_audit.csv |
| C193 | campaign.A4.missing_results | 0 | 0 | PASS | campaign_audit/campaign_audit.csv |
| C194 | campaign.A4.unexpected_results | 0 | 0 | PASS | campaign_audit/campaign_audit.csv |
| C195 | campaign.A4.corrupt_or_incomplete_files | 0 | 0 | PASS | campaign_audit/campaign_audit.csv |
| C196 | campaign.A4.duplicate_results | 0 | 0 | PASS | campaign_audit/campaign_audit.csv |
| C197 | campaign.A4.cleanup_failure | 0 | 0 | PASS | campaign_audit/campaign_audit.csv |
| C198 | campaign.A4.accounting_reconciles | True | True | PASS | campaign_audit/campaign_audit.csv |
| C199 | campaign.A5.records | 1762 | 1762 | PASS | campaign_audit/campaign_audit.csv |
| C200 | campaign.A5.valid_completed_benchmarks | 1068 | 1068 | PASS | campaign_audit/campaign_audit.csv |
| C201 | campaign.A5.export_success | 1195 | 1195 | PASS | campaign_audit/campaign_audit.csv |
| C202 | campaign.A5.export_failure | 567 | 567 | PASS | campaign_audit/campaign_audit.csv |
| C203 | campaign.A5.validation_failure | 4 | 4 | PASS | campaign_audit/campaign_audit.csv |
| C204 | campaign.A5.failure_runtime_load_execution | 105 | 105 | PASS | campaign_audit/campaign_audit.csv |
| C205 | campaign.A5.failure_timeout | 18 | 18 | PASS | campaign_audit/campaign_audit.csv |
| C206 | campaign.A5.missing_results | 0 | 0 | PASS | campaign_audit/campaign_audit.csv |
| C207 | campaign.A5.unexpected_results | 0 | 0 | PASS | campaign_audit/campaign_audit.csv |
| C208 | campaign.A5.corrupt_or_incomplete_files | 0 | 0 | PASS | campaign_audit/campaign_audit.csv |
| C209 | campaign.A5.duplicate_results | 0 | 0 | PASS | campaign_audit/campaign_audit.csv |
| C210 | campaign.A5.cleanup_failure | 0 | 0 | PASS | campaign_audit/campaign_audit.csv |
| C211 | campaign.A5.accounting_reconciles | True | True | PASS | campaign_audit/campaign_audit.csv |
| C212 | campaign.A6.records | 1762 | 1762 | PASS | campaign_audit/campaign_audit.csv |
| C213 | campaign.A6.valid_completed_benchmarks | 1067 | 1067 | PASS | campaign_audit/campaign_audit.csv |
| C214 | campaign.A6.export_success | 1195 | 1195 | PASS | campaign_audit/campaign_audit.csv |
| C215 | campaign.A6.export_failure | 567 | 567 | PASS | campaign_audit/campaign_audit.csv |
| C216 | campaign.A6.validation_failure | 4 | 4 | PASS | campaign_audit/campaign_audit.csv |
| C217 | campaign.A6.failure_runtime_load_execution | 105 | 105 | PASS | campaign_audit/campaign_audit.csv |
| C218 | campaign.A6.failure_timeout | 19 | 19 | PASS | campaign_audit/campaign_audit.csv |
| C219 | campaign.A6.missing_results | 0 | 0 | PASS | campaign_audit/campaign_audit.csv |
| C220 | campaign.A6.unexpected_results | 0 | 0 | PASS | campaign_audit/campaign_audit.csv |
| C221 | campaign.A6.corrupt_or_incomplete_files | 0 | 0 | PASS | campaign_audit/campaign_audit.csv |
| C222 | campaign.A6.duplicate_results | 0 | 0 | PASS | campaign_audit/campaign_audit.csv |
| C223 | campaign.A6.cleanup_failure | 0 | 0 | PASS | campaign_audit/campaign_audit.csv |
| C224 | campaign.A6.accounting_reconciles | True | True | PASS | campaign_audit/campaign_audit.csv |
| C225 | campaign.B1.records | 1762 | 1762 | PASS | campaign_audit/campaign_audit.csv |
| C226 | campaign.B1.valid_completed_benchmarks | 1180 | 1180 | PASS | campaign_audit/campaign_audit.csv |
| C227 | campaign.B1.export_success | 1190 | 1190 | PASS | campaign_audit/campaign_audit.csv |
| C228 | campaign.B1.export_failure | 572 | 572 | PASS | campaign_audit/campaign_audit.csv |
| C229 | campaign.B1.validation_failure | 4 | 4 | PASS | campaign_audit/campaign_audit.csv |
| C230 | campaign.B1.failure_runtime_load_execution | 6 | 6 | PASS | campaign_audit/campaign_audit.csv |
| C231 | campaign.B1.failure_timeout | 0 | 0 | PASS | campaign_audit/campaign_audit.csv |
| C232 | campaign.B1.missing_results | 0 | 0 | PASS | campaign_audit/campaign_audit.csv |
| C233 | campaign.B1.unexpected_results | 0 | 0 | PASS | campaign_audit/campaign_audit.csv |
| C234 | campaign.B1.corrupt_or_incomplete_files | 0 | 0 | PASS | campaign_audit/campaign_audit.csv |
| C235 | campaign.B1.duplicate_results | 0 | 0 | PASS | campaign_audit/campaign_audit.csv |
| C236 | campaign.B1.cleanup_failure | 0 | 0 | PASS | campaign_audit/campaign_audit.csv |
| C237 | campaign.B1.accounting_reconciles | True | True | PASS | campaign_audit/campaign_audit.csv |
| C238 | campaign.B2.records | 1762 | 1762 | PASS | campaign_audit/campaign_audit.csv |
| C239 | campaign.B2.valid_completed_benchmarks | 1179 | 1179 | PASS | campaign_audit/campaign_audit.csv |
| C240 | campaign.B2.export_success | 1190 | 1190 | PASS | campaign_audit/campaign_audit.csv |
| C241 | campaign.B2.export_failure | 572 | 572 | PASS | campaign_audit/campaign_audit.csv |
| C242 | campaign.B2.validation_failure | 4 | 4 | PASS | campaign_audit/campaign_audit.csv |
| C243 | campaign.B2.failure_runtime_load_execution | 7 | 7 | PASS | campaign_audit/campaign_audit.csv |
| C244 | campaign.B2.failure_timeout | 0 | 0 | PASS | campaign_audit/campaign_audit.csv |
| C245 | campaign.B2.missing_results | 0 | 0 | PASS | campaign_audit/campaign_audit.csv |
| C246 | campaign.B2.unexpected_results | 0 | 0 | PASS | campaign_audit/campaign_audit.csv |
| C247 | campaign.B2.corrupt_or_incomplete_files | 0 | 0 | PASS | campaign_audit/campaign_audit.csv |
| C248 | campaign.B2.duplicate_results | 0 | 0 | PASS | campaign_audit/campaign_audit.csv |
| C249 | campaign.B2.cleanup_failure | 0 | 0 | PASS | campaign_audit/campaign_audit.csv |
| C250 | campaign.B2.accounting_reconciles | True | True | PASS | campaign_audit/campaign_audit.csv |
| C251 | campaign.B3.records | 1762 | 1762 | PASS | campaign_audit/campaign_audit.csv |
| C252 | campaign.B3.valid_completed_benchmarks | 1181 | 1181 | PASS | campaign_audit/campaign_audit.csv |
| C253 | campaign.B3.export_success | 1190 | 1190 | PASS | campaign_audit/campaign_audit.csv |
| C254 | campaign.B3.export_failure | 572 | 572 | PASS | campaign_audit/campaign_audit.csv |
| C255 | campaign.B3.validation_failure | 4 | 4 | PASS | campaign_audit/campaign_audit.csv |
| C256 | campaign.B3.failure_runtime_load_execution | 5 | 5 | PASS | campaign_audit/campaign_audit.csv |
| C257 | campaign.B3.failure_timeout | 0 | 0 | PASS | campaign_audit/campaign_audit.csv |
| C258 | campaign.B3.missing_results | 0 | 0 | PASS | campaign_audit/campaign_audit.csv |
| C259 | campaign.B3.unexpected_results | 0 | 0 | PASS | campaign_audit/campaign_audit.csv |
| C260 | campaign.B3.corrupt_or_incomplete_files | 0 | 0 | PASS | campaign_audit/campaign_audit.csv |
| C261 | campaign.B3.duplicate_results | 0 | 0 | PASS | campaign_audit/campaign_audit.csv |
| C262 | campaign.B3.cleanup_failure | 0 | 0 | PASS | campaign_audit/campaign_audit.csv |
| C263 | campaign.B3.accounting_reconciles | True | True | PASS | campaign_audit/campaign_audit.csv |
| C264 | campaign.B4.records | 1762 | 1762 | PASS | campaign_audit/campaign_audit.csv |
| C265 | campaign.B4.valid_completed_benchmarks | 1180 | 1180 | PASS | campaign_audit/campaign_audit.csv |
| C266 | campaign.B4.export_success | 1190 | 1190 | PASS | campaign_audit/campaign_audit.csv |
| C267 | campaign.B4.export_failure | 572 | 572 | PASS | campaign_audit/campaign_audit.csv |
| C268 | campaign.B4.validation_failure | 4 | 4 | PASS | campaign_audit/campaign_audit.csv |
| C269 | campaign.B4.failure_runtime_load_execution | 6 | 6 | PASS | campaign_audit/campaign_audit.csv |
| C270 | campaign.B4.failure_timeout | 0 | 0 | PASS | campaign_audit/campaign_audit.csv |
| C271 | campaign.B4.missing_results | 0 | 0 | PASS | campaign_audit/campaign_audit.csv |
| C272 | campaign.B4.unexpected_results | 0 | 0 | PASS | campaign_audit/campaign_audit.csv |
| C273 | campaign.B4.corrupt_or_incomplete_files | 0 | 0 | PASS | campaign_audit/campaign_audit.csv |
| C274 | campaign.B4.duplicate_results | 0 | 0 | PASS | campaign_audit/campaign_audit.csv |
| C275 | campaign.B4.cleanup_failure | 0 | 0 | PASS | campaign_audit/campaign_audit.csv |
| C276 | campaign.B4.accounting_reconciles | True | True | PASS | campaign_audit/campaign_audit.csv |
| C277 | campaign.B5.records | 1762 | 1762 | PASS | campaign_audit/campaign_audit.csv |
| C278 | campaign.B5.valid_completed_benchmarks | 1181 | 1181 | PASS | campaign_audit/campaign_audit.csv |
| C279 | campaign.B5.export_success | 1190 | 1190 | PASS | campaign_audit/campaign_audit.csv |
| C280 | campaign.B5.export_failure | 572 | 572 | PASS | campaign_audit/campaign_audit.csv |
| C281 | campaign.B5.validation_failure | 4 | 4 | PASS | campaign_audit/campaign_audit.csv |
| C282 | campaign.B5.failure_runtime_load_execution | 5 | 5 | PASS | campaign_audit/campaign_audit.csv |
| C283 | campaign.B5.failure_timeout | 0 | 0 | PASS | campaign_audit/campaign_audit.csv |
| C284 | campaign.B5.missing_results | 0 | 0 | PASS | campaign_audit/campaign_audit.csv |
| C285 | campaign.B5.unexpected_results | 0 | 0 | PASS | campaign_audit/campaign_audit.csv |
| C286 | campaign.B5.corrupt_or_incomplete_files | 0 | 0 | PASS | campaign_audit/campaign_audit.csv |
| C287 | campaign.B5.duplicate_results | 0 | 0 | PASS | campaign_audit/campaign_audit.csv |
| C288 | campaign.B5.cleanup_failure | 0 | 0 | PASS | campaign_audit/campaign_audit.csv |
| C289 | campaign.B5.accounting_reconciles | True | True | PASS | campaign_audit/campaign_audit.csv |
| C290 | campaign.B6.records | 1762 | 1762 | PASS | campaign_audit/campaign_audit.csv |
| C291 | campaign.B6.valid_completed_benchmarks | 1181 | 1181 | PASS | campaign_audit/campaign_audit.csv |
| C292 | campaign.B6.export_success | 1190 | 1190 | PASS | campaign_audit/campaign_audit.csv |
| C293 | campaign.B6.export_failure | 572 | 572 | PASS | campaign_audit/campaign_audit.csv |
| C294 | campaign.B6.validation_failure | 4 | 4 | PASS | campaign_audit/campaign_audit.csv |
| C295 | campaign.B6.failure_runtime_load_execution | 5 | 5 | PASS | campaign_audit/campaign_audit.csv |
| C296 | campaign.B6.failure_timeout | 0 | 0 | PASS | campaign_audit/campaign_audit.csv |
| C297 | campaign.B6.missing_results | 0 | 0 | PASS | campaign_audit/campaign_audit.csv |
| C298 | campaign.B6.unexpected_results | 0 | 0 | PASS | campaign_audit/campaign_audit.csv |
| C299 | campaign.B6.corrupt_or_incomplete_files | 0 | 0 | PASS | campaign_audit/campaign_audit.csv |
| C300 | campaign.B6.duplicate_results | 0 | 0 | PASS | campaign_audit/campaign_audit.csv |
| C301 | campaign.B6.cleanup_failure | 0 | 0 | PASS | campaign_audit/campaign_audit.csv |
| C302 | campaign.B6.accounting_reconciles | True | True | PASS | campaign_audit/campaign_audit.csv |
| C303 | failures.A.export | 3402 | 3402 | PASS | failures/failure_category_summary.csv; campaign_audit/campaign_audit.csv |
| C304 | failures.A.validation | 24 | 24 | PASS | failures/failure_category_summary.csv; campaign_audit/campaign_audit.csv |
| C305 | failures.A.runtime | 634 | 634 | PASS | failures/failure_category_summary.csv; campaign_audit/campaign_audit.csv |
| C306 | failures.A.timeout | 94 | 94 | PASS | failures/failure_category_summary.csv; campaign_audit/campaign_audit.csv |
| C307 | failures.B.export | 3432 | 3432 | PASS | failures/failure_category_summary.csv; campaign_audit/campaign_audit.csv |
| C308 | failures.B.validation | 24 | 24 | PASS | failures/failure_category_summary.csv; campaign_audit/campaign_audit.csv |
| C309 | failures.B.runtime | 34 | 34 | PASS | failures/failure_category_summary.csv; campaign_audit/campaign_audit.csv |
| C310 | failures.B.timeout | 0 | 0 | PASS | failures/failure_category_summary.csv; campaign_audit/campaign_audit.csv |
| C311 | complexity.A.n | 1068 | 1068 | PASS | analysis/inputs/per_model_comparison.csv; complexity/complexity_correlations.csv |
| C312 | complexity.B.n | 1172 | 1172 | PASS | analysis/inputs/per_model_comparison.csv; complexity/complexity_correlations.csv |
| C313 | complexity.A.cpu.flops.rho | 0.6233114716779099 | 0.6233114716779099 | PASS | analysis/inputs/per_model_comparison.csv; complexity/complexity_correlations.csv |
| C314 | complexity.A.cpu.total_params.rho | 0.6427019544156384 | 0.6427019544156384 | PASS | analysis/inputs/per_model_comparison.csv; complexity/complexity_correlations.csv |
| C315 | complexity.A.cpu.total_layers.rho | 0.6320770146679466 | 0.6320770146679466 | PASS | analysis/inputs/per_model_comparison.csv; complexity/complexity_correlations.csv |
| C316 | complexity.A.gpu.flops.rho | 0.6752968286945356 | 0.6752968286945356 | PASS | analysis/inputs/per_model_comparison.csv; complexity/complexity_correlations.csv |
| C317 | complexity.A.gpu.total_params.rho | 0.785499009400061 | 0.785499009400061 | PASS | analysis/inputs/per_model_comparison.csv; complexity/complexity_correlations.csv |
| C318 | complexity.A.gpu.total_layers.rho | 0.8123810177217183 | 0.8123810177217183 | PASS | analysis/inputs/per_model_comparison.csv; complexity/complexity_correlations.csv |
| C319 | complexity.B.cpu.flops.rho | 0.8153874689904852 | 0.8153874689904852 | PASS | analysis/inputs/per_model_comparison.csv; complexity/complexity_correlations.csv |
| C320 | complexity.B.cpu.total_params.rho | 0.9061828858738565 | 0.9061828858738565 | PASS | analysis/inputs/per_model_comparison.csv; complexity/complexity_correlations.csv |
| C321 | complexity.B.cpu.total_layers.rho | 0.8635808009479706 | 0.8635808009479706 | PASS | analysis/inputs/per_model_comparison.csv; complexity/complexity_correlations.csv |
| C322 | complexity.B.gpu.flops.rho | 0.7011871829834194 | 0.7011871829834194 | PASS | analysis/inputs/per_model_comparison.csv; complexity/complexity_correlations.csv |
| C323 | complexity.B.gpu.total_params.rho | 0.7873963287386384 | 0.7873963287386384 | PASS | analysis/inputs/per_model_comparison.csv; complexity/complexity_correlations.csv |
| C324 | complexity.B.gpu.total_layers.rho | 0.7497598723035582 | 0.7497598723035582 | PASS | analysis/inputs/per_model_comparison.csv; complexity/complexity_correlations.csv |
| C325 | pt.n | 1057 | 1057 | PASS | pt_context/matched_pt_a_b.csv; pt_context/model_overlap.csv; analysis/inputs/per_model_comparison.csv |
| C326 | pt.shape_aligned | 227 | 227 | PASS | pt_context/matched_pt_a_b.csv; pt_context/model_overlap.csv; analysis/inputs/per_model_comparison.csv |
| C327 | pt.shape_mismatch | 830 | 830 | PASS | pt_context/matched_pt_a_b.csv; pt_context/model_overlap.csv; analysis/inputs/per_model_comparison.csv |
| C328 | pt.cpu.pt_median_ms | 0.9903 | 0.990304 | PASS | pt_context/matched_pt_a_b.csv; pt_context/model_overlap.csv; analysis/inputs/per_model_comparison.csv |
| C329 | pt.cpu.a_median_ms | 5.4707 | 5.470723191897075 | PASS | pt_context/matched_pt_a_b.csv; pt_context/model_overlap.csv; analysis/inputs/per_model_comparison.csv |
| C330 | pt.cpu.b_median_ms | 0.4828 | 0.48279250000000007 | PASS | pt_context/matched_pt_a_b.csv; pt_context/model_overlap.csv; analysis/inputs/per_model_comparison.csv |
| C331 | pt.cpu.a_ratio | 6.2421 | 6.242106406335511 | PASS | pt_context/matched_pt_a_b.csv; pt_context/model_overlap.csv; analysis/inputs/per_model_comparison.csv |
| C332 | pt.cpu.b_ratio | 0.5916 | 0.5915668786563516 | PASS | pt_context/matched_pt_a_b.csv; pt_context/model_overlap.csv; analysis/inputs/per_model_comparison.csv |
| C333 | pt.cpu.a_rho | 0.712 | 0.7121326505527923 | PASS | pt_context/matched_pt_a_b.csv; pt_context/model_overlap.csv; analysis/inputs/per_model_comparison.csv |
| C334 | pt.cpu.b_rho | 0.928 | 0.9278397008917546 | PASS | pt_context/matched_pt_a_b.csv; pt_context/model_overlap.csv; analysis/inputs/per_model_comparison.csv |
| C335 | pt.gpu.pt_median_ms | 0.3749 | 0.374899 | PASS | pt_context/matched_pt_a_b.csv; pt_context/model_overlap.csv; analysis/inputs/per_model_comparison.csv |
| C336 | pt.gpu.a_median_ms | 2.9993 | 2.9992763996124268 | PASS | pt_context/matched_pt_a_b.csv; pt_context/model_overlap.csv; analysis/inputs/per_model_comparison.csv |
| C337 | pt.gpu.b_median_ms | 2.834 | 2.833964166666667 | PASS | pt_context/matched_pt_a_b.csv; pt_context/model_overlap.csv; analysis/inputs/per_model_comparison.csv |
| C338 | pt.gpu.a_ratio | 7.4516 | 7.451590693615787 | PASS | pt_context/matched_pt_a_b.csv; pt_context/model_overlap.csv; analysis/inputs/per_model_comparison.csv |
| C339 | pt.gpu.b_ratio | 7.1882 | 7.188193858986631 | PASS | pt_context/matched_pt_a_b.csv; pt_context/model_overlap.csv; analysis/inputs/per_model_comparison.csv |
| C340 | pt.gpu.a_rho | 0.824 | 0.8239383426195226 | PASS | pt_context/matched_pt_a_b.csv; pt_context/model_overlap.csv; analysis/inputs/per_model_comparison.csv |
| C341 | pt.gpu.b_rho | 0.789 | 0.788683764703709 | PASS | pt_context/matched_pt_a_b.csv; pt_context/model_overlap.csv; analysis/inputs/per_model_comparison.csv |
| C342 | pt.cpu.b_closer | 824 | 824 | PASS | pt_context/matched_pt_a_b.csv; pt_context/model_overlap.csv; analysis/inputs/per_model_comparison.csv |
| C343 | historical.n | 1762 | 1762 | PASS | provenance/historical_status.csv |
| C344 | historical.exports | 1732 | 1732 | PASS | provenance/historical_status.csv |
| C345 | historical.execution_completions | 814 | 814 | PASS | provenance/historical_status.csv |
| C346 | semantics.a_materializes | True | True | PASS | provenance/runtime_source/Experiment_A_BenchmarkCLI.cs.txt |
| C347 | semantics.b_materializes | True | True | PASS | provenance/runtime_source/Experiment_B_BenchmarkCLI.cs.txt |

## Provenance limits

No missing headline numerical claim was substituted. The historical 814/1732 claim is regenerated from the retained historical status projection, not reconstructed from a fresh historical run. CV distributions are regenerated from retained per-model CVs, not all original per-iteration sample vectors. Environment, timing semantics and same-host provenance remain documentary evidence. Exact byte identity of discarded ONNX artifacts and Unity numerical parity are unavailable and are not claimed.
