using System;
using UnityEngine;
using Unity.Barracuda;

public static class ModelRunner
{
    public static long Run(
        string modelPath,
        string backend,
        out string backendUsed
    )
    {
        backendUsed = backend;
        // var model = ModelLoader.Load(modelPath);
        byte[] modelData = System.IO.File.ReadAllBytes(modelPath);
        var model = ModelLoader.Load(modelData);

        WorkerFactory.Type workerType =
            backend == "gpu"
            ? WorkerFactory.Type.Compute
            : WorkerFactory.Type.CSharp;

        IWorker worker;

        try
        {
            worker = WorkerFactory.CreateWorker(workerType, model);
        }
        catch
        {
            worker = WorkerFactory.CreateWorker(WorkerFactory.Type.CSharp, model);
            backendUsed = "cpu_fallback";
        }

        // Dummy input – shape can be refined later
        using var input = new Tensor(1, 224, 224, 3);

        var sw = System.Diagnostics.Stopwatch.StartNew();
        worker.Execute(input);
        sw.Stop();

        worker.Dispose();
        Resources.UnloadUnusedAssets();
        GC.Collect();

        long durationNs =
            sw.ElapsedTicks * (1_000_000_000L / System.Diagnostics.Stopwatch.Frequency);

        return durationNs;
    }
}
