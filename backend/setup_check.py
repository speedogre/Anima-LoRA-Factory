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
    key_file = os.path.join(sd_scripts_path, "sdxl_train_network.py")

    if not os.path.exists(sd_scripts_path):
        print("[SETUP] sd-scripts not found. Cloning from repository...")
        if not run_command("git clone https://github.com/kohya-ss/sd-scripts.git"):
            print("[ERROR] Failed to clone sd-scripts. Please ensure git is installed and you have an internet connection.")
            return False
        print("[SETUP] sd-scripts cloned successfully.")
    elif not os.path.exists(key_file):
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

def get_nvidia_gpu_info():
    try:
        output = subprocess.check_output(["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"], text=True)
        return output.strip()
    except Exception:
        return None

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
    gpu_name = get_nvidia_gpu_info()
    is_blackwell = gpu_name and "RTX 50" in gpu_name
    is_nvidia = gpu_name is not None
    
    status = get_pytorch_info()
    
    nightly_cmd = f"\"{sys.executable}\" -m pip install torch==2.13.0.dev20260418+cu130 torchvision --index-url https://download.pytorch.org/whl/nightly/cu130"
    stable_cmd = f"\"{sys.executable}\" -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121"

    needs_install = False
    if status == "MISSING":
        needs_install = True
    elif is_nvidia and status == "NO_CUDA":
        print("[SETUP] NVIDIA GPU detected but PyTorch is using CPU. Re-installing GPU version...")
        needs_install = True
    elif is_blackwell and status == "NEEDS_UPGRADE":
        print("[SETUP] RTX 50 series detected. Upgrading to PyTorch Nightly...")
        needs_install = True
    
    if needs_install:
        if is_blackwell:
            print("[SETUP] Installing PyTorch Nightly (CUDA 13.0)...")
            if not run_command(nightly_cmd): return False
        elif is_nvidia:
            print("[SETUP] Installing PyTorch Stable (CUDA 12.1)...")
            if not run_command(stable_cmd): return False
        else:
            print("[SETUP] Installing PyTorch Standard...")
            if not run_command(f"\"{sys.executable}\" -m pip install torch torchvision"): return False
    else:
        print(f"[INFO] PyTorch is ready (GPU: {gpu_name if gpu_name else 'None/Other'}).")
    
    return True

def check_requirements():
    print("[INFO] Checking other dependencies...")
    req_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
    if os.path.exists(req_path):
        run_command(f"\"{sys.executable}\" -m pip install -r \"{req_path}\"")
    
    sd_scripts_path = os.path.join(os.getcwd(), "sd-scripts")
    sd_req_path = os.path.join(sd_scripts_path, "requirements.txt")
    if os.path.exists(sd_req_path):
        print(f"[INFO] Installing sd-scripts requirements...")
        run_command(f"\"{sys.executable}\" -m pip install -r \"requirements.txt\"", cwd=sd_scripts_path)
    
    return True

if __name__ == "__main__":
    print("="*50)
    print("  SDXL LoRA Factory - Environment Setup Check")
    print("="*50)
    
    success = True
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    if not check_sd_scripts(): success = False
    if success and not check_pytorch(): success = False
    if success and not check_requirements(): success = False
    
    # Final check for Blackwell/NVIDIA
    if success:
        gpu_name = get_nvidia_gpu_info()
        if gpu_name:
            status = get_pytorch_info()
            if status in ["NEEDS_UPGRADE", "NO_CUDA", "MISSING"]:
                print(f"[SETUP] Final verification failed (status: {status}). Re-fixing PyTorch...")
                if "RTX 50" in gpu_name:
                    run_command(f"\"{sys.executable}\" -m pip install torch==2.13.0.dev20260418+cu130 torchvision --index-url https://download.pytorch.org/whl/nightly/cu130")
                else:
                    run_command(f"\"{sys.executable}\" -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121")
        
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
