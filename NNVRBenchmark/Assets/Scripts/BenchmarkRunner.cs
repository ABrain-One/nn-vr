using UnityEngine;

// Interactive benchmarking was superseded by the reproducible batch-mode
// BenchmarkCLI entry point. Retaining this component avoids breaking scenes
// that reference it while preventing a second, untracked timing protocol.
public class BenchmarkRunner : MonoBehaviour
{
    private void Start()
    {
        Debug.Log("Experiment B uses BenchmarkCLI.RunBenchmark in batch mode.");
    }
}
