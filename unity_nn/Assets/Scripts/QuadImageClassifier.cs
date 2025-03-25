using UnityEngine;
using UnityEngine.UI;
using Unity.Barracuda;
using System.Linq;
using System.Collections.Generic;

public class QuadImageClassifier : MonoBehaviour
{
    public NNModel[] modelAssets;
    private Model[] runtimeModels;
    private IWorker[] workers;
    private string[] modelNames;

    public Button runInferenceButton;
    public Text resultText;
    public Renderer quadRenderer;  // 🎯 Assign the Quad here!

    private int height = 224;
    private int width = 224;

    void Start()
    {
        // Initialize models
        int modelCount = modelAssets.Length;
        runtimeModels = new Model[modelCount];
        workers = new IWorker[modelCount];
        modelNames = new string[modelCount];

        for (int i = 0; i < modelCount; i++)
        {
            runtimeModels[i] = ModelLoader.Load(modelAssets[i]);
            workers[i] = WorkerFactory.CreateWorker(WorkerFactory.Type.Compute, runtimeModels[i]);
            modelNames[i] = modelAssets[i].name;
        }

        runInferenceButton.onClick.AddListener(RunInference);
    }

    void RunInference()
    {
        if (quadRenderer == null || quadRenderer.material == null || quadRenderer.material.mainTexture == null)
        {
            resultText.text = "Quad texture is missing!";
            return;
        }

        // 🎯 Convert the Quad's Texture to Texture2D
        Texture2D imageTexture = ConvertTextureToTexture2D((Texture)quadRenderer.material.mainTexture);
        if (imageTexture == null)
        {
            resultText.text = "Failed to convert quad texture!";
            return;
        }

        using (Tensor inputTensor = TransformInput(imageTexture))
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

    Texture2D ConvertTextureToTexture2D(Texture sourceTexture)
    {
        RenderTexture renderTex = RenderTexture.GetTemporary(sourceTexture.width, sourceTexture.height, 0, RenderTextureFormat.Default, RenderTextureReadWrite.Linear);
        Graphics.Blit(sourceTexture, renderTex);
        RenderTexture previous = RenderTexture.active;
        RenderTexture.active = renderTex;

        Texture2D readableTexture = new Texture2D(sourceTexture.width, sourceTexture.height);
        readableTexture.ReadPixels(new Rect(0, 0, sourceTexture.width, sourceTexture.height), 0, 0);
        readableTexture.Apply();

        RenderTexture.active = previous;
        RenderTexture.ReleaseTemporary(renderTex);

        return ResizeTexture(readableTexture, width, height);
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
