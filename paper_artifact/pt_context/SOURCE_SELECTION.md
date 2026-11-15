# NN-Dataset source selection

## Decision

Use `nn-dataset/ab/nn/stat/run/pt/fp32/`, restricted to
`img-classification_cifar-10_acc_*/PT_HOST.json`, as the retained
standalone PyTorch source. The relevant subset contains
13,962 exact model records on the
selected host, of which 13,962 are marked valid.
The wider `pt/fp32` root contains 31,989
records across tasks/datasets and is not itself the comparison population.

The selected JSON schema stores an exact `model_name`, validity/error fields,
the `Linux_MS-7E27` host identity, model-specific input dimensions, 20
iterations, CPU/GPU mean/min/max/standard-deviation durations, and device
analytics. Durations are nanoseconds and are converted to milliseconds only in
the derived comparison files.

## Why this is the correct source

`nn-dataset/ab/nn/util/Inference.py` is the retained producer for these files.
It constructs each selected model, calls `eval()`, uses 10 warm-ups and 20
timed iterations, records CPU timings with `time.perf_counter()`, and records
GPU timings with CUDA events followed by `torch.cuda.synchronize()`. The
existing historical manuscript also identifies `pt/fp32` as its standalone
PyTorch/workstation source.

The source records show `{'NVIDIA GeForce RTX 4090': 13962}` for the GPU unit and
`{'Micro-Star International Co., Ltd. MS-7E27': 13962}` for the board identity. Together with the retained
A/B host records, these identify the same physical MS-7E27 / RTX 4090 host.
The PT JSON CPU metadata records 16 logical cores but only the generic
`x86_64` processor string; the more specific Ryzen 7 7800X3D identity is
retained in the A/B environment records.

## Why `structured_l1_layrewise` is rejected

`nn-dataset/ab/nn/stat/run/pt/structured_l1_layrewise/`
`img-classification_cifar-10_ac/all_models.json` is one aggregate
structured-L1 layerwise-pruning summary. It has 589
model entries (589 exact names from
the 1,762-model manifest; {'failed': 9, 'success': 580}) and records pruning ratio,
post-pruning accuracy, parameter/model-size changes, and one `duration` field.
It has no per-model standalone CPU/GPU timing pair, device metadata, input
shape, warm-up/iteration provenance, or completion-boundary information.
It is therefore a pruning/accuracy analysis, not a baseline inference-latency
source, and is not used in the PT/A/B comparison.

## Matching rule

Matching is exact `model_name` equality only. No aliases, prefixes, fuzzy
matching, or checkpoint-name substitutions are applied. The eight original
manifest entries lacking a selected PT record are listed in
`comparison_summary.json` and `model_overlap.csv`.

## Comparability conclusion

The retained source supports **Level 3: context/rank comparison only**. It
shares host, model identifiers, batch size one, FP32 source designation, and
20 measurement iterations with A/B, but not the final timing boundary:

- PT CPU measures synchronous PyTorch forward-return time without an explicit
  output-array materialization.
- PT GPU uses CUDA event elapsed time and synchronizes after the end event, but
  does not include host output readback.
- A/B time host-output materialization in every warm-up and measured iteration.
- The PT runner instantiates `Net` directly and does not load the epoch-50
  checkpoint used by the Unity exports.
- Only 227/
  1057 identity-matched models have
  the same retained PT and A input shapes.

Accordingly, paired ratios and rank correlations are descriptive context, not
portable Unity-overhead or speedup estimates.
