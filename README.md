# Neural Network VR Pipeline (NN-VR)

<img src='https://abrain.one/img/nn-vr-tr.png' width='25%'/>

End-to-end benchmark pipeline: **nn-dataset** → PyTorch export (via direct module import) → **ONNX** → **ADB** → **Unity Barracuda** on the headset → **JSON** logs.

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
- Unity 2022.3+ with Android / VR build support (IL2CPP)
- Android platform-tools (`adb` on `PATH`)
- VR device (e.g., Meta Quest) in developer mode with USB debugging
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

Switch platform:

```text
File → Build Settings → Android
```

Enable:

- IL2CPP
- ARM64
- Development Build (optional for debugging)

---

### 3. Device Setup

Enable Developer Mode and USB Debugging, then verify ADB:

```bash
adb devices
```

Build and install the APK once:

```text
Build Settings → Build And Run
```

---

## Usage

### Full Pipeline

```bash
python main.py --nn AirNet --limit 1
```

```text
PyTorch → ONNX → adb push → Unity Barracuda → JSON result pull
```

### Export Only

```bash
python main.py --nn AirNet --skip-device
```

### Resume Support

The export pipeline is resumable. If an ONNX model already exists, export is skipped automatically.

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

On device, models are read from `/sdcard/nn_models/{name}.onnx` and results written to `/sdcard/nn_results/output.json`.

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
| `model_loader.py`   | nn-dataset integration                                    |
| `onnx_exporter.py`  | Dynamic import + ONNX export (opset 14, static shapes)    |
| `vr_runner.py`      | ADB push/pull + Unity launcher                            |
| `unity_runner.py`   | Unity benchmark runner interface                          |
| `logger.py`         | JSON logging                                              |
| `NNVRBenchmark/`    | Unity benchmark runtime (Barracuda inference)             |

---

## Pipeline Diagram

```text
nn-dataset row
    ↓
PyTorch model
    ↓
ONNX export
    ↓
adb push
    ↓
Unity Barracuda inference
    ↓
JSON benchmark output
    ↓
results.jsonl
```
