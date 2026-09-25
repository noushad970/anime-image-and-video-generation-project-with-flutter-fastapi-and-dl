"""
Model Registry Inspection Endpoints.
"""

import json
from pathlib import Path
from fastapi import APIRouter, HTTPException, status
from backend.schemas import ModelListResponse, ModelItem

router = APIRouter(prefix="/api/v1/models", tags=["Models"])

REGISTRY_PATH = Path("models/registry.json")


@router.get("", response_model=ModelListResponse)
async def list_models():
    """Returns all registered AI models, VRAM requirements, and licenses."""
    if not REGISTRY_PATH.exists():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Model registry not found"
        )

    try:
        with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        models_dict = {}
        for key, m in data.get("models", {}).items():
            models_dict[key] = ModelItem(
                name=m["name"],
                version=m["version"],
                type=m["type"],
                source=m["source"],
                license=m["license"],
                commercial_use=m["commercial_use"],
                recommended_vram=m["recommended_vram"],
                resolution=m["resolution"],
                capabilities=m["capabilities"]
            )

        return ModelListResponse(
            version=data.get("version", "1.0.0"),
            models=models_dict
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to read model registry: {e}"
        )
