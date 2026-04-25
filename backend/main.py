import sys
import os
import subprocess
import threading
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import toml
import json
import glob
import asyncio
import tkinter as tk
from tkinter import filedialog

app = FastAPI()

# Initialize tkinter for folder dialog
root = tk.Tk()
root.withdraw() # Hide main window
root.attributes('-topmost', True) # Bring dialog to front

# Supported image extensions
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}

def get_tag_category(tag):
    tag = tag.strip().lower()
    if tag.startswith("@") or tag in ["1girl", "1boy", "girl", "boy", "solo"]:
        return "tag-char"
    if any(x in tag for x in ["hair", "eyes", "skin", "body"]):
        return "tag-char"
    if any(x in tag for x in ["shirt", "skirt", "pants", "dress", "uniform", "clothes", "wearing"]):
        return "tag-clothes"
    if any(x in tag for x in ["background", "outdoor", "indoor", "room", "sky", "tree", "nature"]):
        return "tag-bg"
    if any(x in tag for x in ["masterpiece", "best quality", "highres", "year", "score"]):
        return "tag-meta"
    return "tag-general"

def generate_dataset_toml(image_dir, output_path):
    config = {
        "general": {
            "enable_bucket": True,
            "resolution": [1024, 1024],
            "min_bucket_reso": 256,
            "max_bucket_reso": 2048,
            "caption_extension": ".txt"
        },
        "datasets": [
            {
                "subsets": [
                    {
                        "image_dir": image_dir,
                        "num_repeats": 10
                    }
                ]
            }
        ]
    }
    with open(output_path, "w") as f:
        toml.dump(config, f)

# Global variable to store logs and active connections
training_logs = ""
tagging_logs = "" # Separate logs for tagging
training_process = None
active_connections: list[WebSocket] = []

@app.websocket("/ws/logs")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        # Send a combined current state or just wait for broadcasts
        await websocket.send_text("--- Connection Established ---")
        while True:
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        active_connections.remove(websocket)

async def broadcast_log(line: str, type="train"):
    global training_logs, tagging_logs
    prefix = "[TRAIN] " if type == "train" else "[TAGGER] "
    full_line = prefix + line
    
    if type == "train":
        training_logs += full_line
    else:
        tagging_logs += full_line
    
    for connection in active_connections:
        try:
            await connection.send_text(full_line)
        except:
            pass

class TrainingConfig(BaseModel):
    path: str
    model: str
    vae: str = ""
    output_dir: str
    name: str
    vram: str
    epochs: int
    lr: str
    rank: int = 4
    alpha: int = 1
    keep_unet: bool = False
    shutdown: bool = False

@app.post("/api/start-training")
async def start_training(config: TrainingConfig, script_path: str = ""):
    global training_logs, training_process
    
    if training_process and training_process.poll() is None:
        return {"status": "error", "message": "Training is already running"}

    training_logs = "Initializing training...\n"
    
    # Check script path
    internal_scripts = os.path.join(os.path.dirname(__file__), "sd-scripts")
    train_script_name = "sdxl_train_network.py"
    
    if not script_path and os.path.exists(internal_scripts):
        script_path = internal_scripts
        
    train_script = os.path.join(script_path, train_script_name) if script_path else train_script_name
    
    if not os.path.exists(train_script):
        msg = f"Error: {train_script} が見つかりません。sd-scriptsのパスを確認するか、セットアップを行ってください。\n"
        await broadcast_log(msg, "train")
        return {"status": "error", "message": "Script not found"}

    # Generate dataset TOML
    toml_path = os.path.join(os.path.dirname(__file__), "dataset_config.toml")
    try:
        generate_dataset_toml(config.path, toml_path)
        training_logs += f"Generated dataset config at {toml_path}\n"
    except Exception as e:
        return {"status": "error", "message": f"Failed to generate TOML: {str(e)}"}

    # In a real scenario, we would run sd-scripts
    command = [
        sys.executable, train_script,
        f"--pretrained_model_name_or_path={config.model}",
        f"--output_dir={config.output_dir}",
        f"--output_name={config.name}",
        f"--dataset_config={toml_path}",
        "--network_module=networks.lora",
        f"--max_train_epochs={config.epochs}",
        f"--learning_rate={config.lr}",
        f"--network_dim={config.rank}",
        f"--network_alpha={config.alpha}",
        "--mixed_precision=bf16",
        "--gradient_checkpointing"
    ]
    
    if config.vae:
        command.append(f"--vae={config.vae}")
    
    # Common optimizations
    command.append("--sdpa")
    command.append("--cache_latents")

    # Add VRAM optimizations based on selected mode
    if config.vram == "low":
        command.append("--lowram")
        command.append("--cache_latents_to_disk")
    elif config.vram == "very_low":
        command.append("--lowram")
        command.append("--cache_latents_to_disk")
        command.append("--cache_text_encoder_outputs")
        command.append("--cache_text_encoder_outputs_to_disk")

    training_logs = f"Running command: {' '.join(command)}\n"
    
    try:
        # Run process and conversion in a task
        asyncio.create_task(train_and_convert_task(config, command, script_path))
        return {"status": "started"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

async def train_and_convert_task(config: TrainingConfig, command: list, script_path: str):
    global training_process
    try:
        training_process = subprocess.Popen(
            command, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT, 
            text=True,
            encoding="utf-8",
            errors="replace"
        )
        await run_and_capture(training_process, "train")
        
        if training_process.returncode != 0:
            await broadcast_log("Training failed.\n", "train")
            return
        
        await broadcast_log("\n--- Training Finished Successfully ---\n", "train")
        
        if config.shutdown:
            await broadcast_log("\n⚠️ シャットダウン命令を受信しました。60秒後にPCをシャットダウンします。\n", "train")
            await broadcast_log("中止する場合はコマンドプロンプトで 'shutdown /a' と入力してください。\n", "train")
            os.system("shutdown /s /t 60")
        
    except Exception as e:
        await broadcast_log(f"Critical Error in process chain: {str(e)}\n", "train")

async def run_and_capture(process, type):
    loop = asyncio.get_event_loop()
    while True:
        line = await loop.run_in_executor(None, process.stdout.readline)
        if not line:
            break
        
        # Filter out noisy but harmless warnings
        if "triton not found" in line or "not compatible with the current PyTorch installation" in line:
            continue

        # Detect missing dependencies
        if "ModuleNotFoundError" in line:
            missing_module = line.split("named")[-1].strip().replace("'", "")
            advice = f"\n[ADVICE] ライブラリ '{missing_module}' が不足しているようです。\n[ADVICE] 「学習エンジンの自動取得 / Setup Training Engine」ボタンをクリックして、セットアップをやり直してください。\n"
            await broadcast_log(advice, type)
            
        await broadcast_log(line, type)
    process.wait()
    await broadcast_log(f"\n--- {type.upper()} Finished ---\n", type)

@app.get("/api/browse-folder")
async def browse_folder():
    try:
        # Open folder dialog
        folder_path = filedialog.askdirectory(title="Select Folder")
        if folder_path:
            return {"path": folder_path}
        return {"path": ""}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/browse-file")
async def browse_file():
    try:
        # Open file dialog
        file_path = filedialog.askopenfilename(
            title="Select Base Model",
            filetypes=[("Safetensors", "*.safetensors"), ("All Files", "*.*")]
        )
        if file_path:
            return {"path": file_path}
        return {"path": ""}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/gpu-info")
async def get_gpu_info():
    try:
        # Try to use nvidia-smi
        process = subprocess.Popen(
            ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate()
        if process.returncode == 0 and stdout:
            parts = stdout.strip().split(', ')
            if len(parts) >= 2:
                return {"name": parts[0], "memory": parts[1]}
        return {"name": "Unknown GPU (or no NVIDIA GPU found)", "memory": "N/A"}
    except FileNotFoundError:
        return {"name": "nvidia-smi not found (CPU only or non-NVIDIA)", "memory": "N/A"}
    except Exception as e:
        return {"name": "Error getting GPU info", "memory": str(e)}

@app.get("/api/check-scripts")
async def check_scripts():
    internal_scripts = os.path.join(os.path.dirname(__file__), "sd-scripts")
    exists = os.path.exists(os.path.join(internal_scripts, "sdxl_train_network.py"))
    return {"exists": exists, "path": internal_scripts if exists else ""}

@app.post("/api/setup-scripts")
async def setup_scripts():
    internal_scripts = os.path.join(os.path.dirname(__file__), "sd-scripts")
    if os.path.exists(internal_scripts):
        # Even if it exists, let's allow running pip install again if needed
        # but for now, let's just trigger the task
        pass
    
    try:
        asyncio.create_task(setup_scripts_task(internal_scripts))
        return {"status": "started", "message": "Setup started..."}
    except Exception as e:
        return {"status": "error", "message": f"Error: {str(e)}"}

async def setup_scripts_task(internal_scripts: str):
    import sys
    try:
        setup_script = os.path.join(os.path.dirname(__file__), "setup_check.py")
        if not os.path.exists(setup_script):
            await broadcast_log(f"Error: {setup_script} not found.\n", "train")
            return

        process = subprocess.Popen(
            [sys.executable, setup_script],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace"
        )
        await run_and_capture(process, "train")
        
        if process.returncode == 0:
            await broadcast_log("\n--- Setup Fully Completed ---\n", "train")
        else:
            await broadcast_log("\n--- Setup Failed. Check logs above. ---\n", "train")
            
    except Exception as e:
        await broadcast_log(f"Setup Error: {str(e)}\n", "train")

@app.get("/api/dataset/images")
async def list_images(path: str):
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Path not found")
    
    files = []
    for f in os.listdir(path):
        ext = os.path.splitext(f)[1].lower()
        if ext in IMAGE_EXTENSIONS:
            base = os.path.splitext(f)[0]
            txt_path = os.path.join(path, base + ".txt")
            tags = []
            if os.path.exists(txt_path):
                with open(txt_path, "r", encoding="utf-8") as tf:
                    raw_tags = tf.read().split(",")
                    for t in raw_tags:
                        t = t.strip()
                        if t:
                            tags.append({"name": t, "category": get_tag_category(t)})
            
            files.append({
                "name": f,
                "path": os.path.join(path, f),
                "tags": tags
            })
    return {"files": files}

class TagUpdate(BaseModel):
    path: str
    tags: list[str]

@app.post("/api/dataset/update-tags")
async def update_tags(update: TagUpdate):
    # 'update.path' is the image path, we need the .txt path
    base = os.path.splitext(update.path)[0]
    txt_path = base + ".txt"
    try:
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(", ".join(update.tags))
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from fastapi.responses import FileResponse
@app.get("/api/image")
async def get_image(path: str):
    if not os.path.exists(path):
        raise HTTPException(status_code=404)
    return FileResponse(path)

class TaggerConfig(BaseModel):
    path: str
    model: str = ""
    output_dir: str = ""
    name: str = ""
    vram: str = ""
    epochs: int = 1
    lr: str = ""

@app.post("/api/run-tagger")
async def run_tagger(config: TaggerConfig):
    global tagging_logs
    
    tagger_script = os.path.join(os.path.dirname(__file__), "bundled_tagger.py")

    command = [
        sys.executable, tagger_script,
        f"--train_data_dir={config.path}"
    ]
    
    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace"
        )
        asyncio.create_task(run_and_capture(process, "tagger"))
        return {"status": "started"}
    except Exception as e:
        return {"status": "error", "message": str(e)}



# capture_logs() was removed (dead code - superseded by run_and_capture() with WebSocket broadcast)

# Serve frontend
app.mount("/", StaticFiles(directory="../frontend", html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
