import os
import subprocess
import sys

def run_command(command, cwd=None):
    try:
        subprocess.check_call(command, shell=True, cwd=cwd)
        return True
    except Exception as e:
        print(f"Error executing command: {command}")
        print(e)
        return False

def check_sd_scripts():
    sd_scripts_path = os.path.join(os.getcwd(), "sd-scripts")
    key_file = os.path.join(sd_scripts_path, "anima_train_network.py")

    if not os.path.exists(sd_scripts_path):
        print("[SETUP] sd-scripts not found. Cloning from repository...")
        if not run_command("git clone https://github.com/kohya-ss/sd-scripts.git"):
            print("[ERROR] Failed to clone sd-scripts. Please ensure git is installed and you have an internet connection.")
            return False
        print("[SETUP] sd-scripts cloned successfully.")
    elif not os.path.exists(key_file):
        # Folder exists but files are missing (e.g. git-managed but deleted)
        git_dir = os.path.join(sd_scripts_path, ".git")
        if os.path.exists(git_dir):
            print("[SETUP] sd-scripts folder found but files are missing. Running git restore...")
            if not run_command("git restore .", cwd=sd_scripts_path):
                print("[WARNING] git restore failed. Please press the setup button in the browser.")
            else:
                print("[INFO] sd-scripts files restored successfully.")
        else:
            print("[WARNING] sd-scripts folder is empty and not a git repo. Please press the setup button in the browser.")
    else:
        print("[INFO] sd-scripts found and ready.")
    
    return True

def is_blackwell_gpu():
    try:
        output = subprocess.check_output(["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"], text=True)
        if "RTX 50" in output:
            return True
    except Exception:
        pass
    return False

def get_pytorch_info():
    code = """
import sys
try:
    import torch
    import torchvision
    if not torch.cuda.is_available():
        print("NO_CUDA")
        sys.exit(0)
    major, minor = torch.cuda.get_device_capability()
    arch_list = torch.cuda.get_arch_list()
    cc = major * 10 + minor
    if cc >= 120 and 'sm_120' not in arch_list:
        print("NEEDS_UPGRADE")
    else:
        print("OK")
except ImportError:
    print("MISSING")
"""
    try:
        output = subprocess.check_output([sys.executable, "-c", code], text=True).strip()
        return output.split('\n')[-1]
    except Exception:
        return "MISSING"

def check_pytorch():
    is_blackwell = is_blackwell_gpu()
    status = get_pytorch_info()
    
    nightly_cmd = f"\"{sys.executable}\" -m pip install torch==2.13.0.dev20260418+cu130 torchvision --index-url https://download.pytorch.org/whl/nightly/cu130"
    stable_cmd = f"\"{sys.executable}\" -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121"

    if status == "MISSING":
        if is_blackwell:
            print("[SETUP] RTX 50 series detected. Installing PyTorch Nightly (CUDA 13.0)...")
            if not run_command(nightly_cmd):
                return False
        else:
            print("[SETUP] PyTorch not found. Installing standard version...")
            if not run_command(stable_cmd):
                return False
    elif status == "NEEDS_UPGRADE":
        print("[SETUP] RTX 50 series detected, but current PyTorch does not support Blackwell (sm_120).")
        print("[SETUP] Upgrading to PyTorch Nightly (CUDA 13.0)...")
        if not run_command(nightly_cmd):
            print("[ERROR] Failed to upgrade PyTorch.")
            return False
        print("[SETUP] PyTorch upgraded successfully.")
    elif status == "NO_CUDA":
        print("[WARNING] CUDA is not available. Training will be extremely slow on CPU.")
    else:
        print("[INFO] PyTorch is compatible with your GPU.")
    
    return True

def check_requirements():
    print("[INFO] Checking other dependencies...")
    
    # 1. Main backend requirements
    req_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
    if os.path.exists(req_path):
        print(f"[INFO] Installing backend requirements from {req_path}...")
        run_command(f"\"{sys.executable}\" -m pip install -r \"{req_path}\"")
    
    # 2. sd-scripts requirements
    sd_scripts_path = os.path.join(os.getcwd(), "sd-scripts")
    sd_req_path = os.path.join(sd_scripts_path, "requirements.txt")
    if os.path.exists(sd_req_path):
        print(f"[INFO] Installing sd-scripts requirements from {sd_req_path}...")
        run_command(f"\"{sys.executable}\" -m pip install -r \"{sd_req_path}\"", cwd=sd_scripts_path)
    
    return True

if __name__ == "__main__":
    print("="*50)
    print("  Anima LoRA Factory - Environment Setup Check")
    print("="*50)
    
    success = True
    # Change to backend directory to ensure relative paths work
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    if not check_sd_scripts():
        success = False
    
    if success and not check_pytorch():
        success = False
        
    if success and not check_requirements():
        success = False
    
    # Final verification for Blackwell
    if success and is_blackwell_gpu():
        status = get_pytorch_info()
        if status in ["NEEDS_UPGRADE", "MISSING"]:
            print(f"[SETUP] Re-installing/Upgrading PyTorch Nightly (status: {status})...")
            run_command(f"\"{sys.executable}\" -m pip install torch==2.13.0.dev20260418+cu130 torchvision --index-url https://download.pytorch.org/whl/nightly/cu130")
        
    if success:
        print("="*50)
        print("  Setup Check Completed Successfully!")
        print("="*50)
        sys.exit(0)
    else:
        print("="*50)
        print("  Setup Check encountered some issues.")
        print("="*50)
        sys.exit(1)
