#!/bin/bash
# ============================================================
#  install-unity.sh — Linux (Ubuntu / Debian)
#  Installs Unity Hub via the official apt repository,
#  then installs Unity 2022.3.62f3 via the Hub headless CLI.
#
#  Usage:
#    bash install-unity.sh
#
#  Tested on: Ubuntu 20.04, 22.04, 24.04
# ============================================================
set -euo pipefail

UNITY_VERSION="2022.3.62f3"
UNITY_CHANGESET="96770f904ca7"

# Unity Hub installs editors here by default on Linux
UNITY_BIN="$HOME/Unity/Hub/Editor/$UNITY_VERSION/Editor/Unity"

# ── helpers ─────────────────────────────────────────────────
step()  { echo -e "\n  \033[36m▶  $*\033[0m"; }
ok()    { echo -e "  \033[32m✅ $*\033[0m"; }
warn()  { echo -e "  \033[33m⚠  $*\033[0m"; }
fail()  { echo -e "  \033[31m❌ $*\033[0m"; exit 1; }

# ── 0. Already installed? ────────────────────────────────────
if [ -f "$UNITY_BIN" ]; then
    ok "Unity $UNITY_VERSION already installed at $UNITY_BIN"
    exit 0
fi

# ── 1. Install Unity Hub ─────────────────────────────────────
if ! command -v unityhub &>/dev/null; then
    step "Installing Unity Hub via apt..."

    sudo install -d /etc/apt/keyrings
    curl -fsSL https://hub.unity3d.com/linux/keys/public \
        | sudo gpg --dearmor -o /etc/apt/keyrings/unityhub.gpg

    echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/unityhub.gpg] \
https://hub.unity3d.com/linux/repos/deb stable main" \
        | sudo tee /etc/apt/sources.list.d/unityhub.list > /dev/null

    sudo apt-get update -q
    sudo apt-get install -y unityhub xvfb libgconf-2-4

    # ── libssl 1.1 compatibility shim for Ubuntu 22.04 / 24.04 ──
    UBUNTU_VER=$(lsb_release -rs 2>/dev/null || echo "0")
    if [[ "$UBUNTU_VER" == "22.04" || "$UBUNTU_VER" == "24.04" ]]; then
        step "Installing libssl1.1 compatibility package..."
        SSL_DEB="libssl1.1_1.1.0g-2ubuntu4_amd64.deb"
        wget -q "http://archive.ubuntu.com/ubuntu/pool/main/o/openssl/$SSL_DEB"
        sudo dpkg -i "$SSL_DEB" || sudo apt-get -f install -y
        rm -f "$SSL_DEB"
    fi

    ok "Unity Hub installed"
else
    ok "Unity Hub already present ($(unityhub --version 2>/dev/null || echo 'version unknown'))"
fi

# ── 2. Install Unity editor ──────────────────────────────────
step "Installing Unity $UNITY_VERSION (changeset $UNITY_CHANGESET)..."
warn "This can take 10-30 minutes depending on your internet speed."

unityhub --headless install \
    --version   "$UNITY_VERSION" \
    --changeset "$UNITY_CHANGESET"

# ── 3. Verify ────────────────────────────────────────────────
step "Verifying installation..."
if [ -f "$UNITY_BIN" ]; then
    ok "Unity $UNITY_VERSION installed successfully at $UNITY_BIN"
    echo ""
    echo "  You can now run the full NN-VR pipeline:"
    echo "    python main.py"
else
    warn "Unity binary not found at expected path yet."
    warn "Unity Hub may still be finishing in the background."
    warn "Check: unityhub --headless editors --installed"
    exit 1
fi
