# Unity Runner - Detailed Insight

This document provides a comprehensive overview of the `unity_runner` project. It is intended to be passed to an AI (like ChatGPT) to provide context on the status, architecture, and current workings of the Unity-based ONNX inference pipeline.

## 1. Project Overview & Architecture
The `unity_runner` is a **Unity 3D project** that utilizes the **Unity.Barracuda** package (a lightweight cross-platform neural network inference library for Unity) to run `.onnx` machine learning models. 

Its primary purpose in the broader project (`nn-vr`) is to act as the **Android/VR inference engine**. The Python backend pushes ONNX models to an Android/VR headset via ADB, triggers the Unity app via Android Intents, and the Unity app runs the model and writes performance metrics (latency, memory usage) to a JSON file which is then pulled back to the host machine.

### Key Working Directories
- **Assets/Scripts/**: Contains all the C# logic for loading models, capturing webcam input, preprocessing data, and running inferences.
- **Assets/NN/Models/** (and `Resources`): Directories where Unity expects to find default or bundled `.onnx` models if they aren't provided dynamically.

---

## 2. Status and Workings of Key Components

### A. The Automated Benchmark Pipeline (`BarracudaRunner.cs`)
**Status**: Core functioning bridge for automated benchmarking.
- **How it works**: 
  - Waits 3 seconds on startup.
  - Tries to read Android Intent extras (`model_name` and `model_hash`) sent via ADB.
  - Attempts to load the ONNX model from the Android shared storage: `/sdcard/nn_models/{model_name}.onnx`.
  - If it fails, falls back to loading a model bundled in Unity's `Resources` folder.
  - Instantiates a Barracuda `IWorker` using the `CSharpBurst` backend (CPU-optimized).
  - Creates a dummy tensor of shape `(1, 224, 224, 3)`.
  - Executes the model and measures inference latency using a `Stopwatch`.
  - Serializes the results (latency, memory, model name, hash, status) into JSON and saves it to `/sdcard/nn_results/output.json`.

### B. UI/Webcam Testing Scripts (`CamClassifier.cs` & `ImageClassifier.cs`)
**Status**: Developer tools / UI modes for testing models directly on images or webcam feeds.
- **`CamClassifier.cs`**: 
  - Allows uploading a static image (via a file picker in Editor or static path) and running inference against two models simultaneously (ResNet and AlexNet).
  - Preprocesses the image (resizing to 224x224, normalizing using ImageNet mean/std).
  - Outputs the top predictions to UI text.
- **`ImageClassifier.cs`**: 
  - Hooks into the device's `WebCamTexture` to stream live camera feeds.
  - On clicking "Run Inference", captures the current frame, preprocesses it, and runs it through an array of assigned ONNX models.
  - Reads `imagenet_classes.txt` from the `StreamingAssets` path to map the output softmax tensor to a human-readable label.

### C. Legacy/Alternative Processing (`Classification.cs`)
**Status**: Likely older or alternative implementation.
- Focuses heavily on grayscale vs RGB preprocessing and uses a Coroutine to run inferences asynchronously. Uses `ComputePrecompiled` (GPU-based) workers instead of `CSharpBurst`.

---

## 3. Which Files to Provide to GPT?

When asking GPT to help you debug, refactor, or add features to this pipeline, you should provide the following files to give it the necessary context:

### **Must-Have Files (The Core Pipeline)**
1. **`Assets/Scripts/BarracudaRunner.cs`**
   - *Why*: This is the heart of the automated benchmarking pipeline. GPT needs this to understand how Unity communicates with the Android filesystem and ADB.
2. **`README.md`** (in `unity_runner`)
   - *Why*: Gives GPT the high-level intent of the folder.

### **Secondary Files (If working on UI, Preprocessing, or WebCam features)**
3. **`Assets/Scripts/ImageClassifier.cs`**
   - *Why*: Shows how the project handles live webcam feeds, ImageNet normalization (mean/std), and label mapping.
4. **`Assets/Scripts/CamClassifier.cs`**
   - *Why*: Shows how the project handles static image loading and multi-model parallel inference.

### **Do NOT Provide**
- `.meta` files, `.csproj`, or `.sln` files. These are Unity metadata and Visual Studio project files that will only clutter the context window and eat up tokens without providing logical value.
