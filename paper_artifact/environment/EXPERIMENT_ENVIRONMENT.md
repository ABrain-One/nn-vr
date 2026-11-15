# Recorded experiment environment

Only retained values are reported. RETAINED_ENVIRONMENT_FIELDS.json is a selected-field projection from one original A record with original source hash; aggregate environment expectations/observations are retained in analysis/inputs/summary.json.

| Field | Verified retained value / limitation |
|---|---|
| Physical host | Same MS-7E27 workstation for A/B and contextual PT, as recorded in retained source-selection/hardware audit |
| OS A | Linux 6.8, Ubuntu 22.04 64bit; host field Linux-6.8.0-138-generic-x86_64-with-glibc2.35 |
| OS PT | Linux-6.8.0-111-generic-x86_64-with-glibc2.35, from comparison_summary.json; kernel snapshot differs |
| CPU / memory | AMD Ryzen 7 7800X3D; 16 logical CPUs; 31,187 MB recorded system memory |
| GPU | NVIDIA GeForce RTX 4090 |
| Graphics API | Forced Vulkan; selected A record reports Vulkan 1.1.0 [0x91104180] |
| NVIDIA driver | Not established as a semantic driver-version number by the selected retained evidence; do not infer it from the Vulkan hexadecimal field |
| Unity A / runtime | 2022.3.62f3 / Barracuda 3.0.2 |
| Unity B / runtime | 6000.6.5f1 / Unity Sentis 2.6.1, package com.unity.ai.inference@2.6.1, API Unity.InferenceEngine |
| A backends | CSharpBurst CPU; ComputePrecompiled GPU |
| B backends | CPU; GPUCompute |
| Python A | 3.10.12 retained host field |
| Historical PyTorch | not recorded in retained historical artifacts |
| ONNX | legacy torch.onnx.export(dynamo=False); main opset 12 verified; model.ir_version=7 assigned and saved, then established accuracy validation path; FP32 |
| Input / batch | Model-specific input shapes, benchmark batch one, dynamic batch export axis; not fixed image resolution |
| Repetitions | Six runtime campaigns; five completed warm-ups, 20 completed samples/backend/campaign |
| A endpoint | Execute -> PeekOutput -> ToReadOnlyArray -> timer stop |
| B endpoint | Schedule -> PeekOutput -> DownloadToArray -> timer stop |
| PT endpoint | 10 warm-ups; 20 iterations; CPU perf_counter forward-return; GPU CUDA events + synchronize, no host-output readback; direct Net construction without A/B checkpoint load |

No transient ONNX byte-identity claim is supported. Model outputs were not subjected to an A/B numerical parity test. Missing historical framework/driver versions are not reconstructed from the current machine.
