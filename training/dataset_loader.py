"""
PyTorch Dataset Loaders for Anime Reality AI Training.
Supports paired/unpaired real-to-anime dataset sampling for lightweight and LoRA training.
"""

import os
import random
from pathlib import Path
from typing import Tuple, List, Optional
from PIL import Image
import torch
from torch.utils.data import Dataset
import torchvision.transforms as T


class UnpairedAnimeDataset(Dataset):
    """
    Unpaired dataset for AnimeGAN / CycleGAN style transfer training.
    Loads real photos from domain A and anime style images from domain B.
    """
    def __init__(
        self,
        real_dir: str = "datasets/real/nature/genv3_train_photo",
        anime_dir: str = "datasets/anime/styles/Shinkai",
        resolution: int = 512,
        augment: bool = True
    ):
        self.real_paths = self._gather_images(Path(real_dir))
        self.anime_paths = self._gather_images(Path(anime_dir))
        self.resolution = resolution

        if not self.real_paths:
            # Fallback to any real directory if specific path not found
            self.real_paths = self._gather_images(Path("datasets/real"))
        if not self.anime_paths:
            self.anime_paths = self._gather_images(Path("datasets/anime"))

        transforms_list = [
            T.Resize((resolution, resolution), interpolation=T.InterpolationMode.BICUBIC),
        ]
        if augment:
            transforms_list.extend([
                T.RandomHorizontalFlip(p=0.5),
                T.ColorJitter(brightness=0.1, contrast=0.1, saturation=0.1)
            ])
        transforms_list.extend([
            T.ToTensor(),
            T.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])  # Scale to [-1, 1]
        ])
        self.transform = T.Compose(transforms_list)

    def _gather_images(self, folder: Path) -> List[Path]:
        if not folder.exists():
            return []
        valid_exts = {".jpg", ".jpeg", ".png", ".webp"}
        files = []
        for p in folder.rglob("*"):
            if p.is_file() and p.suffix.lower() in valid_exts:
                files.append(p)
        return files

    def __len__(self) -> int:
        return max(len(self.real_paths), len(self.anime_paths), 1)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        # Handle index wrapping
        real_idx = idx % len(self.real_paths) if self.real_paths else 0
        anime_idx = random.randint(0, len(self.anime_paths) - 1) if self.anime_paths else 0

        # Load real photo
        if self.real_paths:
            with Image.open(self.real_paths[real_idx]) as img:
                real_tensor = self.transform(img.convert("RGB"))
        else:
            real_tensor = torch.zeros(3, self.resolution, self.resolution)

        # Load anime style image
        if self.anime_paths:
            with Image.open(self.anime_paths[anime_idx]) as img:
                anime_tensor = self.transform(img.convert("RGB"))
        else:
            anime_tensor = torch.zeros(3, self.resolution, self.resolution)

        return real_tensor, anime_tensor
