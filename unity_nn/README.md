# Unity Image Classification Project

## Getting Started

Welcome to the Unity Image Classification project! This project includes three interactive scenes: image classification from uploaded files, live webcam-based classification, and as a future work, scene for object detection.
## Requirments 
- **Unity Editor**: Ensure Unity version 6000.0.40f1 (Silicon, LTS) is installed, If not installed, use Unity Hub to add this version.
- **Platforms**:  install WebGL Build Support and macOS Build Support.
- **Windows**: Install a Windows-compatible LTS version, Open Package Manager and install missing dependencies, Change build target: Go to File → Build Settings → Select Windows Standalone → Switch Platform.

## Features
- **Image Classification**: Upload an image, display it, and run inference using ONNX models.
- **Live Camera Classification**: Capture images from the webcam and classify them in real-time.
- **Logging System**: Displays logs to verify if the ONNX model is running correctly.
- **VR Development**: This prototype has also been tested in a VR environment, and we have confirmed that it functions correctly.
- **Future Development**: Object detection live inference.


## Installation

1. Clone the repository:
   ```sh
   git clone <[repository-url](https://github.com/ABrain-One/nn-vr.git)>
   ```
2. Open the project in Unity (tested with Unity 2021+).
3. Ensure you have the **Barracuda** package installed for ONNX model inference.
4. Place your ONNX models inside the **Assets/NN/Models** folder.
5. Run the project!

## How to Use

### Scene 1: Image Classification
1. Click **Upload Image** to select an image file (PNG, JPG, JPEG).
2. The image will be displayed in the UI and you do not need any manual image preprocessing.
3. Click **Run Inference** to classify the image.
4. Results will be displayed, showing predictions from multiple models.

### Scene 2: Live Camera Classification
1. Ensure your webcam is connected.
2. Click **Start Camera** to begin the live feed.
3. Click **Run Inference** to classify the captured frame.
4. Click **Restart Camera** to reset and capture a new image.

### Scene 3: Object Detection (Future Work)
- This scene is for future project and will allow real-time object detection using ONNX object detection "efficientnet-lite4-11" model .

## Logging System
The system logs model loading status and inference execution:
- **Model Loaded Successfully**: Indicates the ONNX model is working.
- **Inference Running**: Ensures classification is being processed.
- **Errors Logged**: Shows model loading or inference issues.

## Contributing
Feel free to submit issues, feature requests, or pull requests to improve the project!

## Authors
- Mahta Moosavi, Zofia Antonina Bentyn, Arash Torabi Goodarzi

## License
<a href='https://github.com/ABrain-One/nn-vr/blob/main/LICENSE'>MIT license</a> 


