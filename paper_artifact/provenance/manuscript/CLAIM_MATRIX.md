# ARTICLE V3 CLAIM MATRIX

## Use

This matrix is the claim-control sheet for the future V3 manuscript. “Population”
is part of every claim. The listed artifacts are retained, raw-derived inputs;
they are not invitations to rerun the study.

| # | Claim | Exact population / denominator | Supporting artifact and statistic | Limitation | Safe publication wording | Avoid |
|---:|---|---|---|---|---|---|
| 1 | Full-pipeline compatibility improved | 1,762 requested models, strict valid completed benchmark in all 6 campaigns | `summary.json`; `compatibility_transition.csv`; A=1067/1762 (60.56%), B=1177/1762 (66.80%), net +110/+6.24 pp; exact McNemar p=1.60e-27 | Includes acquisition and retained export/validation, not runtime alone; one host/configuration | “Under the recorded full workflow, repeat-stable completion rose from 60.56% to 66.80%.” | “Sentis supports 66.80% of vision models generally.” |
| 2 | Runtime-specific compatibility improved | 1,186 common retained export/validation-eligible models | `post_export_runtime_transition.csv`; A=1064/1186 (89.71%), B=1177/1186 (99.24%), +9.53 pp; exact McNemar p=8.45e-31 | Eligibility is an experiment-level retained-stage outcome propagated to six runtime records; five A-only cases excluded | “Among models reaching both Unity runtime comparisons, Sentis 2.6.1 reduced observed Barracuda-specific runtime failures.” | “The runtime change caused every recovery.” |
| 3 | Recoveries outweigh regressions | Full: 116 FAIL→PASS, 6 PASS→FAIL, 579 FAIL→FAIL (N=1762). Post-export: 116/3/6 plus 1061 PASS→PASS (N=1186) | `compatibility_transition.csv`; `post_export_runtime_transition.csv`; exact McNemar tests above | Transitions are operational outcomes, not operator-level diagnoses | “The paired transitions show 116 recoveries versus 6 full-pipeline regressions; in the common runtime population they show 116 versus 3.” | “All prior Barracuda incompatibilities were fixed.” |
| 4 | Transformer-like association is large | 122 overlapping Transformer-like flagged models in common post-export population | `architecture_comparison.csv`; 73/122 (59.84%) to 119/122 (97.54%), +37.70 pp, 47 recoveries, 1 regression; Wilson intervals | Flags overlap; subgroup is descriptive; no causal graph/operator attribution | “The largest well-powered flagged-group change was observed for Transformer-like models.” | “Sentis fixes Transformer operators.” |
| 5 | CPU completion-aware timing favored B | 1,061 models with valid completed CPU/GPU benchmark in all 6 A and B campaigns | `paired_latency_comparison.csv`; CPU medians A/B=5.4707/0.4780 ms; median B−A=−4.8325 ms; B/A=0.078; B faster 1061/1061; Wilcoxon p=3.75e-175, r_rb=−1.000 | Completion/readback is included; host/runtime/backend specific; not kernel-only timing | “On the stated completion-aware CPU boundary, B was lower for every paired model.” | “Sentis is universally 12.8× faster on CPU.” |
| 6 | GPU timing change is modest and heterogeneous | Same 1,061 paired models | `paired_latency_comparison.csv`; A/B=2.9733/2.8315 ms; B−A=−0.0944 ms; B/A=0.982; B faster 604/1061 (56.93%); p=4.49e-06, r_rb=−0.163 | Statistical detectability does not make a large practical or universal effect | “The observed GPU shift was small and heterogeneous despite a paired statistical difference.” | “Sentis provides a broad GPU speedup.” |
| 7 | Cross-campaign timing stability improved | Models with at least two valid campaigns: A n=1071, B n=1181 for CV summaries | `reproducibility_summary.csv`; CPU median/p95 CV A=12.58%/88.08%, B=2.48%/29.56%; GPU A=9.79%/77.51%, B=4.40%/54.14% | Six campaigns do not cover all system states; CVs are not a causal mechanism | “B had lower observed central and upper-tail CV summaries, especially on CPU.” | “B is deterministic/reproducible in all deployments.” |
| 8 | Failure evidence locates the largest observed contrast at the runtime stage | All six campaign records, not unique model counts | `failure_category_summary.csv`; A export/validation/runtime/timeout=3402/24/634/94; B=3432/24/34/0 | Export/validation outcomes are propagated into six records; error messages are a taxonomy, not root causes | “Near-identical retained-stage record burdens and lower B runtime-failure records localize the principal observed difference to the Unity stage.” | “Export failures happened 3,402 independent times” or “the logs prove a root cause.” |
| 9 | Complexity is associated with timing | Valid timing record plus complete FLOPs, parameter, and layer metadata: A n=1068, B n=1172 | `complexity_correlations.csv`; Spearman rho range 0.623–0.906; strongest B CPU parameters rho=0.906 | Metadata missingness differs from architecture labels; no held-out prediction or causal interpretation | “Existing complexity metadata was positively associated with timing in this environment.” | “Parameters predict latency generally.” |
| 10 | Retained PT evidence gives contextual CPU alignment, mixed GPU relation | 1,057 exact PT/A/B identifier matches; 227 have equal retained PT/A input shape | `nn_dataset_comparison/comparison_summary.json`; CPU B/PT median ratio=0.5916 vs A/PT=6.2421 and rank rho 0.928 vs 0.712; GPU ratios B=7.1882 vs A=7.4516 but rho A=0.824 vs B=0.789 | Same physical host, but different checkpoint handling, shapes, warm-ups, and timing/completion boundaries; Level 3 only | “In the retained same-host context, B was descriptively closer to PT on CPU; GPU relationships were mixed.” | “Unity has a universal overhead multiplier” or “B is faster than PyTorch.” |
| 11 | Historical values are not final latency evidence | Historical 1,762-entry retained snapshot | historical artifacts and source audit; 1,732 exports, **814** Barracuda execution completions after export | Stopwatch ended after non-blocking `PeekOutput`; different workflow and semantics | “The historical survey motivates the deployment problem but its timing values are dispatch/timing-window observations.” | “Historical latency proves completed Unity inference.” |
| 12 | Final timing boundary is completion-aware | A/B warm-ups and timed iterations in actual Unity source | `BenchmarkCLI.cs`; B warm-up calls `MaterializeOutput`; measured path stops timer only after it; helper calls `Schedule`, `PeekOutput`, `DownloadToArray`; A analogous `ToReadOnlyArray` path | It includes output materialization/readback; it is neither an isolated kernel measure nor application-frame latency | “The measured endpoint follows requested host output materialization in both warm-ups and timed iterations.” | “The measurement is pure GPU/kernel latency” or “it certifies XR frame time.” |

## Mandatory terminology and accounting rules

- First B identification: **Unity Sentis 2.6.1**, package
  `com.unity.ai.inference@2.6.1`, API `Unity.InferenceEngine`.
- Later use: **Sentis 2.6.1**. Avoid implying that the experiment used the older
  `com.unity.sentis` package.
- State IR7 as: exporter verifies opset 12, assigns `model.ir_version = 7`, saves,
  then uses the established ONNX validation path. Do not call this graph conversion.
- Distinguish the maximum A/B per-campaign valid counts (1074/1181), the
  independently computed at-least-one-valid unions (also 1074/1181), and strict
  all-six intersections (1067/1177).
- Describe the A counts 1074, 1071, 1070, 1068, 1068, 1067 and timeout counts
  11, 14, 15, 17, 18, 19 as an unresolved monotonic pattern. No causal explanation
  is supported.
- Always describe architecture flags as overlapping associations, and corpus-wide
  p-values as characterizing this potentially related 1,762-entry corpus.
