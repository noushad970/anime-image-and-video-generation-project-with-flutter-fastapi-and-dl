"""
Unit and Integration Tests for Anime Reality AI Inference Pipeline.
"""

import os
import pytest
from pathlib import Path
from PIL import Image
import numpy as np

from inference.memory_manager import VRAMManager
from inference.lightweight_generator import (
    AnimeGeneratorNetwork,
    StylizedAnimeFilter,
    LightweightAnimeEngine
)
from inference.image_to_anime import transform_image_to_anime


@pytest.fixture
def sample_test_image(tmp_path):
    """Creates a sample test photo with geometric content and color variation."""
    img_path = tmp_path / "sample_photo.jpg"
    arr = np.zeros((256, 256, 3), dtype=np.uint8)
    # Sky
    arr[:128, :] = [200, 150, 100]
    # Ground
    arr[128:, :] = [50, 120, 50]
    # Building box
    arr[80:180, 80:180] = [180, 80, 80]
    img = Image.fromarray(arr)
    img.save(img_path, "JPEG")
    return img_path


def test_vram_manager_status():
    status = VRAMManager.get_hardware_status()
    assert "cuda_available" in status
    assert "device_name" in status
    assert "vram_total_gb" in status
    assert isinstance(status["cuda_available"], bool)


def test_anime_generator_network_forward():
    import torch
    network = AnimeGeneratorNetwork().eval()
    dummy_input = torch.randn(1, 3, 128, 128)
    with torch.inference_mode():
        output = network(dummy_input)
    assert output.shape == (1, 3, 128, 128)


def test_stylized_anime_filter(sample_test_image):
    import cv2
    img_bgr = cv2.imread(str(sample_test_image))
    for style in ["default", "watercolor", "fantasy", "cyberpunk"]:
        out = StylizedAnimeFilter.apply(img_bgr, style=style)
        assert out is not None
        assert out.shape == img_bgr.shape


def test_transform_image_to_anime_e2e(sample_test_image, tmp_path):
    output_path = tmp_path / "output_anime.jpg"

    result_img = transform_image_to_anime(
        input_path=sample_test_image,
        output_path=output_path,
        style="default",
        quality="fast",
        engine="lightweight",
        resolution=256
    )

    assert result_img is not None
    assert output_path.exists()
    assert result_img.size == (256, 256)


def test_all_styles_transformation(sample_test_image, tmp_path):
    styles = ["default", "watercolor", "fantasy", "cyberpunk"]
    for s in styles:
        out_file = tmp_path / f"anime_{s}.jpg"
        img = transform_image_to_anime(
            input_path=sample_test_image,
            output_path=out_file,
            style=s,
            quality="fast",
            engine="lightweight",
            resolution=128
        )
        assert out_file.exists()
        assert img.size == (128, 128)
