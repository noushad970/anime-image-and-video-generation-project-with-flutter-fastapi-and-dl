# System Architecture — Anime Reality AI

## Overview
Anime Reality AI is an end-to-end computer vision and generative AI platform designed to transform real-world photos and continuous video streams into stylized anime visuals while strictly maintaining temporal consistency, scene geometry, and human pose.

```
Flutter Mobile App (Android)
       |
       |  HTTP (REST) / WebSockets (Real-time progress)
       v
FastAPI Backend
       |
       v
AI Processing & Inference Engine
       |
       +---> Image Pipeline (Lightweight CNN / LoRA Latent Diffusion)
       |
       +---> Video Pipeline (Temporal Attention / Optical Flow / AnimateDiff / ControlNet)
       |
       +---> Conditioning & Geometry (OpenPose / MiDaS Depth / Canny Lineart)
       |
       v
Hardware Layer (NVIDIA GeForce RTX 5060 8GB VRAM)
```

## Hardware Optimization Strategy (8 GB VRAM)
1. **VAE Slicing & Tiling**: Large spatial latents are decoded in tiled chunks to prevent out-of-memory spikes during high-res frame reconstruction.
2. **Attention Slicing**: Self-attention computation is partitioned into smaller heads.
3. **Sequential & Model CPU Offloading**: Components (Text Encoder, UNet, VAE, ControlNet) are streamed in and out of GPU memory as needed during video generation passes.
4. **FP16 / BF16 Half Precision**: All weights and activations execute in mixed precision.
5. **Frame Batching**: Video frames are processed in tight, memory-bounded sliding batches with latent continuity.
