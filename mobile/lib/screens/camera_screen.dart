import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'dart:io';
import '../theme/app_theme.dart';
import '../services/api_service.dart';

class CameraScreen extends StatefulWidget {
  const CameraScreen({super.key});

  @override
  State<CameraScreen> createState() => _CameraScreenState();
}

class _CameraScreenState extends State<CameraScreen> {
  final ImagePicker _picker = ImagePicker();
  File? _capturedImage;
  String? _stylizedImageUrl;
  bool _isProcessing = false;
  String _selectedStyle = 'watercolor';

  Future<void> _capturePhoto() async {
    try {
      final photo = await _picker.pickImage(source: ImageSource.camera);
      if (photo != null) {
        setState(() {
          _capturedImage = File(photo.path);
          _stylizedImageUrl = null;
          _isProcessing = true;
        });

        // Fast Anime stylization
        final jobId = await ApiService.submitPhotoAnime(
          imageFile: _capturedImage!,
          style: _selectedStyle,
          quality: 'fast',
          resolution: 512,
        );

        while (_isProcessing && mounted) {
          await Future.delayed(const Duration(milliseconds: 250));
          final job = await ApiService.getJobStatus(jobId);
          if (job.isCompleted) {
            setState(() {
              _isProcessing = false;
              _stylizedImageUrl = ApiService.getResultMediaUrl(job.outputUrl!);
            });
            break;
          } else if (job.isFailed) {
            setState(() => _isProcessing = false);
            break;
          }
        }
      }
    } catch (_) {
      setState(() => _isProcessing = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      appBar: AppBar(
        title: const Text('Live Anime Camera'),
        backgroundColor: Colors.transparent,
      ),
      body: Stack(
        fit: StackFit.expand,
        children: [
          // Viewport
          if (_stylizedImageUrl != null)
            Image.network(_stylizedImageUrl!, fit: BoxFit.cover)
          else if (_capturedImage != null)
            Image.file(_capturedImage!, fit: BoxFit.cover)
          else
            Container(
              color: const Color(0xFF0F1117),
              child: Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Container(
                      padding: const EdgeInsets.all(24),
                      decoration: BoxDecoration(
                        color: AppColors.accentPink.withOpacity(0.15),
                        shape: BoxShape.circle,
                      ),
                      child: const Icon(Icons.camera_alt_outlined, size: 54, color: AppColors.accentPink),
                    ),
                    const SizedBox(height: 20),
                    const Text('Tap Capture to Take Anime Photo', style: TextStyle(fontSize: 16, color: Colors.white70)),
                  ],
                ),
              ),
            ),

          if (_isProcessing)
            Container(
              color: Colors.black54,
              child: const Center(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    CircularProgressIndicator(color: AppColors.accentPink),
                    SizedBox(height: 16),
                    Text('Applying Anime Transformation...', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                  ],
                ),
              ),
            ),

          // Bottom Controls Overlay
          Positioned(
            bottom: 36,
            left: 0,
            right: 0,
            child: Column(
              children: [
                // Shutter Button
                GestureDetector(
                  onTap: _isProcessing ? null : _capturePhoto,
                  child: Container(
                    width: 76,
                    height: 76,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      border: Border.all(color: Colors.white, width: 4),
                      color: AppColors.accentPink,
                      boxShadow: [
                        BoxShadow(color: AppColors.accentPink.withOpacity(0.5), blurRadius: 20),
                      ],
                    ),
                    child: const Icon(Icons.camera, size: 36, color: Colors.white),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
