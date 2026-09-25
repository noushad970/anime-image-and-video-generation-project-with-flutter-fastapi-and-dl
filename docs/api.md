# Backend API Reference — Anime Reality AI

The Anime Reality AI FastAPI backend provides self-contained, asynchronous, and memory-safe endpoints for photo and video anime transformation.

Base URL: `http://localhost:8000`

---

## 1. System Health
### `GET /health`
Returns real-time GPU/CPU status, CUDA availability, and dedicated VRAM usage.

**Example Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "device_name": "NVIDIA GeForce RTX 5060",
  "cuda_available": true,
  "vram_total_gb": 7.96,
  "vram_free_gb": 6.87,
  "vram_allocated_gb": 0.03
}
```

---

## 2. Photo → Anime Transformation
### `POST /api/v1/image/anime`
Submits a photo for asynchronous anime transformation.

**Request (`multipart/form-data`):**
* `image` (binary file): Real-world photo (`.jpg`, `.png`, `.webp`, max 20MB)
* `style` (string, optional): Preset (`default`, `watercolor`, `fantasy`, `cyberpunk`, default: `default`)
* `quality` (string, optional): Preset (`fast`, `balanced`, `quality`, default: `balanced`)
* `resolution` (int, optional): Output resolution (default: `512`)

**cURL Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/image/anime" \
  -F "image=@photo.jpg" \
  -F "style=watercolor" \
  -F "quality=balanced"
```

**Response (HTTP 202 Accepted):**
```json
{
  "job_id": "img_a8b9c0d1e2f3",
  "type": "image",
  "status": "QUEUED",
  "style": "watercolor",
  "quality": "balanced",
  "created_at": "2026-09-25T07:37:00.000000"
}
```

---

## 3. Video → Anime Transformation
### `POST /api/v1/video/anime`
Submits a video file for non-blocking asynchronous anime stylization and temporal smoothing.

**Request (`multipart/form-data`):**
* `video` (binary file): Real-world video (`.mp4`, `.avi`, `.mov`, `.webm`, max 100MB)
* `style` (string, optional): Preset (`default`, `watercolor`, `fantasy`, `cyberpunk`, default: `default`)
* `quality` (string, optional): Preset (`fast`, `balanced`, `quality`, default: `fast`)
* `resolution` (int, optional): Frame resolution (default: `512`)

**cURL Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/video/anime" \
  -F "video=@street_video.mp4" \
  -F "style=watercolor" \
  -F "quality=fast"
```

**Response (HTTP 202 Accepted):**
```json
{
  "job_id": "vid_b7c8d9e0f1a2",
  "type": "video",
  "status": "QUEUED",
  "style": "watercolor",
  "quality": "fast",
  "created_at": "2026-09-25T07:37:00.000000"
}
```

---

## 4. Job Management & Results
### `GET /api/v1/jobs/{job_id}`
Returns real-time processing status and progress percentage (0–100%).

**Response:**
```json
{
  "id": "img_a8b9c0d1e2f3",
  "type": "image",
  "status": "COMPLETED",
  "progress": 100,
  "style": "watercolor",
  "quality": "balanced",
  "output_url": "/api/v1/jobs/img_a8b9c0d1e2f3/result",
  "error_message": null,
  "created_at": "2026-09-25T07:37:00.000000",
  "started_at": "2026-09-25T07:37:00.050000",
  "completed_at": "2026-09-25T07:37:00.180000"
}
```

### `GET /api/v1/jobs/{job_id}/result`
Streams or downloads the completed anime image (`image/jpeg`) or anime video (`video/mp4`).

### `POST /api/v1/jobs/{job_id}/cancel`
Cancels a queued or pending job.

---

## 5. Styles & Models Discovery
### `GET /api/v1/styles`
Lists all anime styles configured in the system.

### `GET /api/v1/styles/{style_name}`
Retrieves configuration parameters for a specific style.

### `GET /api/v1/models`
Returns registered AI models, VRAM requirements, and licenses from the model registry.

