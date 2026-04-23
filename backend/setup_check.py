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
    if not os.path.exists(sd_scripts_path):
        print("[SETUP] sd-scripts not found. Cloning from repository...")
        if not run_command("git clone https://github.com/kohya-ss/sd-scripts.git"):
            print("[ERROR] Failed to clone sd-scripts. Please ensure git is installed and you have an internet connection.")
            return False
        
        # Checkout specific version if needed, or just stay on main
        print("[SETUP] sd-scripts cloned successfully.")
    else:
        print("[INFO] sd-scripts found.")
    
    # Ensure dependencies from sd-scripts are also installed
    req_path = os.path.join(sd_scripts_path, "requirements.txt")
    if os.path.exists(req_path):
        print("[SETUP] Installing sd-scripts dependencies...")
        run_command(f"python -m pip install -r \"{req_path}\"")
        
    return True

def check_pytorch():
    try:
        import torch
        print(f"[INFO] PyTorch version: {torch.version.__version__}")
        
        if not torch.cuda.is_available():
            print("[WARNING] CUDA is not available. Training will be extremely slow on CPU.")
            return True
        
        # Blackwell check (RTX 50 series)
        major, minor = torch.cuda.get_device_capability()
        cc = major * 10 + minor
        arch_list = torch.cuda.get_arch_list()
        
        print(f"[INFO] GPU Compute Capability: {major}.{minor}")
        
        if cc >= 120 and "sm_120" not in arch_list:
            print("[SETUP] RTX 50 series detected, but current PyTorch does not support Blackwell (sm_120).")
            print("[SETUP] Upgrading to PyTorch Nightly (CUDA 13.0)...")
            if not run_command("python -m pip install --pre torch torchvision --upgrade --index-url https://download.pytorch.org/whl/nightly/cu130"):
                print("[ERROR] Failed to upgrade PyTorch. Training might fail.")
                return False
            print("[SETUP] PyTorch upgraded successfully.")
        else:
            print("[INFO] PyTorch is compatible with your GPU.")
            
    except ImportError:
        print("[SETUP] PyTorch not found. Installing standard version...")
        if not run_command("python -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121"):
            return False
    
    return True

def check_requirements():
    print("[INFO] Checking other dependencies...")
    req_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
    if os.path.exists(req_path):
        # We use --no-deps or just let pip handle it. 
        # To make it fast/offline, we could skip if certain packages exist, 
        # but "pip install" is usually fast if everything is already there.
        run_command(f"python -m pip install -r \"{req_path}\"")
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
        # We continue anyway, but warning was shown
        pass
        
    if success and not check_requirements():
        success = False
        
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
