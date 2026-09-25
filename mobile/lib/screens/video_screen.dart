import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:share_plus/share_plus.dart';
import '../theme/app_theme.dart';
import '../services/api_service.dart';

class VideoScreen extends StatefulWidget {
  const VideoScreen({super.key});

  @override
  State<VideoScreen> createState() => _VideoScreenState();
}

class _VideoScreenState extends State<VideoScreen> {
  final ImagePicker _picker = ImagePicker();
  File? _selectedVideo;
  String _selectedStyle = 'watercolor';
  String _selectedQuality = 'fast';
  int _resolution = 512;

  bool _isProcessing = false;
  int _progress = 0;
  String _currentStage = 'Uploading';
  String? _resultVideoUrl;
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

  Future<void> _pickVideo(ImageSource source) async {
    try {
      final picked = await _picker.pickVideo(source: source, maxDuration: const Duration(minutes: 2));
      if (picked != null) {
        setState(() {
          _selectedVideo = File(picked.path);
          _resultVideoUrl = null;
          _errorMessage = null;
        });
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Error selecting video: $e')));
    }
  }

  Future<void> _generateAnimeVideo() async {
    if (_selectedVideo == null) return;

    setState(() {
      _isProcessing = true;
      _progress = 5;
      _currentStage = 'Uploading Video...';
      _errorMessage = null;
      _resultVideoUrl = null;
    });

    try {
      final jobId = await ApiService.submitVideoAnime(
        videoFile: _selectedVideo!,
        style: _selectedStyle,
        quality: _selectedQuality,
        resolution: _resolution,
      );

      bool done = false;
      while (!done && mounted) {
        await Future.delayed(const Duration(milliseconds: 500));
        final job = await ApiService.getJobStatus(jobId);

        setState(() {
          _progress = job.progress;
          if (_progress < 20) {
            _currentStage = 'Extracting Video Frames...';
          } else if (_progress < 80) {
            _currentStage = 'AI Temporal Transformation...';
          } else if (_progress < 95) {
            _currentStage = 'Reconstructing Video & Audio...';
          } else {
            _currentStage = 'Completed';
          }
        });

        if (job.isCompleted) {
          done = true;
          setState(() {
            _isProcessing = false;
            _resultVideoUrl = ApiService.getResultMediaUrl(job.outputUrl!);
          });
        } else if (job.isFailed) {
          done = true;
          setState(() {
            _isProcessing = false;
            _errorMessage = job.errorMessage ?? 'Video transformation failed';
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
        title: const Text('Video ➔ Anime Video'),
        actions: [
          if (_resultVideoUrl != null)
            IconButton(
              icon: const Icon(Icons.share_rounded),
              onPressed: () => Share.shareUri(Uri.parse(_resultVideoUrl!)),
            ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Video Viewport
            _buildVideoViewport(),
            const SizedBox(height: 24),

            if (_isProcessing) ...[
              _buildProgressCard(),
              const SizedBox(height: 24),
            ],

            // Style Selector
            Text('Anime Style', style: Theme.of(context).textTheme.titleLarge),
            const SizedBox(height: 12),
            _buildStyleSelector(),
            const SizedBox(height: 20),

            // Quality Presets
            Text('Temporal & Quality Presets', style: Theme.of(context).textTheme.titleLarge),
            const SizedBox(height: 12),
            _buildQualitySelector(),
            const SizedBox(height: 28),

            // Start Processing Button
            SizedBox(
              width: double.infinity,
              height: 56,
              child: ElevatedButton(
                onPressed: (_selectedVideo == null || _isProcessing) ? null : _generateAnimeVideo,
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppColors.secondary,
                  foregroundColor: Colors.black,
                  disabledBackgroundColor: AppColors.surfaceLight,
                ),
                child: _isProcessing
                    ? const Text('Transforming Video...', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16))
                    : const Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(Icons.movie_creation_outlined, color: Colors.black),
                          SizedBox(width: 10),
                          Text('Start Video Transformation', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
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

  Widget _buildVideoViewport() {
    return Container(
      height: 220,
      width: double.infinity,
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: AppColors.surfaceLight),
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            _selectedVideo != null ? Icons.videocam_rounded : Icons.video_file_outlined,
            size: 48,
            color: AppColors.secondary,
          ),
          const SizedBox(height: 12),
          Text(
            _selectedVideo != null ? _selectedVideo!.path.split(Platform.pathSeparator).last : 'Select Video Clip',
            style: const TextStyle(fontSize: 15, fontWeight: FontWeight.bold, color: Colors.white),
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
          const SizedBox(height: 16),
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              OutlinedButton.icon(
                onPressed: () => _pickVideo(ImageSource.gallery),
                icon: const Icon(Icons.video_library_outlined, size: 18),
                label: const Text('Pick Video'),
                style: OutlinedButton.styleFrom(foregroundColor: Colors.white, side: const BorderSide(color: AppColors.surfaceLight)),
              ),
              const SizedBox(width: 12),
              OutlinedButton.icon(
                onPressed: () => _pickVideo(ImageSource.camera),
                icon: const Icon(Icons.videocam_outlined, size: 18),
                label: const Text('Record'),
                style: OutlinedButton.styleFrom(foregroundColor: Colors.white, side: const BorderSide(color: AppColors.surfaceLight)),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildProgressCard() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: AppColors.secondary.withOpacity(0.4)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(_currentStage, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14, color: AppColors.secondary)),
              Text('$_progress%', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14, color: Colors.white)),
            ],
          ),
          const SizedBox(height: 12),
          ClipRRect(
            borderRadius: BorderRadius.circular(10),
            child: LinearProgressIndicator(
              value: _progress / 100.0,
              minHeight: 8,
              backgroundColor: AppColors.surfaceLight,
              valueColor: const AlwaysStoppedAnimation<Color>(AppColors.secondary),
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
              selectedColor: AppColors.secondary,
              backgroundColor: AppColors.surface,
              labelStyle: TextStyle(
                color: isSelected ? Colors.black : AppColors.textSecondary,
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
    final modes = [
      {'key': 'fast', 'title': 'FAST (20+ FPS)', 'desc': 'Lightweight Cel Filter'},
      {'key': 'balanced', 'title': 'BALANCED', 'desc': 'Cross-Frame Temporal Filter'},
      {'key': 'quality', 'title': 'QUALITY', 'desc': 'Ultra Anime Diffusion'},
    ];
    return Column(
      children: modes.map((m) {
        final isSelected = _selectedQuality == m['key'];
        return Padding(
          padding: const EdgeInsets.only(bottom: 8),
          child: InkWell(
            onTap: () => setState(() => _selectedQuality = m['key']!),
            borderRadius: BorderRadius.circular(14),
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
              decoration: BoxDecoration(
                color: isSelected ? AppColors.secondary.withOpacity(0.15) : AppColors.surface,
                borderRadius: BorderRadius.circular(14),
                border: Border.all(color: isSelected ? AppColors.secondary : AppColors.surfaceLight),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(m['title']!, style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14, color: isSelected ? Colors.white : AppColors.textSecondary)),
                      Text(m['desc']!, style: const TextStyle(fontSize: 11, color: AppColors.textSecondary)),
                    ],
                  ),
                  if (isSelected)
                    const Icon(Icons.check_circle_rounded, color: AppColors.secondary, size: 20),
                ],
              ),
            ),
          ),
        );
      }).toList(),
    );
  }
}
