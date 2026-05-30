import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/game_provider.dart';
import 'game_screen.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [Color(0xFF1A0033), Color(0xFF3D0066)],
          ),
        ),
        child: SafeArea(
          child: Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Text(
                  '🎬',
                  style: TextStyle(fontSize: 80),
                ),
                const SizedBox(height: 24),
                const Text(
                  'Indian Movie\nGenie',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    fontSize: 40,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                    height: 1.1,
                  ),
                ),
                const SizedBox(height: 12),
                const Text(
                  'Think of an Indian movie.\nI\'ll guess it!',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    fontSize: 16,
                    color: Colors.white60,
                  ),
                ),
                const SizedBox(height: 60),
                _LanguageChips(),
                const SizedBox(height: 48),
                _StartButton(),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _LanguageChips extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final langs = ['Hindi', 'Tamil', 'Telugu', 'Malayalam', 'Kannada'];
    return Wrap(
      spacing: 8,
      children: langs
          .map((l) => Chip(
                label: Text(l, style: const TextStyle(color: Colors.white70, fontSize: 12)),
                backgroundColor: Colors.white12,
                side: BorderSide.none,
              ))
          .toList(),
    );
  }
}

class _StartButton extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final provider = context.watch<GameProvider>();
    return ElevatedButton(
      onPressed: provider.loading
          ? null
          : () async {
              await context.read<GameProvider>().startGame();
              if (context.mounted && context.read<GameProvider>().error == null) {
                Navigator.push(
                  context,
                  MaterialPageRoute(builder: (_) => const GameScreen()),
                );
              }
            },
      style: ElevatedButton.styleFrom(
        backgroundColor: const Color(0xFFFF6B00),
        foregroundColor: Colors.white,
        padding: const EdgeInsets.symmetric(horizontal: 48, vertical: 16),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(30)),
        textStyle: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
      ),
      child: provider.loading
          ? const SizedBox(width: 24, height: 24, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
          : const Text('Let\'s Play!'),
    );
  }
}
