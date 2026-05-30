import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../models/game_models.dart';
import '../services/game_provider.dart';

class ResultScreen extends StatelessWidget {
  const ResultScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final provider = context.watch<GameProvider>();
    final state = provider.state;
    final guesses = state.guesses;
    final topGuess = guesses.isNotEmpty ? guesses.first : null;

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
          child: Column(
            children: [
              Expanded(
                child: SingleChildScrollView(
                  padding: const EdgeInsets.all(24),
                  child: Column(
                    children: [
                      const SizedBox(height: 16),
                      const Text('🧞', style: TextStyle(fontSize: 72)),
                      const SizedBox(height: 16),
                      const Text(
                        'I think it\'s...',
                        style: TextStyle(color: Colors.white60, fontSize: 18),
                      ),
                      const SizedBox(height: 24),
                      if (topGuess != null) _TopGuessCard(guess: topGuess),
                      if (guesses.length > 1) ...[
                        const SizedBox(height: 24),
                        const Text(
                          'Other possibilities',
                          style: TextStyle(color: Colors.white54, fontSize: 14),
                        ),
                        const SizedBox(height: 12),
                        ...guesses.skip(1).map((g) => _SmallGuessCard(guess: g)),
                      ],
                      const SizedBox(height: 32),
                      if (state.phase != GamePhase.done) _FeedbackRow(provider: provider, guesses: guesses),
                      if (state.phase == GamePhase.done) _DoneMessage(wasCorrect: state.wasCorrect),
                    ],
                  ),
                ),
              ),
              Padding(
                padding: const EdgeInsets.all(24),
                child: ElevatedButton(
                  onPressed: () {
                    provider.reset();
                    Navigator.popUntil(context, (route) => route.isFirst);
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFFFF6B00),
                    foregroundColor: Colors.white,
                    minimumSize: const Size(double.infinity, 52),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                    textStyle: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                  child: const Text('Play Again'),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _TopGuessCard extends StatelessWidget {
  final MovieGuess guess;
  const _TopGuessCard({required this.guess});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.12),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: const Color(0xFFFF6B00), width: 2),
      ),
      child: Column(
        children: [
          Text(
            guess.title,
            textAlign: TextAlign.center,
            style: const TextStyle(
              color: Colors.white,
              fontSize: 28,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            '${guess.year}  ·  ${_capitalize(guess.language)}',
            style: const TextStyle(color: Colors.white60, fontSize: 14),
          ),
          const SizedBox(height: 4),
          Text(
            'Dir: ${guess.director}',
            style: const TextStyle(color: Colors.white54, fontSize: 13),
          ),
          Text(
            'Lead: ${guess.leadActor}',
            style: const TextStyle(color: Colors.white54, fontSize: 13),
          ),
          const SizedBox(height: 16),
          _ConfidenceBar(confidence: guess.confidence),
        ],
      ),
    );
  }

  String _capitalize(String s) =>
      s.isEmpty ? s : s[0].toUpperCase() + s.substring(1);
}

class _ConfidenceBar extends StatelessWidget {
  final int confidence;
  const _ConfidenceBar({required this.confidence});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            const Text('Confidence', style: TextStyle(color: Colors.white54, fontSize: 12)),
            Text('$confidence%', style: const TextStyle(color: Colors.white70, fontSize: 12)),
          ],
        ),
        const SizedBox(height: 6),
        ClipRRect(
          borderRadius: BorderRadius.circular(4),
          child: LinearProgressIndicator(
            value: confidence / 100,
            backgroundColor: Colors.white12,
            valueColor: AlwaysStoppedAnimation<Color>(
              confidence > 70 ? const Color(0xFF00C853) : const Color(0xFFFF6B00),
            ),
            minHeight: 8,
          ),
        ),
      ],
    );
  }
}

class _SmallGuessCard extends StatelessWidget {
  final MovieGuess guess;
  const _SmallGuessCard({required this.guess});

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.07),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.white24),
      ),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(guess.title, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w600)),
                Text('${guess.year} · ${guess.director}',
                    style: const TextStyle(color: Colors.white54, fontSize: 12)),
              ],
            ),
          ),
          Text('${guess.confidence}%', style: const TextStyle(color: Colors.white54, fontSize: 13)),
        ],
      ),
    );
  }
}

class _FeedbackRow extends StatelessWidget {
  final GameProvider provider;
  final List<MovieGuess> guesses;
  const _FeedbackRow({required this.provider, required this.guesses});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        const Text(
          'Was I right?',
          style: TextStyle(color: Colors.white70, fontSize: 16),
        ),
        const SizedBox(height: 12),
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            OutlinedButton.icon(
              onPressed: () => provider.submitFeedback(true),
              icon: const Icon(Icons.check, color: Color(0xFF00C853)),
              label: const Text('Yes!', style: TextStyle(color: Color(0xFF00C853))),
              style: OutlinedButton.styleFrom(side: const BorderSide(color: Color(0xFF00C853))),
            ),
            const SizedBox(width: 16),
            OutlinedButton.icon(
              onPressed: () => provider.submitFeedback(false),
              icon: const Icon(Icons.close, color: Color(0xFFD50000)),
              label: const Text('No', style: TextStyle(color: Color(0xFFD50000))),
              style: OutlinedButton.styleFrom(side: const BorderSide(color: Color(0xFFD50000))),
            ),
          ],
        ),
      ],
    );
  }
}

class _DoneMessage extends StatelessWidget {
  final bool wasCorrect;
  const _DoneMessage({required this.wasCorrect});

  @override
  Widget build(BuildContext context) {
    return Text(
      wasCorrect ? '🎉 Nailed it! Thanks for playing!' : '😅 I\'ll get better. Thanks for the feedback!',
      textAlign: TextAlign.center,
      style: const TextStyle(color: Colors.white70, fontSize: 16),
    );
  }
}
