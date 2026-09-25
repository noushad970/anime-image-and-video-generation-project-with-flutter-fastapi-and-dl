"""
Health and Hardware Diagnostic Endpoint for Anime Reality AI.
"""

from fastapi import APIRouter
from backend.schemas import HealthResponse
from inference.memory_manager import VRAMManager

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def get_health():
    """Returns real-time service health and RTX 5060 VRAM metrics."""
    status = VRAMManager.get_hardware_status()
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        device_name=status.get("device_name", "Unknown"),
        cuda_available=status.get("cuda_available", False),
        vram_total_gb=status.get("vram_total_gb", 0.0),
        vram_free_gb=status.get("vram_free_gb", 0.0),
        vram_allocated_gb=status.get("vram_allocated_gb", 0.0)
    )
