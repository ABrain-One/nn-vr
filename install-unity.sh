#!/bin/bash
# Unity Hub Headless Installation for Ubuntu
set -e

echo "Adding Unity Hub Repository..."
sudo install -d /etc/apt/keyrings
curl -fsSL https://hub.unity3d.com/linux/keys/public | sudo gpg --dearmor -o /etc/apt/keyrings/unityhub.gpg

echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/unityhub.gpg] https://hub.unity3d.com/linux/repos/deb stable main" | sudo tee /etc/apt/sources.list.d/unityhub.list

echo "Installing Dependencies (including libssl1.1 fix for Ubuntu 22+)..."
sudo apt update
sudo apt install -y unityhub xvfb libgconf-2-4

# Required for Unity Editor on newer Ubuntu versions (22.04+)
if [[ $(lsb_release -rs) == "22.04" || $(lsb_release -rs) == "24.04" ]]; then
    wget http://archive.ubuntu.com/ubuntu/pool/main/o/openssl/libssl1.1_1.1.0g-2ubuntu4_amd64.deb
    sudo dpkg -i libssl1.1_1.1.0g-2ubuntu4_amd64.deb || sudo apt -f install -y
fi

echo "Unity Hub installation complete."
echo "To install an editor version (e.g., 2022.3.0f1), run:"
echo "unityhub --headless install --version 2022.3.0f1"
