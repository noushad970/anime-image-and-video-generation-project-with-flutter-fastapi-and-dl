"""
Image-to-Anime Transformation Endpoints.
"""

import uuid
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from backend.schemas import JobCreateResponse
from backend.jobs.manager import job_manager

router = APIRouter(prefix="/api/v1/image", tags=["Image AI"])

UPLOAD_DIR = Path("outputs/uploads/images")
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB


@router.post("/anime", response_model=JobCreateResponse, status_code=status.HTTP_202_ACCEPTED)
async def create_image_anime_job(
    image: UploadFile = File(..., description="Real-world photo to stylize"),
    style: str = Form("default", description="Anime style ('default', 'watercolor', 'fantasy', 'cyberpunk')"),
    quality: str = Form("balanced", description="Quality profile ('fast', 'balanced', 'quality')"),
    resolution: int = Form(512, description="Target image resolution")
):
    """
    Submits a photo for asynchronous Anime transformation.
    Returns a unique job ID to poll for status and retrieve final result.
    """
    ext = Path(image.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '{ext}'. Allowed: {list(ALLOWED_EXTENSIONS)}"
        )

    # Secure temporary file saving
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    temp_filename = f"upload_{uuid.uuid4().hex[:12]}{ext}"
    saved_path = UPLOAD_DIR / temp_filename

    contents = await image.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum allowed size of {MAX_FILE_SIZE // (1024*1024)} MB"
        )

    with open(saved_path, "wb") as f:
        f.write(contents)

    # Submit to serialized job queue
    job_id = job_manager.submit_image_job(
        input_path=str(saved_path),
        style=style,
        quality=quality,
        resolution=resolution
    )

    job = job_manager.get_job_status(job_id)
    return JobCreateResponse(
        job_id=job_id,
        type="image",
        status=job["status"],
        style=job["style"],
        quality=job["quality"],
        created_at=job["created_at"]
    )
