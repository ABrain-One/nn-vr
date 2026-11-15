# Artifact 1.0.0 clean extraction test

Result: PASS in two fresh extractions of the final public artifact, one per tested environment. All workflow commands ran with the extracted artifact as working directory. Active scripts resolved retained inputs within that extraction, with no parent-repository data, Unity project, model cache or network. Dependencies came from already provisioned environments and were not vendored or installed globally.

The acceptance sequence is:

```bash
sha256sum -c SHA256SUMS
python analysis/scripts/verify_canonical_results.py
python analysis/scripts/reproduce_paper_results.py
python analysis/scripts/generate_paper_figures.py
python analysis/scripts/audit_release.py
sha256sum -c SHA256SUMS
```

SHA256SUMS protects immutable inputs/scripts/metadata/release documentation. It deliberately excludes analysis/reproduced_outputs/. The verifier's default report-writing path is tested here, not just --check-only; the top-level frozen REPRODUCTION_REPORT.md stays byte-identical.

| Test | Reference environment | Alternate available environment |
|---|---|---|
| Python / NumPy / SciPy / Matplotlib | 3.10.12 / 2.2.6 / 1.15.3 / 3.10.9 | 3.10.12 / 1.21.5 / 1.8.0 / 3.5.1 |
| Initial immutable SHA-256 check | PASS | PASS |
| Reproduction | PASS | PASS |
| Canonical checks / input-integrity failures | 347/347 PASS / 0 | 347/347 PASS / 0 |
| Figures 3–6 regenerated | PASS | PASS |
| Privacy/release scan | 0 review findings | 0 review findings |
| Post-reproduction immutable hashes | PASS | PASS |
| Frozen top-level report unchanged | PASS | PASS |
| Optional reference-output bytes | All reference hashes PASS | 5 generated files differ; not a scientific failure |

All 347 reproduced canonical fields, including Spearman coefficients, are identical between these particular tested environments. The five differing generated files are the environment-bearing generated report and four figure PDFs. Other compatible library releases can differ in final machine-precision digits of very small p-values or serialized outputs; scientific acceptance remains the unchanged canonical tolerances, not output-byte identity.

Additional negative controls: altering an expected integer by one causes a nonzero canonical-verifier exit; altering a retained input file causes both immutable-hash and input-integrity verification to fail. Only temporary extracted copies are altered for these controls, and their original bytes are restored. No release input is changed.

After writing the test documentation and rebuilding a temporary validation ZIP, the final archive is extracted and the complete sequence repeated in both environments. The ZIP is a local validation aid and is not committed or attached to the review PR. See ENVIRONMENT_COMPATIBILITY_TEST.md for interpretation of reference-output differences. Historical preparation provenance remains preserved separately from the public-facing artifact instructions.
