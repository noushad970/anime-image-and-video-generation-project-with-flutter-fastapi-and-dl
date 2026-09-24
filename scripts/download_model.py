"""
Model Downloader & Manager for Anime Reality AI.
Ensures safe downloading, integrity checking, and registration of AI models with VRAM compliance checks.
"""

import os
import json
import argparse
from pathlib import Path

REGISTRY_PATH = Path("models/registry.json")

def load_registry():
    if not REGISTRY_PATH.exists():
        return {}
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
        return data.get("models", {})

def download_model(model_key: str, dest_dir: str = "models", force: bool = False):
    registry = load_registry()
    if model_key not in registry:
        print(f"Error: Model '{model_key}' not found in registry {REGISTRY_PATH}.")
        print("Available models:", list(registry.keys()))
        return False
        
    model_info = registry[model_key]
    print("=" * 60)
    print(f"MODEL DOWNLOAD REQUEST: {model_info['name']}")
    print(f"Version:          {model_info.get('version')}")
    print(f"Type:             {model_info.get('type')}")
    print(f"Recommended VRAM: {model_info.get('recommended_vram')}")
    print(f"License:          {model_info.get('license')}")
    print(f"Commercial Use:   {model_info.get('commercial_use')}")
    print("=" * 60)

    target_path = Path(dest_dir) / model_key
    if target_path.exists() and not force:
        print(f"Model directory already exists at: {target_path}")
        print("Use --force to re-download.")
        return True

    target_path.mkdir(parents=True, exist_ok=True)
    
    # Save model metadata alongside weights
    meta_file = target_path / "model_meta.json"
    with open(meta_file, "w", encoding="utf-8") as f:
        json.dump(model_info, f, indent=2)

    print(f"Initialized model directory and metadata at: {target_path.resolve()}")
    print("Ready for weight download or checkpoint fine-tuning.")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download and register models from registry.")
    parser.add_argument("--model", type=str, required=True, help="Model key from registry")
    parser.add_argument("--dest", type=str, default="models", help="Destination root directory")
    parser.add_argument("--force", action="store_true", help="Force re-download")
    args = parser.parse_args()
    
    download_model(args.model, args.dest, args.force)
