# Neural Network VR Pipeline (NN-VR)

<img src='https://abrain.one/img/nn-vr-tr.png' width='25%'/>

End-to-end benchmark pipeline: **nn-dataset** → PyTorch export (via direct module import) → **ONNX** → **ADB** → **Unity Barracuda** on the headset → **JSON** logs.

## Prerequisites

- Python 3.10+
- Unity 2022.3+ with Android / VR build support (IL2CPP)
- Android platform-tools (`adb` on `PATH`)
- VR device (e.g., Meta Quest) in developer mode with USB debugging

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows

# Install PyTorch and ONNX dependencies
pip install -r requirements.txt --extra-index-url [https://download.pytorch.org/whl/cu126](https://download.pytorch.org/whl/cu126)
pip install onnx onnxscript onnxruntime

# Install nn-dataset
pip install --no-cache-dir git+[https://github.com/ABrain-One/nn-dataset](https://github.com/ABrain-One/nn-dataset) --upgrade

Install the Unity project under `unity_runner/`, add Barracuda from the Package Manager, build an APK to `unity_runner/Build/` (or your preferred output), and install it on the device once.

## Usage

Export ONNX and run the full device pipeline (requires a connected device):

```bash
python main.py --nn AirNet --limit 1
```

Export only (no `adb`):

```bash
python main.py --nn AirNet --skip-device
```
Note: The export pipeline is fully resumable. If an .onnx file already exists in the `models/` directory, 
the script will skip the export phase for that model.

Tunable timeouts:

- `--export-timeout` (default 60): kills stuck ONNX export subprocesses.
- Logcat wait uses the same order of magnitude inside `vr_runner.wait_for_done`.

Benchmark lines append to `results.jsonl` (JSON Lines).

## Layout

| Path | Role |
|------|------|
| `main.py` | Orchestrator |
| `model_loader.py` | `ab.nn.api.data` |
| `onnx_exporter.py` | `importlib` dynamic loading + `torch.onnx.export` (opset 14, static shapes) + subprocess timeout |
| `vr_runner.py` | `adb` push/pull, `am start`, logcat `DONE` |
| `logger.py` | Append JSON lines |
| `unity_runner/` | Unity + `Assets/Scripts/BarracudaRunner.cs` |

On device, models are read from `/sdcard/nn_models/{name}.onnx` and results written to `/sdcard/nn_results/output.json` (`latency_ms`, `memory_mb`, …).

## Pipeline

```
nn-dataset row → ONNX → adb push → Unity Barracuda → pull output.json → results.jsonl
```
