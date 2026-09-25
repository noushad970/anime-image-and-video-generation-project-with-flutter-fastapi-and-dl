"""
Comprehensive Test Suite for FastAPI Backend Endpoints and Job System.
"""

import io
import time
import pytest
from PIL import Image
from fastapi.testclient import TestClient

from backend.main import app
from backend.database import init_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_test_db():
    init_db()


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "cuda_available" in data
    assert "vram_total_gb" in data


def test_styles_endpoints():
    # List styles
    response = client.get("/api/v1/styles")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 4
    style_names = [s["name"] for s in data["styles"]]
    assert "default" in style_names
    assert "watercolor" in style_names

    # Get single style
    res_single = client.get("/api/v1/styles/watercolor")
    assert res_single.status_code == 200
    style_data = res_single.json()
    assert style_data["name"] == "watercolor"
    assert "Shinkai" in style_data["display_name"]


def test_models_endpoint():
    response = client.get("/api/v1/models")
    assert response.status_code == 200
    data = response.json()
    assert "models" in data
    assert "anime_lightweight_v1" in data["models"]


def test_image_anime_job_lifecycle():
    # Create in-memory test image
    img = Image.new("RGB", (128, 128), color=(200, 100, 50))
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="JPEG")
    img_bytes.seek(0)

    # Submit job
    response = client.post(
        "/api/v1/image/anime",
        files={"image": ("test_photo.jpg", img_bytes, "image/jpeg")},
        data={"style": "default", "quality": "fast", "resolution": 128}
    )
    assert response.status_code == 202
    job_data = response.json()
    assert "job_id" in job_data
    job_id = job_data["job_id"]

    # Poll status until completed (Lightweight runs in <0.2s)
    max_retries = 30
    for _ in range(max_retries):
        status_res = client.get(f"/api/v1/jobs/{job_id}")
        assert status_res.status_code == 200
        cur_status = status_res.json()
        if cur_status["status"] in ("COMPLETED", "FAILED"):
            break
        time.sleep(0.1)

    assert cur_status["status"] == "COMPLETED"
    assert cur_status["progress"] == 100
    assert cur_status["output_url"] == f"/api/v1/jobs/{job_id}/result"

    # Download Result
    result_res = client.get(f"/api/v1/jobs/{job_id}/result")
    assert result_res.status_code == 200
    assert result_res.headers["content-type"] == "image/jpeg"
    assert len(result_res.content) > 0
