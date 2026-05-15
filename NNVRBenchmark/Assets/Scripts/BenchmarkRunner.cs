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
    public class BenchmarkResult
    {
        public string model_name;
        public string backend;
        public double inference_time_ms;
        public int[] input_shape;
        public int[] output_shape;
        public bool success;
        public string error;
    }

    void Start()
    {
        RunBenchmark();
    }

    void RunBenchmark()
    {
        BenchmarkResult result = new BenchmarkResult();

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
            // CREATE WORKER
            // --------------------------------------------------

            IWorker worker = WorkerFactory.CreateWorker(
                WorkerFactory.Type.ComputePrecompiled,
                model
            );

            // --------------------------------------------------
            // CREATE INPUT TENSOR
            // CIFAR-10 shape = [1,3,32,32]
            //
            // Barracuda tensor layout:
            // Tensor(batch, height, width, channels)
            // --------------------------------------------------

            Tensor inputTensor = new Tensor(1, 32, 32, 3);

            // Deterministic tensor values
            for (int i = 0; i < inputTensor.length; i++)
            {
                inputTensor[i] = 1.0f;
            }

            // --------------------------------------------------
            // RUN INFERENCE
            // --------------------------------------------------

            Stopwatch sw = new Stopwatch();

            sw.Start();

            worker.Execute(inputTensor);

            Tensor output = worker.PeekOutput();

            sw.Stop();

            // --------------------------------------------------
            // SAVE RESULTS
            // --------------------------------------------------

            result.model_name = modelAsset.name;
            result.backend = "Barracuda";
            result.inference_time_ms = sw.Elapsed.TotalMilliseconds;

            result.input_shape = new int[]
            {
                1,
                3,
                32,
                32
            };

            result.output_shape = new int[]
            {
                output.shape.batch,
                output.shape.height,
                output.shape.width,
                output.shape.channels
            };

            result.success = true;
            result.error = "";

            UnityEngine.Debug.Log(
                $"Inference completed in {result.inference_time_ms} ms"
            );

            UnityEngine.Debug.Log(
                $"Output shape: " +
                $"[{output.shape.batch}, " +
                $"{output.shape.height}, " +
                $"{output.shape.width}, " +
                $"{output.shape.channels}]"
            );

            // --------------------------------------------------
            // CLEANUP
            // --------------------------------------------------

            inputTensor.Dispose();
            output.Dispose();
            worker.Dispose();
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
}