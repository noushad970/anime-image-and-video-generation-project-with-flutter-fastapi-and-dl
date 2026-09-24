# Mobile Client Architecture — Anime Reality AI

## Technology Stack
- **Framework**: Flutter (Channel stable, Dart 3.13+)
- **Target Platform**: Android (SDK 36 / 37)
- **Networking**: `dio` / `http` with WebSocket progress listeners.
- **Media**: `image_picker`, `camera`, `video_player`, `gallery_saver_plus`.

## Mobile Application Screens
1. **Splash Screen**: Brand identity and connection handshake.
2. **Home Screen**: Feature hubs (Anime Camera, Photo -> Anime, Video -> Anime, Styles, History).
3. **Photo Mode**: Camera capture / gallery import -> interactive style & quality selector -> Split-slider Before/After view -> Export.
4. **Video Mode**: Video upload -> stage-by-stage generation progress (Uploading -> Extracting -> AI Diffusion -> Remuxing) -> Video Player.
5. **Anime Camera (Phase 9)**: Ultra low-latency viewfinder preview.
6. **Style Marketplace / Manager**: Visual preview of available anime models and custom LoRAs.
7. **Job History**: Local cache of generated transformations.
8. **Settings**: API endpoint URL configuration, local cache management, export quality preferences.
