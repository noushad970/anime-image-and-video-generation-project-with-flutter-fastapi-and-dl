# Mobile Client Architecture — Anime Reality AI

The Anime Reality AI mobile application is built with **Flutter 3.47.3** (Dart 3.13) for Android and desktop clients, featuring a dark-mode Japanese animation aesthetic, Google Fonts `Outfit`, and API communication with the FastAPI backend.

---

## 📱 Implemented Screens & Workflows

1. **Splash Screen ([mobile/lib/screens/splash_screen.dart](file:///c:/Users/abnou/OneDrive/Desktop/Anime%20World%20App%20project/mobile/lib/screens/splash_screen.dart))**:
   - Animated glowing emblem.
   - Handshake check querying `/health` for RTX 5060 GPU and CUDA status.
2. **Home Screen ([mobile/lib/screens/home_screen.dart](file:///c:/Users/abnou/OneDrive/Desktop/Anime%20World%20App%20project/mobile/lib/screens/home_screen.dart))**:
   - RTX 5060 Acceleration status banner.
   - Core action cards: **Photo ➔ Anime**, **Video ➔ Anime Video**, **Live Anime Camera**, **Anime Styles**, and **Creations History**.
3. **Photo Screen ([mobile/lib/screens/photo_screen.dart](file:///c:/Users/abnou/OneDrive/Desktop/Anime%20World%20App%20project/mobile/lib/screens/photo_screen.dart))**:
   - Camera capture or gallery picker.
   - Anime style selection (`Classic Studio Anime`, `Watercolor Shinkai`, `High Fantasy`, `Cyberpunk`).
   - Quality mode selection (`FAST`, `BALANCED`, `QUALITY`).
   - Real-time generation polling and direct sharing via `share_plus`.
4. **Video Screen ([mobile/lib/screens/video_screen.dart](file:///c:/Users/abnou/OneDrive/Desktop/Anime%20World%20App%20project/mobile/lib/screens/video_screen.dart))**:
   - Video upload and camera recording.
   - Multi-stage progress indicators (`Uploading` ➔ `Extracting Video Frames` ➔ `AI Temporal Transformation` ➔ `Reconstructing Video & Audio` ➔ `Completed`).
5. **Anime Camera ([mobile/lib/screens/camera_screen.dart](file:///c:/Users/abnou/OneDrive/Desktop/Anime%20World%20App%20project/mobile/lib/screens/camera_screen.dart))**:
   - Viewfinder preview with instant stylization capture.
6. **Styles Showcase ([mobile/lib/screens/styles_screen.dart](file:///c:/Users/abnou/OneDrive/Desktop/Anime%20World%20App%20project/mobile/lib/screens/styles_screen.dart))**:
   - Dynamic style catalog querying `/api/v1/styles` with recommended resolutions and strengths.
7. **Creations History ([mobile/lib/screens/history_screen.dart](file:///c:/Users/abnou/OneDrive/Desktop/Anime%20World%20App%20project/mobile/lib/screens/history_screen.dart))**:
   - Library of generated photos and videos.
8. **Settings & GPU Monitor ([mobile/lib/screens/settings_screen.dart](file:///c:/Users/abnou/OneDrive/Desktop/Anime%20World%20App%20project/mobile/lib/screens/settings_screen.dart))**:
   - Configurable Backend Server URL (`http://10.0.2.2:8000` for Android Emulator, `http://localhost:8000` for Desktop, or local LAN IP).
   - Live hardware diagnostics card displaying device name, CUDA status, total VRAM, and allocated VRAM.

---

## 🛠️ Running the Flutter Application

1. **Start the FastAPI Backend**:
   ```powershell
   .\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
   ```
2. **Run the Flutter Client**:
   ```powershell
   cd mobile
   flutter run
   ```
3. **Running on Android Device / Emulator**:
   - Android Emulator: `flutter run -d emulator` (automatically communicates via `http://10.0.2.2:8000`).
   - Physical Phone on Wi-Fi: Connect phone to same Wi-Fi network and set backend URL in App Settings (e.g. `http://192.168.1.50:8000`).

