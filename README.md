# VR-Ready Neural Network Verifier

Installing/Updating NN Dataset from GitHub:
```bash
pip uninstall -y nn-dataset
rm -rf db
pip install git+https://github.com/ABrain-One/nn-dataset --upgrade --force --extra-index-url https://download.pytorch.org/whl/cu126
```

## Usage

`python port.py <model_name>`

for example:
 
```bash
python port.py AirNet
```
