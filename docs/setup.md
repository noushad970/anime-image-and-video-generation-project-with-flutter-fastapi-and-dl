# Setup & Installation Guide — Anime Reality AI

## Prerequisites
- **OS**: Windows 11 64-bit or Ubuntu 24.04 (WSL2)
- **GPU**: NVIDIA RTX 5060 (8GB VRAM) with Driver >= 550+ (Current: 610.88)
- **CUDA**: 12.8 / 12.6
- **Python**: 3.11.x
- **FFmpeg**: 9.x+ (Gyan Essentials or system FFmpeg)

## 1. Quick Environment Setup
```powershell
# 1. Create Python 3.11 Virtual Environment using uv
uv venv --python 3.11 .venv

# 2. Activate Virtual Environment
.venv\Scripts\activate

# 3. Install PyTorch with CUDA 12.8 Acceleration
uv pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128

# 4. Install Project Dependencies
uv pip install -r requirements.txt
```

## 2. Verify GPU & CUDA Acceleration
```powershell
uv run python scripts/check_gpu.py
```
Expected output:
- `CUDA available: True`
- `GPU: NVIDIA GeForce RTX 5060`
- `VRAM Total: ~8.0 GB`
- `Tensor Test: SUCCESS`
