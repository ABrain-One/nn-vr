# VR-Ready Neural Network Verifier
The original version of the NN VR project was created by <strong>Arash Torabi Goodarzi, Mahta Moosavi and Zofia Antonina Bentyn</strong> at the Computer Vision Laboratory, University of Würzburg, Germany.

Installing/Updating NN Dataset from GitHub:
```bash
rm -rf db
pip uninstall -y nn-dataset
pip install git+https://github.com/ABrain-One/nn-dataset --upgrade --force --extra-index-url https://download.pytorch.org/whl/cu126
```

## Usage in Windows

Performing verification of the neural network model for the specific version of Unity installed in the operating system:

`python port.py <model_name> <unity_version>`

for example:

```bash
python port.py AirNet 6000.0.42f1
```

If the Unity version is not specified, the neural network model will be ported to the 'unity_nn' project without verification:

`python port.py <model_name>`

for example:
 
```bash
python port.py AirNet
```
    
