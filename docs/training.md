# Training Guide — Anime Reality AI

## Training Principles on 8 GB VRAM (RTX 5060)

1. **Lightweight GAN / CNN Fine-Tuning**:
   - Batch size: 4–8 with gradient accumulation.
   - Mixed Precision: FP16 (`torch.cuda.amp`).
   - Resolution: 512x512.

2. **LoRA Fine-Tuning for Anime Diffusion**:
   - Rank: $r=8$ or $r=16$, Alpha: 16.
   - Batch size: 1 (gradient accumulation steps: 4–8).
   - Gradient Checkpointing: Enabled.
   - Memory-Efficient Attention: Enabled (`xformers` / PyTorch SDPA `scaled_dot_product_attention`).
   - Peak VRAM Target: < 6.5 GB.

## Monitoring & Checkpointing
- TensorBoard logging enabled in `training/runs/`.
- Automatic checkpoint rotation (keeping best 3 validation checkpoints).
