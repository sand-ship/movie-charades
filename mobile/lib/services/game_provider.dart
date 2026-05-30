import 'package:flutter/foundation.dart';
import '../models/game_models.dart';
import 'api_service.dart';

class GameProvider extends ChangeNotifier {
  final ApiService _api;
  GameState _state = const GameState();
  String? _error;
  bool _loading = false;

  GameProvider({ApiService? api}) : _api = api ?? const ApiService();

  GameState get state => _state;
  String? get error => _error;
  bool get loading => _loading;

  Future<void> startGame() async {
    _setLoading(true);
    try {
      final result = await _api.startGame();
      _state = GameState(
        sessionId: result.sessionId,
        phase: GamePhase.question,
        currentQuestion: result.question,
        remainingCandidates: result.remaining,
      );
      _error = null;
    } catch (e) {
      _error = e.toString();
    }
    _setLoading(false);
  }

  Future<void> answer(String answer) async {
    final sessionId = _state.sessionId;
    final question = _state.currentQuestion;
    if (sessionId == null || question == null) return;

    _setLoading(true);
    try {
      final result = await _api.sendAnswer(sessionId, question.id, answer);
      _state = _state.copyWith(
        phase: result.phase == 'guess' ? GamePhase.guess : GamePhase.question,
        currentQuestion: result.question,
        guesses: result.guesses,
        questionCount: result.questionCount,
        remainingCandidates: result.remaining,
      );
      _error = null;
    } catch (e) {
      _error = e.toString();
    }
    _setLoading(false);
  }

  Future<void> submitFeedback(bool wasCorrect, {String? correctMovieId}) async {
    final sessionId = _state.sessionId;
    if (sessionId == null) return;
    await _api.sendFeedback(sessionId, wasCorrect, correctMovieId: correctMovieId);
    _state = _state.copyWith(phase: GamePhase.done, wasCorrect: wasCorrect);
    notifyListeners();
  }

  void reset() {
    _state = const GameState();
    _error = null;
    notifyListeners();
  }

  void _setLoading(bool v) {
    _loading = v;
    notifyListeners();
  }
}
