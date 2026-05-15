import torch
import torchvision
import torchvision.transforms as T
import onnxruntime as ort

def eval_onnx_accuracy(onnx_path, target_h, data_root):
    """
    Evaluates ONNX model accuracy on CIFAR-10 test set.
    Validates up to 1000 samples for speed.
    """
    session = ort.InferenceSession(str(onnx_path))
    input_name = session.get_inputs()[0].name

    tfm = T.Compose([
        T.ToTensor(),
        T.Resize((target_h, target_h)),
        T.Normalize((0.4914, 0.4822, 0.4465),
                    (0.2023, 0.1994, 0.2010))
    ])

    dataset = torchvision.datasets.CIFAR10(
        root=str(data_root), train=False, download=True, transform=tfm
    )

    loader = torch.utils.data.DataLoader(dataset, batch_size=100)

    correct, total = 0, 0

    for x, y in loader:
        for i in range(len(x)):
            inp = x[i:i+1].cpu().numpy()

            outputs = session.run(None, {input_name: inp})[0]
            pred = outputs.argmax(axis=1)[0]

            if pred == y[i].item():
                correct += 1

            total += 1

            if total >= 1000:
                break
        if total >= 1000:
            break

    return correct / total
