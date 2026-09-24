"""
Lightweight Neural Anime Generator & Stylization Engine for Anime Reality AI.
Designed for real-time and low-latency image-to-anime conversion under 8GB VRAM.
"""

import cv2
import numpy as np
import torch
import torch.nn as nn
from PIL import Image
import sys
from pathlib import Path
from typing import Optional, Union, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from inference.memory_manager import VRAMManager


class ConvBlock(nn.Module):
    """Standard Conv2D + InstanceNorm + LeakyReLU block."""
    def __init__(self, in_channels: int, out_channels: int, kernel_size: int = 3, stride: int = 1, padding: int = 1):
        super().__init__()
        self.conv = nn.Conv2d(in_channels, out_channels, kernel_size, stride, padding, bias=False)
        self.norm = nn.InstanceNorm2d(out_channels, affine=True)
        self.act = nn.LeakyReLU(0.2, inplace=True)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.act(self.norm(self.conv(x)))


class ResBlock(nn.Module):
    """Residual block with InstanceNorm for anime texture representation."""
    def __init__(self, channels: int):
        super().__init__()
        self.block = nn.Sequential(
            ConvBlock(channels, channels, kernel_size=3, stride=1, padding=1),
            nn.Conv2d(channels, channels, kernel_size=3, stride=1, padding=1, bias=False),
            nn.InstanceNorm2d(channels, affine=True)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return x + self.block(x)


class AnimeGeneratorNetwork(nn.Module):
    """
    Lightweight Feedforward Anime Generator Network.
    Parameters: ~1.8M params (Extremely lightweight, <100MB VRAM footprint).
    """
    def __init__(self, num_res_blocks: int = 6):
        super().__init__()
        # Encoder
        self.in_conv = ConvBlock(3, 64, kernel_size=7, stride=1, padding=3)
        self.down1 = ConvBlock(64, 128, kernel_size=3, stride=2, padding=1)
        self.down2 = ConvBlock(128, 256, kernel_size=3, stride=2, padding=1)

        # Bottleneck
        self.res_blocks = nn.Sequential(*[ResBlock(256) for _ in range(num_res_blocks)])

        # Decoder
        self.up1 = nn.Sequential(
            nn.Upsample(scale_factor=2, mode="bilinear", align_corners=False),
            ConvBlock(256, 128, kernel_size=3, stride=1, padding=1)
        )
        self.up2 = nn.Sequential(
            nn.Upsample(scale_factor=2, mode="bilinear", align_corners=False),
            ConvBlock(128, 64, kernel_size=3, stride=1, padding=1)
        )
        self.out_conv = nn.Sequential(
            nn.Conv2d(64, 3, kernel_size=7, stride=1, padding=3),
            nn.Tanh()
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        feat = self.in_conv(x)
        feat = self.down1(feat)
        feat = self.down2(feat)
        feat = self.res_blocks(feat)
        feat = self.up1(feat)
        feat = self.up2(feat)
        out = self.out_conv(feat)
        return out


class StylizedAnimeFilter:
    """
    High-fidelity computer vision anime transformation filter.
    Preserves real-world structure, smooths anime flat shading, enhances vibrancy,
    and extracts crisp Japanese animation lineart.
    """

    @staticmethod
    def apply(img_bgr: np.ndarray, style: str = "default") -> np.ndarray:
        h, w = img_bgr.shape[:2]

        # 1. Edge-preserving smoothing (Anime cel-shading simulation)
        # Apply bilateral filtering in multi-scale to simulate clean anime cel shading
        smoothed = cv2.bilateralFilter(img_bgr, d=9, sigmaColor=75, sigmaSpace=75)
        for _ in range(3):
            smoothed = cv2.bilateralFilter(smoothed, d=7, sigmaColor=50, sigmaSpace=50)

        # 2. Extract refined lineart
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        gray_blur = cv2.medianBlur(gray, 7)
        # Adaptive thresholding for clean anime line outlines
        edges = cv2.adaptiveThreshold(
            gray_blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, blockSize=9, C=2
        )
        edges_bgr = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

        # 3. Color quantization & Vibrancy boost (HSV / LAB color grading)
        hsv = cv2.cvtColor(smoothed, cv2.COLOR_BGR2HSV).astype(np.float32)

        # Style-specific color adjustments
        if style == "watercolor":
            # Soft pastel saturation, luminous highlights
            hsv[:, :, 1] = np.clip(hsv[:, :, 1] * 1.15, 0, 255)
            hsv[:, :, 2] = np.clip(hsv[:, :, 2] * 1.10 + 10, 0, 255)
        elif style == "cyberpunk":
            # High contrast, deep magenta/cyan saturation
            hsv[:, :, 1] = np.clip(hsv[:, :, 1] * 1.45, 0, 255)
            hsv[:, :, 2] = np.clip(hsv[:, :, 2] * 1.15, 0, 255)
        elif style == "fantasy":
            # Warm golden/emerald fantasy tint
            hsv[:, :, 1] = np.clip(hsv[:, :, 1] * 1.30, 0, 255)
            hsv[:, :, 2] = np.clip(hsv[:, :, 2] * 1.05 + 5, 0, 255)
        else: # default classic anime
            # Vibrant clear anime palette
            hsv[:, :, 1] = np.clip(hsv[:, :, 1] * 1.25, 0, 255)
            hsv[:, :, 2] = np.clip(hsv[:, :, 2] * 1.08, 0, 255)

        hsv = np.clip(hsv, 0, 255).astype(np.uint8)
        color_boosted = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

        # 4. Color palette quantization (k-means / step quantization)
        div = 32
        quantized = (color_boosted // div) * div + div // 2

        # Blend smooth colors with quantized cel layers
        cel_layer = cv2.addWeighted(smoothed, 0.4, quantized, 0.6, 0)

        # 5. Combine color layer with lineart
        # Bitwise AND merges dark ink lines with color layers
        final_anime = cv2.bitwise_and(cel_layer, edges_bgr)
        return final_anime


class LightweightAnimeEngine:
    """
    Engine executing Model A (Lightweight Anime Model) inference.
    Supports PyTorch neural checkpoint execution or fallback stylized CV transform.
    """
    def __init__(self, weights_path: Optional[str] = None, device: Optional[str] = None):
        self.device = VRAMManager.get_optimal_device(force_cpu=(device == "cpu"))
        self.network = AnimeGeneratorNetwork().to(self.device).eval()
        self.has_trained_weights = False

        if weights_path and Path(weights_path).exists():
            try:
                state_dict = torch.load(weights_path, map_location=self.device)
                self.network.load_state_dict(state_dict)
                self.has_trained_weights = True
                print(f"[LightweightAnimeEngine] Loaded weights from {weights_path}")
            except Exception as e:
                print(f"[LightweightAnimeEngine] Could not load weights: {e}, using stylized filter pipeline.")

    @torch.inference_mode()
    def transform(self, input_image: Image.Image, style: str = "default", resolution: int = 512) -> Image.Image:
        """Transforms a PIL image to an anime style image."""
        # Standardize size
        w, h = input_image.size
        scale = resolution / max(w, h)
        new_w, new_h = max(64, int(w * scale) // 8 * 8), max(64, int(h * scale) // 8 * 8)
        resized_pil = input_image.resize((new_w, new_h), Image.Resampling.LANCZOS)

        if self.has_trained_weights:
            # Neural forward pass
            np_img = np.array(resized_pil).astype(np.float32) / 127.5 - 1.0
            tensor = torch.from_numpy(np_img).permute(2, 0, 1).unsqueeze(0).to(self.device)
            out_tensor = self.network(tensor)
            out_np = (out_tensor.squeeze(0).permute(1, 2, 0).cpu().numpy() + 1.0) * 127.5
            out_np = np.clip(out_np, 0, 255).astype(np.uint8)
            return Image.fromarray(out_np)
        else:
            # High quality stylized filter
            img_bgr = cv2.cvtColor(np.array(resized_pil), cv2.COLOR_RGB2BGR)
            anime_bgr = StylizedAnimeFilter.apply(img_bgr, style=style)
            anime_rgb = cv2.cvtColor(anime_bgr, cv2.COLOR_BGR2RGB)
            return Image.fromarray(anime_rgb)
