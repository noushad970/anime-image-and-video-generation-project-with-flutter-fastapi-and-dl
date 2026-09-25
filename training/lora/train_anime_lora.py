"""
Anime Style & Person LoRA Fine-Tuning Pipeline for Anime Reality AI.
Fine-tunes Stable Diffusion UNet cross-attention layers for authentic Anime Character & Style transformation.
Optimized for NVIDIA RTX 5060 (8GB VRAM) using PEFT, FP16 precision, and gradient accumulation.
"""

import os
import sys
import math
import time
import argparse
import random
from pathlib import Path
from typing import Optional, List
from PIL import Image
from tqdm import tqdm

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import torchvision.transforms as T
import torch.nn.functional as F

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from inference.memory_manager import VRAMManager


class AnimeDataset(Dataset):
    """
    Dataset loader for fine-tuning anime diffusion models with image-prompt pairs.
    """
    def __init__(
        self,
        image_dir: str,
        prompt: str = "masterpiece, best quality, authentic anime character, detailed anime portrait, vibrant colors, crisp clean anime lineart",
        resolution: int = 512,
        max_samples: Optional[int] = None
    ):
        self.image_paths = []
        p = Path(image_dir)
        valid_exts = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
        
        if p.exists():
            for f in p.rglob("*"):
                if f.is_file() and f.suffix.lower() in valid_exts:
                    self.image_paths.append(f)
                    if max_samples and len(self.image_paths) >= max_samples:
                        break

        self.prompt = prompt
        self.resolution = resolution
        self.transform = T.Compose([
            T.Resize(resolution, interpolation=T.InterpolationMode.BICUBIC),
            T.CenterCrop(resolution),
            T.RandomHorizontalFlip(p=0.5),
            T.ToTensor(),
            T.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5])
        ])

    def __len__(self) -> int:
        return max(len(self.image_paths), 1)

    def __getitem__(self, idx: int):
        if not self.image_paths:
            img_tensor = torch.zeros(3, self.resolution, self.resolution)
            return {"image": img_tensor, "prompt": self.prompt}
            
        img_path = self.image_paths[idx % len(self.image_paths)]
        try:
            with Image.open(img_path) as img:
                img_rgb = img.convert("RGB")
                img_tensor = self.transform(img_rgb)
        except Exception:
            # Fallback to random black tensor if corrupted image
            img_tensor = torch.zeros(3, self.resolution, self.resolution)

        return {"image": img_tensor, "prompt": self.prompt}


def train_anime_lora(
    dataset_dir: str = "datasets/anime/people",
    base_model_id: str = "runwayml/stable-diffusion-v1-5",
    output_dir: str = "models/anime_lora",
    lora_name: str = "anime_person_lora",
    prompt: str = "masterpiece, best quality, authentic anime character, detailed anime portrait, vibrant anime eyes, crisp lineart",
    rank: int = 16,
    alpha: int = 32,
    lr: float = 1e-4,
    epochs: int = 5,
    max_steps: Optional[int] = 500,
    max_samples: int = 2000,
    batch_size: int = 1,
    gradient_accumulation_steps: int = 4,
    save_steps: int = 100,
    device_name: Optional[str] = None
):
    """
    Executes parameter-efficient fine-tuning (LoRA) on the diffusion UNet.
    """
    device = VRAMManager.get_optimal_device(force_cpu=(device_name == "cpu"))
    dtype = torch.float16 if device.type == "cuda" else torch.float32

    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    print("==================================================")
    print("ANIME REALITY AI — DIFFUSION LoRA FINE-TUNING")
    print("==================================================")
    print(f"Base Model:       {base_model_id}")
    print(f"Dataset Dir:      {dataset_dir}")
    print(f"LoRA Output:      {out_path / (lora_name + '.safetensors')}")
    print(f"LoRA Rank / Alpha:{rank} / {alpha}")
    print(f"Target Device:    {device} ({dtype})")
    print("==================================================")

    from transformers import CLIPTextModel, CLIPTokenizer
    from diffusers import AutoencoderKL, UNet2DConditionModel, DDPMScheduler
    from peft import LoraConfig, get_peft_model

    print("[1/5] Loading tokenizer and text encoder...")
    tokenizer = CLIPTokenizer.from_pretrained(base_model_id, subfolder="tokenizer")
    text_encoder = CLIPTextModel.from_pretrained(base_model_id, subfolder="text_encoder", torch_dtype=dtype)
    text_encoder.to(device)
    text_encoder.requires_grad_(False)

    print("[2/5] Loading VAE...")
    vae = AutoencoderKL.from_pretrained(base_model_id, subfolder="vae", torch_dtype=dtype)
    vae.to(device)
    vae.requires_grad_(False)

    print("[3/5] Loading UNet and injecting LoRA adapters...")
    unet = UNet2DConditionModel.from_pretrained(base_model_id, subfolder="unet", torch_dtype=dtype)
    
    # Configure PEFT LoRA on cross-attention & attention projection layers
    lora_config = LoraConfig(
        r=rank,
        lora_alpha=alpha,
        init_lora_weights="gaussian",
        target_modules=["to_k", "to_q", "to_v", "to_out.0"]
    )
    unet = get_peft_model(unet, lora_config)
    unet.to(device)
    unet.train()

    noise_scheduler = DDPMScheduler.from_pretrained(base_model_id, subfolder="scheduler")

    print("[4/5] Preparing dataset & dataloader...")
    dataset = AnimeDataset(
        image_dir=dataset_dir,
        prompt=prompt,
        resolution=512,
        max_samples=max_samples
    )
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True, drop_last=True)
    print(f"  Training samples: {len(dataset.image_paths)}")

    # Optimizer
    optimizer = torch.optim.AdamW(unet.parameters(), lr=lr, betas=(0.9, 0.999), weight_decay=1e-2)
    lr_scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=max_steps or 500)

    print("\n[5/5] Starting Fine-Tuning loop...")
    global_step = 0
    total_loss = 0.0
    start_time = time.time()

    # Pre-tokenize common prompt
    text_inputs = tokenizer(
        prompt,
        padding="max_length",
        max_length=tokenizer.model_max_length,
        truncation=True,
        return_tensors="pt"
    ).input_ids.to(device)

    with torch.no_grad():
        encoder_hidden_states = text_encoder(text_inputs)[0]

    progress_bar = tqdm(total=max_steps, desc="LoRA Training Steps")

    for epoch in range(epochs):
        for batch in dataloader:
            images = batch["image"].to(device, dtype=dtype)

            # Encode image latents with VAE
            with torch.no_grad():
                latents = vae.encode(images).latent_dist.sample()
                latents = latents * vae.config.scaling_factor

            # Sample random noise & timesteps
            noise = torch.randn_like(latents)
            bsz = latents.shape[0]
            timesteps = torch.randint(0, noise_scheduler.config.num_train_timesteps, (bsz,), device=device).long()

            # Add noise according to scheduler
            noisy_latents = noise_scheduler.add_noise(latents, noise, timesteps)

            # Predict the noise residual
            batch_hidden_states = encoder_hidden_states.repeat(bsz, 1, 1)
            model_pred = unet(noisy_latents, timesteps, encoder_hidden_states=batch_hidden_states).sample

            # Compute loss
            target = noise if noise_scheduler.config.prediction_type == "epsilon" else noise_scheduler.get_velocity(latents, noise, timesteps)
            loss = F.mse_loss(model_pred.float(), target.float(), reduction="mean")
            loss = loss / gradient_accumulation_steps
            loss.backward()

            total_loss += loss.item() * gradient_accumulation_steps

            if (global_step + 1) % gradient_accumulation_steps == 0:
                torch.nn.utils.clip_grad_norm_(unet.parameters(), 1.0)
                optimizer.step()
                lr_scheduler.step()
                optimizer.zero_grad()

            global_step += 1
            progress_bar.update(1)
            progress_bar.set_postfix({"loss": f"{loss.item() * gradient_accumulation_steps:.4f}"})

            if global_step % save_steps == 0 or (max_steps and global_step >= max_steps):
                # Save LoRA adapter weights
                checkpoint_dir = out_path / lora_name
                unet.save_pretrained(str(checkpoint_dir))
                print(f"\n[Checkpoint] Saved LoRA adapter at step {global_step} to {checkpoint_dir}")

            if max_steps and global_step >= max_steps:
                break
        if max_steps and global_step >= max_steps:
            break

    progress_bar.close()
    elapsed = time.time() - start_time

    final_dir = out_path / lora_name
    unet.save_pretrained(str(final_dir))
    print("\n==================================================")
    print("LoRA FINE-TUNING COMPLETE!")
    print(f"Saved LoRA weights to: {final_dir}")
    print(f"Total Steps:           {global_step}")
    print(f"Elapsed Time:          {elapsed:.2f}s ({global_step/elapsed:.2f} steps/s)")
    print("==================================================")

    VRAMManager.clean_vram()


def main():
    parser = argparse.ArgumentParser(description="Fine-tune Anime LoRA for Person/Style Anime Transformation.")
    parser.add_argument("--dataset-dir", type=str, default="datasets/anime/people", help="Path to anime training images")
    parser.add_argument("--base-model", type=str, default="runwayml/stable-diffusion-v1-5", help="Base HuggingFace model ID")
    parser.add_argument("--output-dir", type=str, default="models/anime_lora", help="Output directory for LoRA weights")
    parser.add_argument("--name", type=str, default="anime_person_lora", help="LoRA model name")
    parser.add_argument("--rank", type=int, default=16, help="LoRA attention rank")
    parser.add_argument("--lr", type=float, default=1e-4, help="Learning rate")
    parser.add_argument("--epochs", type=int, default=3, help="Training epochs")
    parser.add_argument("--steps", type=int, default=200, help="Maximum training steps")
    parser.add_argument("--samples", type=int, default=1000, help="Max dataset samples to use")
    parser.add_argument("--batch-size", type=int, default=1, help="Batch size per device")
    parser.add_argument("--device", type=str, default=None, choices=["cuda", "cpu"], help="Device override")

    args = parser.parse_args()

    train_anime_lora(
        dataset_dir=args.dataset_dir,
        base_model_id=args.base_model,
        output_dir=args.output_dir,
        lora_name=args.name,
        rank=args.rank,
        lr=args.lr,
        epochs=args.epochs,
        max_steps=args.steps,
        max_samples=args.samples,
        batch_size=args.batch_size,
        device_name=args.device
    )


if __name__ == "__main__":
    main()
