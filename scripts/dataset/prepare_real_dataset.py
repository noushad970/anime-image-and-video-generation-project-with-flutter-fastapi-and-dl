"""
Real-World Dataset Preparation Pipeline for Anime Reality AI.
Standardizes, resizes, center-crops, and categorizes real-world scene images.
"""

import os
import argparse
from pathlib import Path
from PIL import Image

CATEGORIES = ["people", "buildings", "roads", "vehicles", "nature", "animals", "objects"]

def process_image(src_path: Path, dest_path: Path, resolution: int = 512, quality: int = 95):
    try:
        with Image.open(src_path) as img:
            img = img.convert("RGB")
            w, h = img.size
            scale = resolution / min(w, h)
            new_w, new_h = int(w * scale), int(h * scale)
            img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            
            # Center crop
            left = (new_w - resolution) // 2
            top = (new_h - resolution) // 2
            right = left + resolution
            bottom = top + resolution
            img_cropped = img.crop((left, top, right, bottom))
            
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            img_cropped.save(dest_path, "JPEG", quality=quality)
            return True
    except Exception as e:
        print(f"Error processing {src_path.name}: {e}")
        return False

def prepare_real_dataset(input_dir: str, output_dir: str, category: str = "nature", resolution: int = 512):
    src_root = Path(input_dir)
    dest_root = Path(output_dir) / "real" / category
    
    if not src_root.exists():
        print(f"Source directory '{input_dir}' not found.")
        return
        
    dest_root.mkdir(parents=True, exist_ok=True)
    count = 0
    
    for file_path in src_root.rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}:
            dest_file = dest_root / f"real_{category}_{count:06d}.jpg"
            if process_image(file_path, dest_file, resolution=resolution):
                count += 1
                
    print(f"Successfully processed {count} real-world images into {dest_root}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prepare real-world image datasets.")
    parser.add_argument("--input", type=str, required=True, help="Input directory of raw images")
    parser.add_argument("--output", type=str, default="datasets", help="Output dataset root directory")
    parser.add_argument("--category", type=str, default="nature", choices=CATEGORIES, help="Scene category")
    parser.add_argument("--resolution", type=int, default=512, help="Target image resolution")
    args = parser.parse_args()
    
    prepare_real_dataset(args.input, args.output, args.category, args.resolution)
