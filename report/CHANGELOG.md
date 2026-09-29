# CHANGELOG: Expanded Manuscript v2.0

## Overview
The manuscript has been expanded from approximately 7 pages (219 lines) to approximately 25+ pages (600+ lines), transforming a compact summary into a full-length arXiv-quality research article.

## Sections Added

### New sections (not present in v1)
- **Section 3: Background and Motivation** — VR/XR deployment context, Unity and Barracuda background, ONNX intermediate representation, NN-Dataset/LEMUR ecosystem, and motivation for the study.
- **Section 4: Related Work** — Substantially expanded with seven subsections: model deployment/ONNX portability, edge/mobile inference, neural architecture benchmarking, game-engine ML inference, VR/XR real-time vision, inference latency prediction, and reproducibility in benchmarking.
- **Section 6: Dataset and Model Population** — Detailed description of the 1,762-model population, including composition, architecture flags, metadata availability, and input heterogeneity.
- **Section 7: Deployment Pipeline** — Comprehensive description of the entire pipeline based on direct code inspection:
  - PyTorch model instantiation (from `onnx_exporter.py`)
  - ONNX export configuration (opset 12, FP32, dynamic batch, IR version 7, subprocess timeout)
  - Unity Barracuda execution (from `BenchmarkCLI.cs`)
  - Input tensor construction
  - Warm-up protocol (5 iterations)
  - Timing protocol (20 iterations, `Time.realtimeSinceStartup`)
  - GPU execution environments (RTX 4090/Vulkan, Mesa llvmpipe)
  - Campaign structure
- **Section 8: Experimental Methodology** — Hardware/software environment table, model inputs, ONNX configuration, warm-up and timing, repeated campaigns, success/failure definitions, failure classification, and full statistical methodology.
- **Section 14: RQ6 - VR Deployment Implications** — Evidence-based deployment workflow, explicit non-claims, and three-gate deployment validation.
- **Section 15: Deployment Workflow and Practical Recommendations** — Engineering practices and alternative runtime considerations.
- **Section 17: Recommended Follow-Up Experiments** — Seven specific follow-up experiments: numerical correctness, synchronized GPU latency, failure taxonomy, validated latency modeling, compatibility prediction, target-device evaluation, and runtime comparison.
- **Appendix** — Detailed tables for architecture flags, campaign completion, llvmpipe campaigns, ONNX configuration, benchmark timing configuration, export failure list, and traceability.

### Substantially expanded sections
- **Abstract** — Expanded from 1 paragraph to a comprehensive abstract covering all six research questions.
- **Introduction** — Expanded from 2 paragraphs to a full section with three deployment questions, contribution list.
- **Research Questions** — Expanded from 5 to 6 research questions (added RQ6 on VR implications).
- **RQ1: Compatibility** — Expanded with export failure analysis (30 models: 24 rag-, 1 unq-, 4 named), failure mechanism analysis distinguishing observed association vs. plausible mechanism vs. demonstrated mechanism.
- **RQ2: Reproducibility** — Expanded with model-level completion analysis (806 in all 6, 8 in 5), sources of timing variability discussion, llvmpipe instability analysis.
- **RQ3: Runtime** — Expanded with CPU-faster subset characterization, detailed timing interpretation caveats, Barracuda backend internals.
- **RQ4: Latency** — Expanded with key observations for each correlation, PySR interpretation, architecture flags and runtime analysis, critical caveat about held-out evaluation.
- **RQ5: Unity vs Standalone** — Expanded with separate CPU and GPU analysis subsections, rank agreement analysis, and detailed protocol mismatch analysis (8 specific mismatches enumerated).
- **Limitations** — Expanded from 1 paragraph to 4 subsections: internal validity, external validity, construct validity, and statistical limitations.
- **Conclusion** — Expanded from 1 paragraph to structured conclusion with 6 named paragraphs.

## Analyses Added
- Detailed protocol mismatch analysis for the Unity/workstation comparison (8 specific dimensions)
- Export failure categorization (rag-/unq-/named breakdown: 24/1/4 + 1)
- Failure mechanism distinction framework (association vs. plausible mechanism vs. demonstrated mechanism)
- CPU-faster subset characterization (median params 6,474 vs 492,714; layers 10 vs 36)
- Sources of timing variability analysis
- Three-gate deployment validation framework
- Seven recommended follow-up experiments with specific methodology

## Tables Added
| Table | Description |
|-------|-------------|
| Tab 1 | Hardware/software environment |
| Tab 2 | Pipeline outcomes (carried forward, unchanged) |
| Tab 3 | Architecture failure rates (carried forward, unchanged) |
| Tab 4 | Reproducibility CV distribution |
| Tab 5 | RTX 4090 runtime observations |
| Tab 6 | llvmpipe vs RTX comparison |
| Tab 7 | Pearson correlations (carried forward, unchanged) |
| Tab 8 | PySR expressions (carried forward, unchanged) |
| Tab 9 | Evidence-to-action deployment guidance (expanded with reproducibility row) |
| Tab 10 | Unity/workstation comparison (carried forward, unchanged) |
| App. Tab A1 | Extended architecture-flag outcomes |
| App. Tab A2 | RTX 4090 per-campaign counts |
| App. Tab A3 | llvmpipe per-campaign counts |
| App. Tab A4 | ONNX export configuration |
| App. Tab A5 | Benchmark timing configuration |

## Numerical Corrections
- All numerical values verified against `report/evidence_summary.md` and source artifacts.
- No numerical corrections were required; all original values were confirmed accurate.
- Confirmed from code inspection: opset 12 (not "default"), dynamic batch axis, IR version 7 downgrade.
- Confirmed from `BenchmarkCLI.cs`: 5 warmup iterations, 20 measured iterations, `Time.realtimeSinceStartup` timer, `PeekOutput()` without synchronization.

## Claims Strengthened
- GPU timing interpretation: now includes direct code listing from `BenchmarkCLI.cs` showing the exact timer placement.
- ONNX configuration: now includes all parameters from code inspection (opset, IR version, dynamic axes, subprocess timeout).
- Failure analysis: now explicitly distinguishes three levels (observed association, plausible mechanism, demonstrated mechanism).
- Protocol mismatch: now enumerates 8 specific dimensions of potential mismatch.

## Claims Weakened or Removed
- No claims were weakened; the original paper was already conservative.
- The paper explicitly refrains from: inventing data, inventing significance tests, claiming GPU speed, claiming VR readiness, claiming causal mechanisms, ranking architectures.

## Bibliography Updates
- Added references: `barracuda2022`, `sentis2023`, `howard2017mobilenets`, `he2016deep`, `dosovitskiy2020image`, `simonyan2014very`, `onnxruntime2019`.
- All original references preserved.
- No invented citations.

## Structural Changes
- Document class and formatting: preserved (10pt, twocolumn, letterpaper, CVPR style).
- Added `enumitem`, `listings`, `placeins` packages.
- Title updated to include "Reproducibility" reflecting the expanded scope.
