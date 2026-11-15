# Software versions

Reproduction environment actually used: Python 3.10.12; NumPy 2.2.6; SciPy 1.15.3; optional Matplotlib 3.10.9. These are artifact verification versions, not retroactively assigned experimental framework versions. All computations use local CSV/JSON files. Requirements are in analysis/scripts/requirements.txt; nothing is installed or downloaded by the scripts.

A1.1 additionally tests the already installed alternate environment: Python 3.10.12, NumPy 1.21.5, SciPy 1.8.0 and Matplotlib 3.5.1. Scientific verification passes there using unchanged canonical tolerances. Active reproduction code handles SciPy's equivalent mode/method keyword names and correlation/statistic result-field names; formulas and scientific values are unchanged. No host-global installation or package change was performed. ENVIRONMENT_COMPATIBILITY_TEST.md separates numerical verification from reference-output byte comparison.

Historical experimental Python: 3.10.12 in retained A host metadata. Historical PyTorch: **not recorded in retained historical artifacts**. Historical exporter/ONNX Python package versions are not established by this candidate. No present-day package version is substituted.
