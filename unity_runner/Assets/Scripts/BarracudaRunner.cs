using System.Collections;
using System.IO;
using System.Diagnostics;
using UnityEngine;
using Unity.Barracuda;

/// <summary>
/// Loads ONNX from shared storage, runs one inference, writes /sdcard/nn_results/output.json
/// and logs "DONE {modelName}" for the host pipeline.
/// </summary>
public class BarracudaRunner : MonoBehaviour
{
    public NNModel modelAsset;
    public string modelName = "AirNet";
    public int inputWidth = 224;
    public int inputHeight = 224;
    public int inputChannels = 3;

    private const string RemoteModelDir = "/sdcard/nn_models";
    private const string RemoteResultsPath = "/sdcard/nn_results/output.json";

    public string modelHash = "";

    private Model m_RuntimeModel;
    private IWorker m_Worker;

    IEnumerator Start()
    {
        yield return new WaitForSeconds(3.0f);

        string externalModelName = GetModelNameFromIntent();
        string externalModelHash = GetModelHashFromIntent();

        if (!string.IsNullOrEmpty(externalModelHash))
            modelHash = externalModelHash;

        if (!string.IsNullOrEmpty(externalModelName))
        {
            modelName = externalModelName;
            string path = Path.Combine(RemoteModelDir, modelName + ".onnx");
            if (File.Exists(path))
            {
                UnityEngine.Debug.Log($"Loading model from path: {path}");
                m_RuntimeModel = ModelLoader.Load(path);
            }
            else
            {
                UnityEngine.Debug.LogError($"Model file not found at: {path}");
            }
        }

        if (m_RuntimeModel == null && modelAsset == null)
        {
            modelAsset = Resources.Load<NNModel>(modelName);
            if (modelAsset != null)
                UnityEngine.Debug.Log($"Auto-loaded model '{modelName}' from Resources.");
        }

        if (m_RuntimeModel != null || modelAsset != null)
            RunInference();
        else
            UnityEngine.Debug.LogError(
                $"Could not find model '{modelName}'. Expected under {RemoteModelDir} or Resources.");
    }

    string GetModelNameFromIntent()
    {
#if UNITY_ANDROID && !UNITY_EDITOR
        try
        {
            AndroidJavaClass UnityPlayer = new AndroidJavaClass("com.unity3d.player.UnityPlayer");
            AndroidJavaObject currentActivity = UnityPlayer.GetStatic<AndroidJavaObject>("currentActivity");
            AndroidJavaObject intent = currentActivity.Call<AndroidJavaObject>("getIntent");
            if (intent.Call<bool>("hasExtra", "model_name"))
                return intent.Call<string>("getStringExtra", "model_name");
        }
        catch (System.Exception e)
        {
            UnityEngine.Debug.LogWarning("Failed to get intent extra: " + e.Message);
        }
#endif
        return null;
    }

    string GetModelHashFromIntent()
    {
#if UNITY_ANDROID && !UNITY_EDITOR
        try
        {
            AndroidJavaClass UnityPlayer = new AndroidJavaClass("com.unity3d.player.UnityPlayer");
            AndroidJavaObject currentActivity = UnityPlayer.GetStatic<AndroidJavaObject>("currentActivity");
            AndroidJavaObject intent = currentActivity.Call<AndroidJavaObject>("getIntent");
            if (intent.Call<bool>("hasExtra", "model_hash"))
                return intent.Call<string>("getStringExtra", "model_hash");
        }
        catch (System.Exception e)
        {
            UnityEngine.Debug.LogWarning("Failed to get hash extra: " + e.Message);
        }
#endif
        return null;
    }

    void RunInference()
    {
        UnityEngine.Debug.Log($"Starting inference for {modelName}...");

        if (m_RuntimeModel == null)
            m_RuntimeModel = ModelLoader.Load(modelAsset);

        m_Worker = WorkerFactory.CreateWorker(WorkerFactory.Type.CSharpBurst, m_RuntimeModel);

        var input = new Tensor(1, inputHeight, inputWidth, inputChannels);

        var stopwatch = new Stopwatch();
        stopwatch.Start();

        m_Worker.Execute(input);
        Tensor output = m_Worker.PeekOutput();
        output.ToReadOnlyArray();

        stopwatch.Stop();
        float latencyMs = (float)stopwatch.Elapsed.TotalMilliseconds;

        input.Dispose();
        output.Dispose();
        m_Worker.Dispose();

        SaveResults(latencyMs);
    }

    void SaveResults(float latencyMs)
    {
        int memMb = SystemInfo.systemMemorySize;

        var payload = new BenchJson
        {
            latency_ms = latencyMs,
            memory_mb = memMb,
            model_name = modelName,
            model_hash = modelHash,
            status = "success"
        };

        string json = JsonUtility.ToJson(payload, true);
        string dir = Path.GetDirectoryName(RemoteResultsPath);
        if (!string.IsNullOrEmpty(dir) && !Directory.Exists(dir))
            Directory.CreateDirectory(dir);

        File.WriteAllText(RemoteResultsPath, json);
        UnityEngine.Debug.Log($"Benchmark JSON saved to: {RemoteResultsPath}");
        UnityEngine.Debug.Log($"DONE {modelName}");
    }

    [System.Serializable]
    public class BenchJson
    {
        public float latency_ms;
        public int memory_mb;
        public string model_name;
        public string model_hash;
        public string status;
    }
}
