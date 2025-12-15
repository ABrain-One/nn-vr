import os
import sys
import time
import json
import subprocess
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class VRProcessor:
    def __init__(self):
        self.package_name = "com.DefaultCompany.Test" # Placeholder package name
        self.device_model_dir = "/sdcard/Android/data/com.DefaultCompany.Test/files"
        self.local_stats_dir = Path("nn-dataset/ab/nn/stat/run")
        
        # Absolute paths for tools
        sdk_root = r"C:\Users\haide\AppData\Local\Android\Sdk"
        self.adb_cmd = [os.path.join(sdk_root, "platform-tools", "adb.exe")]
        self.emulator_cmd = [os.path.join(sdk_root, "emulator", "emulator.exe")]

    def check_adb_connection(self) -> bool:
        """Checks if a device is connected via ADB."""
        try:
            result = subprocess.run(self.adb_cmd + ['devices'], capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                # Filter for devices that are not 'List of devices attached'
                devices = [line for line in lines if '\tdevice' in line]
                if devices:
                    logger.info(f"✅ Found connected device(s): {devices}")
                    return True
            logger.warning("⚠️ No device connected via ADB.")
            return False
        except FileNotFoundError:
            logger.error("❌ ADB not found. Please ensure Android SDK Platform-Tools are installed and in PATH.")
            return False

    def push_model(self, local_path: str, model_name: str) -> bool:
        """Pushes the ONNX model to the VR headset."""
        try:
            # Handle model name with or without extension
            if not model_name.endswith('.onnx'):
                filename = f"{model_name}.onnx"
            else:
                filename = model_name
                
            target_path = f"{self.device_model_dir}/{filename}"
            logger.info(f"📤 Pushing model to device: {target_path}")
            
            # Ensure directory exists
            subprocess.run(self.adb_cmd + ['shell', 'mkdir', '-p', self.device_model_dir], capture_output=True)
            
            # Push the main ONNX file
            result = subprocess.run(
                self.adb_cmd + ['push', local_path, target_path],
                capture_output=True, text=True
            )
            
            if result.returncode != 0:
                logger.error(f"❌ Failed to push model: {result.stderr}")
                return False

            # Check for and push external data file (if model is >2GB)
            # The model refers to 'nn.onnx.data' internally, so we must push that specific file.
            # It should be in the same directory as the local_path (AirNet.onnx).
            local_dir = os.path.dirname(local_path)
            
            # We explicitly look for 'nn.onnx.data' because that's what the model expects
            external_data_filename = "nn.onnx.data"
            external_data_file = os.path.join(local_dir, external_data_filename)
            
            if os.path.exists(external_data_file):
                 # We must push it with the SAME name 'nn.onnx.data' to the device
                 target_data_path = f"{self.device_model_dir}/{external_data_filename}"
                 logger.info(f"📤 Pushing external data file: {target_data_path}")
                 res_data = subprocess.run(
                    self.adb_cmd + ['push', external_data_file, target_data_path],
                    capture_output=True, text=True
                 )
                 if res_data.returncode != 0:
                     logger.error(f"❌ Failed to push external data: {res_data.stderr}")
                     return False
            
            logger.info("✅ Model (and data) pushed successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Error pushing model: {e}")
            return False

    def compute_file_hash(self, file_path: str) -> str:
        """Computes SHA-256 hash of a file."""
        import hashlib
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def run_inference_on_device(self, model_name: str, model_hash: str = "") -> bool:
        """Starts the Unity app on the device to run inference."""
        try:
            logger.info(f"🎯 Launching VR app for model: {model_name}")
            
            # Stop previous instance
            subprocess.run(self.adb_cmd + ['shell', 'am', 'force-stop', self.package_name], capture_output=True)
            
            # Launch app with intent extras
            cmd = self.adb_cmd + [
                'shell', 'am', 'start',
                '-n', f"{self.package_name}/com.unity3d.player.UnityPlayerActivity",
                '--es', 'model_name', f"{model_name}",
                '--es', 'model_hash', f"{model_hash}"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("✅ App launched successfully")
                return True
            else:
                logger.error(f"❌ Failed to launch app: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"❌ Error launching app: {e}")
            return False

    def collect_device_analytics(self) -> Dict[str, Any]:
        """Collects CPU and Memory info from the Android device via ADB."""
        analytics = {
            "timestamp": time.time(),
            "memory_info": {},
            "cpu_info": {}
        }
        
        try:
            # Memory Info
            mem_res = subprocess.run(self.adb_cmd + ['shell', 'cat', '/proc/meminfo'], capture_output=True, text=True)
            if mem_res.returncode == 0:
                mem_data = {}
                for line in mem_res.stdout.split('\n'):
                    if ':' in line:
                        k, v = line.split(':', 1)
                        mem_data[k.strip()] = v.strip()
                analytics["memory_info"] = {
                    "total_ram_kb": mem_data.get('MemTotal', 'Unknown'),
                    "free_ram_kb": mem_data.get('MemFree', 'Unknown')
                }

            # CPU Info (Simplified)
            cpu_res = subprocess.run(self.adb_cmd + ['shell', 'cat', '/proc/cpuinfo'], capture_output=True, text=True)
            if cpu_res.returncode == 0:
                analytics["cpu_info"]["raw"] = "CPU info captured" # Parsing full cpuinfo is verbose, keeping it simple
                
            return analytics
        except Exception as e:
            logger.warning(f"⚠️ Failed to collect device analytics: {e}")
            return analytics

    def wait_for_completion(self, model_name: str, timeout: int = 30) -> bool:
        """Monitors logcat for the completion signal."""
        logger.info(f"⏳ Waiting for completion signal for {model_name}...")
        start_time = time.time()
        
        # Clear logcat first
        subprocess.run(self.adb_cmd + ['logcat', '-c'])
        
        process = subprocess.Popen(
            self.adb_cmd + ['logcat', '-s', 'Unity'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        try:
            while time.time() - start_time < timeout:
                line = process.stdout.readline()
                if not line:
                    time.sleep(0.1)
                    continue
                    
                if f"DONE {model_name}" in line:
                    logger.info(f"✅ Detected completion signal for {model_name}")
                    process.terminate()
                    return True
                    
                if "Exception" in line or "Error" in line:
                    # Optional: Log errors seen in logcat
                    pass
                    
            logger.warning(f"⚠️ Timeout waiting for completion signal for {model_name}")
            process.terminate()
            return False
        except Exception as e:
            logger.error(f"❌ Error monitoring logcat: {e}")
            process.terminate()
            return False

    def pull_stats(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Pulls the stats JSON file generated by the VR app."""
        try:
            # Wait for completion signal first
            if not self.wait_for_completion(model_name):
                logger.warning("⚠️ Proceeding to pull stats despite no completion signal (or timeout).")

            local_file = self.local_stats_dir / model_name / "android_vr.json"
            local_file.parent.mkdir(parents=True, exist_ok=True)
            
            device_file = f"{self.device_model_dir}/{model_name}_stats.json"
            
            logger.info(f"📥 Pulling stats from: {device_file}")
            
            result = subprocess.run(self.adb_cmd + ['pull', device_file, str(local_file)], capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"✅ Stats pulled to {local_file}")
                
                # Read and enhance
                with open(local_file, 'r') as f:
                    stats = json.load(f)
                
                stats["device_analytics"] = self.collect_device_analytics()
                
                with open(local_file, 'w') as f:
                    json.dump(stats, f, indent=2)
                    
                return stats
            else:
                logger.error(f"❌ Failed to pull stats: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error pulling stats: {e}")
            return None

    def get_available_avds(self) -> list[str]:
        """Get list of available Android Virtual Devices"""
        try:
            result = subprocess.run(self.emulator_cmd + ['-list-avds'], capture_output=True, text=True)
            if result.returncode == 0:
                avds = [avd.strip() for avd in result.stdout.split('\n') if avd.strip()]
                logger.info(f"Found {len(avds)} available AVDs: {avds}")
                return avds
            else:
                logger.error("Failed to list AVDs")
                return []
        except Exception as e:
            logger.error(f"Error listing AVDs: {e}")
            return []

    def is_emulator_running(self) -> bool:
        """Check if any emulator is already running"""
        try:
            result = subprocess.run(self.adb_cmd + ['devices'], capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                emulators = [line for line in lines if 'emulator-' in line and 'device' in line]
                if emulators:
                    logger.info(f"Found running emulator(s): {emulators}")
                    return True
            return False
        except Exception as e:
            logger.error(f"Error checking emulator status: {e}")
            return False

    def ensure_emulator_running(self) -> bool:
        """Ensure an emulator is running - use any available AVD"""
        try:
            if self.is_emulator_running():
                logger.info("✅ Emulator is already running")
                return True
            
            logger.info("🚀 No emulator running, starting one...")
            available_avds = self.get_available_avds()
            if not available_avds:
                logger.error("❌ No Android Virtual Devices (AVDs) found. Please create one in Android Studio.")
                return False
            
            target_avd = available_avds[0]
            logger.info(f"📱 Starting AVD: '{target_avd}'")
            
            # Start emulator in background
            subprocess.Popen(
                self.emulator_cmd + ['-avd', target_avd, '-no-audio', '-no-window'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            # Wait for device to connect
            logger.info("⏳ Waiting for device to connect...")
            for _ in range(36): # 3 minutes
                if self.is_emulator_running():
                    break
                time.sleep(5)
            
            if not self.is_emulator_running():
                logger.error("❌ Emulator failed to start within timeout")
                return False
            
            # Wait for boot completion
            logger.info("⏳ Waiting for OS to boot completely...")
            for _ in range(24): # 2 minutes
                try:
                    res = subprocess.run(self.adb_cmd + ['shell', 'getprop', 'sys.boot_completed'], capture_output=True, text=True)
                    if res.stdout.strip() == "1":
                        logger.info("✅ Emulator is fully booted and ready")
                        return True
                except:
                    pass
                time.sleep(5)
                
            logger.error("❌ Emulator boot timeout")
            return False
            
        except Exception as e:
            logger.error(f"❌ Emulator startup failed: {e}")
            return False

    def process_model(self, local_onnx_path: str, model_name: str):
        """Orchestrates the full flow for a single model."""
        # Check for physical device first, then try emulator
        if not self.check_adb_connection():
            logger.info("⚠️ No physical device found. Checking for emulator...")
            if not self.ensure_emulator_running():
                logger.warning("⚠️ Skipping VR/Android execution (No device or emulator available).")
                return

        # Compute hash
        model_hash = self.compute_file_hash(local_onnx_path)
        logger.info(f"🔑 Model Hash (SHA256): {model_hash}")

        if self.push_model(local_onnx_path, model_name):
            if self.run_inference_on_device(model_name, model_hash):
                # Wait for completion monitored by pull_stats (via wait_for_completion)
                stats = self.pull_stats(model_name)
                
                if stats:
                    # Verify hash
                    device_hash = stats.get("model_hash", "")
                    if device_hash == model_hash:
                        logger.info("✅ Hash verification successful.")
                    else:
                        logger.warning(f"⚠️ Hash mismatch! Expected: {model_hash}, Got: {device_hash}")
