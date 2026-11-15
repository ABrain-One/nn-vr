# NN-VR retained-evidence reproducibility artifact

**Version 1.0.0.** This artifact contains retained evidence and offline reproduction scripts supporting **From Barracuda to Sentis: Completion-Aware Compatibility Across 1,762 Vision Models in Unity**, by Syed Ali Haider, Dmytro Ignatov and Radu Timofte.

## What it reproduces

The artifact reproduces full-pipeline compatibility, runtime-specific compatibility, transition counts, paired CPU/GPU timing and statistical tests, architecture-associated counts and Wilson intervals, reproducibility summaries, stage-level failure accounting, complexity summaries and the contextual standalone PyTorch comparison. It supports paper Figures 3–6 as documented in [PAPER_OUTPUT_MAP.md](PAPER_OUTPUT_MAP.md). The [claim manifest](RESULTS_MANIFEST.md) maps all 347 checks across the 12 manuscript claim families to retained evidence.

This workflow reproduces manuscript analyses from retained evidence. It does not rerun the original 1,762-model experiment. Pretrained weights, temporary ONNX files, third-party datasets, Unity builds, model caches and complete original experiment reruns are not included.

## Quick start

Recommended reference environment: Python 3.10.12 with the exact dependencies in analysis/scripts/requirements.txt: NumPy 2.2.6, SciPy 1.15.3 and Matplotlib 3.10.9. Create a local environment and install these packages before offline reproduction:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r analysis/scripts/requirements.txt
```

On Windows, activate using `.venv\Scripts\activate.bat` in Command Prompt or `.venv\Scripts\Activate.ps1` in PowerShell. Dependencies are not vendored. Installation uses the package index; the reproduction/verification/plotting scripts themselves do not access the network. Local .venv/venv directories are excluded from packaging and release scanning.

```bash
sha256sum -c SHA256SUMS
python analysis/scripts/verify_canonical_results.py
# Optional retained-result reproduction and presentation plots:
python analysis/scripts/reproduce_paper_results.py
python analysis/scripts/generate_paper_figures.py
python analysis/scripts/audit_release.py
# Reproduction must leave the immutable release files intact:
sha256sum -c SHA256SUMS
```

Expected: **347 / 347 PASS**, with zero supporting-input integrity failures. The verifier recomputes directly from retained CSVs, does not trust generated results.json, never rewrites CANONICAL_RESULTS.json, and exits nonzero on mismatch. Integer/accounting values require exact equality; the justified floating-point tolerances remain fixed. All paths resolve within this directory; a parent checkout is not needed.

The top-level [REPRODUCTION_REPORT.md](REPRODUCTION_REPORT.md) is the frozen reference report. New verification writes analysis/reproduced_outputs/REPRODUCTION_REPORT.generated.md and verification.json, leaving the reference report intact. `--check-only` verifies without writing reports.

## Three distinct verification levels

**Release integrity:** `sha256sum -c SHA256SUMS` verifies immutable retained evidence, canonical values, manifests, provenance/source snapshots, scripts, licenses and release documentation. It includes the frozen top-level reference report. It excludes all files under analysis/reproduced_outputs/ and SHA256SUMS itself. Running the quick start does not invalidate these hashes.

**Scientific reproducibility:** `python analysis/scripts/verify_canonical_results.py` is the authoritative scientific test. All 347 canonical checks should pass in compatible environments. Last-digit differences in tiny floating-point p-values or serialization do not replace this test and do not justify changing its tolerances.

**Reference-render reproducibility:** `sha256sum -c REFERENCE_OUTPUT_HASHES.txt` optionally compares regenerated tables, figures and generated reports with the captured reference outputs. Byte identity has been tested only in the documented reference environment and is not guaranteed across arbitrary Python/SciPy/Matplotlib/font versions or platforms. A reference-output hash mismatch with all canonical checks passing is not, by itself, a scientific failure. See ENVIRONMENT_COMPATIBILITY_TEST.md.

For artifact maintenance, analysis/scripts/package_artifact.py regenerates immutable hashes and a local validation ZIP; it never publishes. Reference hashes are refreshed only by the explicit `--freeze-reference-outputs` option in the pinned environment, not by ordinary packaging. Do not regenerate release hashes to hide a failed input-integrity check.

## Measurement semantics

Six runtime campaigns are repeated Unity executions. A retained model-level export/validation outcome may propagate into all six records; these are not six independent export attempts. Strict success requires valid completed CPU/GPU benchmarks in all six campaigns. Both backends include blocking host-output materialization during five warm-ups and 20 timed observations. Record-level failure totals must not be called unique-model counts. Transient A/B ONNX artifacts were removed by the low-storage workflow; byte identity cannot be checked.

The 1,057 PT matches come from the same physical host, but checkpoint handling, most input shapes, warm-ups and timing boundaries differ. Only 227 retain equal PT/A shapes. PT evidence remains contextual, not a universal Unity-overhead or speedup measurement.

## Provenance and repository relationship

nn-vr supplies the A/B retained analysis and audited runtime/exporter source snapshots. Its nested nn-dataset checkout supplies historical standalone PT records/producer and metadata used by those retained analyses. Inventory HEADs are not assertions that untracked evidence was versioned at those commits. Per-file hashes document the actual inputs. No private machine root is required.

See [environment/PROVENANCE.md](environment/PROVENANCE.md), [RESULTS_MANIFEST.md](RESULTS_MANIFEST.md) and [PAPER_OUTPUT_MAP.md](PAPER_OUTPUT_MAP.md). Historical source inventory, dirty/untracked checkout disclosures, exact source/manuscript hashes and sanitization records are retained. [environment/ARTIFACT_RELEASE.md](environment/ARTIFACT_RELEASE.md) distinguishes source provenance from artifact version 1.0.0.

This bundle does not contain model weights, ONNX artifacts, datasets/images, Unity builds/assets, full historical caches, or complete raw campaign sample archives. Historical timings were deliberately excluded from the status projection. Original full-corpus analysis scripts are inert `.py.txt` provenance snapshots; they require raw archives and are not entry points for this artifact.

## Limitations

Summary reproduction verifies calculations on retained evidence; it is not a rerun of the experiments, raw-sample certification, or numerical output-parity testing. The same-host statement is documentary, not inferred from identifier matching alone. Diagram/source checks are static. See REPRODUCTION_REPORT.md and environment/PROVENANCE.md for authority and limits.

## Licenses

Artifact-authored code is licensed under the [MIT License](LICENSE-CODE). Derived CSV/JSON evidence and artifact-authored documentation/original explanatory material are licensed under [CC BY 4.0](LICENSE-DATA-DOCS). Retained project-source snapshots keep their existing MIT notices; CC BY does not apply to copied code or third-party notices. See [LICENSE_NOTES.md](LICENSE_NOTES.md) for the approved mapping.

## Citation

Please cite the associated paper when using this retained-evidence reproducibility artifact. [CITATION.cff](CITATION.cff) supplies the title, ordered authors, repository and artifact version. No DOI, arXiv identifier or release date is asserted before one is assigned.
