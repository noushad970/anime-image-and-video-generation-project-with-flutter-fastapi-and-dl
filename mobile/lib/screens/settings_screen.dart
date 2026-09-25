import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import '../services/api_service.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  final TextEditingController _urlController = TextEditingController(text: ApiService.baseUrl);
  Map<String, dynamic>? _gpuStatus;
  bool _isLoadingGpu = false;

  @override
  void initState() {
    super.initState();
    _refreshGpuStatus();
  }

  Future<void> _refreshGpuStatus() async {
    setState(() => _isLoadingGpu = true);
    final health = await ApiService.getHealth();
    if (mounted) {
      setState(() {
        _gpuStatus = health;
        _isLoadingGpu = false;
      });
    }
  }

  void _saveServerUrl() {
    ApiService.setBaseUrl(_urlController.text.trim());
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Server URL updated!'), backgroundColor: AppColors.success),
    );
    _refreshGpuStatus();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Settings & GPU Monitor')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Backend Server Configuration
            Text('Backend API Connection', style: Theme.of(context).textTheme.titleLarge),
            const SizedBox(height: 12),
            Container(
              padding: const EdgeInsets.all(18),
              decoration: BoxDecoration(
                color: AppColors.surface,
                borderRadius: BorderRadius.circular(18),
                border: Border.all(color: AppColors.surfaceLight),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('Server Base URL:', style: TextStyle(fontSize: 13, color: AppColors.textSecondary)),
                  const SizedBox(height: 8),
                  TextField(
                    controller: _urlController,
                    style: const TextStyle(color: Colors.white),
                    decoration: InputDecoration(
                      filled: true,
                      fillColor: AppColors.surfaceLight,
                      contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
                      border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide.none),
                      hintText: 'http://192.168.1.x:8000',
                      hintStyle: const TextStyle(color: AppColors.textSecondary),
                    ),
                  ),
                  const SizedBox(height: 14),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.end,
                    children: [
                      ElevatedButton.icon(
                        onPressed: _saveServerUrl,
                        icon: const Icon(Icons.save_outlined, size: 18),
                        label: const Text('Save & Test Connection'),
                      ),
                    ],
                  ),
                ],
              ),
            ),
            const SizedBox(height: 28),

            // Live GPU Hardware Monitor
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text('Inference Hardware Diagnostics', style: Theme.of(context).textTheme.titleLarge),
                IconButton(
                  icon: const Icon(Icons.refresh_rounded, color: AppColors.secondary),
                  onPressed: _refreshGpuStatus,
                ),
              ],
            ),
            const SizedBox(height: 12),

            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: AppColors.surface,
                borderRadius: BorderRadius.circular(20),
                border: Border.all(color: AppColors.surfaceLight),
              ),
              child: _isLoadingGpu
                  ? const Center(child: Padding(padding: EdgeInsets.all(20), child: CircularProgressIndicator(color: AppColors.secondary)))
                  : Column(
                      children: [
                        _buildMetricRow('Device', _gpuStatus?['device_name'] ?? 'Unknown'),
                        const Divider(color: AppColors.surfaceLight, height: 24),
                        _buildMetricRow('CUDA Acceleration', (_gpuStatus?['cuda_available'] == true) ? 'ACTIVE' : 'OFFLINE', isStatus: true),
                        const Divider(color: AppColors.surfaceLight, height: 24),
                        _buildMetricRow('Total VRAM', '${_gpuStatus?['vram_total_gb'] ?? 0.0} GB'),
                        const Divider(color: AppColors.surfaceLight, height: 24),
                        _buildMetricRow('Free VRAM', '${_gpuStatus?['vram_free_gb'] ?? 0.0} GB'),
                        const Divider(color: AppColors.surfaceLight, height: 24),
                        _buildMetricRow('Allocated VRAM', '${_gpuStatus?['vram_allocated_gb'] ?? 0.0} GB'),
                      ],
                    ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMetricRow(String label, String value, {bool isStatus = false}) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(label, style: const TextStyle(fontSize: 14, color: AppColors.textSecondary)),
        Text(
          value,
          style: TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.bold,
            color: isStatus
                ? (value == 'ACTIVE' ? AppColors.success : AppColors.error)
                : Colors.white,
          ),
        ),
      ],
    );
  }
}
