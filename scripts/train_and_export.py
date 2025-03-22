import os
import subprocess

import torch
import torch.onnx
import torchvision

from torch import nn
from torchvision.transforms import transforms
from torch.utils.data import Subset

from CVModelTrainer.CVModelTrainer import CVModelTrainer

number_of_epochs = 100


def check_for_adaptive_pool(model):
    for name, layer in model.named_modules():
        if isinstance(layer, (nn.AdaptiveAvgPool2d, nn.AdaptiveMaxPool2d)):
            if layer.output_size not in [(1, 1), 1, None]:
                return True
    return False


def export_to_onnx(model_path, model_name, model):
    model.load_state_dict(torch.load(model_path, weights_only=True))
    model.eval()

    hasAdaptivePoolingLayer = check_for_adaptive_pool(model)

    dummy_input = torch.randn(1, 3, 224, 224)
    onnx_file_path = f"../Onnx_exports/{model_name}.onnx"

    if hasAdaptivePoolingLayer:
        torch.onnx.export(
            model,
            dummy_input,
            onnx_file_path,
            input_names=["input"],
            output_names=["output"]
        )
    else:
        torch.onnx.export(
            model,
            dummy_input,
            onnx_file_path,
            input_names=["input"],
            output_names=["output"],
            dynamic_axes={
                "input": {0: "batch_size", 2: "height", 3: "width"},
                "output": {0: "batch_size"}
            }
        )

    print(f"Exported {model_name} to ONNX format at {onnx_file_path}")
    return onnx_file_path


# def main():
transform = transforms.Compose(
    [
        transforms.Resize(299),
        transforms.CenterCrop(299),
        transforms.ToTensor(),
        transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225))
    ]
)
train_set_full = torchvision.datasets.CIFAR10(
    root='../data', train=True,
    download=True, transform=transform
)
test_set_full = torchvision.datasets.CIFAR10(
    root='../data', train=False,
    download=True, transform=transform
)

num_images = 100

train_subset_indices = list(range(num_images))
train_set = Subset(train_set_full, train_subset_indices)

test_subset_indices = list(range(num_images))
test_set = Subset(test_set_full, test_subset_indices)

train_loader = torch.utils.data.DataLoader(train_set, batch_size=32, shuffle=True)
test_loader = torch.utils.data.DataLoader(test_set, batch_size=32, shuffle=False)

trained_models = {}
for model in os.listdir("../Dataset"):
    model = str(os.fsdecode(model))
    if os.path.isdir("../Dataset/" + model):
        try:
            trainer = CVModelTrainer("Dataset." + model, train_set, test_set)
            accuracy = trainer.train(number_of_epochs)
            trained_models[model] = trainer.model

            model_save_path = f"../Trained_models/{model}.pth"
            torch.save(trainer.model.state_dict(), model_save_path)

        except Exception as error:
            print("failed to determine accuracy for", model)
            with open("../Dataset/" + model + "/error.txt", "w+") as error_file:
                error_file.write(str(error))

for model_name, trained_model in trained_models.items():
    onnx_path = export_to_onnx(f"../TrainedModels/{model_name}.pth", model_name, trained_model)
    subprocess.run(["python", "convert_for_unity.py", onnx_path])


# if __name__ == "__main__":
#     main()
