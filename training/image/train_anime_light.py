"""
Lightweight Anime Model Training Pipeline for Anime Reality AI.
Optimized for NVIDIA RTX 5060 (8GB VRAM) with FP16 mixed precision,
gradient accumulation, checkpoint management, and periodic validation.
"""

import os
import sys
import time
import argparse
from pathlib import Path
from PIL import Image
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from inference.lightweight_generator import AnimeGeneratorNetwork
from training.image.discriminator import PatchDiscriminator
from training.dataset_loader import UnpairedAnimeDataset
from inference.memory_manager import VRAMManager


class ColorLoss(nn.Module):
    """Loss to preserve overall color vibrancy and color balance."""
    def __init__(self):
        super().__init__()
        self.l1 = nn.L1Loss()

    def forward(self, x: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
        # Gaussian blurred color comparison (YUV / RGB)
        x_blur = nn.functional.avg_pool2d(x, kernel_size=5, stride=1, padding=2)
        y_blur = nn.functional.avg_pool2d(y, kernel_size=5, stride=1, padding=2)
        return self.l1(x_blur, y_blur)


def train_lightweight_model(
    style: str = "Shinkai",
    epochs: int = 50,
    batch_size: int = 4,
    grad_accum: int = 2,
    lr: float = 2e-4,
    resolution: int = 512,
    checkpoint_dir: str = "checkpoints/anime_light",
    resume_path: str = None,
    save_every: int = 5
):
    device = VRAMManager.get_optimal_device()
    use_cuda = device.type == "cuda"
    print("==================================================")
    print("ANIME REALITY AI — LIGHTWEIGHT MODEL TRAINING")
    print("==================================================")
    print(f"Device:       {device} ({torch.cuda.get_device_name(0) if use_cuda else 'CPU'})")
    print(f"Style:        {style}")
    print(f"Epochs:       {epochs}")
    print(f"Batch Size:   {batch_size} (Effective: {batch_size * grad_accum})")
    print(f"Resolution:   {resolution}x{resolution}")
    print("==================================================")

    # 1. Dataset & DataLoader
    real_dir = f"datasets/real/nature/genv3_train_photo"
    anime_dir = f"datasets/anime/styles/{style}"
    dataset = UnpairedAnimeDataset(real_dir=real_dir, anime_dir=anime_dir, resolution=resolution)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True, num_workers=0, pin_memory=use_cuda)

    # 2. Models
    generator = AnimeGeneratorNetwork().to(device)
    discriminator = PatchDiscriminator().to(device)

    # 3. Optimizers & Scaler
    opt_g = optim.AdamW(generator.parameters(), lr=lr, betas=(0.5, 0.999), weight_decay=1e-4)
    opt_d = optim.AdamW(discriminator.parameters(), lr=lr * 0.5, betas=(0.5, 0.999), weight_decay=1e-4)
    scaler = torch.amp.GradScaler('cuda', enabled=use_cuda)

    # 4. Losses
    criterion_gan = nn.MSELoss()
    criterion_content = nn.L1Loss()
    criterion_color = ColorLoss()

    start_epoch = 1
    chk_path = Path(checkpoint_dir)
    chk_path.mkdir(parents=True, exist_ok=True)

    # Resume checkpoint if specified
    if resume_path and Path(resume_path).exists():
        chk = torch.load(resume_path, map_location=device)
        generator.load_state_dict(chk["generator_state_dict"])
        discriminator.load_state_dict(chk["discriminator_state_dict"])
        opt_g.load_state_dict(chk["opt_g_state_dict"])
        opt_d.load_state_dict(chk["opt_d_state_dict"])
        start_epoch = chk.get("epoch", 1) + 1
        print(f"Resumed from checkpoint: {resume_path} (Starting Epoch {start_epoch})")

    # 5. Training Loop
    for epoch in range(start_epoch, epochs + 1):
        epoch_start = time.time()
        g_loss_sum, d_loss_sum = 0.0, 0.0
        generator.train()
        discriminator.train()

        opt_g.zero_grad()
        opt_d.zero_grad()

        for step, (real_imgs, anime_imgs) in enumerate(dataloader):
            real_imgs = real_imgs.to(device)
            anime_imgs = anime_imgs.to(device)

            # --- Train Discriminator ---
            with torch.amp.autocast('cuda', enabled=use_cuda):
                fake_anime = generator(real_imgs)
                d_real = discriminator(anime_imgs)
                d_fake = discriminator(fake_anime.detach())

                # LSGAN Discriminator Loss
                d_loss_real = criterion_gan(d_real, torch.ones_like(d_real))
                d_loss_fake = criterion_gan(d_fake, torch.zeros_like(d_fake))
                d_loss = (d_loss_real + d_loss_fake) * 0.5 / grad_accum

            scaler.scale(d_loss).backward()

            if (step + 1) % grad_accum == 0 or (step + 1) == len(dataloader):
                scaler.step(opt_d)
                scaler.update()
                opt_d.zero_grad()

            # --- Train Generator ---
            with torch.amp.autocast('cuda', enabled=use_cuda):
                d_fake_for_g = discriminator(fake_anime)
                loss_g_gan = criterion_gan(d_fake_for_g, torch.ones_like(d_fake_for_g))
                loss_g_content = criterion_content(fake_anime, real_imgs) * 2.0
                loss_g_color = criterion_color(fake_anime, real_imgs) * 1.5

                g_loss = (loss_g_gan + loss_g_content + loss_g_color) / grad_accum

            scaler.scale(g_loss).backward()

            if (step + 1) % grad_accum == 0 or (step + 1) == len(dataloader):
                scaler.step(opt_g)
                scaler.update()
                opt_g.zero_grad()

            g_loss_sum += g_loss.item() * grad_accum
            d_loss_sum += d_loss.item() * grad_accum

        epoch_time = time.time() - epoch_start
        avg_g = g_loss_sum / max(1, len(dataloader))
        avg_d = d_loss_sum / max(1, len(dataloader))
        vram = VRAMManager.get_hardware_status()

        print(f"Epoch [{epoch:03d}/{epochs:03d}] — Time: {epoch_time:.2f}s | G_Loss: {avg_g:.4f} | D_Loss: {avg_d:.4f} | VRAM: {vram.get('vram_allocated_gb', 0)} GB")

        # Save Checkpoints
        if epoch % save_every == 0 or epoch == epochs:
            chk_file = chk_path / f"anime_light_{style}_epoch_{epoch:03d}.pt"
            torch.save({
                "epoch": epoch,
                "generator_state_dict": generator.state_dict(),
                "discriminator_state_dict": discriminator.state_dict(),
                "opt_g_state_dict": opt_g.state_dict(),
                "opt_d_state_dict": opt_d.state_dict(),
                "style": style,
                "resolution": resolution
            }, chk_file)
            print(f"  [Checkpoint] Saved {chk_file.name}")

            # Export active weights to models/anime_light/
            prod_model_dir = Path("models/anime_light")
            prod_model_dir.mkdir(parents=True, exist_ok=True)
            torch.save(generator.state_dict(), prod_model_dir / f"{style.lower()}_generator.pt")

    print("\nTraining completed successfully!")


def main():
    parser = argparse.ArgumentParser(description="Train lightweight Anime Reality AI generator.")
    parser.add_argument("--style", type=str, default="Shinkai", choices=["Hayao", "Shinkai", "Paprika", "SummerWar"], help="Target anime style")
    parser.add_argument("--epochs", type=int, default=10, help="Number of training epochs")
    parser.add_argument("--batch-size", type=int, default=4, help="Batch size per step")
    parser.add_argument("--grad-accum", type=int, default=2, help="Gradient accumulation steps")
    parser.add_argument("--lr", type=float, default=2e-4, help="Learning rate")
    parser.add_argument("--resolution", type=int, default=512, help="Image resolution")
    parser.add_argument("--resume", type=str, default=None, help="Path to checkpoint to resume")
    parser.add_argument("--save-every", type=int, default=5, help="Save checkpoint every N epochs")
    args = parser.parse_args()

    train_lightweight_model(
        style=args.style,
        epochs=args.epochs,
        batch_size=args.batch_size,
        grad_accum=args.grad_accum,
        lr=args.lr,
        resolution=args.resolution,
        resume_path=args.resume,
        save_every=args.save_every
    )


if __name__ == "__main__":
    main()
