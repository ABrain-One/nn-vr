using UnityEngine;
using Unity.Barracuda;
using System.Collections.Generic;
using System.Linq;
using System.Collections;
using UnityEngine.UI;
using System;

public class Classification : MonoBehaviour {

	const int IMAGE_SIZE = 224;
	const string INPUT_NAME = "images";
	const string OUTPUT_NAME = "Softmax";

	[Header("Model Stuff")]
	public NNModel modelFile;
	public TextAsset labelAsset;

	[Header("Scene Stuff")]
	public CameraView CameraView;
	public Preprocess preprocess;
	public Text uiText;

	string[] labels;
	IWorker worker;

	void Start() {
        var model = ModelLoader.Load(modelFile);
        worker = WorkerFactory.CreateWorker(WorkerFactory.Type.ComputePrecompiled, model);
        LoadLabels();
	}

	void LoadLabels() {
		//get only items in quotes
		var stringArray = labelAsset.text.Split('"').Where((item, index) => index % 2 != 0);
		//get every other item
		labels = stringArray.Where((x, i) => i % 2 != 0).ToArray();
	}

	void Update() {

		WebCamTexture webCamTexture = CameraView.GetCamImage();

		if (webCamTexture.didUpdateThisFrame && webCamTexture.width > 100) {
			preprocess.ScaleAndCropImage(webCamTexture, IMAGE_SIZE, RunModel);
		}
	}

	void RunModel(byte[] pixels) {
		StartCoroutine(RunModelRoutine(pixels));
	}

	IEnumerator RunModelRoutine(byte[] pixels) {

		Tensor tensor = TransformInput(pixels);

		var inputs = new Dictionary<string, Tensor> {
			{ INPUT_NAME, tensor }
		};

		worker.Execute(inputs);
		Tensor outputTensor = worker.PeekOutput(OUTPUT_NAME);

		//get largest output
		List<float> temp = outputTensor.ToReadOnlyArray().ToList();
		float max = temp.Max();
		int index = temp.IndexOf(max);

        //set UI text
        uiText.text = labels[index];

        //dispose tensors
        tensor.Dispose();
		outputTensor.Dispose();
		yield return null;
	}

	//transform from 0-255 to -1 to 1
	Tensor TransformInput(byte[] pixels){
		float[] transformedPixels = new float[pixels.Length];

		for (int i = 0; i < pixels.Length; i++){
			transformedPixels[i] = (pixels[i] - 127f) / 128f;
		}
		return new Tensor(1, IMAGE_SIZE, IMAGE_SIZE, 3, transformedPixels);
	}
}
/*using UnityEngine;
using Unity.Barracuda;
using System.Collections.Generic;
using System.Linq;
using System.Collections;
using UnityEngine.UI;

public class Classification : MonoBehaviour {
    const int IMAGE_SIZE = 224;
    const string INPUT_NAME = "input";
    const string OUTPUT_NAME = "output";

    [Header("Model Settings")]
    public NNModel modelFile;
    public TextAsset labelAsset;

    [Header("Scene References")]
    public CameraView CameraView;
    public Preprocess preprocess;
    public Text uiText;

    string[] labels;
    IWorker worker;

    void Start() {
        var model = ModelLoader.Load(modelFile);
        worker = WorkerFactory.CreateWorker(WorkerFactory.Type.ComputePrecompiled, model);
        LoadLabels();
    }

    void LoadLabels() {
        if (labelAsset == null) {
            Debug.LogError("No label file provided!");
            return;
        }

        labels = labelAsset.text.Split('\n').Select(line => line.Trim()).ToArray();
    }

    void Update() {
        WebCamTexture webCamTexture = CameraView.GetCamImage();

        if (webCamTexture.didUpdateThisFrame && webCamTexture.width > 100) {
            bool isGrayscale = modelFile.name.ToLower().Contains("emotion");
            preprocess.ScaleAndCropImage(webCamTexture, IMAGE_SIZE, IMAGE_SIZE, isGrayscale, RunModel);
        }
    }

    void RunModel(byte[] pixels) {
        StartCoroutine(RunModelRoutine(pixels));
    }

    IEnumerator RunModelRoutine(byte[] pixels) {
        bool isGrayscale = modelFile.name.ToLower().Contains("emotion");

        using (Tensor tensor = TransformInput(pixels, isGrayscale)) {
            var inputs = new Dictionary<string, Tensor> {
                { INPUT_NAME, tensor }
            };

            worker.Execute(inputs);
            Tensor outputTensor = worker.PeekOutput(OUTPUT_NAME);

            if (outputTensor != null) {
                List<float> temp = outputTensor.ToReadOnlyArray().ToList();
                float max = temp.Max();
                int index = temp.IndexOf(max);
                uiText.text = labels[index];

                outputTensor.Dispose(); // ✅ Dispose the output tensor
            }
        }

        yield return null;
    }

    void OnDestroy() {
        worker?.Dispose(); // ✅ Ensure worker is disposed
    }

    Tensor TransformInput(byte[] pixels, bool grayscale) {
        float[] transformedPixels;

        if (grayscale) {
            transformedPixels = new float[IMAGE_SIZE * IMAGE_SIZE];
            for (int i = 0; i < transformedPixels.Length; i++) {
                transformedPixels[i] = pixels[i] / 255.0f;
            }
            return new Tensor(1, IMAGE_SIZE, IMAGE_SIZE, 1, transformedPixels);
        } else {
            transformedPixels = new float[pixels.Length];
            for (int i = 0; i < pixels.Length; i++) {
                transformedPixels[i] = (pixels[i] - 127f) / 128f;
            }
            return new Tensor(1, IMAGE_SIZE, IMAGE_SIZE, 3, transformedPixels);
        }
    }
}*/