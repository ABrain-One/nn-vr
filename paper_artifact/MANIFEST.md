# Artifact file manifest

Artifact version: 1.0.0. SHA256SUMS covers immutable release inputs, active scripts, provenance and release documentation, including the frozen top-level REPRODUCTION_REPORT.md. It excludes generated files under analysis/reproduced_outputs/ and itself. REFERENCE_OUTPUT_HASHES.txt separately records optional pinned-environment output hashes; it is not a cross-version scientific criterion. Local .venv/venv environments and .git metadata are not packaged. The validation ZIP is generated outside this directory; packaging performs no Git or public action.

| File | Integrity class | Purpose |
|---|---|---|
| `ARTIFACT_SOURCE_INVENTORY.md` | immutable release file | Artifact instructions, output map, provenance, integrity, audit or citation documentation. |
| `CANONICAL_RESULTS.json` | immutable release file | Selected retained derived evidence or fixed canonical/claim metadata. |
| `CITATION.cff` | immutable release file | Artifact instructions, output map, provenance, integrity, audit or citation documentation. |
| `CLEAN_EXTRACTION_TEST.md` | immutable release file | Artifact instructions, output map, provenance, integrity, audit or citation documentation. |
| `ENVIRONMENT_COMPATIBILITY_TEST.md` | immutable release file | Artifact instructions, output map, provenance, integrity, audit or citation documentation. |
| `LICENSE-CODE` | immutable release file | Artifact instructions, output map, provenance, integrity, audit or citation documentation. |
| `LICENSE-DATA-DOCS` | immutable release file | Artifact instructions, output map, provenance, integrity, audit or citation documentation. |
| `LICENSE_NOTES.md` | immutable release file | Artifact instructions, output map, provenance, integrity, audit or citation documentation. |
| `MANIFEST.md` | immutable release file | Artifact instructions, output map, provenance, integrity, audit or citation documentation. |
| `PAPER_OUTPUT_MAP.md` | immutable release file | Artifact instructions, output map, provenance, integrity, audit or citation documentation. |
| `README.md` | immutable release file | Artifact instructions, output map, provenance, integrity, audit or citation documentation. |
| `REFERENCE_OUTPUT_HASHES.txt` | immutable release file | Optional pinned-environment output-byte reference; not a cross-version scientific requirement. |
| `RELEASE_SAFETY_AUDIT.md` | immutable release file | Artifact instructions, output map, provenance, integrity, audit or citation documentation. |
| `REPRODUCTION_REPORT.md` | immutable release file | Frozen A1 reference report; verification writes a separate generated report. |
| `RESULTS_MANIFEST.json` | immutable release file | Selected retained derived evidence or fixed canonical/claim metadata. |
| `RESULTS_MANIFEST.md` | immutable release file | Artifact instructions, output map, provenance, integrity, audit or citation documentation. |
| `SHA256SUMS` | integrity manifest (self excluded) | Artifact instructions, output map, provenance, integrity, audit or citation documentation. |
| `THIRD_PARTY_CONTENT_AUDIT.md` | immutable release file | Artifact instructions, output map, provenance, integrity, audit or citation documentation. |
| `analysis/inputs/per_model_comparison.csv` | immutable release file | Selected retained derived evidence or fixed canonical/claim metadata. |
| `analysis/inputs/statistical_tests.json` | immutable release file | Selected retained derived evidence or fixed canonical/claim metadata. |
| `analysis/inputs/summary.json` | immutable release file | Selected retained derived evidence or fixed canonical/claim metadata. |
| `analysis/reproduced_outputs/REPRODUCTION_REPORT.generated.md` | generated reference output | Deterministically regenerated paper summary/table/figure or verification output. |
| `analysis/reproduced_outputs/architecture.csv` | generated reference output | Deterministically regenerated paper summary/table/figure or verification output. |
| `analysis/reproduced_outputs/campaigns.csv` | generated reference output | Deterministically regenerated paper summary/table/figure or verification output. |
| `analysis/reproduced_outputs/compatibility.csv` | generated reference output | Deterministically regenerated paper summary/table/figure or verification output. |
| `analysis/reproduced_outputs/complexity.csv` | generated reference output | Deterministically regenerated paper summary/table/figure or verification output. |
| `analysis/reproduced_outputs/failures.csv` | generated reference output | Deterministically regenerated paper summary/table/figure or verification output. |
| `analysis/reproduced_outputs/figure3_transitions.pdf` | generated reference output | Deterministically regenerated paper summary/table/figure or verification output. |
| `analysis/reproduced_outputs/figure4_architecture.pdf` | generated reference output | Deterministically regenerated paper summary/table/figure or verification output. |
| `analysis/reproduced_outputs/figure5_paired_latency.pdf` | generated reference output | Deterministically regenerated paper summary/table/figure or verification output. |
| `analysis/reproduced_outputs/figure6_reproducibility.pdf` | generated reference output | Deterministically regenerated paper summary/table/figure or verification output. |
| `analysis/reproduced_outputs/paper_tables.md` | generated reference output | Deterministically regenerated paper summary/table/figure or verification output. |
| `analysis/reproduced_outputs/pt_context.csv` | generated reference output | Deterministically regenerated paper summary/table/figure or verification output. |
| `analysis/reproduced_outputs/reproducibility.csv` | generated reference output | Deterministically regenerated paper summary/table/figure or verification output. |
| `analysis/reproduced_outputs/results.json` | generated reference output | Deterministically regenerated paper summary/table/figure or verification output. |
| `analysis/reproduced_outputs/timing.csv` | generated reference output | Deterministically regenerated paper summary/table/figure or verification output. |
| `analysis/reproduced_outputs/verification.json` | generated reference output | Deterministically regenerated paper summary/table/figure or verification output. |
| `analysis/scripts/audit_release.py` | immutable release file | Offline reproduction, verification, plotting or local packaging helper / requirements. |
| `analysis/scripts/generate_paper_figures.py` | immutable release file | Offline reproduction, verification, plotting or local packaging helper / requirements. |
| `analysis/scripts/package_artifact.py` | immutable release file | Offline reproduction, verification, plotting or local packaging helper / requirements. |
| `analysis/scripts/reproduce_paper_results.py` | immutable release file | Offline reproduction, verification, plotting or local packaging helper / requirements. |
| `analysis/scripts/requirements.txt` | immutable release file | Offline reproduction, verification, plotting or local packaging helper / requirements. |
| `analysis/scripts/verify_canonical_results.py` | immutable release file | Offline reproduction, verification, plotting or local packaging helper / requirements. |
| `architecture/architecture_comparison.csv` | immutable release file | Selected retained derived evidence or fixed canonical/claim metadata. |
| `campaign_audit/campaign_audit.csv` | immutable release file | Selected retained derived evidence or fixed canonical/claim metadata. |
| `campaign_audit/export_contract_audit.csv` | immutable release file | Selected retained derived evidence or fixed canonical/claim metadata. |
| `compatibility/compatibility_transition.csv` | immutable release file | Selected retained derived evidence or fixed canonical/claim metadata. |
| `compatibility/post_export_runtime_transition.csv` | immutable release file | Selected retained derived evidence or fixed canonical/claim metadata. |
| `complexity/complexity_correlations.csv` | immutable release file | Selected retained derived evidence or fixed canonical/claim metadata. |
| `environment/ARTIFACT_RELEASE.md` | immutable release file | Recorded environment and checkout provenance; missing historical values explicitly marked. |
| `environment/EXPERIMENT_ENVIRONMENT.md` | immutable release file | Recorded environment and checkout provenance; missing historical values explicitly marked. |
| `environment/PROVENANCE.md` | immutable release file | Recorded environment and checkout provenance; missing historical values explicitly marked. |
| `environment/REPOSITORY_STATE.json` | immutable release file | Recorded environment and checkout provenance; missing historical values explicitly marked. |
| `environment/RETAINED_ENVIRONMENT_FIELDS.json` | immutable release file | Recorded environment and checkout provenance; missing historical values explicitly marked. |
| `environment/SOFTWARE_VERSIONS.md` | immutable release file | Recorded environment and checkout provenance; missing historical values explicitly marked. |
| `failures/failure_category_summary.csv` | immutable release file | Selected retained derived evidence or fixed canonical/claim metadata. |
| `failures/failure_message_summary.csv` | immutable release file | Selected retained derived evidence or fixed canonical/claim metadata. |
| `failures/transition_failure_evidence.csv` | immutable release file | Selected retained derived evidence or fixed canonical/claim metadata. |
| `provenance/FROZEN_MANUSCRIPT_HASHES.json` | immutable release file | Original/released-file hashes, transformations or retained historical identity/status projection. |
| `provenance/ORIGIN_PRESERVATION_CHECK.md` | immutable release file | Original/released-file hashes, transformations or retained historical identity/status projection. |
| `provenance/SANITIZATION_LOG.json` | immutable release file | Original/released-file hashes, transformations or retained historical identity/status projection. |
| `provenance/SOURCE_FILE_HASHES.json` | immutable release file | Original/released-file hashes, transformations or retained historical identity/status projection. |
| `provenance/analysis_source/Inference.py.txt` | immutable release file | Inert original source snapshot; provenance only, never executed by artifact workflow. |
| `provenance/analysis_source/analyze_experiment_ab.py.txt` | immutable release file | Inert original source snapshot; provenance only, never executed by artifact workflow. |
| `provenance/analysis_source/compare_nn_dataset.py.txt` | immutable release file | Inert original source snapshot; provenance only, never executed by artifact workflow. |
| `provenance/analysis_source/generate_paired_latency_figure.py.txt` | immutable release file | Inert original source snapshot; provenance only, never executed by artifact workflow. |
| `provenance/historical_status.csv` | immutable release file | Original/released-file hashes, transformations or retained historical identity/status projection. |
| `provenance/licenses/nn-dataset-LICENSE` | immutable release file | Original project license notice; retained verbatim. |
| `provenance/licenses/nn-vr-LICENSE` | immutable release file | Original project license notice; retained verbatim. |
| `provenance/manuscript/CLAIM_MATRIX.md` | immutable release file | Frozen claim, table, diagram or scientific-source evidence copied for traceability. |
| `provenance/manuscript/V3_2_CONSISTENCY_REPORT.md` | immutable release file | Frozen claim, table, diagram or scientific-source evidence copied for traceability. |
| `provenance/manuscript/appendix.tex` | immutable release file | Frozen claim, table, diagram or scientific-source evidence copied for traceability. |
| `provenance/manuscript/experimental_setup.tex` | immutable release file | Frozen claim, table, diagram or scientific-source evidence copied for traceability. |
| `provenance/manuscript/figures.tex` | immutable release file | Frozen claim, table, diagram or scientific-source evidence copied for traceability. |
| `provenance/manuscript/results.tex` | immutable release file | Frozen claim, table, diagram or scientific-source evidence copied for traceability. |
| `provenance/manuscript/study_design.tex` | immutable release file | Frozen claim, table, diagram or scientific-source evidence copied for traceability. |
| `provenance/runtime_source/Experiment_A_BenchmarkCLI.cs.txt` | immutable release file | Inert original source snapshot; provenance only, never executed by artifact workflow. |
| `provenance/runtime_source/Experiment_B_BenchmarkCLI.cs.txt` | immutable release file | Inert original source snapshot; provenance only, never executed by artifact workflow. |
| `provenance/runtime_source/onnx_exporter.py.txt` | immutable release file | Inert original source snapshot; provenance only, never executed by artifact workflow. |
| `pt_context/SOURCE_SELECTION.md` | immutable release file | Artifact instructions, output map, provenance, integrity, audit or citation documentation. |
| `pt_context/comparison_summary.json` | immutable release file | Selected retained derived evidence or fixed canonical/claim metadata. |
| `pt_context/matched_pt_a_b.csv` | immutable release file | Selected retained derived evidence or fixed canonical/claim metadata. |
| `pt_context/model_overlap.csv` | immutable release file | Selected retained derived evidence or fixed canonical/claim metadata. |
| `reproducibility/per_model_reproducibility.csv` | immutable release file | Selected retained derived evidence or fixed canonical/claim metadata. |
| `reproducibility/reproducibility_summary.csv` | immutable release file | Selected retained derived evidence or fixed canonical/claim metadata. |
| `reproducibility/timing_reproducibility_outliers.csv` | immutable release file | Selected retained derived evidence or fixed canonical/claim metadata. |
| `timing/paired_latency_comparison.csv` | immutable release file | Selected retained derived evidence or fixed canonical/claim metadata. |
| `timing/runtime_latency_summary.csv` | immutable release file | Selected retained derived evidence or fixed canonical/claim metadata. |
