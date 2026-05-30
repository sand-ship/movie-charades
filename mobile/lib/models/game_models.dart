class Question {
  final String id;
  final String text;

  const Question({required this.id, required this.text});

  factory Question.fromJson(Map<String, dynamic> j) =>
      Question(id: j['id'] as String, text: j['text'] as String);
}

class MovieGuess {
  final String id;
  final String title;
  final int year;
  final String language;
  final String director;
  final String leadActor;
  final double imdbRating;
  final int confidence;

  const MovieGuess({
    required this.id,
    required this.title,
    required this.year,
    required this.language,
    required this.director,
    required this.leadActor,
    required this.imdbRating,
    required this.confidence,
  });

  factory MovieGuess.fromJson(Map<String, dynamic> j) => MovieGuess(
        id: j['id'] as String,
        title: j['title'] as String,
        year: j['year'] as int,
        language: j['language'] as String,
        director: j['director'] as String,
        leadActor: j['lead_actor'] as String,
        imdbRating: (j['imdb_rating'] as num).toDouble(),
        confidence: j['confidence'] as int,
      );
}

enum GamePhase { idle, question, guess, done }

class GameState {
  final String? sessionId;
  final GamePhase phase;
  final Question? currentQuestion;
  final List<MovieGuess> guesses;
  final int questionCount;
  final int remainingCandidates;
  final bool wasCorrect;

  const GameState({
    this.sessionId,
    this.phase = GamePhase.idle,
    this.currentQuestion,
    this.guesses = const [],
    this.questionCount = 0,
    this.remainingCandidates = 0,
    this.wasCorrect = false,
  });

  GameState copyWith({
    String? sessionId,
    GamePhase? phase,
    Question? currentQuestion,
    List<MovieGuess>? guesses,
    int? questionCount,
    int? remainingCandidates,
    bool? wasCorrect,
  }) =>
      GameState(
        sessionId: sessionId ?? this.sessionId,
        phase: phase ?? this.phase,
        currentQuestion: currentQuestion ?? this.currentQuestion,
        guesses: guesses ?? this.guesses,
        questionCount: questionCount ?? this.questionCount,
        remainingCandidates: remainingCandidates ?? this.remainingCandidates,
        wasCorrect: wasCorrect ?? this.wasCorrect,
      );
}
