import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../models/game_models.dart';
import '../services/game_provider.dart';
import 'result_screen.dart';

class GameScreen extends StatelessWidget {
  const GameScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final provider = context.watch<GameProvider>();
    final state = provider.state;

    if (state.phase == GamePhase.guess) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(builder: (_) => const ResultScreen()),
        );
      });
    }

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
              _Header(state: state),
              Expanded(child: _QuestionCard(provider: provider, state: state)),
              if (provider.error != null)
                Padding(
                  padding: const EdgeInsets.all(16),
                  child: Text(provider.error!, style: const TextStyle(color: Colors.redAccent)),
                ),
            ],
          ),
        ),
      ),
    );
  }
}

class _Header extends StatelessWidget {
  final GameState state;
  const _Header({required this.state});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(20),
      child: Row(
        children: [
          IconButton(
            icon: const Icon(Icons.close, color: Colors.white54),
            onPressed: () {
              context.read<GameProvider>().reset();
              Navigator.pop(context);
            },
          ),
          const Spacer(),
          Column(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Text(
                'Question ${state.questionCount + 1}',
                style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16),
              ),
              Text(
                '${state.remainingCandidates} films left',
                style: const TextStyle(color: Colors.white54, fontSize: 12),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _QuestionCard extends StatelessWidget {
  final GameProvider provider;
  final GameState state;
  const _QuestionCard({required this.provider, required this.state});

  @override
  Widget build(BuildContext context) {
    final question = state.currentQuestion;
    if (question == null) {
      return const Center(child: CircularProgressIndicator(color: Colors.white));
    }

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 24),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Text('🧞', style: TextStyle(fontSize: 64)),
          const SizedBox(height: 32),
          Container(
            padding: const EdgeInsets.all(28),
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.1),
              borderRadius: BorderRadius.circular(20),
              border: Border.all(color: Colors.white24),
            ),
            child: Text(
              question.text,
              textAlign: TextAlign.center,
              style: const TextStyle(
                color: Colors.white,
                fontSize: 22,
                fontWeight: FontWeight.w600,
                height: 1.4,
              ),
            ),
          ),
          const SizedBox(height: 48),
          if (provider.loading)
            const CircularProgressIndicator(color: Colors.white)
          else
            _AnswerButtons(provider: provider, questionId: question.id),
        ],
      ),
    );
  }
}

class _AnswerButtons extends StatelessWidget {
  final GameProvider provider;
  final String questionId;
  const _AnswerButtons({required this.provider, required this.questionId});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Row(
          children: [
            Expanded(child: _AnswerButton(label: 'YES', color: const Color(0xFF00C853), answer: 'yes', provider: provider)),
            const SizedBox(width: 12),
            Expanded(child: _AnswerButton(label: 'NO', color: const Color(0xFFD50000), answer: 'no', provider: provider)),
          ],
        ),
        const SizedBox(height: 12),
        _AnswerButton(
          label: "DON'T KNOW",
          color: Colors.white24,
          answer: 'dunno',
          provider: provider,
          fullWidth: true,
        ),
      ],
    );
  }
}

class _AnswerButton extends StatelessWidget {
  final String label;
  final Color color;
  final String answer;
  final GameProvider provider;
  final bool fullWidth;

  const _AnswerButton({
    required this.label,
    required this.color,
    required this.answer,
    required this.provider,
    this.fullWidth = false,
  });

  @override
  Widget build(BuildContext context) {
    final btn = ElevatedButton(
      onPressed: () => provider.answer(answer),
      style: ElevatedButton.styleFrom(
        backgroundColor: color,
        foregroundColor: Colors.white,
        padding: const EdgeInsets.symmetric(vertical: 16),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
        textStyle: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold, letterSpacing: 1),
      ),
      child: Text(label),
    );
    return fullWidth ? SizedBox(width: double.infinity, child: btn) : btn;
  }
}
