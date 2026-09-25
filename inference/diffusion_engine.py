"""
Latent Diffusion Anime Stylization Engine for Anime Reality AI.
Optimized for 8GB VRAM with FP16, VAE Slicing/Tiling, Attention Slicing, and fine-tuned Anime LoRA integration.
"""

import os
import sys
import json
import torch
from pathlib import Path
from PIL import Image
from typing import Optional, Dict, Any, Union

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from inference.memory_manager import VRAMManager

# Specialized prompts for person portrait and anime transformation
STYLE_PROMPTS = {
    "default": "masterpiece, best quality, authentic Japanese anime style, highly detailed anime character portrait, vibrant anime eyes, clean defined anime line art, soft cel shading, studio anime production, Kyoto Animation and Makoto Shinkai aesthetic, 8k anime illustration",
    "person": "masterpiece, best quality, ultra-detailed anime character, 1person, detailed anime face, luminous anime eyes, styled anime hair, clean dark lineart, smooth anime skin cel shading, expressive anime aesthetic, official anime visual",
    "watercolor": "masterpiece, best quality, soft watercolor anime style, pastel tones, luminous atmosphere, hand-painted aesthetic, Studio Ghibli watercolor, gentle anime portrait",
    "fantasy": "masterpiece, best quality, high fantasy anime artwork, ethereal glowing lighting, vibrant lush colors, detailed fantasy background, anime warrior portrait",
    "cyberpunk": "masterpiece, best quality, futuristic cyberpunk anime, neon glowing lights, holographic reflections, moody atmospheric dark anime, cyberpunk anime hero"
}

NEGATIVE_PROMPT = (
    "photorealistic, real life photo, 3d render, western comic, lowres, deformed face, bad anatomy, "
    "blurry, worst quality, low quality, duplicate, extra limbs, poorly drawn eyes, realistic skin texture, noise, grain"
)


class DiffusionAnimeEngine:
    """
    Manages Stable Diffusion Img2Img & LoRA style inference under 8GB VRAM budget.
    """
    def __init__(
        self,
        model_id: str = "runwayml/stable-diffusion-v1-5",
        lora_dir: Optional[str] = "models/anime_lora/anime_person_lora",
        device: Optional[str] = None
    ):
        self.device = VRAMManager.get_optimal_device(force_cpu=(device == "cpu"))
        self.dtype = torch.float16 if self.device.type == "cuda" else torch.float32
        self.model_id = model_id
        self.lora_dir = lora_dir
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

        # Load fine-tuned anime person LoRA if available
        if self.lora_dir:
            self.load_style_lora(self.lora_dir)

    def load_style_lora(self, lora_path: Union[str, Path], weight_name: Optional[str] = None):
        """Loads or swaps LoRA style weights (supports PEFT directory or safetensors)."""
        p = Path(lora_path)
        if not p.exists():
            print(f"[DiffusionAnimeEngine] LoRA path not found at {lora_path}, skipping LoRA load.")
            return

        if self.pipe is None:
            self.load_pipeline()
            return

        if self.current_lora != str(p):
            try:
                self.pipe.unload_lora_weights()
            except Exception:
                pass
            try:
                self.pipe.load_lora_weights(str(p), weight_name=weight_name)
                self.current_lora = str(p)
                print(f"[DiffusionAnimeEngine] Loaded and applied fine-tuned Anime LoRA from {p}")
            except Exception as e:
                print(f"[DiffusionAnimeEngine] Note loading LoRA: {e}")

    @torch.inference_mode()
    def transform(
        self,
        input_image: Image.Image,
        style: str = "default",
        strength: float = 0.65,
        num_inference_steps: int = 15,
        guidance_scale: float = 7.5,
        resolution: int = 512,
        custom_prompt: Optional[str] = None
    ) -> Image.Image:
        """Transforms photo to anime using diffusion."""
        self.load_pipeline()

        # Resize image to divisible by 8 dimensions
        w, h = input_image.size
        scale = resolution / max(w, h)
        new_w, new_h = max(64, int(w * scale) // 8 * 8), max(64, int(h * scale) // 8 * 8)
        init_img = input_image.resize((new_w, new_h), Image.Resampling.LANCZOS)

        if custom_prompt:
            prompt = custom_prompt
        else:
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
