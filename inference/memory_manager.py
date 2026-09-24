"""
VRAM & Memory Management Engine for Anime Reality AI.
Optimized specifically for NVIDIA RTX 5060 (8GB VRAM) and limited memory hardware.
"""

import gc
import torch
from typing import Dict, Any, Optional


class VRAMManager:
    """Manages VRAM allocations, low-memory hooks, and garbage collection."""

    @staticmethod
    def get_hardware_status() -> Dict[str, Any]:
        """Returns comprehensive real-time GPU/CPU memory metrics."""
        is_cuda = torch.cuda.is_available()
        metrics = {
            "cuda_available": is_cuda,
            "device_name": torch.cuda.get_device_name(0) if is_cuda else "CPU",
            "vram_total_gb": 0.0,
            "vram_allocated_gb": 0.0,
            "vram_reserved_gb": 0.0,
            "vram_free_gb": 0.0,
        }
        if is_cuda:
            props = torch.cuda.get_device_properties(0)
            total = props.total_memory / (1024 ** 3)
            allocated = torch.cuda.memory_allocated(0) / (1024 ** 3)
            reserved = torch.cuda.memory_reserved(0) / (1024 ** 3)
            free = total - reserved
            metrics.update({
                "vram_total_gb": round(total, 2),
                "vram_allocated_gb": round(allocated, 2),
                "vram_reserved_gb": round(reserved, 2),
                "vram_free_gb": round(free, 2),
            })
        return metrics

    @staticmethod
    def get_optimal_device(force_cpu: bool = False) -> torch.device:
        """Returns the best available torch.device."""
        if force_cpu or not torch.cuda.is_available():
            return torch.device("cpu")
        return torch.device("cuda:0")

    @staticmethod
    def optimize_diffusion_pipeline(pipeline: Any, max_vram_gb: float = 8.0) -> Any:
        """
        Applies memory-efficient attention, VAE tiling, and slicing to stay safely under 8GB VRAM.
        """
        if not torch.cuda.is_available():
            return pipeline

        # Enable attention slicing to lower peak VRAM during attention computation
        if hasattr(pipeline, "enable_attention_slicing"):
            pipeline.enable_attention_slicing(slice_size="auto")

        # Enable VAE slicing and tiling to prevent OOM during high-res decode
        if hasattr(pipeline, "enable_vae_slicing"):
            pipeline.enable_vae_slicing()

        if hasattr(pipeline, "enable_vae_tiling"):
            pipeline.enable_vae_tiling()

        # If available VRAM is under 6GB, enable sequential or model CPU offload
        free_gb = VRAMManager.get_hardware_status().get("vram_free_gb", 8.0)
        if free_gb < 4.0 and hasattr(pipeline, "enable_model_cpu_offload"):
            pipeline.enable_model_cpu_offload()

        return pipeline

    @staticmethod
    def clean_vram() -> None:
        """Forces garbage collection and flushes the PyTorch CUDA cache."""
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()
