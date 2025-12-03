from huggingface_hub import snapshot_download
import os

def download_model():
    model_id = "runwayml/stable-diffusion-v1-5"
    local_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models", "stable-diffusion-v1-5")
    
    print(f"Downloading {model_id} to {local_dir}...")
    snapshot_download(repo_id=model_id, local_dir=local_dir, local_dir_use_symlinks=False, ignore_patterns=["*.safetensors", "*.onnx", "*.xml"])
    print("Download complete.")

if __name__ == "__main__":
    download_model()
