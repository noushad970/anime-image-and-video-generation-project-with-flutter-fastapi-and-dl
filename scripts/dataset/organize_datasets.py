"""
Master Dataset Ingestion & Organization Script for Anime Reality AI.
Categorizes, sorts, and structures all images, videos, and anime assets from `datasets/Sets/`
into the official project taxonomy:
- datasets/real/{people, buildings, roads, vehicles, nature, animals, objects}
- datasets/anime/{styles, series, people, scenery, objects}
- datasets/real_video/{clips, frames}
- datasets/anime_video/
"""

import os
import sys
import shutil
from pathlib import Path

SETS_ROOT = Path("datasets/Sets")
TARGET_ROOT = Path("datasets")

def organize_datasets():
    if not SETS_ROOT.exists():
        print("datasets/Sets not found.")
        return

    print("==================================================")
    print("ANIME REALITY AI — DATASET INGESTION & ORGANIZATION")
    print("==================================================")

    # 1. Ensure target directories exist
    real_cats = ["people", "buildings", "roads", "vehicles", "nature", "animals", "objects"]
    anime_cats = ["styles", "series", "people", "buildings", "roads", "vehicles", "nature", "animals", "objects"]
    
    for cat in real_cats:
        (TARGET_ROOT / "real" / cat).mkdir(parents=True, exist_ok=True)
    for cat in anime_cats:
        (TARGET_ROOT / "anime" / cat).mkdir(parents=True, exist_ok=True)
    (TARGET_ROOT / "real_video" / "clips").mkdir(parents=True, exist_ok=True)
    (TARGET_ROOT / "real_video" / "frames").mkdir(parents=True, exist_ok=True)
    (TARGET_ROOT / "anime_video").mkdir(parents=True, exist_ok=True)

    # 2. Process Genv3 (AnimeGAN & Style sets)
    genv3 = SETS_ROOT / "Genv3"
    if genv3.exists():
        print("\n[1/6] Ingesting Genv3 (AnimeGAN Styles & Paired Real Photos)...")
        for style_dir in ["Hayao", "Paprika", "Shinkai", "SummerWar"]:
            src = genv3 / style_dir
            if src.exists():
                dest = TARGET_ROOT / "anime" / "styles" / style_dir
                if not dest.exists():
                    shutil.move(str(src), str(dest))
                    print(f"  Moved style set: {style_dir} -> anime/styles/{style_dir}")
        
        # Real paired photos from Genv3
        for real_sub in ["train_photo", "val", "test"]:
            src = genv3 / real_sub
            if src.exists():
                dest = TARGET_ROOT / "real" / "nature" / f"genv3_{real_sub}"
                if not dest.exists():
                    shutil.move(str(src), str(dest))
                    print(f"  Moved paired real photos: {real_sub} -> real/nature/genv3_{real_sub}")

    # 3. Process anime3 (Anime Series Library)
    anime3 = SETS_ROOT / "anime3"
    if anime3.exists():
        print("\n[2/6] Ingesting anime3 (Anime Series & Scenery Frames)...")
        data_dir = anime3 / "data" / "anime_images"
        if not data_dir.exists():
            data_dir = anime3
        
        target_series_dir = TARGET_ROOT / "anime" / "series"
        for series_folder in data_dir.iterdir():
            if series_folder.is_dir():
                dest = target_series_dir / series_folder.name
                if not dest.exists():
                    shutil.move(str(series_folder), str(dest))
        print(f"  Moved anime series library into datasets/anime/series/")

    # 4. Process video (UCF101 Real Action Video Clips)
    video_dir = SETS_ROOT / "video"
    if video_dir.exists():
        print("\n[3/6] Ingesting real action video clips (UCF101)...")
        for split in ["train", "val", "test"]:
            src = video_dir / split
            if src.exists():
                dest = TARGET_ROOT / "real_video" / "clips" / split
                if not dest.exists():
                    shutil.move(str(src), str(dest))
                    print(f"  Moved video split: {split} -> real_video/clips/{split}")

    # 5. Process archive (8) (HMDB51 Video Frame Sequences)
    archive8 = SETS_ROOT / "archive (8)"
    if archive8.exists():
        print("\n[4/6] Ingesting HMDB51 Action Video Frames...")
        hmdb_src = archive8 / "HMDB51"
        if hmdb_src.exists():
            dest = TARGET_ROOT / "real_video" / "frames" / "HMDB51"
            if not dest.exists():
                shutil.move(str(hmdb_src), str(dest))
                print("  Moved HMDB51 action video frames -> real_video/frames/HMDB51")

    # 6. Process archive (9) (BDD100K Urban, Road, Vehicle Dataset)
    archive9 = SETS_ROOT / "archive (9)"
    if archive9.exists():
        print("\n[5/6] Ingesting BDD100K Urban Driving & Street Scenes...")
        bdd_src = archive9 / "bdd100k"
        if bdd_src.exists():
            dest = TARGET_ROOT / "real" / "roads" / "bdd100k"
            if not dest.exists():
                shutil.move(str(bdd_src), str(dest))
                print("  Moved BDD100K road & vehicle imagery -> real/roads/bdd100k")

    # 7. Process real image sets (COCO 2017 & Object Detection Datasets)
    coco_dir = SETS_ROOT / "real image coco"
    if coco_dir.exists():
        print("\n[6/6] Ingesting COCO 2017 Real World Image Library...")
        coco_src = coco_dir / "coco2017"
        if coco_src.exists():
            dest = TARGET_ROOT / "real" / "objects" / "coco2017"
            if not dest.exists():
                shutil.move(str(coco_src), str(dest))
                print("  Moved COCO 2017 dataset -> real/objects/coco2017")

    # Process ODS_New and real image 2
    for real_set, sub_cat in [("real image", "objects"), ("real image 2", "people")]:
        set_path = SETS_ROOT / real_set
        if set_path.exists():
            dest = TARGET_ROOT / "real" / sub_cat / real_set.replace(" ", "_")
            if not dest.exists():
                shutil.move(str(set_path), str(dest))
                print(f"  Moved {real_set} -> real/{sub_cat}/{real_set.replace(' ', '_')}")

    print("\n==================================================")
    print("DATASET INGESTION COMPLETED SUCCESSFULLY!")
    print("==================================================")

if __name__ == "__main__":
    organize_datasets()
