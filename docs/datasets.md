# Dataset Strategy & Pipeline — Anime Reality AI

## Dataset Directory Structure
```
datasets/
├── real/
│   ├── people/
│   ├── buildings/
│   ├── roads/
│   ├── vehicles/
│   ├── nature/
│   ├── animals/
│   └── objects/
├── anime/
│   ├── people/
│   ├── buildings/
│   ├── roads/
│   ├── vehicles/
│   ├── nature/
│   ├── animals/
│   └── objects/
├── real_video/
└── anime_video/
```

## Ingested Datasets & Taxonomy

The dataset repository has been structured into clean functional domains:

### 1. Real-World Datasets (`datasets/real/`) — 379,291 Assets (47.9 GB)
* **Roads & Urban Driving (`datasets/real/roads/bdd100k`)**: BDD100K driving dataset with 120,000+ street/building/vehicle images, segmentation masks, and bounding labels.
* **Objects & Everyday Scenes (`datasets/real/objects/coco2017`)**: MS COCO 2017 complete dataset (163,957 images) containing 80 object categories across people, animals, vehicles, indoor/outdoor scenes.
* **Object Detection Benchmarks (`datasets/real/objects/real_image`)**: ODS_New dataset with 17,326 real-world scenes.
* **Human Action & Interaction (`datasets/real/people/real_image_2`)**: 17,754 real-world images.
* **Nature & Paired Scenery (`datasets/real/nature/genv3_*`)**: AnimeGAN paired real photography (`train_photo`, `val`, `test`).

### 2. Anime & Stylized Datasets (`datasets/anime/`) — 138,707 Assets (1.23 GB)
* **Style Signatures (`datasets/anime/styles/`)**:
  * `Hayao`: Studio Ghibli / Hayao Miyazaki aesthetics (smooth lines, lush nature palette).
  * `Shinkai`: Makoto Shinkai aesthetics (luminous skies, hyper-detailed cloudscapes, rich atmospheric lighting).
  * `Paprika`: Satoshi Kon / Paprika aesthetic (bold lines, stylized color gradients).
  * `SummerWar`: Mamoru Hosoda / Summer Wars aesthetic (clean cel-shading, vibrant summer tones).
* **Anime Series & Scenery (`datasets/anime/series/`)**: 62,400+ anime scenery and character frames indexed across popular animation series.

### 3. Video Transformation Datasets (`datasets/real_video/`) — 142,547 Assets (10.1 GB)
* **Action Video Clips (`datasets/real_video/clips/`)**: 13,451 UCF101 real-world video clips (.avi) partitioned into `train`, `val`, and `test`.
* **Sequential Video Frames (`datasets/real_video/frames/HMDB51`)**: 129,093 extracted temporal video frames across 51 human action categories for temporal consistency benchmarks.

---

## Dataset Preprocessing Pipeline
1. **Ingestion & Organization**: Automatically sorts raw datasets into the official taxonomy.
   ```powershell
   python scripts/dataset/organize_datasets.py
   ```
2. **Validation**: Check file integrity and remove corrupted/truncated images.
   ```powershell
   python scripts/dataset/validate_dataset.py --dir datasets --remove-corrupt
   ```
3. **Deduplication**: Remove exact and perceptual near duplicates.
   ```powershell
   python scripts/dataset/remove_duplicates.py --dir datasets --perceptual --delete
   ```
4. **Ingestion & Standardized Resizing**: Standardize resolution (512x512) and center-crop.
   ```powershell
   python scripts/dataset/prepare_real_dataset.py --input datasets/real/nature/genv3_train_photo --category nature
   python scripts/dataset/prepare_anime_dataset.py --input datasets/anime/styles/Shinkai --category nature --style default
   ```
5. **Metadata & Splitting**:
   ```powershell
   python scripts/dataset/create_metadata.py --root datasets
   python scripts/dataset/split_dataset.py --root datasets --train-ratio 0.8 --val-ratio 0.1 --test-ratio 0.1
   ```
