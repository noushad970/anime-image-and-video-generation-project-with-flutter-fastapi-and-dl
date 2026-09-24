"""
Dataset Metadata Generator for Anime Reality AI.
Scans the dataset directories and produces a comprehensive JSON metadata manifest
including file counts, resolutions, category distributions, and hashes.
"""

import json
import argparse
from pathlib import Path
from PIL import Image

def generate_dataset_metadata(dataset_root: str, output_json: str = "datasets/metadata.json"):
    root_path = Path(dataset_root)
    if not root_path.exists():
        print(f"Error: {dataset_root} does not exist.")
        return

    metadata = {
        "dataset_name": "Anime Reality AI Comprehensive Dataset",
        "version": "1.0.0",
        "categories": {},
        "statistics": {
            "total_real_images": 0,
            "total_anime_images": 0,
            "total_images": 0
        },
        "files": []
    }

    supported_ext = {".jpg", ".jpeg", ".png", ".webp"}

    for file_path in root_path.rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() in supported_ext:
            rel_path = file_path.relative_to(root_path).as_posix()
            parts = rel_path.split("/")
            
            domain = parts[0] if len(parts) > 0 else "unknown"  # real or anime
            category = parts[1] if len(parts) > 1 else "general"
            
            try:
                with Image.open(file_path) as img:
                    width, height = img.size
                    channels = len(img.getbands())
            except Exception:
                width, height, channels = 0, 0, 0
                
            file_entry = {
                "path": rel_path,
                "domain": domain,
                "category": category,
                "width": width,
                "height": height,
                "channels": channels,
                "size_bytes": file_path.stat().st_size
            }
            metadata["files"].append(file_entry)
            
            # Update counts
            if domain == "real":
                metadata["statistics"]["total_real_images"] += 1
            elif domain == "anime":
                metadata["statistics"]["total_anime_images"] += 1
                
            cat_key = f"{domain}/{category}"
            metadata["categories"][cat_key] = metadata["categories"].get(cat_key, 0) + 1

    metadata["statistics"]["total_images"] = len(metadata["files"])
    
    out_path = Path(output_json)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
        
    print(f"Dataset metadata successfully written to: {out_path.resolve()}")
    print(f"Real Images:  {metadata['statistics']['total_real_images']}")
    print(f"Anime Images: {metadata['statistics']['total_anime_images']}")
    print(f"Total:        {metadata['statistics']['total_images']}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create JSON metadata manifest for dataset.")
    parser.add_argument("--root", type=str, default="datasets", help="Root dataset directory")
    parser.add_argument("--output", type=str, default="datasets/metadata.json", help="Output metadata file path")
    args = parser.parse_args()
    
    generate_dataset_metadata(args.root, args.output)
