# Review notes

Only the following issues require an author or professor decision.

1. **Exact historical PyTorch and ONNX package versions.** The benchmark JSON records Python 3.10.12, but not exact PyTorch/ONNX package versions. `requirements.txt` specifies `onnx>=1.14.0` and leaves PyTorch unpinned. The manuscript includes `% TODO(VERIFY)` for the PyTorch version.
2. **CVPR template migration.** The requested CVPR class/style file is not present in the repository. The project retains a portable two-column Overleaf layout; migrate to `cvpr.sty` only after obtaining the lab-approved template files.
3. **Artifact URL/release.** The local Git remote is `https://github.com/ABrain-One/nn-vr.git`, but no public release, commit identifier, DOI, or archival policy was verified for citation in the manuscript. The paper therefore names local paths and scripts without asserting a public artifact release.
4. **Before arXiv submission.** Perform numerical output-parity tests and completion-aware timing on target XR hardware. The present execution-success criterion does not establish correctness, and the current timer does not establish completed CPU or GPU inference.
5. **Compile review.** This environment has no TeX engine. Compile in Overleaf with the intended template and inspect figure/table placement before submission.
