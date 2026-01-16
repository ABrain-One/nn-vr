using UnityEngine;
using Unity.Barracuda;
using System.IO;

public static class ModelRunner
{
    public static long Run(
        string modelPath,
        string backend,
        out string backendUsed
    )
    {
        backendUsed = backend;

        Debug.Log($"[ModelRunner] Loading model from: {modelPath}");
        Debug.Log($"[ModelRunner] File exists: {File.Exists(modelPath)}");

        byte[] modelData = File.ReadAllBytes(modelPath);
        Debug.Log($"[ModelRunner] Model bytes length: {modelData.Length}");

        var model = ModelLoader.Load(modelData);
        Debug.Log("[ModelRunner] Model loaded successfully");

        WorkerFactory.Type workerType =
            backend == "gpu"
                ? WorkerFactory.Type.Compute
                : WorkerFactory.Type.CSharp;

        IWorker worker;

        try
        {
            worker = WorkerFactory.CreateWorker(workerType, model);
            Debug.Log($"[ModelRunner] Worker created with backend: {workerType}");
        }
        catch (System.Exception e)
        {
            Debug.LogWarning($"[ModelRunner] GPU worker failed, falling back to CPU. Error: {e}");
            worker = WorkerFactory.CreateWorker(WorkerFactory.Type.CSharp, model);
            backendUsed = "cpu_fallback";
        }

        using var input = new Tensor(1, 224, 224, 3);

        var sw = System.Diagnostics.Stopwatch.StartNew();
        worker.Execute(input);
        sw.Stop();

        worker.Dispose();
        Resources.UnloadUnusedAssets();
        System.GC.Collect();

        long durationNs =
            sw.ElapsedTicks * (1_000_000_000L / System.Diagnostics.Stopwatch.Frequency);

        Debug.Log($"[ModelRunner] Inference finished in {durationNs} ns");

        return durationNs;
    }
}
