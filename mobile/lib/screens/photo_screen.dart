import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:share_plus/share_plus.dart';
import '../theme/app_theme.dart';
import '../services/api_service.dart';

class PhotoScreen extends StatefulWidget {
  const PhotoScreen({super.key});

  @override
  State<PhotoScreen> createState() => _PhotoScreenState();
}

class _PhotoScreenState extends State<PhotoScreen> {
  final ImagePicker _picker = ImagePicker();
  File? _selectedImage;
  String _selectedStyle = 'watercolor';
  String _selectedQuality = 'balanced';
  int _resolution = 512;

  bool _isProcessing = false;
  int _progress = 0;
  String? _resultImageUrl;
  String? _errorMessage;
  List<AnimeStyle> _styles = [];

  @override
  void initState() {
    super.initState();
    _loadStyles();
  }

  Future<void> _loadStyles() async {
    final styles = await ApiService.getStyles();
    if (mounted) setState(() => _styles = styles);
  }

  Future<void> _pickImage(ImageSource source) async {
    try {
      final picked = await _picker.pickImage(source: source, maxWidth: 1920, maxHeight: 1920);
      if (picked != null) {
        setState(() {
          _selectedImage = File(picked.path);
          _resultImageUrl = null;
          _errorMessage = null;
        });
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Error picking image: $e')));
    }
  }

  Future<void> _generateAnime() async {
    if (_selectedImage == null) return;

    setState(() {
      _isProcessing = true;
      _progress = 10;
      _errorMessage = null;
      _resultImageUrl = null;
    });

    try {
      final jobId = await ApiService.submitPhotoAnime(
        imageFile: _selectedImage!,
        style: _selectedStyle,
        quality: _selectedQuality,
        resolution: _resolution,
      );

      // Poll job progress
      bool done = false;
      while (!done && mounted) {
        await Future.delayed(const Duration(milliseconds: 300));
        final job = await ApiService.getJobStatus(jobId);
        setState(() => _progress = job.progress);

        if (job.isCompleted) {
          done = true;
          setState(() {
            _isProcessing = false;
            _resultImageUrl = ApiService.getResultMediaUrl(job.outputUrl!);
          });
        } else if (job.isFailed) {
          done = true;
          setState(() {
            _isProcessing = false;
            _errorMessage = job.errorMessage ?? 'Transformation failed';
          });
        }
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _isProcessing = false;
          _errorMessage = e.toString();
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Photo ➔ Anime'),
        actions: [
          if (_resultImageUrl != null)
            IconButton(
              icon: const Icon(Icons.share_rounded),
              onPressed: () => Share.shareUri(Uri.parse(_resultImageUrl!)),
            ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Preview Viewport (Interactive Before/After or Picker)
            _buildImageViewport(),
            const SizedBox(height: 24),

            // Style Selection Chips
            Text('Select Anime Style', style: Theme.of(context).textTheme.titleLarge),
            const SizedBox(height: 12),
            _buildStyleSelector(),
            const SizedBox(height: 20),

            // Quality & Resolution Controls
            Text('Quality & Engine', style: Theme.of(context).textTheme.titleLarge),
            const SizedBox(height: 12),
            _buildQualitySelector(),
            const SizedBox(height: 28),

            // Generate CTA Button
            SizedBox(
              width: double.infinity,
              height: 56,
              child: ElevatedButton(
                onPressed: (_selectedImage == null || _isProcessing) ? null : _generateAnime,
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppColors.primary,
                  disabledBackgroundColor: AppColors.surfaceLight,
                ),
                child: _isProcessing
                    ? Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white)),
                          const SizedBox(width: 14),
                          Text('Generating Anime ($_progress%)...'),
                        ],
                      )
                    : Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: const [
                          Icon(Icons.auto_awesome, color: Colors.white),
                          SizedBox(width: 10),
                          Text('Transform Photo to Anime', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                        ],
                      ),
              ),
            ),

            if (_errorMessage != null) ...[
              const SizedBox(height: 16),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(color: AppColors.error.withOpacity(0.15), borderRadius: BorderRadius.circular(12)),
                child: Row(
                  children: [
                    const Icon(Icons.error_outline, color: AppColors.error),
                    const SizedBox(width: 10),
                    Expanded(child: Text(_errorMessage!, style: const TextStyle(color: AppColors.error, fontSize: 13))),
                  ],
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildImageViewport() {
    if (_selectedImage == null) {
      return Container(
        height: 280,
        width: double.infinity,
        decoration: BoxDecoration(
          color: AppColors.surface,
          borderRadius: BorderRadius.circular(24),
          border: Border.all(color: AppColors.surfaceLight, style: BorderStyle.solid),
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: AppColors.primary.withOpacity(0.15),
                shape: BoxShape.circle,
              ),
              child: const Icon(Icons.add_photo_alternate_outlined, size: 40, color: AppColors.primary),
            ),
            const SizedBox(height: 16),
            const Text('Upload a Real-World Photo', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.white)),
            const SizedBox(height: 6),
            const Text('Street, scenery, portrait, or landscape', style: TextStyle(fontSize: 12, color: AppColors.textSecondary)),
            const SizedBox(height: 20),
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                OutlinedButton.icon(
                  onPressed: () => _pickImage(ImageSource.gallery),
                  icon: const Icon(Icons.photo_library_outlined, size: 18),
                  label: const Text('Gallery'),
                  style: OutlinedButton.styleFrom(foregroundColor: Colors.white, side: const BorderSide(color: AppColors.surfaceLight)),
                ),
                const SizedBox(width: 12),
                OutlinedButton.icon(
                  onPressed: () => _pickImage(ImageSource.camera),
                  icon: const Icon(Icons.camera_alt_outlined, size: 18),
                  label: const Text('Camera'),
                  style: OutlinedButton.styleFrom(foregroundColor: Colors.white, side: const BorderSide(color: AppColors.surfaceLight)),
                ),
              ],
            ),
          ],
        ),
      );
    }

    return Container(
      height: 320,
      width: double.infinity,
      decoration: BoxDecoration(
        color: Colors.black,
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: AppColors.surfaceLight),
      ),
      clipBehavior: Clip.antiAlias,
      child: Stack(
        fit: StackFit.expand,
        children: [
          _resultImageUrl != null
              ? Image.network(_resultImageUrl!, fit: BoxFit.cover)
              : Image.file(_selectedImage!, fit: BoxFit.cover),
          Positioned(
            bottom: 12,
            right: 12,
            child: Row(
              children: [
                FloatingActionButton.small(
                  heroTag: 'change_img',
                  backgroundColor: Colors.black87,
                  foregroundColor: Colors.white,
                  onPressed: () => _pickImage(ImageSource.gallery),
                  child: const Icon(Icons.refresh),
                ),
              ],
            ),
          ),
          if (_resultImageUrl != null)
            Positioned(
              top: 12,
              left: 12,
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                decoration: BoxDecoration(color: AppColors.success, borderRadius: BorderRadius.circular(12)),
                child: const Text('Anime AI Generated', style: TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.bold)),
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildStyleSelector() {
    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: Row(
        children: _styles.map((s) {
          final isSelected = _selectedStyle == s.name;
          return Padding(
            padding: const EdgeInsets.only(right: 10),
            child: ChoiceChip(
              label: Text(s.displayName),
              selected: isSelected,
              onSelected: (_) => setState(() => _selectedStyle = s.name),
              selectedColor: AppColors.primary,
              backgroundColor: AppColors.surface,
              labelStyle: TextStyle(
                color: isSelected ? Colors.white : AppColors.textSecondary,
                fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
              ),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
            ),
          );
        }).toList(),
      ),
    );
  }

  Widget _buildQualitySelector() {
    final modes = ['fast', 'balanced', 'quality'];
    return Row(
      children: modes.map((m) {
        final isSelected = _selectedQuality == m;
        return Expanded(
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 4),
            child: InkWell(
              onTap: () => setState(() => _selectedQuality = m),
              borderRadius: BorderRadius.circular(12),
              child: Container(
                padding: const EdgeInsets.symmetric(vertical: 12),
                decoration: BoxDecoration(
                  color: isSelected ? AppColors.primary.withOpacity(0.25) : AppColors.surface,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: isSelected ? AppColors.primary : AppColors.surfaceLight),
                ),
                child: Column(
                  children: [
                    Text(m.toUpperCase(), style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: isSelected ? Colors.white : AppColors.textSecondary)),
                    const SizedBox(height: 2),
                    Text(
                      m == 'fast' ? '<150ms' : (m == 'balanced' ? 'Balanced' : 'Ultra SD'),
                      style: const TextStyle(fontSize: 10, color: AppColors.textSecondary),
                    ),
                  ],
                ),
              ),
            ),
          ),
        );
      }).toList(),
    );
  }
}
