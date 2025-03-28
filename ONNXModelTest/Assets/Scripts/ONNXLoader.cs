using UnityEngine;
using Unity.Barracuda;

public class ONNXLoader : MonoBehaviour
{
    public NNModel modelAsset;

    void Start()
    {
        if (modelAsset == null)
        {
            Debug.LogError("No ONNX model assigned!");
            return;
        }

        try
        {
            var runtimeModel = ModelLoader.Load(modelAsset);
            var worker = WorkerFactory.CreateWorker(WorkerFactory.Type.Auto, runtimeModel);
            Debug.Log("Model loaded and worker created successfully.");
            worker.Dispose();
        }
        catch (System.Exception ex)
        {
            Debug.LogError("Failed to load ONNX model: " + ex.Message);
        }
    }
}
