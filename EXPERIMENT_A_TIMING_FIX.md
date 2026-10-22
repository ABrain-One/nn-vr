# Experiment A — completion-aware legacy Barracuda baseline

## Scope and status

Experiment A corrects the timing semantics of the frozen legacy pipeline only:
Unity **2022.3.62f3**, Barracuda **3.0.2**, `CSharpBurst`, and
`ComputePrecompiled` on the physical NVIDIA RTX 4090 using Vulkan.  It is the
baseline for a later, separately authorized Experiment B; no Sentis/Unity
Inference Engine code, package, or project migration is included here.

Status: validation passed on 2026-10-04 after the exporter and provenance
corrections below. The six-campaign physical run completed on 2026-10-05.

## Historical and corrected timing boundaries

The historical `BenchmarkCLI.cs` measured:

```csharp
start = Time.realtimeSinceStartup;
worker.Execute(input);
Tensor output = worker.PeekOutput();
end = Time.realtimeSinceStartup;
```

`IWorker.PeekOutput()` is documented as non-blocking in the vendored package at
`NNVRBenchmark/Library/PackageCache/com.unity.barracuda@3.0.2/Barracuda/Runtime/Core/Barracuda.cs`
(interface documentation, lines 197–212).  `GenericWorker.PeekOutput()` also
calls `PrepareCacheForAccess(blocking:false)` only for small outputs
(`.../Backends/GenericWorker.cs`, lines 1285–1309).  Thus it can merely enqueue
an asynchronous download; it was not a completion boundary.

The corrected Experiment A boundary is:

```csharp
start = Time.realtimeSinceStartup;
worker.Execute(input);
Tensor output = worker.PeekOutput();
output.ToReadOnlyArray();
end = Time.realtimeSinceStartup;
```

This operation is also run after every warm-up. `Tensor.ToReadOnlyArray()` calls
the default (blocking) `PrepareCacheForAccess()` (`.../Core/Tensor.cs`, lines
2768–2779); that method obtains `m_TensorOnDevice.Download(shape)` when no host
cache exists (`Tensor.cs`, lines 2317–2340).  Consequently host output
materialization/readback is part of the measured latency definition.

For `CSharpBurst`, `BurstTensorData.Download()` invokes
`CompleteAllPendingOperations()`, which calls `fence.Complete()` and
`reuse.Complete()` before exposing data (`.../Backends/BarracudaBurstCPU.Core.cs`,
lines 90–135).  Therefore Burst jobs are complete before the stopwatch stops.

For `ComputePrecompiled`, the compute tensor `Download()` waits for an already
requested async GPU readback via `WaitForCompletion()`, or synchronously calls
`ComputeBuffer.GetData()` (`.../Backends/BarracudaReferenceCompute.cs`, lines
338–392).  Both make GPU output available on the host before the stopwatch
stops. `FlushSchedule(true)` is not relied on: it synchronizes an intermediate
tensor rather than explicitly materializing the requested output
(`GenericWorker.cs`, lines 201–205). `ToReadOnlyArray()` is the stronger,
output-specific boundary.

## Warm-ups and measurements

Each backend performs exactly five `Execute → PeekOutput → ToReadOnlyArray`
warm-ups, then exactly 20 identically completed timed iterations. Unity stores
all 20 samples plus the warm-up count, measured count, and
`completion_operation` in the result. A subsequent iteration cannot start
before the previous output has been materialized.

## Low-memory lifecycle and ONNX configuration

`ab/vr/experiment_a.py` deliberately reuses the existing population lookup
(`ab/vr/process_models.py`), exporter (`ab/vr/onnx_exporter.py`) and ONNX
validator (`ab/vr/onnx_validator.py`) while giving this experiment independent
state. The per-model lifecycle is:

`metadata/checkpoint acquisition → temporary ONNX export → existing ONNX
checker → existing CIFAR-10 ONNX validation → one Unity run per requested
campaign → permanent result → delete temporary ONNX/.onnx.data and Unity
copies`.

For the six-campaign production mode, the one downloaded/exported/validated
ONNX artifact is reused sequentially for v1–v6 before cleanup. The Unity runs
remain serial to avoid concurrent GPU contention.

The exporter preserves existing semantics: CPU/FP32 model construction,
checkpoint `NN-Dataset/checkpoints-epoch-50`, model-specific inferred shape,
opset 12, input/output names `input`/`output`, dynamic batch axis for both, ONNX
IR version 7, and `onnx.checker.check_model`. On newer PyTorch installations it
explicitly uses `dynamo=False`: without this, the new default exporter may emit
opset 18 and unsuccessfully try to downgrade it. The exporter hard-fails unless
the final main ONNX opset is exactly 12. The validator continues to use
ONNX Runtime with batch size 1 and model-specific resolution. Temporary files
are removed in `finally`; permanent records are written first.

Failure records distinguish acquisition/loading, export, ONNX validation,
Unity/Barracuda execution, CPU/GPU/materialization where identifiable, timeout/
infrastructure, and cleanup failure. A new re-export is never replaced with a
historical result.

## Result isolation

Historical trees under `out/nn/stat/real_gpu_versions/`, `out/nn/stat/run/`,
and `out/nn/stat/run_llvmpipe_old/` are never read as resume targets or written
by Experiment A.

Experiment A writes only:

```text
out/nn/stat/
  barracuda_completion_aware_validation/
    manifest.json
    experiment_a.log
    onnx/fp32/img-classification_cifar-10_acc_<model>/linux_<device>.json
    failed_benchmarks/<model>.json       # only for failed models
  barracuda_completion_aware_v1/ ... barracuda_completion_aware_v6/
    onnx/fp32/...
    failed_benchmarks/...
```

Temporary ONNX, downloaded checkpoints, and validation data follow the
repository's existing `_work/onnx_temp`, `_work/temp`, and `_work/data`
locations; campaign directories contain permanent benchmark records only.

Resume is per campaign: a completed success or classified failure in that exact
campaign is skipped by default, matching the established pipeline; `--rerun`
is the explicit retry path. Thus a completed
`barracuda_completion_aware_v1` model never suppresses v2–v6.

## Validation selection and command

The three models are historically successful RTX/Vulkan models selected by
stored ONNX size and architectural family, not historical timing outcome:

- `rag-3ddaa7990db4d69304d17811dbd6bbf9` — light (0.01 MB; generated RAG family).
- `UNet2D` — medium (2.18 MB; encoder–decoder family).
- `InceptionV3-1` — heavy (83.51 MB; Inception family).

The intended operator command is:

```bash
cd /home/syedalihaider/Desktop/nn-vr
python -m ab.vr.experiment_a rag-3ddaa7990db4d69304d17811dbd6bbf9,UNet2D,InceptionV3-1 --campaign barracuda_completion_aware_validation
```

The runner itself supplies the exact repository-configured Unity executable,
`-batchmode -force-vulkan`, project path, `BenchmarkCLI.RunBenchmark`, and
`VK_ICD_FILENAMES=/usr/share/vulkan/icd.d/nvidia_icd.json`. It will reject
non-Vulkan, llvmpipe, and non-RTX-4090 Unity results.

## Validation results / revalidation / campaigns

Initial execution (2026-09-29) produced three valid records: each completed
acquisition, export, ONNX validation, Unity execution, and ONNX cleanup; each
identified Unity 2022.3.62f3, Barracuda 3.0.2, CSharpBurst,
ComputePrecompiled, NVIDIA GeForce RTX 4090, Vulkan, five warm-ups, 20 samples
per backend, and `Tensor.ToReadOnlyArray()`. GPU samples show periodic
variation, which is retained as data rather than filtered. A source audit shows
fresh per-execution Tensor objects, so the blocking output access is not a
reused host cache.

The first run did not persist batchmode stdout/stderr. The runner now stores
bounded stdout/stderr tails, exact Unity command, return code, and NVIDIA ICD
path under `unity.unity_process`. A final revalidation of `InceptionV3-1`
completed successfully on 2026-10-04. Its permanent record is:

`out/nn/stat/barracuda_completion_aware_validation/onnx/fp32/img-classification_cifar-10_acc_InceptionV3-1/linux_guest-MS-7E27.json`

It records: ONNX main opset `[12]`; IR version `7`; the legacy
`dynamo=False` exporter; Unity exit code `0`; NVIDIA ICD
`/usr/share/vulkan/icd.d/nvidia_icd.json`; Unity 2022.3.62f3; Barracuda 3.0.2;
CSharpBurst; ComputePrecompiled; NVIDIA GeForce RTX 4090; Vulkan; five warm-ups
and 20 positive completed samples per backend. CPU timing was 100.60–104.24 ms
(mean 101.92 ms); GPU timing was 7.58–8.85 ms (mean 8.04 ms). These values are
reported only as validation evidence, not aggregate study statistics.

The initial sandboxed revalidation attempt failed before model import because
the restricted process could not reach Unity's licensing IPC channel. It is
retained in `experiment_a.log` as an infrastructure event; the final
unsandboxed run succeeded and removed its stale `failed_benchmarks` sidecar.

Newer PyTorch initially selected the Dynamo ONNX exporter and attempted an
opset-18-to-12 conversion. This was corrected by explicitly passing
`dynamo=False` and hard-failing any exported model whose main ONNX opset is not
exactly 12. No latency expectation is specified.

The completed production run requested all 1,762 models in every campaign and
persisted 1,762 records in each of v1–v6. Valid completion-aware timing records
were 1,074 (v1), 1,071 (v2), 1,070 (v3), 1,068 (v4), 1,068 (v5), and 1,067
(v6); remaining records are explicit acquisition/export/validation/Unity
failure outcomes. A post-run audit found no valid v1 record with an incorrect
opset/IR, timing protocol, Vulkan RTX 4090 environment, backend pair, sample
count, or completion operation.

## Files changed

- `NNVRBenchmark/Assets/Editor/BenchmarkCLI.cs` — blocking output
  materialization, per-sample evidence, timing protocol, and fail-closed GPU
  environment checks.
- `ab/vr/experiment_a.py` — isolated low-storage Experiment A production runner.
- `ab/vr/onnx_exporter.py` — preserves legacy ONNX-export semantics under
  newer PyTorch and verifies the final opset/IR contract.
- `ab/vr/unity_runner.py` — removes per-model Unity ONNX/result copies after
  their result has been read; Unity timeouts terminate the invocation process
  group rather than leaving children behind.
- This document — synchronization evidence, protocol, lifecycle, and validation
  plan.

## Measurement limitations

This is completed-inference-to-host-materialized-output latency, not a complete
application-frame latency: it excludes caller-side input construction, Unity
process startup/import overhead, and downstream application work. GPU readback
is intentionally included.
