using System;
using System.Diagnostics;
using System.IO;
using UnityEngine;
using Unity.Barracuda;

public class BenchmarkRunner : MonoBehaviour
{
    // Assign this in the Unity Inspector
    public NNModel modelAsset;

    [Serializable]
    public class TimingStats
    {
        public double avg_ms;
        public double min_ms;
        public double max_ms;
        public double std_dev_ms;
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

        public string gpu_name;

        public string gpu_api;

        public string backend_cpu;

        public string backend_gpu;
    }

    void Start()
    {
        RunBenchmark();
    }

    void RunBenchmark()
    {
        BenchmarkResult result = new BenchmarkResult();
        result.model_name = modelAsset.name;

        try
        {
            // --------------------------------------------------
            // VALIDATE MODEL ASSET
            // --------------------------------------------------

            if (modelAsset == null)
            {
                throw new Exception(
                    "No NNModel assigned in Inspector."
                );
            }

            UnityEngine.Debug.Log(
                $"Loading model asset: {modelAsset.name}"
            );

            // --------------------------------------------------
            // LOAD MODEL
            // --------------------------------------------------

            Model model = ModelLoader.Load(modelAsset);

        // --------------------------------------------------
        // CREATE INPUT TENSOR
        // --------------------------------------------------

        // Barracuda tensor layout:
        // Tensor(batch, height, width, channels)

        Tensor inputTensor = new Tensor(
            1,
            32,
            32,
            3
        );

        // Deterministic values

        for (int i = 0; i < inputTensor.length; i++)
        {
            inputTensor[i] = 1.0f;
        }

        // --------------------------------------------------
        // EXTRACT INPUT SHAPE
        // --------------------------------------------------

        // result.input_shape = new int[]
        // {
        //     1,
        //     3,
        //     32,
        //     32
        // };

        int[] rawShape = model.inputs[0].shape;

        int len = rawShape.Length;

        result.input_shape = new int[]
        {
            rawShape[len - 4],
            rawShape[len - 3],
            rawShape[len - 2],
            rawShape[len - 1]
        };

        // --------------------------------------------------
        // BENCHMARK CPU
        // --------------------------------------------------

        try
        {
            result.cpu = BenchmarkBackend(
                WorkerFactory.Type.CSharpBurst,
                model,
                inputTensor
            );

            result.backend_cpu = "CSharpBurst";
        }
        catch (Exception e)
        {
            UnityEngine.Debug.LogError(
                $"CPU benchmark failed: {e}"
            );
        }

        // --------------------------------------------------
        // BENCHMARK GPU
        // --------------------------------------------------

        try
        {
            result.gpu = BenchmarkBackend(
                WorkerFactory.Type.ComputePrecompiled,
                model,
                inputTensor
            );

            result.backend_gpu = "ComputePrecompiled";
        }
        catch (Exception e)
        {
            UnityEngine.Debug.LogError(
                $"GPU benchmark failed: {e}"
            );
        }

        // --------------------------------------------------
        // GPU INFO
        // --------------------------------------------------

        result.gpu_name =
            SystemInfo.graphicsDeviceName;

        result.gpu_api =
            SystemInfo.graphicsDeviceType.ToString();

        // --------------------------------------------------
        // GET OUTPUT SHAPE
        // --------------------------------------------------

        // Use lightweight worker only for shape extraction

        IWorker shapeWorker =
            WorkerFactory.CreateWorker(
                WorkerFactory.Type.CSharpBurst,
                model
            );

        shapeWorker.Execute(inputTensor);

        Tensor output =
            shapeWorker.PeekOutput();

        result.output_shape = new int[]
        {
            output.shape.batch,
            output.shape.height,
            output.shape.width,
            output.shape.channels
        };

        output.Dispose();

        shapeWorker.Dispose();

        // --------------------------------------------------
        // FINAL RESULT
        // --------------------------------------------------

        // result.model_name = modelAsset.name;

        result.success = true;

        result.error = "";

        // Cleanup

        inputTensor.Dispose();
        }
        catch (Exception e)
        {
            result.success = false;
            result.error = e.ToString();

            UnityEngine.Debug.LogError(e);
        }

        SaveResult(result);
    }

    void SaveResult(BenchmarkResult result)
    {
        try
        {
            string json = JsonUtility.ToJson(result, true);

            string resultsDir = Path.Combine(
                Application.dataPath,
                "Results"
            );

            Directory.CreateDirectory(resultsDir);

            string outputPath = Path.Combine(
                resultsDir,
                $"{result.model_name}_results.json"
            );

            File.WriteAllText(outputPath, json);

            UnityEngine.Debug.Log(
                $"Saved results to: {outputPath}"
            );
        }
        catch (Exception e)
        {
            UnityEngine.Debug.LogError(
                $"Failed to save JSON: {e}"
            );
        }
    }

    TimingStats BenchmarkBackend(
        WorkerFactory.Type backendType,
        Model model,
        Tensor inputTensor,
        int warmupRuns = 5,
        int measuredRuns = 20
    )
    {
        IWorker worker = WorkerFactory.CreateWorker(
            backendType,
            model
        );

        // ----------------------------------------
        // WARMUP
        // ----------------------------------------

        for (int i = 0; i < warmupRuns; i++)
        {
            worker.Execute(inputTensor);

            Tensor warmupOutput =
                worker.PeekOutput();

            warmupOutput.Dispose();
        }

        // ----------------------------------------
        // MEASURED RUNS
        // ----------------------------------------

        double[] timings = new double[measuredRuns];

        for (int i = 0; i < measuredRuns; i++)
        {
            Stopwatch sw = new Stopwatch();

            sw.Start();

            worker.Execute(inputTensor);

            Tensor output = worker.PeekOutput();

            sw.Stop();

            timings[i] = sw.Elapsed.TotalMilliseconds;

            output.Dispose();
        }

        worker.Dispose();

        // ----------------------------------------
        // COMPUTE STATS
        // ----------------------------------------

        double sum = 0.0;

        double min = double.MaxValue;

        double max = double.MinValue;

        for (int i = 0; i < timings.Length; i++)
        {
            double t = timings[i];

            sum += t;

            if (t < min)
                min = t;

            if (t > max)
                max = t;
        }

        double avg = sum / timings.Length;

        double variance = 0.0;

        for (int i = 0; i < timings.Length; i++)
        {
            variance += Math.Pow(
                timings[i] - avg,
                2
            );
        }

        variance /= timings.Length;

        double stdDev = Math.Sqrt(variance);

        return new TimingStats
        {
            avg_ms = avg,
            min_ms = min,
            max_ms = max,
            std_dev_ms = stdDev
        };
    }
}