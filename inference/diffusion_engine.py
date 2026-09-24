"""
Latent Diffusion Anime Stylization Engine for Anime Reality AI.
Optimized for 8GB VRAM with FP16, VAE Slicing/Tiling, and Attention Slicing.
"""

import os
import sys
import json
import torch
from pathlib import Path
from PIL import Image
from typing import Optional, Dict, Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from inference.memory_manager import VRAMManager

STYLE_PROMPTS = {
    "default": "masterpiece, best quality, ultra-detailed classic anime style, vibrant colors, crisp clean anime lines, Makoto Shinkai aesthetic, 8k anime art",
    "watercolor": "masterpiece, best quality, soft watercolor anime style, pastel tones, luminous atmosphere, hand-painted aesthetic, Studio Ghibli watercolor",
    "fantasy": "masterpiece, best quality, high fantasy anime artwork, ethereal glowing lighting, vibrant lush colors, detailed fantasy background",
    "cyberpunk": "masterpiece, best quality, futuristic cyberpunk anime, neon glowing lights, holographic reflections, moody atmospheric dark anime"
}

NEGATIVE_PROMPT = "photorealistic, 3d render, deformed, disfigured, lowres, bad anatomy, blurry, worst quality, low quality, duplicate, ugly"


class DiffusionAnimeEngine:
    """
    Manages Stable Diffusion Img2Img & LoRA style inference under 8GB VRAM budget.
    """
    def __init__(self, model_id: str = "runwayml/stable-diffusion-v1-5", device: Optional[str] = None):
        self.device = VRAMManager.get_optimal_device(force_cpu=(device == "cpu"))
        self.dtype = torch.float16 if self.device.type == "cuda" else torch.float32
        self.model_id = model_id
        self.pipe = None
        self.current_lora = None

    def load_pipeline(self):
        """Lazy loader for the diffusers pipeline."""
        if self.pipe is not None:
            return

        from diffusers import AutoPipelineForImage2Image, DPMSolverMultistepScheduler

        print(f"[DiffusionAnimeEngine] Initializing Image-to-Image pipeline ({self.model_id})...")
        self.pipe = AutoPipelineForImage2Image.from_pretrained(
            self.model_id,
            torch_dtype=self.dtype,
            safety_checker=None,
            requires_safety_checker=False
        )

        # Use fast DPM++ solver for high quality in 8-15 steps
        self.pipe.scheduler = DPMSolverMultistepScheduler.from_config(
            self.pipe.scheduler.config,
            use_karras_sigmas=True
        )

        self.pipe.to(self.device)

        # Apply mandatory 8GB VRAM optimizations
        self.pipe = VRAMManager.optimize_diffusion_pipeline(self.pipe, max_vram_gb=8.0)
        print("[DiffusionAnimeEngine] Pipeline loaded and optimized for RTX 5060 8GB.")

    def load_style_lora(self, lora_path: str, weight_name: Optional[str] = None):
        """Loads or swaps LoRA style weights."""
        if not Path(lora_path).exists():
            print(f"[DiffusionAnimeEngine] LoRA file not found at {lora_path}, skipping.")
            return

        self.load_pipeline()
        if self.current_lora != lora_path:
            try:
                self.pipe.unload_lora_weights()
            except Exception:
                pass
            self.pipe.load_lora_weights(lora_path, weight_name=weight_name)
            self.current_lora = lora_path
            print(f"[DiffusionAnimeEngine] Applied LoRA style from {lora_path}")

    @torch.inference_mode()
    def transform(
        self,
        input_image: Image.Image,
        style: str = "default",
        strength: float = 0.65,
        num_inference_steps: int = 12,
        guidance_scale: float = 7.5,
        resolution: int = 512
    ) -> Image.Image:
        """Transforms photo to anime using diffusion."""
        self.load_pipeline()

        # Resize image to divisible by 8 dimensions
        w, h = input_image.size
        scale = resolution / max(w, h)
        new_w, new_h = max(64, int(w * scale) // 8 * 8), max(64, int(h * scale) // 8 * 8)
        init_img = input_image.resize((new_w, new_h), Image.Resampling.LANCZOS)

        prompt = STYLE_PROMPTS.get(style, STYLE_PROMPTS["default"])

        result = self.pipe(
            prompt=prompt,
            negative_prompt=NEGATIVE_PROMPT,
            image=init_img,
            strength=strength,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale
        ).images[0]

        VRAMManager.clean_vram()
        return result
