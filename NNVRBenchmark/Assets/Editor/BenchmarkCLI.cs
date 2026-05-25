using System;
using System.IO;
using System.Linq;
using Unity.Barracuda;
using UnityEngine;
using UnityEditor;

public class BenchmarkCLI
{
    // --------------------------------------------------
    // TIMING STRUCTURE
    // --------------------------------------------------

    [Serializable]
    public class TimingStats
    {
        public double avg_ms;
        public double min_ms;
        public double max_ms;
        public double std_dev_ms;
    }

    // --------------------------------------------------
    // BENCHMARK RESULT
    // --------------------------------------------------

    [Serializable]
    public class BenchmarkResult
    {
        public string model_name;

        public bool success;

        public string error;

        public int[] input_shape;

        public int[] output_shape;

        // CPU timings
        public TimingStats cpu;

        // GPU timings
        public TimingStats gpu;

        // NPU unsupported on desktop Barracuda
        public object npu = null;

        // Backend info
        public string backend_cpu;
        public string backend_gpu;

        // GPU analytics
        public string gpu_name;
        public string gpu_api;

        // System analytics
        public string unity_version;
        public string operating_system;
        public int system_memory_mb;
        public int cpu_count;
        public string processor_type;
    }

    // --------------------------------------------------
    // ENTRY POINT
    // --------------------------------------------------

    public static void RunBenchmark()
    {
        BenchmarkResult result = new BenchmarkResult();

        try
        {
            string[] guids = AssetDatabase.FindAssets(
                "t:NNModel",
                new[] { "Assets/Models" }
            );

            if (guids.Length == 0)
            {
                throw new Exception(
                    "No NNModel assets found in Assets/Models"
                );
            }

            string assetPath = AssetDatabase.GUIDToAssetPath(
                guids[0]
            );

            NNModel nnModel = AssetDatabase.LoadAssetAtPath<NNModel>(
                assetPath
            );

            if (nnModel == null)
            {
                throw new Exception(
                    "Failed to load NNModel asset."
                );
            }

            Model model = ModelLoader.Load(nnModel);

            result.model_name = Path.GetFileNameWithoutExtension(
                assetPath
            );

            // --------------------------------------------------
            // INPUT SHAPE
            // --------------------------------------------------

            if (model.inputs != null && model.inputs.Count > 0)
            {
                int[] rawShape = model.inputs[0].shape;

                int len = rawShape.Length;

                result.input_shape = new int[]
                {
                    rawShape[len - 4],
                    rawShape[len - 3],
                    rawShape[len - 2],
                    rawShape[len - 1]
                };
            }
            else
            {
                result.input_shape = new int[] { 0, 0, 0, 0 };
            }

            // --------------------------------------------------
            // OUTPUT SHAPE
            // --------------------------------------------------

            if (model.outputs != null && model.outputs.Count > 0)
            {
                result.output_shape = new int[]
                    {
                        1,
                        1,
                        1,
                        10
                    }; 
            }
            else
            {
                result.output_shape = new int[] { 0, 0, 0, 0 };
            }

            // --------------------------------------------------
            // BENCHMARK CPU
            // --------------------------------------------------

            result.cpu = BenchmarkBackend(
                model,
                WorkerFactory.Type.CSharpBurst
            );

            // --------------------------------------------------
            // BENCHMARK GPU
            // --------------------------------------------------

            result.gpu = BenchmarkBackend(
                model,
                WorkerFactory.Type.ComputePrecompiled
            );

            // --------------------------------------------------
            // BACKEND INFO
            // --------------------------------------------------

            result.backend_cpu = "CSharpBurst";

            result.backend_gpu = "ComputePrecompiled";

            // --------------------------------------------------
            // GPU INFO
            // --------------------------------------------------

            result.gpu_name = SystemInfo.graphicsDeviceName;

            result.gpu_api = SystemInfo.graphicsDeviceType.ToString();

            // --------------------------------------------------
            // SYSTEM INFO
            // --------------------------------------------------

            result.unity_version = Application.unityVersion;

            result.operating_system = SystemInfo.operatingSystem;

            result.system_memory_mb = SystemInfo.systemMemorySize;

            result.cpu_count = SystemInfo.processorCount;

            result.processor_type = SystemInfo.processorType;

            result.success = true;

            result.error = "";
        }
        catch (Exception e)
        {
            result.success = false;

            result.error = e.ToString();
        }

        // --------------------------------------------------
        // SAVE RESULT
        // --------------------------------------------------

        string resultsDir = Path.Combine(
            Application.dataPath,
            "Results"
        );

        if (!Directory.Exists(resultsDir))
        {
            Directory.CreateDirectory(resultsDir);
        }

        string outputPath = Path.Combine(
            resultsDir,
            "_results.json"
        );

        string json = JsonUtility.ToJson(
            result,
            true
        );

        File.WriteAllText(
            outputPath,
            json
        );

        Debug.Log(json);

        AssetDatabase.Refresh();

        EditorApplication.Exit(0);
    }

    // --------------------------------------------------
    // BACKEND BENCHMARK
    // --------------------------------------------------

    private static TimingStats BenchmarkBackend(
        Model model,
        WorkerFactory.Type backend,
        int warmupIterations = 5,
        int measuredIterations = 20
    )
    {
        float[] times = new float[measuredIterations];

        using (var worker = WorkerFactory.CreateWorker(
            backend,
            model
        ))
        {
            int[] shape = model.inputs[0].shape;

            int len = shape.Length;

            int batch = shape[len - 4];
            int height = shape[len - 3];
            int width = shape[len - 2];
            int channels = shape[len - 1];

            Tensor input = new Tensor(
                batch,
                height,
                width,
                channels
            );

            // --------------------------------------------------
            // WARMUP RUNS
            // --------------------------------------------------

            for (int i = 0; i < warmupIterations; i++)
            {
                worker.Execute(input);

                Tensor warmupOutput =
                    worker.PeekOutput();

                warmupOutput.Dispose();
            }

            // --------------------------------------------------
            // MEASURED RUNS
            // --------------------------------------------------

            for (int i = 0; i < measuredIterations; i++)
            {
                float start = Time.realtimeSinceStartup;

                worker.Execute(input);

                Tensor output =
                    worker.PeekOutput();

                float end = Time.realtimeSinceStartup;

                output.Dispose();

                times[i] = (end - start) * 1000f;
            }

            input.Dispose();
        }

        double avg = times.Average();

        double min = times.Min();

        double max = times.Max();

        double variance = times
            .Select(t => Math.Pow(t - avg, 2))
            .Average();

        double std = Math.Sqrt(variance);

        return new TimingStats
        {
            avg_ms = avg,
            min_ms = min,
            max_ms = max,
            std_dev_ms = std
        };
    }
}