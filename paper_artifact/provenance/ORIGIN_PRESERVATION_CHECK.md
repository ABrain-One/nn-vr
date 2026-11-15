# Origin preservation check

PASS: all 43 files in the frozen arxiv_article_v3_2 baseline remain byte-identical to their before-build SHA-256 values. This includes its finalized PDF, clean submission ZIP, manuscript sources and audits. No finalized manuscript file was overwritten.

PASS: all selected original analysis/source files still match the original hashes recorded before copying. All numerical and Boolean fields in the released A/B summary and PT comparison summary equal their original values; sanitization affects provenance strings only. Original raw records were only read to select a small environment projection.

PASS: nn-vr, nested nn-dataset, and sibling nn-vr-experiment-b HEADs are unchanged from environment/REPOSITORY_STATE.json. No git add, commit, tag, push, remote mutation, GitHub/Zenodo release or upload was performed. Existing repository files were not deleted.

Only the new paper_artifact_candidate directory, its local ZIP and temporary preparation/test files were created. The workflow ran deterministic retained-evidence reproduction and presentation rendering only. No model inference, weights download, ONNX export, Unity launch, GPU benchmark, new experimental population, or new scientific analysis was executed.
