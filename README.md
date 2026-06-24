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
# Create virtual environment
python -m venv .venv

# Activate on Linux/macOS
source .venv/bin/activate

# Activate on Windows (PowerShell)
# If blocked by execution policy, run first: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cu126
pip install onnx onnxscript onnxruntime
```

Install `nn-dataset` (GitHub source required — PyPI version lacks `ab.nn.nn`):

> **⚠️ Do NOT use `pip install nn-dataset`** — the PyPI release ships a different `ab` namespace
> that does not include `ab.nn.nn`, causing a `ModuleNotFoundError` at startup.
> The `pip install git+...` form also **hangs for 20+ minutes** building a wheel over 307 000 files.
> Use the clone + `.pth` approach below instead.

```bash
# Clone source (blob-less, fast)
git clone --filter=blob:none https://github.com/ABrain-One/nn-dataset _work/nn-dataset-src

# Register it on the venv path (no wheel build needed)
python -c "open(r'.venv/Lib/site-packages/nn-dataset-src.pth','w').write(r'$(pwd)/_work/nn-dataset-src')"
```

On **Windows (PowerShell)** use:

```powershell
git clone --filter=blob:none https://github.com/ABrain-One/nn-dataset _work\nn-dataset-src

$src = (Resolve-Path _work\nn-dataset-src).Path
[IO.File]::WriteAllText((Resolve-Path .venv\Lib\site-packages).Path + '\nn-dataset-src.pth', $src)
```

Verify:

```bash
python -c "import ab.nn.nn; print('OK')"
```

---

### 2. Unity Setup

Unity `2022.3.62f3` (changeset `96770f904ca7`) must be installed via Unity Hub.
Use the provided install scripts to automate this — they install Unity Hub if absent, then pull the exact editor version:

**Windows (PowerShell — run from repo root):**

```powershell
# If blocked by execution policy, run first:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
.\scripts\install-unity.ps1
```

**Linux (Ubuntu / Debian):**

```bash
bash install-unity.sh
```

**macOS (Intel + Apple Silicon):**

```bash
bash scripts/install-unity-macos.sh
```

> All three scripts skip installation if the correct Unity version is already present.
> The macOS script tries Homebrew first, falls back to direct DMG download.

After installation, open `NNVRBenchmark/` in Unity Hub and ensure the target platform is set to your local desktop OS (Windows/PC, Mac, or Linux Standalone) so that `ComputePrecompiled` shaders are built for the local GPU.

Required Unity packages (installed via Package Manager inside Unity):

- Barracuda
- Burst
- Mathematics

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
