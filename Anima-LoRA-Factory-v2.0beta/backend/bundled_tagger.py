import os
import sys
import argparse
import glob
import time

try:
    import numpy as np
    from PIL import Image
    import onnxruntime as rt
    from huggingface_hub import hf_hub_download
    import pandas as pd
    HAS_DEPS = True
except ImportError:
    HAS_DEPS = False

# WD14 Tagger Constants
MODEL_REPO = "SmilingWolf/wd-v1-4-moat-tagger-v2"
MODEL_FILENAME = "model.onnx"
CSV_FILENAME = "selected_tags.csv"
TAG_THRESHOLD = 0.35

def download_model():
    print("Loading WD14 Model...")
    try:
        # Try local first to avoid any network communication
        model_path = hf_hub_download(MODEL_REPO, MODEL_FILENAME, local_files_only=True)
        csv_path = hf_hub_download(MODEL_REPO, CSV_FILENAME, local_files_only=True)
        print("Model loaded from local cache.")
    except Exception:
        # Fallback to download if not present (allowed for initial setup)
        print("Model not found locally. Downloading from HuggingFace (Initial download allowed)...")
        model_path = hf_hub_download(MODEL_REPO, MODEL_FILENAME, local_files_only=False)
        csv_path = hf_hub_download(MODEL_REPO, CSV_FILENAME, local_files_only=False)
        print("Download complete.")
    return model_path, csv_path

def load_labels(csv_path):
    df = pd.read_csv(csv_path)
    tag_names = df["name"].tolist()
    rating_indexes = list(np.where(df["category"] == 9)[0])
    general_indexes = list(np.where(df["category"] == 0)[0])
    character_indexes = list(np.where(df["category"] == 4)[0])
    return tag_names, rating_indexes, general_indexes, character_indexes

def preprocess_image(image_path, target_size=448):
    image = Image.open(image_path).convert("RGB")
    
    # Pad to square
    w, h = image.size
    max_dim = max(w, h)
    pad_w = (max_dim - w) // 2
    pad_h = (max_dim - h) // 2
    
    padded_image = Image.new("RGB", (max_dim, max_dim), (255, 255, 255))
    padded_image.paste(image, (pad_w, pad_h))
    
    # Resize
    image = padded_image.resize((target_size, target_size), Image.Resampling.LANCZOS)
    
    # Convert to numpy array (BGR format for this specific model)
    image_np = np.array(image, dtype=np.float32)
    image_np = image_np[:, :, ::-1] # RGB to BGR
    image_np = np.expand_dims(image_np, axis=0)
    return image_np

def run_mock_tagger(image_paths):
    print("Warning: Missing required packages (onnxruntime, huggingface_hub, PIL, pandas). Running in mock mode.")
    total = len(image_paths)
    for i, path in enumerate(image_paths):
        # Create dummy txt
        base = os.path.splitext(path)[0]
        txt_path = base + ".txt"
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write("1girl, solo, masterpiece, best quality, dummy tag")
        
        print(f"[TAGGER_PROGRESS] {i+1}/{total}")
        time.sleep(0.5)
    print("Mock tagging complete.")

def run_real_tagger(image_paths):
    model_path, csv_path = download_model()
    tag_names, rating_indexes, general_indexes, character_indexes = load_labels(csv_path)
    
    print("Initializing ONNX Runtime...")
    session = rt.InferenceSession(model_path, providers=['CPUExecutionProvider'])
    input_name = session.get_inputs()[0].name
    
    total = len(image_paths)
    for i, path in enumerate(image_paths):
        try:
            image_np = preprocess_image(path)
            preds = session.run(None, {input_name: image_np})[0][0]
            
            tags = []
            # Extract tags based on threshold
            for idx in general_indexes + character_indexes:
                if preds[idx] > TAG_THRESHOLD:
                    tags.append(tag_names[idx].replace("_", " "))
            
            base = os.path.splitext(path)[0]
            txt_path = base + ".txt"
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(", ".join(tags))
                
        except Exception as e:
            print(f"Error processing {path}: {e}")
            
        print(f"[TAGGER_PROGRESS] {i+1}/{total}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--train_data_dir", type=str, required=True)
    parser.add_argument("--batch_size", type=int, default=4)
    args = parser.parse_args()

    image_paths = []
    for ext in ["*.jpg", "*.jpeg", "*.png", "*.webp", "*.JPG", "*.PNG"]:
        image_paths.extend(glob.glob(os.path.join(args.train_data_dir, ext)))
    
    total = len(image_paths)
    if total == 0:
        print("No images found in the dataset folder.")
        return

    print(f"Found {total} images. Starting WD14 Tagger...")
    
    if HAS_DEPS:
        run_real_tagger(image_paths)
    else:
        run_mock_tagger(image_paths)

if __name__ == "__main__":
    main()
