"""
Dataset Train / Validation / Test Splitter for Anime Reality AI.
Creates deterministic train/val/test file lists or directory splits with reproducible random seed.
"""

import os
import json
import random
import argparse
from pathlib import Path

def split_dataset(dataset_root: str, output_dir: str = "datasets/splits", train_ratio: float = 0.8, val_ratio: float = 0.1, test_ratio: float = 0.1, seed: int = 42):
    random.seed(seed)
    root_path = Path(dataset_root)
    
    if not root_path.exists():
        print(f"Error: {dataset_root} does not exist.")
        return
        
    supported_ext = {".jpg", ".jpeg", ".png", ".webp"}
    images_by_domain = {"real": [], "anime": []}
    
    for file_path in root_path.rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() in supported_ext:
            rel_path = file_path.relative_to(root_path).as_posix()
            if rel_path.startswith("real/"):
                images_by_domain["real"].append(rel_path)
            elif rel_path.startswith("anime/"):
                images_by_domain["anime"].append(rel_path)
                
    splits = {}
    for domain, file_list in images_by_domain.items():
        random.shuffle(file_list)
        total = len(file_list)
        n_train = int(total * train_ratio)
        n_val = int(total * val_ratio)
        
        splits[f"{domain}_train"] = file_list[:n_train]
        splits[f"{domain}_val"] = file_list[n_train:n_train + n_val]
        splits[f"{domain}_test"] = file_list[n_train + n_val:]
        
        print(f"[{domain.upper()}] Total: {total} | Train: {len(splits[f'{domain}_train'])} | Val: {len(splits[f'{domain}_val'])} | Test: {len(splits[f'{domain}_test'])}")
        
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    
    for split_name, files in splits.items():
        split_file = out_dir / f"{split_name}.txt"
        with open(split_file, "w", encoding="utf-8") as f:
            for f_path in files:
                f.write(f"{f_path}\n")
                
    with open(out_dir / "split_manifest.json", "w", encoding="utf-8") as f:
        json.dump(splits, f, indent=2)
        
    print(f"\nSplit files successfully saved to: {out_dir.resolve()}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Split dataset into train, val, and test partitions.")
    parser.add_argument("--root", type=str, default="datasets", help="Root dataset directory")
    parser.add_argument("--output", type=str, default="datasets/splits", help="Output directory for split lists")
    parser.add_argument("--train-ratio", type=float, default=0.8, help="Train set ratio (default: 0.8)")
    parser.add_argument("--val-ratio", type=float, default=0.1, help="Validation set ratio (default: 0.1)")
    parser.add_argument("--test-ratio", type=float, default=0.1, help="Test set ratio (default: 0.1)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    args = parser.parse_args()
    
    split_dataset(args.root, args.output, args.train_ratio, args.val_ratio, args.test_ratio, args.seed)
