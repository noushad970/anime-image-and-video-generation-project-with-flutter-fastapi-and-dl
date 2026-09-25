import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import '../services/api_service.dart';

class StylesScreen extends StatefulWidget {
  const StylesScreen({super.key});

  @override
  State<StylesScreen> createState() => _StylesScreenState();
}

class _StylesScreenState extends State<StylesScreen> {
  List<AnimeStyle> _styles = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _fetchStyles();
  }

  Future<void> _fetchStyles() async {
    final list = await ApiService.getStyles();
    if (mounted) {
      setState(() {
        _styles = list;
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Anime Style Presets')),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator(color: AppColors.primary))
          : ListView.separated(
              padding: const EdgeInsets.all(20),
              itemCount: _styles.length,
              separatorBuilder: (_, __) => const SizedBox(height: 16),
              itemBuilder: (context, index) {
                final s = _styles[index];
                return Container(
                  padding: const EdgeInsets.all(20),
                  decoration: BoxDecoration(
                    color: AppColors.surface,
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(color: AppColors.surfaceLight),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text(s.displayName, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.white)),
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                            decoration: BoxDecoration(
                              color: AppColors.primary.withOpacity(0.2),
                              borderRadius: BorderRadius.circular(12),
                            ),
                            child: Text(s.model, style: const TextStyle(fontSize: 11, color: AppColors.primaryLight, fontWeight: FontWeight.bold)),
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      Text(s.description ?? 'High quality Japanese animation aesthetic', style: const TextStyle(fontSize: 13, color: AppColors.textSecondary)),
                      const SizedBox(height: 16),
                      Row(
                        children: [
                          const Icon(Icons.tune_rounded, size: 16, color: AppColors.secondary),
                          const SizedBox(width: 6),
                          Text('Strength: ${(s.strength * 100).toInt()}%', style: const TextStyle(fontSize: 12, color: AppColors.textSecondary)),
                          const SizedBox(width: 16),
                          const Icon(Icons.aspect_ratio_rounded, size: 16, color: AppColors.secondary),
                          const SizedBox(width: 6),
                          Text('Res: ${s.recommendedResolution}px', style: const TextStyle(fontSize: 12, color: AppColors.textSecondary)),
                        ],
                      ),
                    ],
                  ),
                );
              },
            ),
    );
  }
}
