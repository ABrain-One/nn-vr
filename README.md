# NN-VR: vision-model deployment in Unity

NN-VR studies the deployment path from NN-Dataset/PyTorch through ONNX to Unity inference. The checked-in Unity project uses **Unity 6000.6.5f1** and **Unity Inference Engine 2.6.1**, the Sentis successor, for Experiment B. The completion-aware Barracuda baseline is preserved in Git history.

## Start here for project review

The finalized retained-evidence artifact is in [paper_artifact/](paper_artifact/README.md). It supports the paper **From Barracuda to Sentis: Completion-Aware Compatibility Across 1,762 Vision Models in Unity**.

- [Public artifact release v1.0.0](https://github.com/ABrain-One/nn-vr/releases/tag/paper-v1-arxiv)
- [Claim-to-evidence manifest](paper_artifact/RESULTS_MANIFEST.md)
- [Paper figure/table map](paper_artifact/PAPER_OUTPUT_MAP.md)
- [Experiment environment and limitations](paper_artifact/environment/EXPERIMENT_ENVIRONMENT.md)

Reviewing the published results does not require Unity, model weights, PyTorch inference, or a GPU. From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r paper_artifact/analysis/scripts/requirements.txt
cd paper_artifact
sha256sum -c SHA256SUMS
python analysis/scripts/verify_canonical_results.py --check-only
```

Expected: **347/347 PASS** and zero input-integrity failures. The `--check-only` flag leaves the checkout unchanged. These commands verify existing retained evidence; they do not rerun the original experiments.

The artifact README documents optional table/figure reproduction, the pinned reference environment, and the distinction between immutable input hashes, scientific verification, and reference-output byte hashes.

## Repository layout

```text
nn-vr/
├── ab/vr/                       # Python exporters, runners and experiment protocols
│   ├── experiment_a.py          # Completion-aware Barracuda protocol
│   ├── experiment_b.py          # Primary Unity 6 Inference Engine protocol
│   ├── inference_engine_runner.py
│   ├── onnx_exporter.py
│   └── onnx_validator.py
├── NNVRBenchmark/              # Unity Assets, Packages and ProjectSettings
├── paper_artifact/             # Published, bounded reproducibility evidence
├── scripts/                    # Shape helpers and historical setup/diagnostics
├── main.py                     # Legacy general pipeline CLI
├── requirements.txt            # Pipeline Python dependencies
└── EXPERIMENT_B_PROTOCOL.md    # Experiment B contract and campaign namespace
```

Private manuscript drafts, practicum sources, raw campaign statistics, model caches, generated Unity state, temporary files and local ZIP bundles are intentionally ignored. The published `paper_artifact/` is a deliberate versioned exception; it contains the reviewed evidence, not the full raw campaign archive.

## Experiment protocols

| Protocol | Unity/runtime | Completion endpoint | Source configuration |
|---|---|---|---|
| Experiment A | Unity 2022.3.62f3, Barracuda 3.0.2 | `Execute` → `PeekOutput` → `ToReadOnlyArray` | [Barracuda baseline commit](https://github.com/ABrain-One/nn-vr/tree/27cd3c2) |
| Experiment B | Unity 6000.6.5f1, Inference Engine 2.6.1 | `Schedule` → `PeekOutput` → `DownloadToArray` | Current `NNVRBenchmark/` and `ab/vr/experiment_b.py` |

Both protocols use five completed warm-ups and 20 completed measurements per backend, model-specific input shapes, FP32, and the opset-12/IR-7 export contract. Six runtime campaigns reuse one temporary export per model within an experiment. A retained export/validation outcome can propagate into the six records; these are not six independent exports.

Timing includes blocking host-output materialization. It is not isolated kernel timing or an application/XR frame-time measurement. Temporary ONNX artifacts were removed by the low-storage workflow, so byte-identical reuse between A and B cannot be verified. The standalone PyTorch comparison remains contextual because its measurement semantics differ.

See [Experiment B protocol](EXPERIMENT_B_PROTOCOL.md), [Experiment A timing notes](EXPERIMENT_A_TIMING_FIX.md), and the artifact provenance for the recorded controls and limitations.

## Running new pipeline work

The following setup and commands perform real downloads, exports and benchmarks. They are separate from the retained-evidence review workflow above.

### Python and model metadata

Use Python 3.10 or newer in a virtual environment:

```bash
python -m pip install -r requirements.txt
python -m pip install 'git+https://github.com/ABrain-One/nn-dataset.git'
python -c 'import ab.nn.nn; print("NN-Dataset import OK")'
```

`ab` is a namespace package shared with NN-Dataset. Model/checkpoint access and dataset downloads require the corresponding network access and storage. Select a PyTorch build appropriate for the intended hardware; these general pipeline dependencies are not a reconstruction of historically unrecorded framework versions.

### Unity 6 configuration

Install the exact editor recorded in [ProjectVersion.txt](NNVRBenchmark/ProjectSettings/ProjectVersion.txt), then open `NNVRBenchmark/` and resolve the packages declared in [manifest.json](NNVRBenchmark/Packages/manifest.json). The inference package is `com.unity.ai.inference@2.6.1`, accessed through `Unity.InferenceEngine`.

Set `UNITY_EDITOR_PATH` when the editor is installed outside the standard locations:

```bash
export UNITY_EDITOR_PATH=/absolute/path/to/Unity
```

The Experiment B runner supports an explicit editor path and standard platform installation paths. Its recorded benchmark environment remains Linux, forced Vulkan and a physical NVIDIA RTX 4090. The Unity benchmark intentionally checks that GPU/API contract. Configuring a different editor location does not make this a portable CPU-only benchmark or a new scientifically equivalent hardware setup.

The existing Unity installation scripts target the historical Unity 2022.3.62f3 Barracuda setup. They do not install the current Unity 6 project. Legacy Android tooling and shape-export diagnostics remain available for historical development, but are not required for offline paper verification.

### Experiment B commands

Inspect options without running a model:

```bash
python -m ab.vr.experiment_b --help
```

Run one model in the separate validation namespace:

```bash
python -m ab.vr.experiment_b InceptionV3-1 --campaign inference_engine_opset12_completion_aware_validation
```

Run the established population across all six primary runtime campaigns:

```bash
python -m ab.vr.experiment_b --all --all-versions
```

Completed success and classified failure records are retained for resume. `--rerun` explicitly retries requested models. Use a separate checkout/output tree when preserving an existing campaign; do not overwrite the finalized evidence merely to inspect this project.

### Recreating the Barracuda configuration

Use the historical baseline in a separate worktree instead of running Experiment A against the current Unity 6 project:

```bash
git worktree add ../nn-vr-barracuda 27cd3c2
```

That checkout retains the Unity 2022/Barracuda project and its corresponding runner. The current `main.py`, `unity_runner.py`, and Android helpers belong to the legacy workflow; they are not substitutes for the explicit Experiment B entry point.

## Result storage and repository hygiene

Experiment B writes primary per-model JSON records to:

```text
out/nn/stat/inference_engine_opset12_completion_aware_v1/ ... v6/
├── manifest.json
├── onnx/fp32/<model-configuration>/<host>.json
└── failed_benchmarks/<model>.json
```

The validation pilot uses its own `_validation` campaign. Export and validation failures are retained in the per-model records and failure copies, not treated as successful Unity invocations. The runner writes permanent results before removing each temporary ONNX artifact and sidecar.

Keep `Assets/`, `Packages/` and `ProjectSettings/` under version control. Unity `Library/`, generated IDE files, `_work/`, local environments and raw output trees are ignored. `.gitignore` preserves these local files; it does not delete them.

## Licensing

The repository code uses the [MIT License](LICENSE). The published artifact has an explicit [license mapping](paper_artifact/LICENSE_NOTES.md): artifact-authored code is MIT, derived evidence/documentation is CC BY 4.0, and copied project-source snapshots retain their original notices. See [CITATION.cff](paper_artifact/CITATION.cff) for the three-author paper/artifact citation metadata.
