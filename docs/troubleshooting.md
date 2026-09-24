# Troubleshooting Guide — Anime Reality AI

## Common Issues & Solutions

### 1. CUDA Out of Memory (OOM) during Generation
- **Symptom**: `RuntimeError: CUDA out of memory. Tried to allocate...`
- **Remedy**:
  1. Close background VRAM-heavy apps (Unreal Editor, BlueStacks, browser hardware acceleration).
  2. Enable VAE slicing: `pipe.enable_vae_slicing()`
  3. Enable VAE tiling: `pipe.enable_vae_tiling()`
  4. Enable attention slicing: `pipe.enable_attention_slicing()`
  5. Reduce batch size to 1 or lower image resolution to 512x512.

### 2. FFmpeg Not Found on Windows
- **Symptom**: `FileNotFoundError: ffmpeg executable not found`
- **Remedy**: Ensure FFmpeg is installed via winget (`winget install Gyan.FFmpeg.Essentials`) and on system PATH.

### 3. PyTorch not detecting CUDA on Windows
- **Symptom**: `torch.cuda.is_available() == False`
- **Remedy**: Reinstall PyTorch with the CUDA 12.8 wheel via:
  ```powershell
  uv pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128
  ```

### 4. Video Flickering / Temporal Inconsistency
- **Symptom**: Objects change color or morph textures between adjacent frames.
- **Remedy**:
  1. Increase ControlNet conditioning weight (0.75 - 1.0).
  2. Use optical flow latent initialization between adjacent frames.
  3. Switch from frame-by-frame mode to AnimateDiff temporal motion module.
