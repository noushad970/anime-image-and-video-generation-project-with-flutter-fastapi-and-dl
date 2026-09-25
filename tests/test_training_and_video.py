"""
Unit and Integration Tests for Training Pipeline and Video Transformation Engine.
"""

import os
import pytest
import numpy as np
import cv2
import torch
from pathlib import Path
from PIL import Image

from training.dataset_loader import UnpairedAnimeDataset
from training.image.discriminator import PatchDiscriminator
from video.video_to_anime import TemporalSmoother, transform_video_to_anime, get_video_info


@pytest.fixture
def sample_video_clip(tmp_path):
    """Generates a synthetic 15-frame test video clip with moving shapes."""
    video_path = tmp_path / "test_motion.mp4"
    fps = 24
    w, h = 256, 256
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(str(video_path), fourcc, fps, (w, h))

    for i in range(15):
        frame = np.zeros((h, w, 3), dtype=np.uint8)
        # Gradient background
        frame[:, :, 0] = np.linspace(50, 200, w)
        frame[:, :, 1] = 100
        # Moving circle
        cx = int(40 + i * 12)
        cy = 128
        cv2.circle(frame, (cx, cy), 30, (0, 255, 255), -1)
        out.write(frame)

    out.release()
    return video_path


def test_unpaired_dataset_loader(tmp_path):
    real_p = tmp_path / "real"
    anime_p = tmp_path / "anime"
    real_p.mkdir()
    anime_p.mkdir()

    # Create dummy images
    Image.new("RGB", (128, 128), (255, 0, 0)).save(real_p / "r1.jpg")
    Image.new("RGB", (128, 128), (0, 255, 0)).save(anime_p / "a1.jpg")

    ds = UnpairedAnimeDataset(real_dir=str(real_p), anime_dir=str(anime_p), resolution=128, augment=False)
    assert len(ds) >= 1

    r_tensor, a_tensor = ds[0]
    assert r_tensor.shape == (3, 128, 128)
    assert a_tensor.shape == (3, 128, 128)


def test_patch_discriminator_forward():
    d = PatchDiscriminator(in_channels=3, num_filters=16, num_layers=2).eval()
    dummy = torch.randn(2, 3, 128, 128)
    with torch.no_grad():
        out = d(dummy)
    assert out.dim() == 4
    assert out.shape[0] == 2


def test_temporal_smoother():
    smoother = TemporalSmoother(alpha=0.3)
    img1 = Image.new("RGB", (128, 128), (100, 100, 100))
    img2 = Image.new("RGB", (128, 128), (200, 200, 200))

    smoothed1 = smoother.smooth(img1)
    assert smoothed1.size == (128, 128)

    smoothed2 = smoother.smooth(img2)
    assert smoothed2.size == (128, 128)
    # Value should be blended between 100 and 200
    arr2 = np.array(smoothed2)
    assert 120 < arr2[0, 0, 0] < 190


def test_video_to_anime_e2e(sample_video_clip, tmp_path):
    output_video = tmp_path / "output_anime.mp4"

    info = get_video_info(str(sample_video_clip))
    assert info["total_frames"] == 15

    transform_video_to_anime(
        input_path=str(sample_video_clip),
        output_path=str(output_video),
        style="default",
        quality="fast",
        resolution=128,
        temporal_smoothing=True,
        max_frames=5
    )

    assert output_video.exists()
    assert output_video.stat().st_size > 0
