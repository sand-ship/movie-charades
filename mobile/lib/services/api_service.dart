import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/game_models.dart';

class ApiService {
  final String baseUrl;

  const ApiService({this.baseUrl = 'http://localhost:8000'});

  Future<Map<String, dynamic>> _post(String path, Map<String, dynamic> body) async {
    final res = await http.post(
      Uri.parse('$baseUrl$path'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(body),
    );
    if (res.statusCode != 200) {
      throw Exception('API error ${res.statusCode}: ${res.body}');
    }
    return jsonDecode(res.body) as Map<String, dynamic>;
  }

  Future<({String sessionId, Question? question, int remaining})> startGame() async {
    final data = await _post('/game/start', {});
    return (
      sessionId: data['session_id'] as String,
      question: data['question'] != null
          ? Question.fromJson(data['question'] as Map<String, dynamic>)
          : null,
      remaining: data['remaining_candidates'] as int,
    );
  }

  Future<({String phase, Question? question, List<MovieGuess> guesses, int questionCount, int remaining})>
      sendAnswer(String sessionId, String questionId, String answer) async {
    final data = await _post('/game/answer', {
      'session_id': sessionId,
      'question_id': questionId,
      'answer': answer,
    });

    final phase = data['phase'] as String? ?? 'question';
    final qData = data['question'] as Map<String, dynamic>?;
    final gData = data['guesses'] as List<dynamic>? ?? [];

    return (
      phase: phase,
      question: qData != null ? Question.fromJson(qData) : null,
      guesses: gData.map((g) => MovieGuess.fromJson(g as Map<String, dynamic>)).toList(),
      questionCount: data['question_count'] as int,
      remaining: data['remaining_candidates'] as int,
    );
  }

  Future<void> sendFeedback(String sessionId, bool wasCorrect, {String? correctMovieId}) async {
    await _post('/game/feedback', {
      'session_id': sessionId,
      'was_correct': wasCorrect,
      if (correctMovieId != null) 'correct_movie_id': correctMovieId,
    });
  }
}
