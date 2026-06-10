# Neural Network VR Pipeline (NN-VR)

<img src='https://abrain.one/img/nn-vr-tr.png' width='25%'/>

End-to-end benchmark pipeline: **nn-dataset** → PyTorch export (via direct module import) → **ONNX** → **Unity Barracuda** (Desktop Headless Batchmode) → **JSON** logs.

---

## Repository Structure

The Unity benchmark project is embedded directly inside the main repository:

```text
nn-vr/
├── data/
├── db/
├── logs/
├── nn-dataset/
├── NNVRBenchmark/
│   ├── Assets/
│   ├── Packages/
│   └── ProjectSettings/
├── main.py
├── vr_runner.py
└── README.md
```

The Unity project is used as the runtime execution layer for Barracuda inference benchmarking.

---

## Unity Project Management

When embedding Unity inside a Git repository, Unity generates thousands of temporary/cache files.
Most of these should **NOT** be committed.

### Commit These

These folders should remain under version control:

```text
Assets/
Packages/
ProjectSettings/
```

These contain source code, scenes, scripts, package dependencies, and reproducible project configuration.

### Do NOT Commit These

These are generated automatically and can always be rebuilt locally:

```text
Library/
Temp/
Obj/
Build/
Builds/
Logs/
MemoryCaptures/
UserSettings/
.vscode/
.idea/
*.csproj
*.sln
```

### Rebuilding Unity State

If `Library/`, `Temp/`, or generated project files are deleted, simply reopen the project in Unity and they will be regenerated automatically.

---

## Prerequisites

- Python 3.10+
- Unity 2022.3+ (for desktop batchmode inference)
- Barracuda package installed inside Unity

---

## Setup

### 1. Python Environment

```bash
python -m venv .venv
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cu126
pip install onnx onnxscript onnxruntime
```

Install `nn-dataset`:

```bash
pip install --no-cache-dir git+https://github.com/ABrain-One/nn-dataset --upgrade
```

---

### 2. Unity Setup

Open `NNVRBenchmark/` inside Unity Hub.

Unity version:

```text
2022.3.62f3
```

Required packages:

- Barracuda
- Burst
- Mathematics

Ensure your Unity target platform is set to your local desktop OS (e.g., Windows/PC, Mac, Linux Standalone) so that `ComputePrecompiled` shaders can be built locally for the desktop GPU.

---

## Usage

The `main.py` orchestrator supports running the entire pipeline for all models, a single model, or a selective list of models.

### 1. Run Pipeline for All Models
To process every model available in the dataset (Export + Unity Benchmark):
```bash
python main.py
```

### 2. Run Pipeline for a Single Model
Pass the model name as a positional argument:
```bash
python main.py AirNet
```

### 3. Run Pipeline for Selective Models
Pass a comma-separated list of model names:
```bash
python main.py ResNet,UNet2D,GoogLeNet
```

### 4. Stage-Specific Execution
If you only want to run **Stage 1 (ONNX Export)** and skip the Unity benchmarking:
```bash
python main.py AirNet --skip-device
```

If you only want to run **Stage 2 (Unity Benchmark)** on already exported ONNX files:
```bash
python main.py AirNet --benchmark-only
```

### Resume Support

The export pipeline is resumable. If an ONNX model already exists in `_work/onnx_temp/`, export is skipped automatically.
You can force a re-export of all models by adding the `--force` flag.

### 5. Automated Data Persistence
To automatically clone the `nn-dataset` repository, push your local generated telemetry from `out/` to GitHub, and clean up the local disk space when the pipeline finishes, append the `--push-dataset` flag:
```bash
python main.py --push-dataset
```

---

## Benchmark Output

Results are appended to `results.jsonl` (JSON Lines format).

*Note: Benchmark outputs (`results.jsonl`, `unity_benchmarks.json`) are intentionally gitignored to prevent committing volatile runtime data.*

Each entry contains:

- model metadata
- runtime/backend info
- CPU/GPU/NPU timing
- tensor dimensions
- Unity version
- device analytics
- crash/failure information

Models are processed locally and results are routed directly into the dataset output directories.

---

## Benchmark Status Types

| Status          | Meaning                                  |
| --------------- | ---------------------------------------- |
| `success`       | Inference completed successfully         |
| `partial`       | Model loaded but timings failed          |
| `runtime_error` | Unity/Barracuda crashed                  |
| `unsupported`   | Unsupported ONNX/Barracuda operation     |
| `timeout`       | Benchmark exceeded timeout               |

---

## Layout

| Path                | Role                                                      |
| ------------------- | --------------------------------------------------------- |
| `main.py`           | Pipeline orchestrator                                     |
| `process_models.py` | Stage 1: ONNX exporter & evaluator                        |
| `benchmark_models.py`| Stage 2: Unity benchmark orchestrator                     |
| `model_loader.py`   | nn-dataset integration                                    |
| `onnx_exporter.py`  | Dynamic import + ONNX export (opset 14, static shapes)    |
| `vr_runner.py`      | (Legacy) ADB push/pull + Unity launcher                   |
| `unity_runner.py`   | Unity desktop batchmode benchmark runner interface        |
| `logger.py`         | JSON logging                                              |
| `NNVRBenchmark/`    | Unity benchmark runtime (Barracuda inference)             |

---

## Pipeline Diagram

```text
nn-dataset row
    ↓
PyTorch model
    ↓
ONNX export (opset 12, IR 7)
    ↓
Unity Barracuda inference (Desktop Headless Batchmode)
    ↓
JSON benchmark output
    ↓
out/nn/stat/run/onnx/fp32/ (per-model JSON artifacts)
```
