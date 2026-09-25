"""
Job Status, Result Retrieval, and Cancellation Endpoints.
"""

from pathlib import Path
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse
from backend.schemas import JobStatusResponse
from backend.jobs.manager import job_manager

router = APIRouter(prefix="/api/v1/jobs", tags=["Jobs"])


@router.get("/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """Retrieves current processing progress, status, and metadata for a job."""
    job = job_manager.get_job_status(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job '{job_id}' not found"
        )

    output_url = None
    if job["status"] == "COMPLETED" and job.get("output_path"):
        output_url = f"/api/v1/jobs/{job_id}/result"

    return JobStatusResponse(
        id=job["id"],
        type=job["type"],
        status=job["status"],
        progress=job.get("progress", 0),
        style=job["style"],
        quality=job["quality"],
        output_url=output_url,
        error_message=job.get("error_message"),
        created_at=job["created_at"],
        started_at=job.get("started_at"),
        completed_at=job.get("completed_at")
    )


@router.get("/{job_id}/result")
async def get_job_result(job_id: str):
    """Downloads or streams the final generated anime image or video."""
    job = job_manager.get_job_status(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job '{job_id}' not found"
        )

    if job["status"] != "COMPLETED" or not job.get("output_path"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Job is not completed yet (current status: {job['status']})"
        )

    out_file = Path(job["output_path"])
    if not out_file.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Output result file not found on disk"
        )

    media_type = "image/jpeg" if job["type"] == "image" else "video/mp4"
    return FileResponse(
        path=str(out_file),
        media_type=media_type,
        filename=out_file.name
    )


@router.post("/{job_id}/cancel")
async def cancel_job(job_id: str):
    """Cancels a pending or queued job."""
    success = job_manager.cancel_job(job_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not cancel job '{job_id}'"
        )
    return {"message": f"Job '{job_id}' has been cancelled"}
