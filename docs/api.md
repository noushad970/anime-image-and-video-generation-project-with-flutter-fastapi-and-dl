# Backend API Reference — Anime Reality AI

## Endpoints Specification

### System Health
- `GET /health`
  - Returns backend status, GPU availability, free VRAM, active jobs.

### Image Anime Transformation
- `POST /api/v1/image/anime`
  - **Form Data**: `image` (file), `style` (string: default/watercolor/fantasy/cyberpunk), `quality` (fast/balanced/quality)
  - **Response**: `{ "job_id": "...", "status": "QUEUED" }`

### Video Anime Transformation
- `POST /api/v1/video/anime`
  - **Form Data**: `video` (file), `style` (string), `quality` (string), `fps` (int)
  - **Response**: `{ "job_id": "...", "status": "QUEUED" }`

### Asynchronous Job Queue
- `GET /api/v1/jobs/{job_id}`
  - Returns job status (`QUEUED`, `PROCESSING`, `COMPLETED`, `FAILED`), progress (`0-100%`), and stage message.
- `GET /api/v1/jobs/{job_id}/result`
  - Downloads processed output image or video.

### Styles & Models
- `GET /api/v1/styles`
  - Lists available anime style presets with preview thumbnails and metadata.
- `GET /api/v1/models`
  - Lists registered models and hardware status.
