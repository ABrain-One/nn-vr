# VR-Ready Neural Network Verifier
The original version of the NN VR project was created by <strong>Arash Torabi Goodarzi, Mahta Moosavi and Zofia Antonina Bentyn</strong> at the Computer Vision Laboratory, University of Würzburg, Germany.

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
