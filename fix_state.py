import json
import os
from pathlib import Path
from collections import defaultdict

state_file = Path("_work/processing_state.json")
if not state_file.exists():
    print("No state file found")
    exit(0)

with open(state_file) as f:
    state = json.load(f)

model_versions = defaultdict(int)
for version_dir in Path("out/nn/stat").glob("*/onnx/fp32"):
    if version_dir.exists():
        for d in version_dir.iterdir():
            if d.is_dir() and "img-classification_" in d.name:
                model_name = d.name.split("_acc_")[-1]
                model_versions[model_name] += 1

success_models = set()
for model, count in model_versions.items():
    if count == 5:
        success_models.add(model)

old_count = len(state.get("processed", []))
new_processed = [m for m in state.get("processed", []) if m in success_models]

state["processed"] = new_processed
state["failed"] = []

with open(state_file, "w") as f:
    json.dump(state, f, indent=2)
    
print(f"Cleaned processing_state.json! Kept {len(new_processed)} FULLY successful models (all 5 versions) out of {old_count}.")
