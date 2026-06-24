# ============================================================
#  install-unity.ps1 -- Windows (PowerShell 5+)
#  Downloads Unity Hub, installs it silently, then installs
#  Unity 2022.3.62f3 via the Unity Hub headless CLI.
#
#  Usage (from repo root):
#    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
#    .\scripts\install-unity.ps1
# ============================================================
#Requires -Version 5

$UNITY_VERSION   = "2022.3.62f3"
$UNITY_CHANGESET = "96770f904ca7"

$HUB_EXE   = "C:\Program Files\Unity Hub\Unity Hub.exe"
$UNITY_EXE = "C:\Program Files\Unity\Hub\Editor\$UNITY_VERSION\Editor\Unity.exe"

# Direct installer URL (x64). This is the URL winget itself resolves to.
$HUB_URL  = "https://public-cdn.cloud.unity3d.com/hub/prod/UnityHubSetup-x64.exe"
$HUB_PATH = "$env:TEMP\UnityHubSetup-x64.exe"

# -- helpers --------------------------------------------------
function Write-Step { param($msg) Write-Host "`n  >> $msg" -ForegroundColor Cyan }
function Write-OK   { param($msg) Write-Host "  [OK]   $msg" -ForegroundColor Green }
function Write-Fail { param($msg) Write-Host "  [FAIL] $msg" -ForegroundColor Red; exit 1 }
function Write-Warn { param($msg) Write-Host "  [WARN] $msg" -ForegroundColor Yellow }

# -- 0. Already installed? ------------------------------------
if (Test-Path $UNITY_EXE) {
    Write-OK "Unity $UNITY_VERSION already installed at:"
    Write-Host "       $UNITY_EXE"
    exit 0
}

# -- 1. Install Unity Hub -------------------------------------
if (-not (Test-Path $HUB_EXE)) {
    Write-Step "Downloading Unity Hub installer (~146 MB)..."
    Write-Host "  Source: $HUB_URL"

    try {
        # Use BITS if available for faster download with progress, else WebRequest
        if (Get-Command Start-BitsTransfer -ErrorAction SilentlyContinue) {
            Start-BitsTransfer -Source $HUB_URL -Destination $HUB_PATH -DisplayName "Unity Hub"
        } else {
            $ProgressPreference = 'SilentlyContinue'  # speeds up Invoke-WebRequest
            Invoke-WebRequest -Uri $HUB_URL -OutFile $HUB_PATH -UseBasicParsing
            $ProgressPreference = 'Continue'
        }
    } catch {
        Write-Fail "Download failed: $_"
    }

    Write-Step "Installing Unity Hub silently..."
    $proc = Start-Process -FilePath $HUB_PATH -ArgumentList "/S" -PassThru -Wait
    if ($proc.ExitCode -ne 0 -and $proc.ExitCode -ne $null) {
        Write-Warn "Installer exited with code $($proc.ExitCode) -- checking if Hub appeared anyway..."
    }

    Remove-Item $HUB_PATH -Force -ErrorAction SilentlyContinue

    # Wait up to 120 s for Hub to appear
    Write-Step "Waiting for Unity Hub to register..."
    $deadline = (Get-Date).AddSeconds(120)
    while (-not (Test-Path $HUB_EXE) -and (Get-Date) -lt $deadline) {
        Start-Sleep -Seconds 3
    }

    if (-not (Test-Path $HUB_EXE)) {
        Write-Fail "Unity Hub not found at expected path after install."
        Write-Fail "Expected: $HUB_EXE"
        Write-Fail "Try installing manually from https://unity.com/download then re-run."
    }

    Write-OK "Unity Hub installed"
} else {
    Write-OK "Unity Hub already present"
}

# -- 2. Install Unity 2022.3.62f3 via Hub CLI -----------------
Write-Step "Installing Unity $UNITY_VERSION (changeset $UNITY_CHANGESET)..."
Write-Warn "This can take 10-30 minutes depending on your internet speed."
Write-Host ""

# Hub CLI requires the double-dash separator before --headless flags
& "$HUB_EXE" -- --headless install `
    --version   $UNITY_VERSION `
    --changeset $UNITY_CHANGESET

# -- 3. Verify ------------------------------------------------
Write-Step "Verifying installation..."
if (Test-Path $UNITY_EXE) {
    Write-OK "Unity $UNITY_VERSION installed successfully at:"
    Write-Host "       $UNITY_EXE"
    Write-Host ""
    Write-Host "  Next steps:" -ForegroundColor White
    Write-Host "    1. Open NNVRBenchmark/ in Unity Hub" -ForegroundColor White
    Write-Host "    2. Run the pipeline: python main.py" -ForegroundColor White
} else {
    Write-Warn "Unity.exe not found at expected path yet."
    Write-Warn "Unity Hub may still be installing in the background."
    Write-Warn "Open Unity Hub -> Installs to confirm $UNITY_VERSION appears."
    exit 1
}
