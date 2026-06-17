#!/usr/bin/env python3
"""
Comprehensive analysis of Indian Movie Charades game data.
"""
import json
import sys
from pathlib import Path
from collections import defaultdict
import statistics
import httpx

# ─────────────────────────────────────────────────────────────────────────────
# Local Data Loading
# ─────────────────────────────────────────────────────────────────────────────

DATA_DIR = Path(__file__).parent / "backend" / "data"
STUMPERS_LOG = DATA_DIR / "stumpers.jsonl"
GAMES_LOG = DATA_DIR / "games.jsonl"
MOVIES_JSON = DATA_DIR / "movies.json"

def load_stumpers():
    """Load stumper records from local file."""
    if not STUMPERS_LOG.exists():
        return []
    return [json.loads(l) for l in STUMPERS_LOG.read_text().splitlines() if l.strip()]

def load_games():
    """Load game records from local file."""
    if not GAMES_LOG.exists():
        return []
    return [json.loads(l) for l in GAMES_LOG.read_text().splitlines() if l.strip()]

def load_movies():
    """Load movies from database."""
    if not MOVIES_JSON.exists():
        return []
    data = json.loads(MOVIES_JSON.read_text())
    if isinstance(data, list):
        return data
    elif isinstance(data, dict) and "films" in data:
        return data.get("films", [])
    return []

def try_fetch_remote_games():
    """Try to fetch games from live API (will fail without auth)."""
    try:
        BASE_URL = "https://movie-charades.onrender.com"
        # Health check first
        r = httpx.get(f"{BASE_URL}/health", timeout=5)
        if r.status_code == 200:
            return True  # Server is up
    except:
        pass
    return False

# ─────────────────────────────────────────────────────────────────────────────
# Analysis Functions
# ─────────────────────────────────────────────────────────────────────────────

def analyze_stumpers(stumpers, movies):
    """Analyze stumper patterns."""
    print("=" * 80)
    print("STUMPERS ANALYSIS")
    print("=" * 80)
    print()

    print(f"Total stumpers logged: {len(stumpers)}")
    print()

    if stumpers:
        print("Stumpers breakdown:")
        # Build lookup
        movie_titles = {m.get("title", "").lower(): m for m in movies}

        for i, s in enumerate(stumpers, 1):
            title = s.get("title", "?").strip()
            remaining = s.get("remaining_candidates")
            ts = s.get("ts", "?")
            yes_q = s.get("yes_answers", [])

            matched_film = title.lower() in movie_titles

            print(f"  {i}. '{title}'")
            print(f"     Remaining candidates: {remaining}")
            print(f"     Yes answers: {len(yes_q)} ({', '.join(yes_q[:5])}{'...' if len(yes_q) > 5 else ''})")
            if matched_film:
                print(f"     Status: IN CATALOG")
            else:
                print(f"     Status: NOT IN CATALOG")
            print()

        # Stats
        remaining_candidates = [s.get("remaining_candidates") for s in stumpers
                               if s.get("remaining_candidates") is not None]
        if remaining_candidates:
            print("Remaining candidates statistics (for stumped games):")
            print(f"  Average: {statistics.mean(remaining_candidates):.1f}")
            print(f"  Median: {statistics.median(remaining_candidates):.0f}")
            print(f"  Min: {min(remaining_candidates)}")
            print(f"  Max: {max(remaining_candidates)}")
            print()

        yes_answer_counts = [len(s.get("yes_answers", [])) for s in stumpers]
        if yes_answer_counts:
            print("Questions answered 'yes' per stumper:")
            print(f"  Average: {statistics.mean(yes_answer_counts):.1f}")
            print(f"  Range: {min(yes_answer_counts)}-{max(yes_answer_counts)}")
            print()

    print()

def analyze_games(games):
    """Analyze completed games."""
    print("=" * 80)
    print("GAMES ANALYSIS")
    print("=" * 80)
    print()

    print(f"Total games recorded: {len(games)}")
    print()

    if not games:
        print("No game records available locally.")
        print("(Games are stored in Supabase database, not in local git repo)")
        print()
        return

    # Outcomes
    outcomes = defaultdict(list)
    for game in games:
        outcome = game.get("outcome", "unknown")
        outcomes[outcome].append(game)

    print("Outcomes breakdown:")
    for outcome, game_list in sorted(outcomes.items()):
        pct = (len(game_list) / len(games)) * 100
        print(f"  {outcome}: {len(game_list)} ({pct:.1f}%)")
    print()

    # Metrics
    correct_games = outcomes.get("correct", [])
    wrong_guess_games = outcomes.get("wrong_guess", [])
    stumped_games = outcomes.get("stumped", [])

    total_games = len(games)
    total_guessed = len(correct_games) + len(wrong_guess_games)

    if total_games > 0:
        success_rate = (len(correct_games) / total_games) * 100
        stump_rate = (len(stumped_games) / total_games) * 100

        print("Success metrics:")
        print(f"  Success rate (correct guesses): {success_rate:.1f}% ({len(correct_games)}/{total_games})")
        print(f"  Stump rate (couldn't guess): {stump_rate:.1f}% ({len(stumped_games)}/{total_games})")
        if total_guessed > 0:
            accuracy_of_guesses = (len(correct_games) / total_guessed) * 100
            print(f"  Guess accuracy (when it makes a guess): {accuracy_of_guesses:.1f}%")
        print()

    # Questions
    question_counts = [g.get("question_count", 0) for g in games if g.get("question_count") is not None]
    if question_counts:
        print("Questions asked per game:")
        print(f"  Average: {statistics.mean(question_counts):.1f}")
        print(f"  Median: {statistics.median(question_counts):.0f}")
        print(f"  Min-Max: {min(question_counts)}-{max(question_counts)}")
        print()

    # Language breakdown
    lang_outcomes = defaultdict(lambda: defaultdict(int))
    for game in games:
        answers = game.get("all_answers", {})
        language = None
        if answers.get("q_hindi") == "yes":
            language = "Hindi"
        elif answers.get("q_tamil") == "yes":
            language = "Tamil"
        elif answers.get("q_telugu") == "yes":
            language = "Telugu"

        if language:
            lang_outcomes[language][game.get("outcome", "unknown")] += 1

    if lang_outcomes:
        print("Results by language:")
        for lang in sorted(lang_outcomes.keys()):
            outcomes_dict = lang_outcomes[lang]
            total = sum(outcomes_dict.values())
            correct = outcomes_dict.get("correct", 0)
            success_pct = (correct / total * 100) if total > 0 else 0
            print(f"  {lang}: {correct}/{total} correct ({success_pct:.0f}%)")
            for outcome in sorted(set(outcomes_dict.keys()) - {"correct"}):
                print(f"    {outcome}: {outcomes_dict[outcome]}")
        print()

    # Most common wrong guesses
    wrong_guesses = defaultdict(int)
    for game in wrong_guess_games:
        guessed_title = game.get("guessed_movie_title", "Unknown")
        if guessed_title:
            wrong_guesses[guessed_title] += 1

    if wrong_guesses:
        print("Top incorrect guesses (repeated errors):")
        for title, count in sorted(wrong_guesses.items(), key=lambda x: -x[1])[:5]:
            print(f"  '{title}': {count} times")
        print()

    # Remaining candidates for stumped
    remaining_for_stumped = [g.get("remaining_candidates") for g in stumped_games
                            if g.get("remaining_candidates") is not None]
    if remaining_for_stumped:
        print("For stumped games - remaining candidates at time of stump:")
        print(f"  Average: {statistics.mean(remaining_for_stumped):.1f}")
        print(f"  Median: {statistics.median(remaining_for_stumped):.0f}")
        print(f"  Range: {min(remaining_for_stumped)}-{max(remaining_for_stumped)}")
        print()

    print()

def analyze_movies(movies):
    """Analyze movie catalog."""
    print("=" * 80)
    print("MOVIE CATALOG")
    print("=" * 80)
    print()

    print(f"Total films in database: {len(movies)}")
    print()

    if movies:
        # Language breakdown
        lang_counts = defaultdict(int)
        for film in movies:
            lang = film.get("language", "Unknown")
            lang_counts[lang] += 1

        print("Films by language:")
        for lang in sorted(lang_counts.keys()):
            print(f"  {lang}: {lang_counts[lang]}")
        print()

        # Year range
        years = []
        for film in movies:
            year = film.get("year")
            if year:
                years.append(year)

        if years:
            print(f"Year range: {min(years)} - {max(years)}")
            print()

    print()

def main():
    print("\n")
    print("*" * 80)
    print("INDIAN MOVIE CHARADES - COMPREHENSIVE DATA ANALYSIS")
    print("*" * 80)
    print()

    # Load data
    stumpers = load_stumpers()
    games = load_games()
    movies = load_movies()

    # Check live server
    print("Checking live server status...")
    server_up = try_fetch_remote_games()
    if server_up:
        print("✓ Live server is accessible at https://movie-charades.onrender.com")
        print("  (Admin endpoints require authentication key)")
    else:
        print("✗ Live server is not reachable")
    print()

    # Analysis
    analyze_stumpers(stumpers, movies)
    analyze_games(games)
    analyze_movies(movies)

    # Summary
    print("=" * 80)
    print("DATA SOURCES & LIMITATIONS")
    print("=" * 80)
    print()
    print("Local Data Available:")
    print(f"  - Stumpers: {len(stumpers)} entries from {STUMPERS_LOG}")
    print(f"  - Games: {len(games)} entries from {GAMES_LOG}")
    print(f"  - Movies: {len(movies)} films from {MOVIES_JSON}")
    print()
    print("Remote Data (Supabase):")
    print("  - The live game endpoint stores all game records in Supabase")
    print("  - Admin endpoints require ADMIN_KEY for access")
    print("  - Public endpoints available: /health, /movies, /game/*, /admin/stumpers (auth)")
    print()
    print("=" * 80)

if __name__ == "__main__":
    main()
