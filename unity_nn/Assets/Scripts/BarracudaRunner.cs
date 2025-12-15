using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Unity.Barracuda;
using System.IO;
using System.Diagnostics;
using System.Linq;

public class BarracudaRunner : MonoBehaviour
{
    public NNModel modelAsset;
    public string modelName = "AirNet"; // Default, can be overwritten or loaded dynamically
    public int inputWidth = 224;
    public int inputHeight = 224;
    public int inputChannels = 3;

    private Model m_RuntimeModel;
    private IWorker m_Worker;

    public string modelHash = "";

    IEnumerator Start()
    {
        yield return new WaitForSeconds(3.0f);

        string externalModelName = GetModelNameFromIntent();
        string externalModelHash = GetModelHashFromIntent();
        
        if (!string.IsNullOrEmpty(externalModelHash))
        {
            modelHash = externalModelHash;
        }

        if (!string.IsNullOrEmpty(externalModelName))
        if (!string.IsNullOrEmpty(externalModelName))
        {
            modelName = externalModelName;
            string path = Path.Combine(Application.persistentDataPath, modelName + ".onnx");
            if (File.Exists(path))
            {
                UnityEngine.Debug.Log($"Loading model from path: {path}");
                // Load directly from file
                // Note: ModelLoader.Load can take a file path or byte array
                m_RuntimeModel = ModelLoader.Load(path);
            }
            else
            {
                UnityEngine.Debug.LogError($"Model file not found at: {path}");
            }
        }

        if (m_RuntimeModel == null && modelAsset == null)
        {
            // Try to load from Resources (requires model to be in Assets/Resources folder)
            modelAsset = Resources.Load<NNModel>(modelName);
            
            if (modelAsset != null)
            {
                UnityEngine.Debug.Log($"Auto-loaded model '{modelName}' from Resources.");
            }
        }

        if (m_RuntimeModel != null || modelAsset != null)
        {
            RunInference();
        }
        else
        {
            UnityEngine.Debug.LogError($"Could not find model '{modelName}'. Make sure it is in persistent data path, Resources folder, or assigned in the Inspector.");
        }
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
            {
                return intent.Call<string>("getStringExtra", "model_name");
            }
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
            {
                return intent.Call<string>("getStringExtra", "model_hash");
            }
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
        // Mocking inference to verify pipeline stability on Emulator
        UnityEngine.Debug.Log($"Starting Mock Inference for {modelName}...");

        if (m_RuntimeModel == null)
        {
            m_RuntimeModel = ModelLoader.Load(modelAsset);
        }
        
        // Use CPU worker to avoid Emulator GPU crashes
        m_Worker = WorkerFactory.CreateWorker(WorkerFactory.Type.CSharpBurst, m_RuntimeModel);

        // Create dummy input
        Tensor input = new Tensor(1, inputHeight, inputWidth, inputChannels);
        
        Stopwatch stopwatch = new Stopwatch();
        stopwatch.Start();

        m_Worker.Execute(input);
        Tensor output = m_Worker.PeekOutput();
        
        // Force execution to complete for timing
        output.ToReadOnlyArray();

        stopwatch.Stop();
        long durationNs = stopwatch.ElapsedTicks * (1000000000L / Stopwatch.Frequency);
        
        input.Dispose();
        output.Dispose();
        m_Worker.Dispose();

        // Mock delay
        UnityEngine.Debug.Log($"Inference finished. Duration: {durationNs} ns");

        SaveStats(durationNs);
    }

    void SaveStats(long durationNs)
    {
        StatsData data = new StatsData();
        data.model_name = modelName;
        data.model_hash = modelHash;
        data.duration_ns = durationNs;
        data.status = "success";
        
        // Mock device analytics
        data.device_analytics = new DeviceAnalytics();
        data.device_analytics.timestamp = (double)System.DateTime.UtcNow.Subtract(new System.DateTime(1970, 1, 1)).TotalSeconds;
        data.device_analytics.memory_info = new MemoryInfo();
        data.device_analytics.memory_info.total_ram_kb = SystemInfo.systemMemorySize * 1024 + " kB";
        data.device_analytics.cpu_info = new CpuInfo();
        data.device_analytics.cpu_info.raw = SystemInfo.processorType;

        string json = JsonUtility.ToJson(data, true);
        // Use persistentDataPath for Android compatibility
        string fileName = modelName + "_stats.json";
        string path = Path.Combine(Application.persistentDataPath, fileName);
        
        // Ensure directory exists (persistentDataPath always exists, but good practice)
        string dir = Path.GetDirectoryName(path);
        if (!Directory.Exists(dir))
        {
            Directory.CreateDirectory(dir);
        }

        File.WriteAllText(path, json);
        UnityEngine.Debug.Log($"Stats saved to: {path}");
        UnityEngine.Debug.Log($"DONE {modelName}");
    }

    [System.Serializable]
    public class StatsData
    {
        public string model_name;
        public string model_hash;
        public long duration_ns;
        public string status;
        public DeviceAnalytics device_analytics;
    }

    [System.Serializable]
    public class DeviceAnalytics
    {
        public double timestamp;
        public MemoryInfo memory_info;
        public CpuInfo cpu_info;
    }

    [System.Serializable]
    public class MemoryInfo
    {
        public string total_ram_kb;
        public string free_ram_kb = "N/A"; // Not easily available in generic Unity API
    }

    [System.Serializable]
    public class CpuInfo
    {
        public string raw;
    }
}
