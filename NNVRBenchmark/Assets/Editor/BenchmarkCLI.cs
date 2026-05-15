using System;
using System.IO;
using System.Diagnostics;
using UnityEngine;
using Unity.Barracuda;
using UnityEditor;

public class BenchmarkCLI
{
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

    public static void RunBenchmark()
    {
        BenchmarkResult result = new BenchmarkResult();

        try
        {
            // --------------------------------------------------
            // FIND MODEL
            // --------------------------------------------------

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

            NNModel modelAsset = AssetDatabase.LoadAssetAtPath<NNModel>(
                assetPath
            );

            UnityEngine.Debug.Log(
                $"Loading model: {modelAsset.name}"
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
            // --------------------------------------------------

            Tensor inputTensor = new Tensor(1, 32, 32, 3);

            for (int i = 0; i < inputTensor.length; i++)
            {
                inputTensor[i] = 1.0f;
            }

            // --------------------------------------------------
            // WARMUP
            // --------------------------------------------------

            for (int i = 0; i < 5; i++)
            {
                worker.Execute(inputTensor);
            }

            // --------------------------------------------------
            // TIMED RUNS
            // --------------------------------------------------

            int runs = 20;

            Stopwatch sw = new Stopwatch();

            sw.Start();

            for (int i = 0; i < runs; i++)
            {
                worker.Execute(inputTensor);
            }

            Tensor output = worker.PeekOutput();

            sw.Stop();

            double avgMs =
                sw.Elapsed.TotalMilliseconds / runs;

            // --------------------------------------------------
            // SAVE RESULTS
            // --------------------------------------------------

            result.model_name = modelAsset.name;
            result.backend = "Barracuda";
            result.inference_time_ms = avgMs;

            result.input_shape = new int[]
            {
                1, 3, 32, 32
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
                $"Average inference time: {avgMs} ms"
            );

            // Cleanup
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

        // --------------------------------------------------
        // EXIT UNITY
        // --------------------------------------------------

        EditorApplication.Exit(0);
    }

    static void SaveResult(BenchmarkResult result)
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
}