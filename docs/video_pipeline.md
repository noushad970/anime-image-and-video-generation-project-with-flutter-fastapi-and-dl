# Video Pipeline & Temporal Consistency — Anime Reality AI

## Video Processing Flow
```
Input Video (MP4/MOV/WEBM)
       |
       v
FFmpeg Demuxing & Frame Extraction (e.g. 24 fps)
       |
       v
Conditioning Extractors:
   - MiDaS / Depth Anything (Depth Map)
   - Lineart / Canny (Structural Edges)
   - OpenPose / DWPose (Human Poses)
       |
       v
Temporal AI Engine (Latent Reuse / Optical Flow Warping / AnimateDiff Motion Module)
       |
       v
Post-Processing & Tiled VAE Decoding
       |
       v
FFmpeg Remuxing (H.264 / AAC Audio Pass-through)
       |
       v
Consistent Anime Video
```

## Anti-Flickering Strategies for 8 GB VRAM
1. **Latent Blending**: Initial noise latents for frame $t$ are partially initialized from warped latents of frame $t-1$ using Farneback / DIS optical flow.
2. **Motion Module Conditioning**: Temporal self-attention layers compute cross-frame feature representations across sliding window chunks (16–32 frames).
3. **ControlNet Depth Locking**: Restricts background geometry and building silhouettes from morphing between frames.
