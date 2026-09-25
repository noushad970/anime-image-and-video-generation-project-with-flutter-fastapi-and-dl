import os
import sys
from pathlib import Path
from collections import Counter

sets_path = Path("datasets/Sets")
print("=== SCANNING DATASETS/SETS ===", flush=True)

if not sets_path.exists():
    print("datasets/Sets does not exist!", flush=True)
    sys.exit(1)

for item in sorted(sets_path.iterdir()):
    if not item.is_dir():
        continue
    
    print(f"\nAnalyzing: {item.name}...", flush=True)
    ext_counter = Counter()
    total_files = 0
    total_size = 0
    subdirs = set()
    sample_files = []

    for root, dirs, files in os.walk(item):
        rel_root = Path(root).relative_to(item).as_posix()
        if rel_root != ".":
            subdirs.add(rel_root.split("/")[0])
        for f in files:
            total_files += 1
            ext = Path(f).suffix.lower()
            ext_counter[ext] += 1
            full_p = os.path.join(root, f)
            try:
                total_size += os.path.getsize(full_p)
            except Exception:
                pass
            if len(sample_files) < 4:
                sample_files.append(Path(full_p).relative_to(item).as_posix())

    size_mb = total_size / (1024 * 1024)
    print(f"  Folder:       {item.name}")
    print(f"  Subfolders:   {sorted(list(subdirs))[:10]}")
    print(f"  Total Files:  {total_files} ({size_mb:.2f} MB)")
    print(f"  Extensions:   {dict(ext_counter)}")
    print(f"  Samples:      {sample_files}", flush=True)

print("\n=== SCAN COMPLETE ===", flush=True)
