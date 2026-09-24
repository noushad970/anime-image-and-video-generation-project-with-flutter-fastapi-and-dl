# Anime Reality AI

> Transform real-world photos and continuous video into temporally consistent anime visual worlds on modern 8GB VRAM consumer GPUs.

---

## Key Capabilities
- **Photo to Anime**: Fast, high-fidelity stylization with custom LoRA and lightweight CNN inference.
- **Video to Anime**: Geometry-preserving and pose-consistent anime video generation with minimal flickering.
- **Temporal Consistency**: Built with optical flow latent warping, ControlNet depth/lineart conditioning, and video motion modules.
- **8 GB VRAM Architecture**: Optimized for NVIDIA GeForce RTX 5060 with VAE slicing, tiling, FP16 precision, and attention slicing.
- **Modular Ecosystem**: Decoupled Python AI inference engine, asynchronous FastAPI backend, and Flutter Android mobile client.

---

## Project Structure
```
├── backend/            # FastAPI async REST/WebSocket server & local job queue
├── configs/            # System & pipeline YAML configurations
├── datasets/           # Preprocessed real-world and anime-style dataset directories
├── docs/               # Technical architecture, setup, models, and video pipeline docs
├── inference/          # Standalone inference scripts (image_to_anime.py, etc.)
├── models/             # Registered model weights, LoRAs, and metadata registry
├── scripts/            # Environment checks, dataset prep, and model downloader
│   └── dataset/        # Validation, frame extraction, deduplication, metadata scripts
├── styles/             # Style definition presets (default, watercolor, fantasy, cyberpunk)
├── training/           # Image, LoRA, and video fine-tuning pipelines
├── video/              # Video processing, optical flow, and demuxing/muxing engine
├── .env.example        # Environment variable template
├── config.yaml         # Central hardware and generation configuration
├── ENVIRONMENT_REPORT.md # Diagnostic report of current hardware and toolchains
└── requirements.txt    # Python dependencies
```

---

## Quick Start

### 1. Verify GPU and Environment
```powershell
# Run GPU diagnostic
uv run python scripts/check_gpu.py
```

### 2. Dataset Management
```powershell
# Validate dataset images
python scripts/dataset/validate_dataset.py --dir datasets

# Remove duplicate images
python scripts/dataset/remove_duplicates.py --dir datasets --perceptual

# Extract frames from video
python scripts/dataset/extract_video_frames.py --video input.mp4 --output datasets/real_video/frames/ --fps 24
```

---

## Development Roadmap
- [x] **Phase 0: Environment Diagnostics & Hardware Verification** (Verified NVIDIA RTX 5060 8GB, PyTorch 2.11+cu128, FFmpeg 9.0.1, Flutter 3.47)
- [ ] **Phase 1: Dataset System & Small Target Ingestion**
- [ ] **Phase 2: Photo -> Anime Working Model (Milestone 1)**
- [ ] **Phase 3: Custom Anime Style LoRA Fine-Tuning**
- [ ] **Phase 4: Video -> Anime Pipeline with FFmpeg**
- [ ] **Phase 5: Temporal Consistency & ControlNet Conditioning**
- [ ] **Phase 6: Fast Video Model Benchmarking (AnimateDiff / AnimateLCM)**
- [ ] **Phase 7: FastAPI Asynchronous Backend & Job Queue**
- [ ] **Phase 8: Flutter Mobile App (Android)**
- [ ] **Phase 9: Real-Time Live Anime Camera**

---

## License & Compliance
All datasets and models used in this repository adhere strictly to their respective licenses (MIT, Apache-2.0, CreativeML OpenRAIL-M). Commercial use permissions and attribution requirements are recorded in `models/registry.json`.
