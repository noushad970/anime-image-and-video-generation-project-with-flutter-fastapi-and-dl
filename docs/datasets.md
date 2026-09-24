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

## Dataset Preprocessing Pipeline
1. **Validation**: Check file integrity and remove corrupted/truncated images.
   ```powershell
   python scripts/dataset/validate_dataset.py --dir datasets --remove-corrupt
   ```
2. **Deduplication**: Remove exact and perceptual near duplicates.
   ```powershell
   python scripts/dataset/remove_duplicates.py --dir datasets --perceptual --delete
   ```
3. **Ingestion & Standardized Resizing**: Standardize resolution (512x512) and center-crop.
   ```powershell
   python scripts/dataset/prepare_real_dataset.py --input raw_real_images/ --category nature
   python scripts/dataset/prepare_anime_dataset.py --input raw_anime_images/ --category nature --style default
   ```
4. **Metadata & Splitting**:
   ```powershell
   python scripts/dataset/create_metadata.py --root datasets
   python scripts/dataset/split_dataset.py --root datasets --train-ratio 0.8 --val-ratio 0.1 --test-ratio 0.1
   ```
