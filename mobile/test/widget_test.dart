import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:anime_reality_mobile/theme/app_theme.dart';
import 'package:anime_reality_mobile/screens/home_screen.dart';

void main() {
  testWidgets('Anime Reality AI HomeScreen smoke test', (WidgetTester tester) async {
    await tester.pumpWidget(
      MaterialApp(
        theme: AppTheme.darkTheme,
        home: const HomeScreen(),
      ),
    );
    await tester.pump();
    expect(find.text('Anime Reality AI'), findsOneWidget);
    expect(find.text('Photo ➔ Anime'), findsOneWidget);
    expect(find.text('Video ➔ Anime Video'), findsOneWidget);
    expect(find.text('Live Anime Camera'), findsOneWidget);
  });
}
