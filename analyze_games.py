#!/usr/bin/env python3
"""
Analyze Indian Movie Charades game metrics from local and API data.
"""
import json
import sys
from pathlib import Path
from collections import defaultdict
import statistics

# Load local data
DATA_DIR = Path(__file__).parent / "backend" / "data"
STUMPERS_LOG = DATA_DIR / "stumpers.jsonl"
GAMES_LOG = DATA_DIR / "games.jsonl"

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

def analyze():
    """Analyze all available game data."""
    stumpers = load_stumpers()
    games = load_games()

    print("=" * 80)
    print("INDIAN MOVIE CHARADES - GAME ANALYSIS")
    print("=" * 80)
    print()

    # ─── STUMPERS ANALYSIS ───
    print("STUMPERS (Films the genie couldn't guess):")
    print(f"  Total stumpers: {len(stumpers)}")
    if stumpers:
        print(f"  Sample stumpers:")
        for s in stumpers[:5]:
            print(f"    - '{s.get('title', '?')}' (remaining candidates: {s.get('remaining_candidates', '?')})")

        remaining_candidates = [s.get('remaining_candidates') for s in stumpers if s.get('remaining_candidates') is not None]
        if remaining_candidates:
            print(f"  Average remaining_candidates for stumpers: {statistics.mean(remaining_candidates):.1f}")
            print(f"  Min/Max: {min(remaining_candidates)}/{max(remaining_candidates)}")
    print()

    # ─── GAMES ANALYSIS ───
    print("GAMES (Completed game records):")
    print(f"  Total games recorded: {len(games)}")
    print()

    if games:
        # Categorize outcomes
        outcomes = defaultdict(list)
        for game in games:
            outcome = game.get('outcome', 'unknown')
            outcomes[outcome].append(game)

        print("  Game outcomes:")
        for outcome, game_list in sorted(outcomes.items()):
            print(f"    - {outcome}: {len(game_list)}")
        print()

        # Calculate metrics
        correct_games = outcomes.get('correct', [])
        wrong_guess_games = outcomes.get('wrong_guess', [])
        stumped_games = outcomes.get('stumped', [])

        total_games = len(games)
        total_guessed = len(correct_games) + len(wrong_guess_games)

        if total_games > 0:
            success_rate = (len(correct_games) / total_games) * 100
            stump_rate = (len(stumped_games) / total_games) * 100

            print(f"  Success metrics:")
            print(f"    - Total success rate: {success_rate:.1f}% ({len(correct_games)}/{total_games})")
            print(f"    - Stump rate: {stump_rate:.1f}% ({len(stumped_games)}/{total_games})")
            if total_guessed > 0:
                accuracy_of_guesses = (len(correct_games) / total_guessed) * 100
                print(f"    - Accuracy when it guesses: {accuracy_of_guesses:.1f}% ({len(correct_games)}/{total_guessed})")

        print()

        # Questions per game
        question_counts = [g.get('question_count', 0) for g in games]
        if question_counts:
            avg_q = statistics.mean(question_counts)
            median_q = statistics.median(question_counts)
            print(f"  Questions per game:")
            print(f"    - Average: {avg_q:.1f}")
            print(f"    - Median: {median_q:.0f}")
            print(f"    - Range: {min(question_counts)}-{max(question_counts)}")
        print()

        # Language breakdown
        lang_outcomes = defaultdict(lambda: defaultdict(int))
        for game in games:
            answers = game.get('all_answers', {})
            language = None
            if 'q_hindi' in answers and answers['q_hindi'] == 'yes':
                language = 'Hindi'
            elif 'q_tamil' in answers and answers['q_tamil'] == 'yes':
                language = 'Tamil'
            elif 'q_telugu' in answers and answers['q_telugu'] == 'yes':
                language = 'Telugu'

            if language:
                lang_outcomes[language][game.get('outcome', 'unknown')] += 1

        if lang_outcomes:
            print(f"  Outcomes by language:")
            for lang in sorted(lang_outcomes.keys()):
                outcomes_dict = lang_outcomes[lang]
                total = sum(outcomes_dict.values())
                correct = outcomes_dict.get('correct', 0)
                success_pct = (correct / total * 100) if total > 0 else 0
                print(f"    - {lang}: {success_pct:.0f}% success ({correct}/{total})")
                for outcome in sorted(outcomes_dict.keys()):
                    if outcome != 'correct':
                        print(f"      {outcome}: {outcomes_dict[outcome]}")
        print()

        # Most common wrong guesses
        wrong_guesses = defaultdict(int)
        for game in wrong_guess_games:
            guessed_title = game.get('guessed_movie_title', 'Unknown')
            if guessed_title:
                wrong_guesses[guessed_title] += 1

        if wrong_guesses:
            print(f"  Most common wrong guesses (top 5):")
            for title, count in sorted(wrong_guesses.items(), key=lambda x: -x[1])[:5]:
                print(f"    - '{title}': {count} times")
        print()

        # Remaining candidates for stumped games
        remaining_for_stumped = [g.get('remaining_candidates') for g in stumped_games
                                  if g.get('remaining_candidates') is not None]
        if remaining_for_stumped:
            print(f"  Stumped games - remaining candidates:")
            print(f"    - Average: {statistics.mean(remaining_for_stumped):.1f}")
            print(f"    - Median: {statistics.median(remaining_for_stumped):.0f}")
            print(f"    - Range: {min(remaining_for_stumped)}-{max(remaining_for_stumped)}")
        print()

    print("=" * 80)
    print("Note: This analysis is based on local game logs.")
    print("Live data may be stored in Supabase database.")
    print("=" * 80)

if __name__ == "__main__":
    analyze()
