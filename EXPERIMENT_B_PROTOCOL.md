# Experiment B protocol

Experiment B measures the Unity inference-runtime change while preserving the
Experiment A export contract. Its Unity 6 configuration and runner are kept
alongside the existing project sources; Experiment A campaigns are not
modified.

## Primary comparison

- Runtime: Unity 6000.6.5f1 with `com.unity.ai.inference@2.6.1`.
- Export contract: `torch.onnx.export(dynamo=False)`, ONNX main opset 12, IR 7,
  FP32, and the established CIFAR-10 model population.
- Timing: five warm-ups and 20 measured iterations per backend. Every
  iteration schedules the model, obtains its output, and calls the blocking
  `Tensor<float>.DownloadToArray()` before stopping the timer.
- Campaign namespace: `inference_engine_opset12_completion_aware_validation`
  and `inference_engine_opset12_completion_aware_v1` through `v6`.

Experiment A's low-storage process removed its transient ONNX files. The B
driver therefore re-creates an artifact with the same frozen contract, loads it
with ONNX to verify `[12]` and IR `7`, records its SHA-256, then reuses that one
temporary artifact across all requested B repeat campaigns before deleting it.
It must not be described as byte-identical reuse of a deleted A artifact.

## Secondary newer-opset study

A newer-ONNX-opset experiment, if performed, is a separate study. It must use a
separate script and a separate campaign namespace (for example,
`inference_engine_opset18_*`), with the export metadata recorded per model. Its
results are not part of the primary runtime-only comparison.
