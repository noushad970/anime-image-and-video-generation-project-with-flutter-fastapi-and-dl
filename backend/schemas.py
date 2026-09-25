"""
Pydantic Data Schemas for Anime Reality AI Backend API.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "1.0.0"
    device_name: str
    cuda_available: bool
    vram_total_gb: float
    vram_free_gb: float
    vram_allocated_gb: float


class JobCreateResponse(BaseModel):
    job_id: str
    type: str
    status: str
    style: str
    quality: str
    created_at: str


class JobStatusResponse(BaseModel):
    id: str
    type: str
    status: str
    progress: int
    style: str
    quality: str
    output_url: Optional[str] = None
    error_message: Optional[str] = None
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


class StyleItem(BaseModel):
    name: str
    display_name: str
    description: Optional[str] = None
    model: str
    lora: Optional[str] = None
    strength: float = 1.0
    recommended_resolution: int = 512
    license: Optional[str] = "MIT"


class StyleListResponse(BaseModel):
    total: int
    styles: List[StyleItem]


class ModelItem(BaseModel):
    name: str
    version: str
    type: str
    source: str
    license: str
    commercial_use: bool
    recommended_vram: str
    resolution: str
    capabilities: List[str]


class ModelListResponse(BaseModel):
    version: str
    models: Dict[str, ModelItem]
