using System;
using System.Diagnostics;
using System.IO;
using System.Linq;
using Unity.InferenceEngine;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;

// Batch-mode entry point for Experiment B. This is deliberately separate from
// Experiment A's Barracuda runner, while preserving its timing semantics.
public static class BenchmarkCLI
{
    private const int WarmupIterations = 5;
    private const int MeasuredIterations = 20;
    private const string InputShapeFilename = "model_input_shape.json";

    [Serializable]
    private class InputShapeConfig
    {
        public int[] shape;
    }

    [Serializable]
    public class TimingStats
    {
        public double avg_ms;
        public double min_ms;
        public double max_ms;
        public double std_dev_ms;
        public double[] samples_ms;
        public int warmup_iterations;
        public int measured_iterations;
        public string completion_operation;
    }

    [Serializable]
    public class BenchmarkResult
    {
        public string model_name;
        public bool success;
        public string error;
        public int[] input_shape;
        public int[] output_shape;
        public TimingStats cpu;
        public TimingStats gpu;
        public object npu = null;
        public string backend_cpu;
        public string backend_gpu;
        public string runtime;
        public string inference_engine_package;
        public string gpu_name;
        public string gpu_api;
        public string unity_version;
        public string operating_system;
        public int system_memory_mb;
        public int cpu_count;
        public string processor_type;
        public string timing_protocol;
        public string output_materialization;
        public string graphics_device_version;
    }

    public static void RunBenchmark()
    {
        var result = new BenchmarkResult();
        try
        {
            AssetDatabase.Refresh();
            var guids = AssetDatabase.FindAssets("t:ModelAsset", new[] { "Assets/Models" });
            if (guids.Length == 0)
                throw new Exception("No ModelAsset assets found in Assets/Models");

            var assetPath = AssetDatabase.GUIDToAssetPath(guids[0]);
            result.model_name = Path.GetFileNameWithoutExtension(assetPath);
            var modelAsset = AssetDatabase.LoadAssetAtPath<ModelAsset>(assetPath);
            if (modelAsset == null)
                throw new Exception("Failed to load ModelAsset.");

            // Retain A's physical RTX 4090 / Vulkan environment rather than
            // silently accepting a Mesa or llvmpipe software fallback.
            if (SystemInfo.graphicsDeviceType != GraphicsDeviceType.Vulkan)
                throw new Exception("Experiment B requires Vulkan; detected " + SystemInfo.graphicsDeviceType + ".");
            var gpuName = SystemInfo.graphicsDeviceName ?? "";
            if (!gpuName.ToLowerInvariant().Contains("nvidia") ||
                !gpuName.Contains("RTX 4090") ||
                gpuName.ToLowerInvariant().Contains("llvmpipe"))
                throw new Exception("Experiment B requires the physical NVIDIA RTX 4090; detected " + gpuName + ".");

            var model = ModelLoader.Load(modelAsset);
            if (model.inputs == null || model.inputs.Count != 1)
                throw new Exception("Experiment B requires exactly one model input.");
            // The frozen A/B ONNX contract declares batch dimension 0 as
            // dynamic. The exporter nevertheless uses a known, fixed input
            // shape for each benchmark (batch=1). Use that exporter-provided
            // concrete shape without changing the ONNX artifact.
            var inputShape = LoadBenchmarkInputShape();
            if (model.inputs[0].shape.isRankDynamic || model.inputs[0].shape.rank != inputShape.rank)
                throw new Exception("ONNX model input rank differs from the exporter-provided benchmark input shape.");
            result.input_shape = ShapeToArray(inputShape);

            int[] cpuOutputShape;
            result.cpu = BenchmarkBackend(model, inputShape, BackendType.CPU, out result.backend_cpu, out cpuOutputShape);
            int[] gpuOutputShape;
            result.gpu = BenchmarkBackend(model, inputShape, BackendType.GPUCompute, out result.backend_gpu, out gpuOutputShape);
            result.output_shape = gpuOutputShape ?? cpuOutputShape;

            result.runtime = "Unity Inference Engine";
            result.inference_engine_package = "com.unity.ai.inference@2.6.1";
            result.gpu_name = gpuName;
            result.gpu_api = SystemInfo.graphicsDeviceType.ToString();
            result.unity_version = Application.unityVersion;
            result.operating_system = SystemInfo.operatingSystem;
            result.system_memory_mb = SystemInfo.systemMemorySize;
            result.cpu_count = SystemInfo.processorCount;
            result.processor_type = SystemInfo.processorType;
            result.timing_protocol = "completion_aware_inference_engine_v1";
            result.output_materialization = "Tensor<float>.DownloadToArray blocking host readback inside every warm-up and timed iteration";
            result.graphics_device_version = SystemInfo.graphicsDeviceVersion;
            result.success = true;
            result.error = "";
        }
        catch (Exception e)
        {
            result.success = false;
            result.error = e.ToString();
        }

        var resultsDir = Path.Combine(Application.dataPath, "Results");
        Directory.CreateDirectory(resultsDir);
        var outputPath = Path.Combine(resultsDir, "_results.json");
        var json = JsonUtility.ToJson(result, true);
        File.WriteAllText(outputPath, json);
        UnityEngine.Debug.Log(json);
        AssetDatabase.Refresh();
        EditorApplication.Exit(0);
    }

    private static TimingStats BenchmarkBackend(
        Model model,
        TensorShape inputShape,
        BackendType backend,
        out string actualBackendName,
        out int[] outputShape)
    {
        actualBackendName = backend.ToString();
        outputShape = null;
        var times = new double[MeasuredIterations];
        using (var worker = new Worker(model, backend))
        using (var input = new Tensor<float>(inputShape, new float[inputShape.length]))
        {
            for (var i = 0; i < WarmupIterations; i++)
                MaterializeOutput(worker, input, ref outputShape);

            for (var i = 0; i < MeasuredIterations; i++)
            {
                var stopwatch = Stopwatch.StartNew();
                MaterializeOutput(worker, input, ref outputShape);
                stopwatch.Stop();
                times[i] = stopwatch.Elapsed.TotalMilliseconds;
            }
        }

        var average = times.Average();
        var variance = times.Select(t => Math.Pow(t - average, 2)).Average();
        return new TimingStats
        {
            avg_ms = average,
            min_ms = times.Min(),
            max_ms = times.Max(),
            std_dev_ms = Math.Sqrt(variance),
            samples_ms = times,
            warmup_iterations = WarmupIterations,
            measured_iterations = MeasuredIterations,
            completion_operation = "Tensor<float>.DownloadToArray()"
        };
    }

    private static TensorShape LoadBenchmarkInputShape()
    {
        var path = Path.Combine(Application.dataPath, "Models", InputShapeFilename);
        if (!File.Exists(path))
            throw new Exception("Missing exporter-provided input shape sidecar: " + path);
        var config = JsonUtility.FromJson<InputShapeConfig>(File.ReadAllText(path));
        if (config == null || config.shape == null || config.shape.Length == 0 || config.shape.Length > TensorShape.maxRank)
            throw new Exception("Invalid exporter-provided input shape sidecar.");
        if (config.shape.Any(dimension => dimension <= 0))
            throw new Exception("Benchmark input shape dimensions must be positive.");
        return new TensorShape(config.shape);
    }

    private static void MaterializeOutput(Worker worker, Tensor<float> input, ref int[] outputShape)
    {
        worker.Schedule(input);
        var output = worker.PeekOutput() as Tensor<float>;
        if (output == null)
            throw new Exception("Expected the model output to be Tensor<float>.");
        outputShape = ShapeToArray(output.shape);
        // This call blocks until the host can read the output. It belongs
        // inside both warm-up and timed iterations to prevent GPU spillover.
        output.DownloadToArray();
    }

    private static int[] ShapeToArray(TensorShape shape)
    {
        var dimensions = new int[shape.rank];
        for (var i = 0; i < shape.rank; i++)
            dimensions[i] = shape[i];
        return dimensions;
    }
}
