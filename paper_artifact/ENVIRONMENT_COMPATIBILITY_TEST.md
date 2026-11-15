# Artifact 1.0.0 environment compatibility and reference-render test

Both tests use only the packaged retained evidence and the original 347 canonical values/tolerances. No host-global package installation or change was made.

| Environment | Python | NumPy | SciPy | Matplotlib | Scientific verification | Immutable integrity before/after |
|---|---|---|---|---|---|---|
| Pinned reference | 3.10.12 | 2.2.6 | 1.15.3 | 3.10.9 | 347/347 PASS; 0 input-integrity failures | PASS / PASS |
| Existing alternate | 3.10.12 | 1.21.5 | 1.8.0 | 3.5.1 | 347/347 PASS; 0 input-integrity failures | PASS / PASS |

The exact reference requirements remain in analysis/scripts/requirements.txt. Reproduction uses the same Wilcoxon/binomial/Spearman formulas and original tolerances. A small API compatibility adaptation selects SciPy's mode versus method keyword and correlation versus statistic result-field name. It does not change any hypothesis, population, test setting or numeric tolerance.

In the reference environment, all 16 generated reference-output files match REFERENCE_OUTPUT_HASHES.txt after a fresh extraction, report generation and figure rendering. This is a tested result in the documented environment, not a universal byte-identity guarantee across dependency versions, Python builds, fonts or platforms.

In the alternate environment, all 347 canonical fields are identical to the reference results, and all Spearman rho fields are identical. Five reference-output byte hashes differ: REPRODUCTION_REPORT.generated.md records the alternate environment; figure3_transitions.pdf, figure4_architecture.pdf, figure5_paired_latency.pdf and figure6_reproducibility.pdf use the alternate Matplotlib version. These are expected reference-byte mismatches with scientific verification and immutable integrity still passing.

For other compatible library releases, tiny floating-point p-values may differ in last serialization digits. This is not a reason to weaken tolerances or rewrite canonical values. If any canonical check fails within its existing justified tolerance or an immutable input hash fails, treat that as a failure and investigate. The frozen top-level REPRODUCTION_REPORT.md is never overwritten by either environment.
