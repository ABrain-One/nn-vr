# Unity runner (Barracuda)

See the repository root `README.md` for the full nn-dataset → ONNX → ADB → Barracuda flow.

- Open this folder in Unity (version in `ProjectSettings/ProjectVersion.txt`).
- Ensure the **Barracuda** package is installed.
- Build an Android APK and install it on the headset; `main.py` pushes ONNX to `/sdcard/nn_models/` and pulls `/sdcard/nn_results/output.json`.

Core script: `Assets/Scripts/BarracudaRunner.cs`.
