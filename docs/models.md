# Model Strategy & Registry — Anime Reality AI

## Multi-Tier Model Strategy

### Model A: Lightweight Feed-Forward Anime Generator
- **Architecture**: AnimeGANv2 / Fast Image-to-Image ResNet-UNet
- **Use Case**: Real-time photo transformation and fast video translation.
- **VRAM**: < 2 GB
- **Speed**: < 50ms per frame

### Model B: Anime Style LoRA with Latent Diffusion
- **Architecture**: Stable Diffusion 1.5 / SDXL + Anime Style LoRA
- **Use Case**: High-fidelity artistic transformations with fine-grained style conditioning (Watercolor, Fantasy, Cyberpunk).
- **VRAM**: 4–6 GB (FP16)
- **Speed**: 1–3s per 512x512 image

### Model C: Video Diffusion with Temporal Motion Module
- **Architecture**: AnimateDiff / AnimateLCM + ControlNet (Depth + Lineart)
- **Use Case**: High-end cinematic video transformation with structural preservation.
- **VRAM**: 6–8 GB (with VAE tiling and attention slicing)
- **Speed**: 4–8 FPS generation speed
