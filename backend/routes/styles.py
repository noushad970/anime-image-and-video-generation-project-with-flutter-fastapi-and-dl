"""
Anime Style Presets Endpoints.
"""

from fastapi import APIRouter, HTTPException, status
from backend.schemas import StyleListResponse, StyleItem
from backend.database import get_all_styles

router = APIRouter(prefix="/api/v1/styles", tags=["Styles"])


@router.get("", response_model=StyleListResponse)
async def list_styles():
    """Lists all available anime styles and metadata."""
    styles = get_all_styles()
    items = [
        StyleItem(
            name=s["name"],
            display_name=s["display_name"],
            description=s.get("description"),
            model=s["model"],
            lora=s.get("lora"),
            strength=s.get("strength", 1.0),
            recommended_resolution=s.get("recommended_resolution", 512),
            license=s.get("license", "MIT")
        ) for s in styles
    ]
    return StyleListResponse(total=len(items), styles=items)


@router.get("/{style_name}", response_model=StyleItem)
async def get_style(style_name: str):
    """Retrieves metadata for a specific style."""
    styles = get_all_styles()
    for s in styles:
        if s["name"].lower() == style_name.lower():
            return StyleItem(
                name=s["name"],
                display_name=s["display_name"],
                description=s.get("description"),
                model=s["model"],
                lora=s.get("lora"),
                strength=s.get("strength", 1.0),
                recommended_resolution=s.get("recommended_resolution", 512),
                license=s.get("license", "MIT")
            )
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Style '{style_name}' not found"
    )
