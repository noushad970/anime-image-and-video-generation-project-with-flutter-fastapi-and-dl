"""
Video-to-Anime Transformation Pipeline for Anime Reality AI.
Extracts frames, applies temporal consistency smoothing, transforms each frame to anime style,
and reconstructs the video with audio preservation via FFmpeg.
"""

import os
import sys
import time
import shutil
import tempfile
import argparse
import subprocess
from pathlib import Path
from PIL import Image
import cv2
import numpy as np
from tqdm import tqdm

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from inference.image_to_anime import transform_image_to_anime
from inference.memory_manager import VRAMManager


class TemporalSmoother:
    """
    Temporal smoothing engine to eliminate flickering and maintain cross-frame consistency.
    Uses exponential moving average blending and luminance stabilization.
    """
    def __init__(self, alpha: float = 0.25):
        self.alpha = alpha  # Blend weight for previous frame (0.0 = no smoothing, 0.5 = strong)
        self.prev_frame_np = None

    def smooth(self, current_pil: Image.Image) -> Image.Image:
        curr_np = np.array(current_pil).astype(np.float32)
        if self.prev_frame_np is None:
            self.prev_frame_np = curr_np
            return current_pil

        # Match dimensions if needed
        if self.prev_frame_np.shape != curr_np.shape:
            self.prev_frame_np = cv2.resize(self.prev_frame_np, (curr_np.shape[1], curr_np.shape[0]))

        # Temporal EMA blending: curr = (1 - alpha) * curr + alpha * prev
        smoothed_np = (1.0 - self.alpha) * curr_np + self.alpha * self.prev_frame_np
        smoothed_np = np.clip(smoothed_np, 0, 255).astype(np.uint8)
        self.prev_frame_np = smoothed_np.astype(np.float32)

        return Image.fromarray(smoothed_np)


def get_video_info(video_path: str):
    """Extracts FPS, frame count, width, and height using OpenCV."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Unable to open video: {video_path}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()
    return {"fps": fps, "total_frames": total_frames, "width": width, "height": height}


def transform_video_to_anime(
    input_path: str,
    output_path: str = "outputs/anime_video.mp4",
    style: str = "default",
    quality: str = "fast",
    resolution: int = 512,
    temporal_smoothing: bool = True,
    smoothing_alpha: float = 0.25,
    max_frames: int = None
):
    start_time = time.time()
    in_p = Path(input_path)
    if not in_p.exists():
        raise FileNotFoundError(f"Input video not found: {input_path}")

    out_p = Path(output_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)

    info = get_video_info(str(in_p))
    fps = info["fps"]
    total_frames = info["total_frames"]
    if max_frames and max_frames < total_frames:
        total_frames = max_frames

    print("==================================================")
    print("ANIME REALITY AI — VIDEO TRANSFORMATION ENGINE")
    print("==================================================")
    print(f"Input Video:      {in_p.name} ({info['width']}x{info['height']} @ {fps:.2f} FPS)")
    print(f"Total Frames:     {total_frames}")
    print(f"Style Preset:     {style}")
    print(f"Quality Mode:     {quality}")
    print(f"Target Res:       {resolution}px")
    print(f"Temporal Smooth:  {temporal_smoothing} (alpha: {smoothing_alpha})")
    print("==================================================")

    # 1. Prepare temporary workspaces
    temp_dir = Path(tempfile.mkdtemp(prefix="anime_video_"))
    frames_in_dir = temp_dir / "raw_frames"
    frames_out_dir = temp_dir / "anime_frames"
    frames_in_dir.mkdir()
    frames_out_dir.mkdir()
    audio_path = temp_dir / "audio.aac"

    try:
        # 2. Extract audio track if present (via FFmpeg)
        has_audio = False
        try:
            cmd_audio = [
                "ffmpeg", "-y", "-i", str(in_p),
                "-vn", "-acodec", "copy", str(audio_path)
            ]
            res = subprocess.run(cmd_audio, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if res.returncode == 0 and audio_path.exists() and audio_path.stat().st_size > 0:
                has_audio = True
                print("Extracted original audio track for synchronization.")
        except Exception:
            pass

        # 3. Process video frames
        cap = cv2.VideoCapture(str(in_p))
        smoother = TemporalSmoother(alpha=smoothing_alpha) if temporal_smoothing else None

        frame_idx = 0
        pbar = tqdm(total=total_frames, desc="AI Frame Processing", unit="frame")

        while cap.isOpened() and (max_frames is None or frame_idx < max_frames):
            ret, frame = cap.read()
            if not ret:
                break

            # Convert BGR frame to PIL RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(frame_rgb)

            # Apply AI Anime Transformation
            anime_pil = transform_image_to_anime(
                input_path=pil_img,
                style=style,
                quality=quality,
                engine="lightweight" if quality in ("fast", "balanced") else "auto",
                resolution=resolution
            )

            # Apply Temporal Consistency Smoothing
            if smoother:
                anime_pil = smoother.smooth(anime_pil)

            # Save processed frame
            frame_out_file = frames_out_dir / f"frame_{frame_idx:06d}.jpg"
            anime_pil.save(frame_out_file, "JPEG", quality=95)

            frame_idx += 1
            pbar.update(1)

        cap.release()
        pbar.close()

        # 4. Reconstruct video using FFmpeg
        print("\nReconstructing output video with FFmpeg...")
        temp_video_out = temp_dir / "rendered_silent.mp4"
        cmd_render = [
            "ffmpeg", "-y",
            "-framerate", str(fps),
            "-i", str(frames_out_dir / "frame_%06d.jpg"),
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-crf", "18",
            "-preset", "medium",
            str(temp_video_out)
        ]
        subprocess.run(cmd_render, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # 5. Merge audio back if available
        if has_audio:
            cmd_merge = [
                "ffmpeg", "-y",
                "-i", str(temp_video_out),
                "-i", str(audio_path),
                "-c:v", "copy",
                "-c:a", "aac",
                "-shortest",
                str(out_p)
            ]
            subprocess.run(cmd_merge, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            shutil.copy(str(temp_video_out), str(out_p))

        elapsed = time.time() - start_time
        processed_fps = frame_idx / max(elapsed, 0.001)
        print("==================================================")
        print("VIDEO TRANSFORMATION COMPLETED SUCCESSFULLY!")
        print(f"Output File:    {out_p.resolve()}")
        print(f"Total Time:     {elapsed:.2f}s ({processed_fps:.2f} FPS throughput)")
        print("==================================================")

    finally:
        # Cleanup temporary workspace
        shutil.rmtree(temp_dir, ignore_errors=True)


def main():
    parser = argparse.ArgumentParser(description="Anime Reality AI — Video to Anime Transformation CLI")
    parser.add_argument("--input", "-i", type=str, required=True, help="Input video (.mp4, .avi, .mov, .webm)")
    parser.add_argument("--output", "-o", type=str, default="outputs/anime_video.mp4", help="Output video path")
    parser.add_argument("--style", "-s", type=str, default="default", choices=["default", "watercolor", "fantasy", "cyberpunk"], help="Anime style")
    parser.add_argument("--quality", "-q", type=str, default="fast", choices=["fast", "balanced", "quality"], help="Quality profile")
    parser.add_argument("--resolution", "-r", type=int, default=512, help="Frame resolution")
    parser.add_argument("--smoothing", action="store_true", default=True, help="Enable temporal consistency smoothing")
    parser.add_argument("--alpha", type=float, default=0.25, help="Temporal blend strength (0.0 - 0.5)")
    parser.add_argument("--max-frames", type=int, default=None, help="Limit max frames for testing")
    args = parser.parse_args()

    transform_video_to_anime(
        input_path=args.input,
        output_path=args.output,
        style=args.style,
        quality=args.quality,
        resolution=args.resolution,
        temporal_smoothing=args.smoothing,
        smoothing_alpha=args.alpha,
        max_frames=args.max_frames
    )


if __name__ == "__main__":
    main()
