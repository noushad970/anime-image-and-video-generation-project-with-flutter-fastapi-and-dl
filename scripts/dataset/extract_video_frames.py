"""
Video Frame Extraction Utility for Anime Reality AI.
Extracts frames from video files with configurable FPS, resolution, and output naming.
"""

import os
import argparse
import subprocess
from pathlib import Path
import cv2

def extract_frames_opencv(video_path: Path, output_dir: Path, target_fps: float = None, max_frames: int = None, resolution: int = 512):
    output_dir.mkdir(parents=True, exist_ok=True)
    cap = cv2.VideoCapture(str(video_path))
    
    if not cap.isOpened():
        print(f"Error: Could not open video file {video_path}")
        return 0
        
    src_fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_src_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"Source Video: {video_path.name} | FPS: {src_fps:.2f} | Total Frames: {total_src_frames}")
    
    frame_interval = int(round(src_fps / target_fps)) if target_fps and target_fps < src_fps else 1
    
    frame_idx = 0
    saved_idx = 0
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        if frame_idx % frame_interval == 0:
            # Resize preserving aspect ratio or center crop
            h, w = frame.shape[:2]
            scale = resolution / min(h, w)
            new_w, new_h = int(w * scale), int(h * scale)
            resized = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_AREA)
            
            # Center crop to target resolution
            start_x = (new_w - resolution) // 2
            start_y = (new_h - resolution) // 2
            cropped = resized[start_y:start_y + resolution, start_x:start_x + resolution]
            
            out_filename = output_dir / f"frame_{saved_idx:06d}.jpg"
            cv2.imwrite(str(out_filename), cropped, [cv2.IMWRITE_JPEG_QUALITY, 95])
            saved_idx += 1
            
            if max_frames and saved_idx >= max_frames:
                break
                
        frame_idx += 1
        
    cap.release()
    print(f"Extracted {saved_idx} frames to {output_dir}")
    return saved_idx

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract and preprocess frames from video files.")
    parser.add_argument("--video", type=str, required=True, help="Path to input video file")
    parser.add_argument("--output", type=str, required=True, help="Destination directory for extracted frames")
    parser.add_argument("--fps", type=float, default=24.0, help="Target extraction FPS")
    parser.add_argument("--resolution", type=int, default=512, help="Target square resolution (e.g., 512)")
    parser.add_argument("--max-frames", type=int, default=None, help="Maximum number of frames to extract")
    args = parser.parse_args()
    
    extract_frames_opencv(
        video_path=Path(args.video),
        output_dir=Path(args.output),
        target_fps=args.fps,
        max_frames=args.max_frames,
        resolution=args.resolution
    )
