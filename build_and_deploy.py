# UTILITY: Helper script to build and deploy the Unity project.
import os
import subprocess
import argparse
import sys

def find_unity_executable():
    # Common paths for Unity Hub installations on Windows
    possible_paths = [
        r"C:\Program Files\Unity\Hub\Editor",
        r"C:\Program Files\Unity\Editor",
    ]
    
    for base_path in possible_paths:
        if os.path.exists(base_path):
            for version in os.listdir(base_path):
                unity_exe = os.path.join(base_path, version, "Editor", "Unity.exe")
                if os.path.exists(unity_exe):
                    return unity_exe
    return None

def build_android(unity_exe, project_path):
    print(f"Building Android APK using Unity at: {unity_exe}")
    cmd = [
        unity_exe,
        "-batchmode",
        "-quit",
        "-executeMethod", "BuildScript.BuildAndroid",
        "-projectPath", project_path,
        "-logFile", "build.log"
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("Build completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Build failed with error code {e.returncode}. Check build.log for details.")
        sys.exit(1)

def install_apk(apk_path):
    print(f"Installing APK: {apk_path}")
    try:
        subprocess.run(["adb", "install", "-r", apk_path], check=True)
        print("APK installed successfully.")
    except subprocess.CalledProcessError:
        print("Failed to install APK. Ensure device is connected and ADB is in PATH.")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build and Deploy Unity App")
    parser.add_argument("--unity-path", help="Path to Unity.exe")
    parser.add_argument("--project-path", default=os.path.abspath("unity_nn"), help="Path to Unity project")
    parser.add_argument("--skip-build", action="store_true", help="Skip build step")
    
    args = parser.parse_args()
    
    unity_exe = args.unity_path or find_unity_executable()
    
    if not args.skip_build:
        if not unity_exe:
            print("Unity executable not found. Please specify with --unity-path")
            sys.exit(1)
        build_android(unity_exe, args.project_path)
    
    apk_path = os.path.join(args.project_path, "build", "nnvr.apk")
    if os.path.exists(apk_path):
        install_apk(apk_path)
    else:
        print(f"APK not found at {apk_path}")
