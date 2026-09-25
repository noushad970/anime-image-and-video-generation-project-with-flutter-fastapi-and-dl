"""
Job Queue and Background Processing Engine for Anime Reality AI.
Ensures single-GPU task serialization to protect 8GB VRAM against concurrent thrashing.
"""

import os
import sys
import uuid
import time
import shutil
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.database import save_job, get_job
from inference.image_to_anime import transform_image_to_anime
from video.video_to_anime import transform_video_to_anime

logger = logging.getLogger("AnimeReality.JobManager")


class JobManager:
    """Manages asynchronous AI generation jobs for images and videos."""
    def __init__(self, max_workers: int = 1):
        # 1 worker guarantees serialized GPU execution on the 8GB RTX 5060
        self.executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="AIWorker")
        self.jobs: Dict[str, Dict[str, Any]] = {}
        self.cancelled_jobs = set()

    def submit_image_job(self, input_path: str, style: str = "default", quality: str = "balanced", resolution: int = 512) -> str:
        job_id = f"img_{uuid.uuid4().hex[:12]}"
        now = datetime.utcnow().isoformat()

        job_data = {
            "id": job_id,
            "type": "image",
            "status": "QUEUED",
            "progress": 0,
            "style": style,
            "quality": quality,
            "input_path": input_path,
            "output_path": f"outputs/jobs/{job_id}.jpg",
            "error_message": None,
            "created_at": now,
            "started_at": None,
            "completed_at": None,
            "resolution": resolution
        }

        self.jobs[job_id] = job_data
        save_job(job_data)

        self.executor.submit(self._execute_image_job, job_id)
        return job_id

    def submit_video_job(self, input_path: str, style: str = "default", quality: str = "fast", resolution: int = 512) -> str:
        job_id = f"vid_{uuid.uuid4().hex[:12]}"
        now = datetime.utcnow().isoformat()

        job_data = {
            "id": job_id,
            "type": "video",
            "status": "QUEUED",
            "progress": 0,
            "style": style,
            "quality": quality,
            "input_path": input_path,
            "output_path": f"outputs/jobs/{job_id}.mp4",
            "error_message": None,
            "created_at": now,
            "started_at": None,
            "completed_at": None,
            "resolution": resolution
        }

        self.jobs[job_id] = job_data
        save_job(job_data)

        self.executor.submit(self._execute_video_job, job_id)
        return job_id

    def _execute_image_job(self, job_id: str):
        job = self.jobs.get(job_id) or get_job(job_id)
        if not job or job_id in self.cancelled_jobs:
            return

        try:
            job["status"] = "PROCESSING"
            job["progress"] = 25
            job["started_at"] = datetime.utcnow().isoformat()
            save_job(job)

            out_p = Path(job["output_path"])
            out_p.parent.mkdir(parents=True, exist_ok=True)

            transform_image_to_anime(
                input_path=job["input_path"],
                output_path=str(out_p),
                style=job["style"],
                quality=job["quality"],
                resolution=job.get("resolution", 512)
            )

            job["progress"] = 100
            job["status"] = "COMPLETED"
            job["completed_at"] = datetime.utcnow().isoformat()
            save_job(job)

        except Exception as e:
            logger.error(f"Image job {job_id} failed: {e}", exc_info=True)
            job["status"] = "FAILED"
            job["error_message"] = str(e)
            job["completed_at"] = datetime.utcnow().isoformat()
            save_job(job)

    def _execute_video_job(self, job_id: str):
        job = self.jobs.get(job_id) or get_job(job_id)
        if not job or job_id in self.cancelled_jobs:
            return

        try:
            job["status"] = "PROCESSING"
            job["progress"] = 15
            job["started_at"] = datetime.utcnow().isoformat()
            save_job(job)

            out_p = Path(job["output_path"])
            out_p.parent.mkdir(parents=True, exist_ok=True)

            transform_video_to_anime(
                input_path=job["input_path"],
                output_path=str(out_p),
                style=job["style"],
                quality=job["quality"],
                resolution=job.get("resolution", 512),
                temporal_smoothing=True
            )

            job["progress"] = 100
            job["status"] = "COMPLETED"
            job["completed_at"] = datetime.utcnow().isoformat()
            save_job(job)

        except Exception as e:
            logger.error(f"Video job {job_id} failed: {e}", exc_info=True)
            job["status"] = "FAILED"
            job["error_message"] = str(e)
            job["completed_at"] = datetime.utcnow().isoformat()
            save_job(job)

    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        return self.jobs.get(job_id) or get_job(job_id)

    def cancel_job(self, job_id: str) -> bool:
        job = self.get_job_status(job_id)
        if not job or job["status"] in ("COMPLETED", "FAILED", "CANCELLED"):
            return False
        self.cancelled_jobs.add(job_id)
        job["status"] = "CANCELLED"
        save_job(job)
        return True


# Global singleton instance
job_manager = JobManager(max_workers=1)
