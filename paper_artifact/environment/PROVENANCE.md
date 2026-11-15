# Provenance

Artifact inventory/build timestamp (UTC): 2026-11-15T22:12:10.478472+00:00.

| Repository | Branch | Inventory HEAD |
|---|---|---|
| nn-dataset | main | fa7c741fbb372cb4360296ac5f508253c67a8633 |
| nn-vr | main | d103cd388e57f7ae6070bd3fb3c9d0c678337b9f |
| nn-vr-experiment-b | experiment-b-inference-engine | 642e8cd42277dbfbaad19a5fe4acaca4dd7fbe59 |

The frozen V3.2 manuscript lives at nn-vr/arxiv_article_v3_2 and is untracked at inventory; do not cite the checkout HEAD as its manuscript commit. Its complete before-build file hash list is provenance/FROZEN_MANUSCRIPT_HASHES.json. No manuscript file is modified by this preparation. nn-dataset is a nested checkout at nn-vr/nn-dataset, not an assumed sibling. The B checkout is a sibling named nn-vr-experiment-b and contains uncommitted runtime changes; the candidate uses hashed retained/current sources rather than pretending they are all in HEAD.

Authority order: frozen V3.2 consistency audit and approved claim matrix; retained A/B per-model and audit tables; retained summary/statistical-test files as cross-checks; retained PT comparison tables/source-selection audit; audited producer source for measurement semantics. Experimental records remain unchanged outside this candidate.

Experiment A source is extracted read-only from nn-vr commit 27cd3c203dd17996f963b8839848e17ae2b3bef6, whose warm-up and timed paths include ToReadOnlyArray. Current nn-vr source is B, so it is not mislabeled as A. B source is the hashed current BenchmarkCLI.cs snapshot. Producer code snapshots are inert .txt provenance, not executable artifact entry points. Historical 814 execution completions and 1732 exports are regenerated from a projection of retained aggregated_unity_stats.csv; the original producer script is not rerun against present-day directories.

Analysis sources: nn-vr/analysis/experiment_ab/analyze_experiment_ab.py; nn-vr/analysis/experiment_ab/nn_dataset_comparison/compare_nn_dataset.py; historical PT producer nn-dataset/ab/nn/util/Inference.py. Originals and their exact hashes are mapped in provenance/SOURCE_FILE_HASHES.json. Repository-relative source labels do not imply those paths exist in this extracted artifact. All active scripts use packaged paths only.

Sanitization changes only filesystem-root and host-filename provenance strings, plus a documented historical column projection. Original source hashes remain available; released-file hashes identify sanitized copies. No claim value or model identifier was changed. No new scientific test/design or experiment was introduced; deterministic re-execution reproduces existing reported statistics only.
