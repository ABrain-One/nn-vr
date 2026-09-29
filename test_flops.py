import torch
import ab.nn.nn.AirNet as module
from ptflops import get_model_complexity_info

prm = {'lr': 0.1, 'transform': 'norm_128', 'batch': 64, 'dropout': 0.0, 'momentum': 0.9, 'weight_decay': 0.0}
model = module.Net((3, 128, 128), (10,), prm, torch.device("cpu"))
macs, params = get_model_complexity_info(model, (3, 128, 128), as_strings=False, print_per_layer_stat=False)
print(f"\n--- VALIDATION ---")
print(f"Our Script FLOPs: {macs * 2}")
print(f"Our Script Parameters: {params}")
print(f"------------------\n")
