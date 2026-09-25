"""
Quick-start script to fine-tune HuggingFace Stable Diffusion model on the 63k Anime Person dataset.
Optimized for NVIDIA RTX 5060 (8GB VRAM).
"""

import sys
import argparse
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from training.lora.train_anime_lora import train_anime_lora


def main():
    parser = argparse.ArgumentParser(description="Fine-tune HuggingFace Diffusion Model for Realistic Person Anime.")
    parser.add_argument("--steps", type=int, default=300, help="Number of fine-tuning steps (default: 300)")
    parser.add_argument("--samples", type=int, default=2000, help="Number of anime portrait dataset images to sample (default: 2000)")
    parser.add_argument("--lr", type=float, default=1e-4, help="Learning rate (default: 1e-4)")
    parser.add_argument("--rank", type=int, default=16, help="LoRA rank (default: 16)")
    parser.add_argument("--device", type=str, default=None, help="Device ('cuda' or 'cpu')")

    args = parser.parse_args()

    print("==================================================")
    print("STARTING PERSON ANIME LoRA FINE-TUNING")
    print("==================================================")
    train_anime_lora(
        dataset_dir="datasets/anime/people",
        base_model_id="runwayml/stable-diffusion-v1-5",
        output_dir="models/anime_lora",
        lora_name="anime_person_lora",
        prompt="masterpiece, best quality, authentic Japanese anime character, detailed anime face, luminous anime eyes, vibrant anime coloring, clean line art",
        rank=args.rank,
        lr=args.lr,
        max_steps=args.steps,
        max_samples=args.samples,
        batch_size=1,
        gradient_accumulation_steps=4,
        save_steps=100,
        device_name=args.device
    )


if __name__ == "__main__":
    main()
