# Neural Network VR Pipeline (NN-VR)

This repository contains the end-to-end pipeline for porting, verifying, and deploying Neural Network (NN) models from the `nn-dataset` to VR/Android devices using Unity and Barracuda.

## Prerequisites

- **Python 3.8+**
- **Unity 2022.3+** (with Android Build Support & IL2CPP)
- **Android Studio** (for SDK/ADB)
- **VR Headset** (Meta Quest 2/3/Pro) in Developer Mode

## Setup Instructions

### 1. Create and Activate a Virtual Environment (Recommended)

**For Linux/Mac:**
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

**For Windows:**
```bash
python3 -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
```

### 2. Install Requirements

Install the project dependencies and PyTorch (CUDA 12.6):
```bash
pip install -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cu126
```

### 3. Install/Update NN Dataset

This installs the core dataset and logic required to fetch/train models. Warning: This clears the local `db` folder.
```bash
rm -rf db
pip install --no-cache-dir git+https://github.com/ABrain-One/nn-dataset --upgrade --force --extra-index-url https://download.pytorch.org/whl/cu126
```

### 4. Install Android Studio (Linux)

If you need a fresh Android Studio installation:
```bash
chmod +x install-android-studio.sh
./install-android-studio.sh
```

---

## Usage Pipeline

The main entry point is `port.py`. It handles:
1.  **Fetching/Training**: Gets the model from `nn-dataset`.
2.  **Validation**: Checks VR compatibility (Size, Ops).
3.  **Import**: Copies model to Unity project (`unity_nn`).
4.  **Build**: Auto-builds APK if missing.
5.  **Deploy & Run**: Pushes to connected Android/VR device and runs inference.

**Single Model Run:**
```bash
python port.py AirNet
```

**Batch Run (All Supported Models):**
```bash
python port_all.py
```

## Project Structure

- `port.py`: Main orchestration script.
- `unity_nn/`: The Unity project (VR App).
- `vr_processor.py`: Handles ADB communication and stats collection.
- `build_and_deploy.py`: Handles Unity command-line building.
