import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;

class AnimeStyle {
  final String name;
  final String displayName;
  final String? description;
  final String model;
  final double strength;
  final int recommendedResolution;

  AnimeStyle({
    required this.name,
    required this.displayName,
    this.description,
    required this.model,
    required this.strength,
    required this.recommendedResolution,
  });

  factory AnimeStyle.fromJson(Map<String, dynamic> json) {
    return AnimeStyle(
      name: json['name'] ?? 'default',
      displayName: json['display_name'] ?? 'Default',
      description: json['description'],
      model: json['model'] ?? '',
      strength: (json['strength'] as num?)?.toDouble() ?? 1.0,
      recommendedResolution: json['recommended_resolution'] ?? 512,
    );
  }
}

class JobStatus {
  final String id;
  final String type;
  final String status;
  final int progress;
  final String style;
  final String quality;
  final String? outputUrl;
  final String? errorMessage;

  JobStatus({
    required this.id,
    required this.type,
    required this.status,
    required this.progress,
    required this.style,
    required this.quality,
    this.outputUrl,
    this.errorMessage,
  });

  factory JobStatus.fromJson(Map<String, dynamic> json) {
    return JobStatus(
      id: json['id'] ?? '',
      type: json['type'] ?? 'image',
      status: json['status'] ?? 'QUEUED',
      progress: json['progress'] ?? 0,
      style: json['style'] ?? 'default',
      quality: json['quality'] ?? 'balanced',
      outputUrl: json['output_url'],
      errorMessage: json['error_message'],
    );
  }

  bool get isCompleted => status == 'COMPLETED';
  bool get isFailed => status == 'FAILED';
}

class ApiService {
  static String baseUrl = 'http://10.0.2.2:8000'; // Default Android emulator host loopback

  static void setBaseUrl(String url) {
    if (url.endsWith('/')) {
      baseUrl = url.substring(0, url.length - 1);
    } else {
      baseUrl = url;
    }
  }

  static Future<Map<String, dynamic>> getHealth() async {
    try {
      final res = await http.get(Uri.parse('$baseUrl/health')).timeout(const Duration(seconds: 4));
      if (res.statusCode == 200) {
        return jsonDecode(res.body);
      }
    } catch (_) {}
    return {'status': 'offline', 'cuda_available': false, 'device_name': 'Unknown'};
  }

  static Future<List<AnimeStyle>> getStyles() async {
    try {
      final res = await http.get(Uri.parse('$baseUrl/api/v1/styles')).timeout(const Duration(seconds: 5));
      if (res.statusCode == 200) {
        final data = jsonDecode(res.body);
        final list = data['styles'] as List;
        return list.map((e) => AnimeStyle.fromJson(e)).toList();
      }
    } catch (_) {}
    // Fallback default styles if offline
    return [
      AnimeStyle(name: 'default', displayName: 'Classic Studio Anime', model: 'anime_lightweight_v1', strength: 1.0, recommendedResolution: 512, description: 'Crisp lineart, vibrant anime cel shading.'),
      AnimeStyle(name: 'watercolor', displayName: 'Watercolor Shinkai', model: 'anime_diffusion_base', strength: 0.85, recommendedResolution: 512, description: 'Luminous skies, soft painterly atmosphere.'),
      AnimeStyle(name: 'fantasy', displayName: 'High Fantasy Glow', model: 'anime_diffusion_base', strength: 0.85, recommendedResolution: 512, description: 'Rich magical glow and vibrant emerald/gold lighting.'),
      AnimeStyle(name: 'cyberpunk', displayName: 'Cyberpunk Neon', model: 'anime_diffusion_base', strength: 0.90, recommendedResolution: 512, description: 'High contrast neon highlights and moody cyber vibes.'),
    ];
  }

  static Future<String> submitPhotoAnime({
    required File imageFile,
    String style = 'default',
    String quality = 'balanced',
    int resolution = 512,
  }) async {
    final uri = Uri.parse('$baseUrl/api/v1/image/anime');
    final req = http.MultipartRequest('POST', uri)
      ..fields['style'] = style
      ..fields['quality'] = quality
      ..fields['resolution'] = resolution.toString()
      ..files.add(await http.MultipartFile.fromPath('image', imageFile.path));

    final streamedRes = await req.send();
    final res = await http.Response.fromStream(streamedRes);
    if (res.statusCode == 202) {
      final data = jsonDecode(res.body);
      return data['job_id'];
    } else {
      throw Exception('Failed to submit photo: ${res.body}');
    }
  }

  static Future<String> submitVideoAnime({
    required File videoFile,
    String style = 'default',
    String quality = 'fast',
    int resolution = 512,
  }) async {
    final uri = Uri.parse('$baseUrl/api/v1/video/anime');
    final req = http.MultipartRequest('POST', uri)
      ..fields['style'] = style
      ..fields['quality'] = quality
      ..fields['resolution'] = resolution.toString()
      ..files.add(await http.MultipartFile.fromPath('video', videoFile.path));

    final streamedRes = await req.send();
    final res = await http.Response.fromStream(streamedRes);
    if (res.statusCode == 202) {
      final data = jsonDecode(res.body);
      return data['job_id'];
    } else {
      throw Exception('Failed to submit video: ${res.body}');
    }
  }

  static Future<JobStatus> getJobStatus(String jobId) async {
    final uri = Uri.parse('$baseUrl/api/v1/jobs/$jobId');
    final res = await http.get(uri);
    if (res.statusCode == 200) {
      return JobStatus.fromJson(jsonDecode(res.body));
    } else {
      throw Exception('Job not found or server error');
    }
  }

  static String getResultMediaUrl(String relativeUrl) {
    if (relativeUrl.startsWith('http')) return relativeUrl;
    return '$baseUrl$relativeUrl';
  }
}
