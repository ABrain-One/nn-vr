# V3.2 consistency report

This report verifies the approved claim matrix against retained artifacts. It
records source/document checks only; no model, benchmark, or statistical test
was rerun.

| Row | Approved claim | V3.2 verification |
|---|---|---|
| 1 | P1 is 1067/1762 (60.56%) versus 1177/1762 (66.80%) | Preserved in abstract, Sections 1 and 5, Figure 3, and Appendix Table 3. |
| 2 | P1 transitions are 1061 PP, 116 FP, 6 PF, 579 FF; p=1.60e-27 | Preserved in Figure 3 and complete Appendix Table 3. |
| 3 | P2 is 1064/1186 (89.71%) versus 1177/1186 (99.24%) | Preserved in abstract, Sections 1 and 5, Figure 3, and Appendix Table 3. |
| 4 | P2 transitions are 1061 PP, 116 FP, 3 PF, 6 FF; p=8.45e-31 | Preserved in Figure 3 and complete Appendix Table 3. |
| 5 | Transformer-like P2 association is 73/122 to 119/122 | Preserved in Section 5 and Figure 4 with retained Wilson endpoints. |
| 6 | P3 CPU: 5.4707/0.4780 ms, -4.8325 ms, .078, 1061/1061, p=3.75e-175, rrb=-1.000 | Preserved in Section 5 and Table 2. |
| 7 | P3 GPU: 2.9733/2.8315 ms, -0.0944 ms, .982, 604/1061, p=4.49e-6, rrb=-.163 | Preserved in Section 5 and Table 2. |
| 8 | Failure records are A 3402/24/634/94 and B 3432/24/34/0 | Preserved as propagated runtime-campaign records, distinct from unique-model counts. |
| 9 | CV summaries are A 12.58/88.08 and 9.79/77.51 versus B 2.48/29.56 and 4.40/54.14 | Preserved in Section 5 and Figure 6. |
| 10 | P4 has 1057 matches, 227 shape-aligned; CPU closer and GPU mixed | Preserved as contextual discussion/appendix evidence only. |
| 11 | Historical context is 1732 exports and exactly 814 recorded completions | Preserved as motivation only, with non-blocking PeekOutput semantics. |
| 12 | Final endpoint is A Execute-PeekOutput-ToReadOnlyArray and B Schedule-PeekOutput-DownloadToArray | Preserved in Sections 3.3--3.4, Listing 1, and Figure 1. |

Figure 4 directly encodes the retained endpoints for all displayed groups,
including Transformer-like A 50.97--68.11 and B 93.02--99.16, MobileNet-like
A 70.34--88.22 and B 95.00--100.00, Residual-connections B 94.70--99.83, and
ResNet-like B 98.63--99.96.

The manuscript explicitly says that one retained model-level export/validation
outcome may be propagated into six runtime-campaign records. It never treats
them as six independent export attempts.
