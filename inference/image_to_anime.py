"""
Photo-to-Anime Transformation Master CLI & API for Anime Reality AI.
Implements Phase 2 milestone inference with fast and diffusion pipelines.
"""

import os
import sys
import time
import argparse
from pathlib import Path
from PIL import Image
from typing import Optional, Union

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from inference.memory_manager import VRAMManager
from inference.lightweight_generator import LightweightAnimeEngine
from inference.diffusion_engine import DiffusionAnimeEngine


def transform_image_to_anime(
    input_path: Union[str, Path, Image.Image],
    output_path: Optional[Union[str, Path]] = None,
    style: str = "default",
    quality: str = "balanced",
    engine: str = "auto",
    resolution: int = 512,
    device: Optional[str] = None
) -> Image.Image:
    """
    Core function to transform any real-world photo into an anime-styled image.

    Args:
        input_path: File path or PIL Image instance.
        output_path: Optional destination file path.
        style: Selected anime style ('default', 'watercolor', 'fantasy', 'cyberpunk').
        quality: Quality profile ('fast', 'balanced', 'quality').
        engine: Inference engine ('lightweight', 'diffusion', or 'auto').
        resolution: Target resolution (default 512).
        device: Device override ('cuda' or 'cpu').

    Returns:
        PIL.Image of the transformed anime output.
    """
    start_time = time.time()
    vram_before = VRAMManager.get_hardware_status()

    # 1. Load input image
    if isinstance(input_path, (str, Path)):
        p = Path(input_path)
        if not p.exists():
            raise FileNotFoundError(f"Input image not found at: {input_path}")
        image = Image.open(p).convert("RGB")
    elif isinstance(input_path, Image.Image):
        image = input_path.convert("RGB")
    else:
        raise ValueError("Unsupported input_path type. Must be str, Path, or PIL.Image.")

    # 2. Decide engine based on quality & preference
    chosen_engine = engine.lower()
    if chosen_engine == "auto":
        if quality == "quality" and VRAMManager.get_hardware_status()["cuda_available"]:
            chosen_engine = "diffusion"
        else:
            chosen_engine = "lightweight"

    print(f"\n[Anime Reality AI] Transforming image...")
    print(f"  Style:      {style}")
    print(f"  Quality:    {quality}")
    print(f"  Engine:     {chosen_engine}")
    print(f"  Resolution: {resolution}px")

    # 3. Execute transformation
    if chosen_engine == "diffusion":
        try:
            diff_engine = DiffusionAnimeEngine(device=device)
            steps = 15 if quality == "quality" else 8
            anime_image = diff_engine.transform(
                image,
                style=style,
                strength=0.65,
                num_inference_steps=steps,
                resolution=resolution
            )
        except Exception as e:
            print(f"[Warning] Diffusion engine encounter: {e}. Falling back to lightweight engine.")
            light_engine = LightweightAnimeEngine(device=device)
            anime_image = light_engine.transform(image, style=style, resolution=resolution)
    else:
        light_engine = LightweightAnimeEngine(device=device)
        anime_image = light_engine.transform(image, style=style, resolution=resolution)

    elapsed = time.time() - start_time
    vram_after = VRAMManager.get_hardware_status()

    print(f"[Success] Transformation completed in {elapsed:.3f}s")
    if vram_after["cuda_available"]:
        print(f"  Peak VRAM:  {vram_after['vram_allocated_gb']} GB / {vram_after['vram_total_gb']} GB")

    # 4. Save output if path provided
    if output_path:
        out_p = Path(output_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        anime_image.save(out_p, quality=95)
        print(f"  Output:     {out_p.resolve()}")

    return anime_image


def main():
    parser = argparse.ArgumentParser(
        description="Anime Reality AI — Photo to Anime Inference CLI",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("--input", "-i", type=str, required=True, help="Path to input photo (.jpg, .png, .webp)")
    parser.add_argument("--output", "-o", type=str, default="outputs/anime_output.jpg", help="Path to output anime image")
    parser.add_argument("--style", "-s", type=str, default="default", choices=["default", "watercolor", "fantasy", "cyberpunk"], help="Anime style preset")
    parser.add_argument("--quality", "-q", type=str, default="balanced", choices=["fast", "balanced", "quality"], help="Generation quality preset")
    parser.add_argument("--engine", "-e", type=str, default="auto", choices=["auto", "lightweight", "diffusion"], help="Underlying AI engine")
    parser.add_argument("--resolution", "-r", type=int, default=512, help="Output image resolution")
    parser.add_argument("--device", type=str, default=None, choices=["cuda", "cpu"], help="Compute device override")

    args = parser.parse_args()

    try:
        transform_image_to_anime(
            input_path=args.input,
            output_path=args.output,
            style=args.style,
            quality=args.quality,
            engine=args.engine,
            resolution=args.resolution,
            device=args.device
        )
    except Exception as e:
        print(f"\n[Error] Failed to process image: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
