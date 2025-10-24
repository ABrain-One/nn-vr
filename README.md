# VR-Ready Neural Network Verifier

<img src='https://abrain.one/img/nn-vr-tr.png' width='25%'/>

The original version of the NN VR project was created by <strong>Arash Torabi Goodarzi, Mahta Moosavi and Zofia Antonina Bentyn</strong> at the Computer Vision Laboratory, University of Würzburg, Germany.

## Create and Activate a Virtual Environment (recommended)
For Linux/Mac:
```bash
python3 -m venv .venv
source .venv/bin/activate
```
For Windows:
```bash
python3 -m venv .venv
.venv\Scripts\activate
```

It is assumed that CUDA 12.6 is installed. If you have a different version, please replace 'cu126' with the appropriate version number.

## Environment for NN Stat Contributors

Run the following command to install all the project dependencies:
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cu126
```

Installing/Updating NN Dataset from GitHub:
```bash
rm -rf db
pip install --no-cache-dir git+https://github.com/ABrain-One/nn-dataset --upgrade --force --extra-index-url https://download.pytorch.org/whl/cu126
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

#### The idea and leadership of Dr. Ignatov
