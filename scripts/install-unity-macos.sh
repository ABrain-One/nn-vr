#!/bin/bash
# ============================================================
#  install-unity-macos.sh — macOS (Intel + Apple Silicon)
#  Installs Unity Hub (via Homebrew or direct DMG download)
#  then installs Unity 2022.3.62f3 via the Hub headless CLI.
#
#  Usage:
#    bash scripts/install-unity-macos.sh
#
#  Tested on: macOS 13 Ventura, 14 Sonoma (Intel + M1/M2)
# ============================================================
set -euo pipefail

UNITY_VERSION="2022.3.62f3"
UNITY_CHANGESET="96770f904ca7"

HUB_APP="/Applications/Unity Hub.app"
HUB_EXEC="/Applications/Unity Hub.app/Contents/MacOS/Unity Hub"

# Unity Hub installs editors under ~/Unity/Hub/Editor/ by default
UNITY_BIN="$HOME/Unity/Hub/Editor/$UNITY_VERSION/Editor/Unity.app/Contents/MacOS/Unity"

HUB_DMG_URL="https://public-cdn.cloud.unity3d.com/hub/prod/UnityHubSetup.dmg"
TMP_DMG="/tmp/UnityHubSetup-$$.dmg"

# ── helpers ─────────────────────────────────────────────────
step()  { echo -e "\n  \033[36m▶  $*\033[0m"; }
ok()    { echo -e "  \033[32m✅ $*\033[0m"; }
warn()  { echo -e "  \033[33m⚠  $*\033[0m"; }
fail()  { echo -e "  \033[31m❌ $*\033[0m"; exit 1; }

# ── 0. Already installed? ────────────────────────────────────
if [ -f "$UNITY_BIN" ]; then
    ok "Unity $UNITY_VERSION already installed at:"
    echo "     $UNITY_BIN"
    exit 0
fi

# ── 1. Install Unity Hub ─────────────────────────────────────
if [ ! -d "$HUB_APP" ]; then
    # Prefer Homebrew (avoids manual DMG mounting / Gatekeeper prompts)
    if command -v brew &>/dev/null; then
        step "Installing Unity Hub via Homebrew..."
        brew install --cask unity-hub
        ok "Unity Hub installed via Homebrew"
    else
        step "Homebrew not found — downloading Unity Hub DMG directly..."
        curl -L --progress-bar -o "$TMP_DMG" "$HUB_DMG_URL"

        step "Mounting DMG and copying app..."
        MOUNT_POINT=$(hdiutil attach "$TMP_DMG" -nobrowse -quiet | awk 'END{print $NF}')
        cp -r "$MOUNT_POINT/Unity Hub.app" /Applications/
        hdiutil detach "$MOUNT_POINT" -quiet
        rm -f "$TMP_DMG"

        ok "Unity Hub installed from DMG"
    fi
else
    ok "Unity Hub already present at $HUB_APP"
fi

# ── 2. Accept Gatekeeper (ARM Macs sometimes need this) ──────
if [[ "$(uname -m)" == "arm64" ]]; then
    xattr -dr com.apple.quarantine "$HUB_APP" 2>/dev/null || true
fi

# ── 3. Install Unity editor ──────────────────────────────────
step "Installing Unity $UNITY_VERSION (changeset $UNITY_CHANGESET)..."
warn "This can take 10-30 minutes depending on your internet speed."

# macOS Hub CLI requires the double-dash separator
"$HUB_EXEC" -- --headless install \
    --version   "$UNITY_VERSION" \
    --changeset "$UNITY_CHANGESET"

# ── 4. Verify ────────────────────────────────────────────────
step "Verifying installation..."
if [ -f "$UNITY_BIN" ]; then
    ok "Unity $UNITY_VERSION installed successfully at:"
    echo "     $UNITY_BIN"
    echo ""
    echo "  You can now run the full NN-VR pipeline:"
    echo "    python main.py"
else
    warn "Unity binary not found at expected path yet."
    warn "Unity Hub may still be finishing in the background."
    warn "To check:  \"$HUB_EXEC\" -- --headless editors --installed"
    exit 1
fi
