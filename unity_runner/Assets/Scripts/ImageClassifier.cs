
using UnityEngine;
using UnityEngine.UI;
using Unity.Barracuda;
using System.Linq;
using System.Collections.Generic;

public class ImageClassifier : MonoBehaviour
{
    public NNModel[] modelAssets;
    private Model[] runtimeModels;
    private IWorker[] workers;
    private string[] modelNames;

    public Button runInferenceButton;
    public Button restartCameraButton;
    public Text resultText;
    public RawImage displayImage;

    private WebCamTexture webcamTexture;
    private int height = 224;
    private int width = 224;
    private bool isCameraRunning = false;

    void Start()
    {
        // Initialize models
        int modelCount = modelAssets.Length;
        runtimeModels = new Model[modelCount];
        workers = new IWorker[modelCount];
        modelNames = new string[modelCount];

        for (int i = 0; i < modelCount; i++)
        {
            try
            {
                runtimeModels[i] = ModelLoader.Load(modelAssets[i]);
                workers[i] = WorkerFactory.CreateWorker(WorkerFactory.Type.Compute, runtimeModels[i]);
                Debug.Log("Model loaded and worker created successfully.");
                modelNames[i] = modelAssets[i].name;
            }
            catch (System.Exception ex)
            {
                Debug.LogError("Failed to load ONNX model: " + ex.Message);
            }
        }

        StartCamera();

        runInferenceButton.onClick.AddListener(RunInference);
        restartCameraButton.onClick.AddListener(StartCamera);
    }

    void StartCamera()
    {
        if (webcamTexture != null)
        {
            webcamTexture.Stop();
        }

        webcamTexture = new WebCamTexture();
        displayImage.texture = webcamTexture;
        webcamTexture.Play();
        isCameraRunning = true;
        resultText.text = "Camera started. Click 'Run Inference' to capture.";
    }

    void RunInference()
    {
        if (!isCameraRunning)
        {
            resultText.text = "Camera is not running!";
            return;
        }

        Texture2D cameraFrame = GetCameraFrame();
        if (cameraFrame == null) return;

        // Stop the camera after capturing the frame
        webcamTexture.Stop();
        isCameraRunning = false;

        using (Tensor inputTensor = TransformInput(cameraFrame))
        {
            string result = "Top Predictions:\n";

            for (int i = 0; i < workers.Length; i++)
            {
                workers[i].Execute(inputTensor);
                using (Tensor outputTensor = workers[i].PeekOutput())
                {
                    float[] scores = outputTensor.ToReadOnlyArray();
                    int predictedIndex = GetTopPrediction(scores);
                    string label = GetLabel(predictedIndex);
                    float confidence = scores[predictedIndex];

                    result += $"{modelNames[i]}: {label} (Confidence: {confidence:P2})\n";
                }
            }

            resultText.text = result;
        }
    }

    Texture2D GetCameraFrame()
    {
        Texture2D texture = new Texture2D(webcamTexture.width, webcamTexture.height);
        texture.SetPixels(webcamTexture.GetPixels());
        texture.Apply();
        return ResizeTexture(texture, width, height);
    }

    Tensor TransformInput(Texture2D texture)
    {
        Color32[] pixels = texture.GetPixels32();
        float[] inputData = new float[3 * width * height];

        float[] mean = { 0.485f, 0.456f, 0.406f };
        float[] std = { 0.229f, 0.224f, 0.225f };

        for (int i = 0; i < pixels.Length; i++)
        {
            int x = i % width;
            int y = i / width;

            inputData[y * width + x] = (pixels[i].r / 255.0f - mean[0]) / std[0];  
            inputData[width * height + y * width + x] = (pixels[i].g / 255.0f - mean[1]) / std[1];
            inputData[2 * width * height + y * width + x] = (pixels[i].b / 255.0f - mean[2]) / std[2];
        }

        return new Tensor(1, width, height, 3, inputData);
    }

    int GetTopPrediction(float[] scores)
    {
        return scores.ToList().IndexOf(scores.Max());
    }

    string GetLabel(int index)
    {
        string labelsPath = System.IO.Path.Combine(Application.streamingAssetsPath, "imagenet_classes.txt");
        if (!System.IO.File.Exists(labelsPath))
        {
            Debug.LogError("Labels file not found.");
            return "Unknown";
        }

        string[] labels = System.IO.File.ReadAllLines(labelsPath);
        return labels.Length > index ? labels[index] : "Unknown";
    }

    void OnDestroy()
    {
        foreach (var worker in workers)
        {
            worker?.Dispose();
        }

        if (webcamTexture != null)
        {
            webcamTexture.Stop();
        }
    }

    Texture2D ResizeTexture(Texture2D source, int width, int height)
    {
        RenderTexture rt = new RenderTexture(width, height, 24);
        RenderTexture.active = rt;
        Graphics.Blit(source, rt);
        Texture2D result = new Texture2D(width, height);
        result.ReadPixels(new Rect(0, 0, width, height), 0, 0);
        result.Apply();
        return result;
    }
}