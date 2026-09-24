"""
Dataset Validation Utility for Anime Reality AI.
Scans image datasets for corruption, invalid dimensions, truncated bytes, and unsupported formats.
"""

import os
import sys
import argparse
from pathlib import Path
from PIL import Image

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}

def validate_image_file(file_path: Path):
    try:
        if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            return False, "Unsupported file extension"
        
        with Image.open(file_path) as img:
            img.verify()  # Verify image header and stream integrity
            
        with Image.open(file_path) as img:
            img.load()    # Load raw pixel data to catch truncated files
            width, height = img.size
            if width < 64 or height < 64:
                return False, f"Resolution too low: {width}x{height}"
            
        return True, "Valid"
    except Exception as e:
        return False, str(e)

def validate_dataset_directory(dataset_dir: str, remove_corrupt: bool = False):
    root_path = Path(dataset_dir)
    if not root_path.exists():
        print(f"Error: Directory '{dataset_dir}' does not exist.")
        return
    
    print(f"Validating dataset at: {root_path.resolve()}")
    valid_count = 0
    corrupt_count = 0
    corrupt_files = []
    
    for file_path in root_path.rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_EXTENSIONS:
            is_valid, reason = validate_image_file(file_path)
            if is_valid:
                valid_count += 1
            else:
                corrupt_count += 1
                corrupt_files.append((str(file_path), reason))
                print(f"[INVALID] {file_path.name} -> Reason: {reason}")
                if remove_corrupt:
                    try:
                        file_path.unlink()
                        print(f"          Removed: {file_path.name}")
                    except Exception as err:
                        print(f"          Failed to remove: {err}")
                        
    print("\n" + "=" * 50)
    print("DATASET VALIDATION SUMMARY")
    print("=" * 50)
    print(f"Total Valid Images:   {valid_count}")
    print(f"Total Corrupt/Bad:    {corrupt_count}")
    print(f"Health Score:         {(valid_count / (valid_count + corrupt_count) * 100) if (valid_count + corrupt_count) > 0 else 0:.2f}%")
    print("=" * 50)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate image files in dataset directory.")
    parser.add_argument("--dir", type=str, default="datasets", help="Path to dataset directory")
    parser.add_argument("--remove-corrupt", action="store_true", help="Automatically delete corrupt files")
    args = parser.parse_args()
    
    validate_dataset_directory(args.dir, args.remove_corrupt)
