"""
Unit and Integration Tests for Anime Reality AI Dataset Preprocessing Pipeline.
"""

import os
import json
import pytest
from pathlib import Path
from PIL import Image

from scripts.dataset.validate_dataset import validate_image_file, validate_dataset_directory
from scripts.dataset.remove_duplicates import get_file_md5, get_dhash, remove_duplicates
from scripts.dataset.create_metadata import generate_dataset_metadata
from scripts.dataset.split_dataset import split_dataset
from scripts.dataset.prepare_real_dataset import process_image


@pytest.fixture
def sample_dataset_dir(tmp_path):
    """Creates a mock dataset structure with sample test images."""
    real_nature = tmp_path / "real" / "nature"
    anime_nature = tmp_path / "anime" / "nature"
    real_nature.mkdir(parents=True, exist_ok=True)
    anime_nature.mkdir(parents=True, exist_ok=True)

    # 1. Create valid real images
    img1 = Image.new("RGB", (256, 256), color=(255, 100, 100))
    img1.save(real_nature / "real_01.jpg", "JPEG")

    img2 = Image.new("RGB", (300, 200), color=(100, 255, 100))
    img2.save(real_nature / "real_02.jpg", "JPEG")

    # 2. Create duplicate image
    img1.save(real_nature / "real_01_dup.jpg", "JPEG")

    # 3. Create corrupt image
    corrupt_file = real_nature / "corrupt.jpg"
    corrupt_file.write_bytes(b"\xFF\xD8\xFF\xE0\x00\x10JFIF\x00\x01\x01NOT_A_VALID_IMAGE_STREAM")

    # 4. Create tiny invalid image (resolution < 64)
    tiny_img = Image.new("RGB", (32, 32), color=(50, 50, 50))
    tiny_img.save(real_nature / "tiny.png", "PNG")

    # 5. Create anime images
    img3 = Image.new("RGB", (512, 512), color=(100, 100, 255))
    img3.save(anime_nature / "anime_01.jpg", "JPEG")

    return tmp_path


def test_validate_image_file(sample_dataset_dir):
    valid_file = sample_dataset_dir / "real" / "nature" / "real_01.jpg"
    corrupt_file = sample_dataset_dir / "real" / "nature" / "corrupt.jpg"
    tiny_file = sample_dataset_dir / "real" / "nature" / "tiny.png"

    is_valid, _ = validate_image_file(valid_file)
    assert is_valid is True

    is_valid, reason = validate_image_file(corrupt_file)
    assert is_valid is False

    is_valid, reason = validate_image_file(tiny_file)
    assert is_valid is False
    assert "Resolution too low" in reason


def test_remove_duplicates(sample_dataset_dir):
    real_dir = sample_dataset_dir / "real" / "nature"
    file1 = real_dir / "real_01.jpg"
    file1_dup = real_dir / "real_01_dup.jpg"

    # Exact MD5 match
    assert get_file_md5(file1) == get_file_md5(file1_dup)

    # Perceptual hash match
    assert get_dhash(file1) == get_dhash(file1_dup)


def test_process_image_resize_and_crop(tmp_path):
    src = tmp_path / "input.jpg"
    dest = tmp_path / "output.jpg"

    # Create non-square test image (600x400)
    img = Image.new("RGB", (600, 400), color=(128, 128, 128))
    img.save(src, "JPEG")

    success = process_image(src, dest, resolution=256)
    assert success is True
    assert dest.exists()

    with Image.open(dest) as out_img:
        assert out_img.size == (256, 256)


def test_generate_dataset_metadata(sample_dataset_dir, tmp_path):
    metadata_out = tmp_path / "metadata.json"
    generate_dataset_metadata(str(sample_dataset_dir), str(metadata_out))

    assert metadata_out.exists()
    with open(metadata_out, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "dataset_name" in data
    assert "statistics" in data
    assert data["statistics"]["total_real_images"] >= 2
    assert data["statistics"]["total_anime_images"] >= 1


def test_split_dataset(sample_dataset_dir, tmp_path):
    splits_out = tmp_path / "splits"
    split_dataset(str(sample_dataset_dir), str(splits_out), train_ratio=0.5, val_ratio=0.25, test_ratio=0.25, seed=42)

    manifest_file = splits_out / "split_manifest.json"
    assert manifest_file.exists()

    with open(manifest_file, "r", encoding="utf-8") as f:
        splits = json.load(f)

    assert "real_train" in splits
    assert "real_val" in splits
    assert "real_test" in splits
    assert "anime_train" in splits
