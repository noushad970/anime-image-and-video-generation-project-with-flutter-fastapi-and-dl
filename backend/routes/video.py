"""
Video-to-Anime Transformation Endpoints.
"""

import uuid
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from backend.schemas import JobCreateResponse
from backend.jobs.manager import job_manager

router = APIRouter(prefix="/api/v1/video", tags=["Video AI"])

UPLOAD_DIR = Path("outputs/uploads/videos")
ALLOWED_EXTENSIONS = {".mp4", ".avi", ".mov", ".webm"}
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB


@router.post("/anime", response_model=JobCreateResponse, status_code=status.HTTP_202_ACCEPTED)
async def create_video_anime_job(
    video: UploadFile = File(..., description="Real-world video to transform into Anime"),
    style: str = Form("default", description="Anime style preset"),
    quality: str = Form("fast", description="Quality profile ('fast', 'balanced', 'quality')"),
    resolution: int = Form(512, description="Output frame resolution")
):
    """
    Submits a video file for asynchronous Anime transformation and temporal smoothing.
    Returns a job ID for non-blocking status tracking.
    """
    ext = Path(video.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported video format '{ext}'. Allowed: {list(ALLOWED_EXTENSIONS)}"
        )

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    temp_filename = f"upload_{uuid.uuid4().hex[:12]}{ext}"
    saved_path = UPLOAD_DIR / temp_filename

    contents = await video.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Video exceeds maximum allowed size of {MAX_FILE_SIZE // (1024*1024)} MB"
        )

    with open(saved_path, "wb") as f:
        f.write(contents)

    job_id = job_manager.submit_video_job(
        input_path=str(saved_path),
        style=style,
        quality=quality,
        resolution=resolution
    )

    job = job_manager.get_job_status(job_id)
    return JobCreateResponse(
        job_id=job_id,
        type="video",
        status=job["status"],
        style=job["style"],
        quality=job["quality"],
        created_at=job["created_at"]
    )
