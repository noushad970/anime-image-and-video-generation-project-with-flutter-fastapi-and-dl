import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import 'photo_screen.dart';
import 'video_screen.dart';
import 'camera_screen.dart';
import 'styles_screen.dart';
import 'history_screen.dart';
import 'settings_screen.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Anime Reality AI'),
        actions: [
          IconButton(
            icon: const Icon(Icons.settings_outlined),
            onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const SettingsScreen())),
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Hero Banner Card
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(24),
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(24),
                gradient: const LinearGradient(
                  colors: [Color(0xFF2E1065), Color(0xFF164E63)],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                border: Border.all(color: AppColors.primary.withOpacity(0.3)),
                boxShadow: [
                  BoxShadow(
                    color: AppColors.primary.withOpacity(0.2),
                    blurRadius: 20,
                    offset: const Offset(0, 8),
                  ),
                ],
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                        decoration: BoxDecoration(
                          color: AppColors.primary.withOpacity(0.3),
                          borderRadius: BorderRadius.circular(20),
                          border: Border.all(color: AppColors.primaryLight.withOpacity(0.5)),
                        ),
                        child: const Row(
                          children: [
                            Icon(Icons.bolt, size: 14, color: AppColors.secondary),
                            SizedBox(width: 4),
                            Text('RTX 5060 Accelerated', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Colors.white)),
                          ],
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  const Text(
                    'Transform Reality\nInto Anime Worlds',
                    style: TextStyle(fontSize: 26, fontWeight: FontWeight.bold, height: 1.2, color: Colors.white),
                  ),
                  const SizedBox(height: 8),
                  const Text(
                    'High-fidelity neural stylization with temporal stability & Japanese animation aesthetics.',
                    style: TextStyle(fontSize: 13, color: AppColors.textSecondary),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 28),

            Text('Core AI Tools', style: Theme.of(context).textTheme.titleLarge),
            const SizedBox(height: 16),

            // Main Action Cards
            _buildFeatureCard(
              context: context,
              title: 'Photo ➔ Anime',
              subtitle: 'Transform any photo with classic & watercolor anime styles',
              icon: Icons.image_rounded,
              gradient: const LinearGradient(colors: [Color(0xFF8B5CF6), Color(0xFF6366F1)]),
              onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const PhotoScreen())),
            ),
            const SizedBox(height: 14),

            _buildFeatureCard(
              context: context,
              title: 'Video ➔ Anime Video',
              subtitle: 'Smooth, temporally consistent anime video conversion with audio',
              icon: Icons.video_collection_rounded,
              gradient: const LinearGradient(colors: [Color(0xFF06B6D4), Color(0xFF0284C7)]),
              onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const VideoScreen())),
            ),
            const SizedBox(height: 14),

            _buildFeatureCard(
              context: context,
              title: 'Live Anime Camera',
              subtitle: 'Real-time camera viewfinder with instant anime filters',
              icon: Icons.camera_alt_rounded,
              gradient: const LinearGradient(colors: [Color(0xFFEC4899), Color(0xFFD946EF)]),
              onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const CameraScreen())),
            ),

            const SizedBox(height: 28),
            Text('Explore & Library', style: Theme.of(context).textTheme.titleLarge),
            const SizedBox(height: 14),

            // Secondary Options Grid
            Row(
              children: [
                Expanded(
                  child: _buildSmallActionCard(
                    context: context,
                    title: 'Anime Styles',
                    subtitle: 'Shinkai, Ghibli, Cyberpunk',
                    icon: Icons.palette_outlined,
                    onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const StylesScreen())),
                  ),
                ),
                const SizedBox(width: 14),
                Expanded(
                  child: _buildSmallActionCard(
                    context: context,
                    title: 'Creations History',
                    subtitle: 'Saved photos & videos',
                    icon: Icons.history_rounded,
                    onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const HistoryScreen())),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 24),
          ],
        ),
      ),
    );
  }

  Widget _buildFeatureCard({
    required BuildContext context,
    required String title,
    required String subtitle,
    required IconData icon,
    required Gradient gradient,
    required VoidCallback onTap,
  }) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(20),
      child: Container(
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: AppColors.surface,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: AppColors.surfaceLight),
          boxShadow: [
            BoxShadow(color: Colors.black.withOpacity(0.3), blurRadius: 10, offset: const Offset(0, 4)),
          ],
        ),
        child: Row(
          children: [
            Container(
              width: 56,
              height: 56,
              decoration: BoxDecoration(
                gradient: gradient,
                borderRadius: BorderRadius.circular(16),
              ),
              child: Icon(icon, size: 30, color: Colors.white),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(title, style: const TextStyle(fontSize: 17, fontWeight: FontWeight.bold, color: Colors.white)),
                  const SizedBox(height: 4),
                  Text(subtitle, style: const TextStyle(fontSize: 12, color: AppColors.textSecondary)),
                ],
              ),
            ),
            const Icon(Icons.arrow_forward_ios_rounded, size: 16, color: AppColors.textSecondary),
          ],
        ),
      ),
    );
  }

  Widget _buildSmallActionCard({
    required BuildContext context,
    required String title,
    required String subtitle,
    required IconData icon,
    required VoidCallback onTap,
  }) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(18),
      child: Container(
        padding: const EdgeInsets.all(18),
        decoration: BoxDecoration(
          color: AppColors.surface,
          borderRadius: BorderRadius.circular(18),
          border: Border.all(color: AppColors.surfaceLight),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Icon(icon, color: AppColors.secondary, size: 28),
            const SizedBox(height: 12),
            Text(title, style: const TextStyle(fontSize: 15, fontWeight: FontWeight.bold, color: Colors.white)),
            const SizedBox(height: 2),
            Text(subtitle, style: const TextStyle(fontSize: 11, color: AppColors.textSecondary)),
          ],
        ),
      ),
    );
  }
}
