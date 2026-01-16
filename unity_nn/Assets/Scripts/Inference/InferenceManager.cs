using System.IO;
using UnityEngine;

public class InferenceManager : MonoBehaviour
{
    void Start()
    {
        RunOnce();
    }

    void RunOnce()
    {
        string configPath =
            Path.Combine(Application.persistentDataPath, "run_config.json");

        if (!File.Exists(configPath))
        {
            Debug.LogError("Run config not found");
            Debug.Log($"persistentDataPath = {Application.persistentDataPath}");
            return;
        }

        RunConfig config =
            JsonUtility.FromJson<RunConfig>(File.ReadAllText(configPath));

        var model = config.models[0];

        var result = new InferenceResult
        {
            model_name = model.name,
            model_hash = model.hash,
            status = "failed"
        };

        try
        {
            string backendUsed;
            long durationNs = ModelRunner.Run(
                model.path,
                config.backend,
                out backendUsed
            );

            result.backend = backendUsed;
            result.duration_ns = durationNs;
            result.status = "success";
            result.device_analytics = DeviceAnalytics.Collect();
        }
        catch (System.Exception e)
        {
            Debug.LogError(e);
            result.status = "failed";
            result.device_analytics = DeviceAnalytics.Collect();
        }

        string json =
            JsonUtility.ToJson(result, true);

        Directory.CreateDirectory(
            Path.GetDirectoryName(config.output_path));

        File.WriteAllText(config.output_path, json);

        Debug.Log($"Inference done. Output: {config.output_path}");

        Application.Quit();
    }
}
