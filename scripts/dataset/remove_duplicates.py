"""
Duplicate Image Detection & Cleanup for Anime Reality AI.
Computes image hashes to identify exact and near duplicates.
"""

import hashlib
import argparse
from pathlib import Path
from PIL import Image

def get_file_md5(file_path: Path) -> str:
    hasher = hashlib.md5()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()

def get_dhash(file_path: Path, hash_size: int = 8) -> int:
    """Computes difference hash (dHash) for fast perceptual duplicate matching."""
    try:
        with Image.open(file_path) as img:
            img = img.convert("L").resize((hash_size + 1, hash_size), Image.Resampling.LANCZOS)
            # Convert to flattened pixel values
            pixels = list(getattr(img, "get_flattened_data", img.getdata)())
            
            diff = []
            for row in range(hash_size):
                for col in range(hash_size):
                    left_pixel = pixels[row * (hash_size + 1) + col]
                    right_pixel = pixels[row * (hash_size + 1) + col + 1]
                    diff.append(left_pixel > right_pixel)
            
            # Convert boolean array to integer hash
            decimal_value = 0
            for index, value in enumerate(diff):
                if value:
                    decimal_value += 1 << index
            return decimal_value
    except Exception:
        return 0

def remove_duplicates(dataset_dir: str, dry_run: bool = True, perceptual: bool = False):
    root_path = Path(dataset_dir)
    if not root_path.exists():
        print(f"Directory {dataset_dir} does not exist.")
        return

    seen_hashes = {}
    duplicates = []
    
    print(f"Scanning for duplicates in: {root_path.resolve()} (Perceptual: {perceptual})")
    
    for file_path in root_path.rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}:
            img_hash = get_dhash(file_path) if perceptual else get_file_md5(file_path)
            
            if img_hash in seen_hashes:
                duplicates.append((file_path, seen_hashes[img_hash]))
                print(f"[DUPLICATE] {file_path.name} == {seen_hashes[img_hash].name}")
                if not dry_run:
                    file_path.unlink()
                    print(f"            Deleted {file_path.name}")
            else:
                seen_hashes[img_hash] = file_path
                
    print("\n" + "=" * 50)
    print(f"Total Unique Images:   {len(seen_hashes)}")
    print(f"Duplicates Detected:   {len(duplicates)}")
    if dry_run and len(duplicates) > 0:
        print("Note: Run with --delete to actually remove duplicate files.")
    print("=" * 50)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find and remove duplicate images in datasets.")
    parser.add_argument("--dir", type=str, required=True, help="Path to dataset directory")
    parser.add_argument("--delete", action="store_true", help="Permanently delete duplicate files")
    parser.add_argument("--perceptual", action="store_true", help="Use perceptual difference hashing")
    args = parser.parse_args()
    
    remove_duplicates(args.dir, dry_run=not args.delete, perceptual=args.perceptual)
