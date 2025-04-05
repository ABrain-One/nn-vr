using System.IO;
using UnityEngine;
using UnityEngine.UI;
using Unity.Barracuda;
using System.Linq;

public class CamClassifier : MonoBehaviour
{
    public NNModel resnetModelAsset; // Assign ResNet model in the Inspector
    public NNModel alexnetModelAsset; // Assign AlexNet model in the Inspector
    private Model[] runtimeModels;
    private IWorker[] workers;

    public Button uploadButton;
    public Button runInferenceButton;
    public Text resultText;
    public RawImage displayImage;

    private Texture2D inputTexture;
    
    private int height;
    private int width;

    void Start()
    {
        runtimeModels = new Model[2]; // Size adjustment
        workers = new IWorker[2];

        runtimeModels[0] = ModelLoader.Load(resnetModelAsset);
        runtimeModels[1] = ModelLoader.Load(alexnetModelAsset);

        width = runtimeModels[0].inputs[0].shape[5];
        height = runtimeModels[0].inputs[0].shape[6];
        Debug.Log($"Using width:{width} ");
        Debug.Log($"Using height:{height} ");
        Debug.Log($"Model Input Shape: {string.Join(", ", runtimeModels[0].inputs[0].shape)}");

        for (int i = 0; i < runtimeModels.Length; i++)
        {
            try
            {
                workers[i] = WorkerFactory.CreateWorker(WorkerFactory.Type.Compute, runtimeModels[i]);
                Debug.Log("Model loaded and worker created successfully.");
            }
            catch (System.Exception ex)
            {
                Debug.LogError("Failed to load ONNX model: " + ex.Message);
            }
        }

        uploadButton.onClick.AddListener(OpenFilePicker);
        runInferenceButton.onClick.AddListener(RunInference);
    }

    void OpenFilePicker()
    {
        Debug.Log("Opening file picker...");
        string path = UnityEditor.EditorUtility.OpenFilePanel("Select an image", "", "png,jpg,jpeg");
        if (!string.IsNullOrEmpty(path))
        {
            Debug.Log("Selected file: " + path);
            LoadImage(path);
        }
        else
        {
            Debug.Log("No file selected.");
        }
    }

    void LoadImage(string path)
    {
        byte[] imageBytes = File.ReadAllBytes(path);
        inputTexture = new Texture2D(2, 2);
        bool isLoaded = inputTexture.LoadImage(imageBytes);

        if (isLoaded)
        {
            // Resize the image to 224x224
            inputTexture = ResizeTexture(inputTexture, width, height);

            // Display the image in UI
            displayImage.texture = inputTexture;
            Debug.Log("Image loaded and displayed.");
        }
        else
        {
            Debug.LogError("Failed to load image from path: " + path);
        }
    }

    void RunInference()
    {
        if (inputTexture == null)
        {
            resultText.text = "Please upload an image first!";
            return;
        }

        using (Tensor inputTensor = TransformInput(inputTexture))
        {
            string result = "Top Predictions:\n";

            // Run inference on all models
            for (int i = 0; i < workers.Length; i++)
            {
                workers[i].Execute(inputTensor);
                using (Tensor outputTensor = workers[i].PeekOutput())
                {
                    float[] scores = outputTensor.ToReadOnlyArray();

                    // Get the top prediction for this model
                    int predictedIndex = GetTopPrediction(scores);
                    string label = GetLabel(predictedIndex);
                    float confidence = scores[predictedIndex];

                    result += $"Model {i + 1}: {label} (Confidence: {confidence})\n";
                }
            }

            resultText.text = result;
        }
    }

    Tensor TransformInput(Texture2D texture)
    {
        // Resize the texture to 224x224
        Texture2D resizedTexture = ResizeTexture(texture, 224, 224);

        // Get pixel data
        Color32[] pixels = resizedTexture.GetPixels32();
        float[] inputData = new float[3 * 224 * 224];

        // Normalize pixel values using ImageNet mean and std
        float[] mean = new float[] { 0.485f, 0.456f, 0.406f };
        float[] std = new float[] { 0.229f, 0.224f, 0.225f };

        for (int i = 0; i < pixels.Length; i++)
        {
            int x = i % 224;
            int y = i / 224;

            // Normalize and apply mean/std
            inputData[y * 224 + x] = (pixels[i].r / 255.0f - mean[0]) / std[0];          // Red channel
            inputData[224 * 224 + y * 224 + x] = (pixels[i].g / 255.0f - mean[1]) / std[1];  // Green channel
            inputData[2 * 224 * 224 + y * 224 + x] = (pixels[i].b / 255.0f - mean[2]) / std[2];  // Blue channel
        }

        // Create a tensor with shape (1, 224, 224, 3) for NHWC format
        return new Tensor(1, 224, 224, 3, inputData);
    }

    int GetTopPrediction(float[] scores)
    {
        return scores.ToList().IndexOf(scores.Max());
    }

    string[] GetLabels()
    {
        string labelsPath = Path.Combine(Application.streamingAssetsPath, "imagenet_classes.txt");

        if (!File.Exists(labelsPath))
        {
            Debug.LogError("Labels file not found at: " + labelsPath);
            return new string[0];
        }

        return File.ReadAllLines(labelsPath);
    }

    string GetLabel(int index)
    {
        string[] labels = GetLabels();
        return labels[index];
    }

    void OnDestroy()
    {
        for (int i = 0; i < workers.Length; i++)
        {
            workers[i]?.Dispose();
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
