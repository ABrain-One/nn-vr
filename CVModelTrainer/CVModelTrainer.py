import time
import os

import torch.nn
from torch.utils.data import Dataset
from tqdm import tqdm


class CVModelTrainer:
    def __init__(self, model_source_package: str, train_dataset: Dataset, test_dataset: Dataset):
        """
        Evaluates a given model on a specified dataset for classification
        :param model_source_package: source package containing the CV model within code.py file
               ex: (Dataset.AlexNet) which has a module Net so "from Dataset.AlexNet.Code import Net" would work.
        :param train_dataset: the dataset to be used for the training.
        :param test_dataset: the dataset to be used for testing to determine the actual accuracy.
        """
        self.train_dataset = train_dataset
        self.test_dataset = test_dataset
        self.model_package = model_source_package
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'

        model_class = getattr(
            __import__(
                model_source_package + ".code",
                fromlist=["Net"]
            ),
            "Net"
        )

        args = getattr(
            __import__(
                model_source_package + ".args",
                fromlist=["args"]
            ),
            "args"
        )
        self.model: torch.nn.Module = model_class(*args)
        assert isinstance(self.model, torch.nn.Module)

        self.args = args

    def train(self, num_epochs, batch_size=4):
        train_loader = torch.utils.data.DataLoader(
            self.train_dataset, batch_size=batch_size, shuffle=True, num_workers=2
        )
        test_loader = torch.utils.data.DataLoader(
            self.test_dataset, batch_size=batch_size, shuffle=False, num_workers=2
        )

        self.model.to(self.device)

        criterion = torch.nn.CrossEntropyLoss().to(self.device)
        optimizer = torch.optim.SGD(self.model.parameters(), lr=0.005, momentum=0.9)

        print("Training", self.model_package, "on", self.device)
        time.sleep(0.5)
        for _ in tqdm(range(num_epochs)):
            for i, data in enumerate(train_loader):
                inputs, label = data
                assert isinstance(inputs, torch.Tensor)
                assert isinstance(label, torch.Tensor)
                inputs, label = inputs.to(self.device), label.to(self.device)

                optimizer.zero_grad()
                output = self.model(inputs)
                loss = criterion(output, label)
                loss.backward()
                optimizer.step()

                del inputs
                del label
        print("Finished Training for", self.model_package)

        total = 0
        correct = 0
        with torch.no_grad():
            for data in test_loader:
                image, label = data
                assert isinstance(image, torch.Tensor)
                assert isinstance(label, torch.Tensor)
                image, label = image.to(self.device), label.to(self.device)

                outputs = self.model(image)
                # Using the highest energy as output
                _, predicted = torch.max(outputs.data, 1)
                total += label.size(0)
                correct += (predicted == label).sum().item()

                del image
                del label

        model_accuracy = correct / total
        print("Determined accuracy for ", self.model_package + ":", model_accuracy)
        print(os.getcwd())

        torch.save(self.model.state_dict(), f"TrainedModels/{self.model_package.split('.')[1]}.pth")

        self.model.to('cpu')

        return model_accuracy

    def get_args(self):
        return self.args
