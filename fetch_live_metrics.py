#!/usr/bin/env python3
"""
Fetch and analyze live game metrics from the Movie Charades API.

Usage:
    python3 fetch_live_metrics.py --key YOUR_ADMIN_KEY [--output metrics.json]
"""
import json
import argparse
import httpx
from pathlib import Path
from collections import defaultdict
import statistics
from typing import Optional

BASE_URL = "https://movie-charades.onrender.com"

def fetch_games(key: str) -> Optional[dict]:
    """Fetch all games from API."""
    try:
        r = httpx.get(f"{BASE_URL}/admin/games", params={"key": key}, timeout=10)
        if r.status_code == 403:
            print("ERROR: Invalid admin key")
            return None
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"ERROR fetching games: {e}")
        return None

def fetch_stumpers(key: str) -> Optional[dict]:
    """Fetch all stumpers from API."""
    try:
        r = httpx.get(f"{BASE_URL}/admin/stumpers", params={"key": key}, timeout=10)
        if r.status_code == 403:
            print("ERROR: Invalid admin key")
            return None
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"ERROR fetching stumpers: {e}")
        return None

def analyze_games(games_response: dict) -> dict:
    """Analyze game data."""
    games = games_response.get("entries", [])
    count = games_response.get("count", len(games))

    print(f"\nProcessing {count} games...")

    # Categorize by outcome
    outcomes = defaultdict(list)
    for game in games:
        outcome = game.get("outcome", "unknown")
        outcomes[outcome].append(game)

    # Calculate metrics
    total = len(games)
    correct = len(outcomes.get("correct", []))
    wrong_guess = len(outcomes.get("wrong_guess", []))
    stumped = len(outcomes.get("stumped", []))

    metrics = {
        "total_games": total,
        "by_outcome": {
            "correct": correct,
            "wrong_guess": wrong_guess,
            "stumped": stumped,
            "unknown": len(outcomes.get("unknown", [])),
        },
        "success_rate_pct": (correct / total * 100) if total > 0 else 0,
        "stump_rate_pct": (stumped / total * 100) if total > 0 else 0,
        "guess_accuracy_pct": (correct / (correct + wrong_guess) * 100) if (correct + wrong_guess) > 0 else 0,
    }

    # Questions per game
    q_counts = [g.get("question_count", 0) for g in games if g.get("question_count") is not None]
    if q_counts:
        metrics["questions_per_game"] = {
            "average": statistics.mean(q_counts),
            "median": statistics.median(q_counts),
            "min": min(q_counts),
            "max": max(q_counts),
            "stdev": statistics.stdev(q_counts) if len(q_counts) > 1 else 0,
        }

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

    metrics["by_language"] = {}
    for lang in sorted(lang_outcomes.keys()):
        outcomes_dict = lang_outcomes[lang]
        total_lang = sum(outcomes_dict.values())
        correct_lang = outcomes_dict.get("correct", 0)
        metrics["by_language"][lang] = {
            "total": total_lang,
            "correct": correct_lang,
            "success_rate_pct": (correct_lang / total_lang * 100) if total_lang > 0 else 0,
            "breakdown": dict(outcomes_dict),
        }

    # Wrong guesses
    wrong_guesses = defaultdict(int)
    for game in outcomes.get("wrong_guess", []):
        title = game.get("guessed_movie_title", "Unknown")
        if title:
            wrong_guesses[title] += 1

    metrics["top_wrong_guesses"] = sorted(
        [{"title": k, "count": v} for k, v in wrong_guesses.items()],
        key=lambda x: -x["count"]
    )[:10]

    # Remaining candidates
    remaining_all = [g.get("remaining_candidates") for g in games
                    if g.get("remaining_candidates") is not None]
    remaining_stumped = [g.get("remaining_candidates") for g in outcomes.get("stumped", [])
                        if g.get("remaining_candidates") is not None]

    if remaining_all:
        metrics["remaining_candidates"] = {
            "all_games": {
                "average": statistics.mean(remaining_all),
                "median": statistics.median(remaining_all),
                "min": min(remaining_all),
                "max": max(remaining_all),
            }
        }
        if remaining_stumped:
            metrics["remaining_candidates"]["stumped_only"] = {
                "average": statistics.mean(remaining_stumped),
                "median": statistics.median(remaining_stumped),
                "min": min(remaining_stumped),
                "max": max(remaining_stumped),
            }

    return metrics

def print_metrics(metrics: dict):
    """Pretty-print metrics."""
    print("\n" + "=" * 80)
    print("GAME METRICS SUMMARY")
    print("=" * 80)

    print(f"\nTotal games: {metrics['total_games']}")
    print("\nOutcomes:")
    for outcome, count in metrics["by_outcome"].items():
        pct = (count / metrics["total_games"] * 100) if metrics["total_games"] > 0 else 0
        print(f"  {outcome}: {count} ({pct:.1f}%)")

    print("\nSuccess Metrics:")
    print(f"  Success rate: {metrics['success_rate_pct']:.1f}%")
    print(f"  Stump rate: {metrics['stump_rate_pct']:.1f}%")
    print(f"  Guess accuracy (when guessing): {metrics['guess_accuracy_pct']:.1f}%")

    if "questions_per_game" in metrics:
        qpg = metrics["questions_per_game"]
        print("\nQuestions per game:")
        print(f"  Average: {qpg['average']:.1f}")
        print(f"  Median: {qpg['median']:.0f}")
        print(f"  Range: {qpg['min']}-{qpg['max']}")

    if "by_language" in metrics:
        print("\nResults by language:")
        for lang, data in sorted(metrics["by_language"].items()):
            print(f"  {lang}: {data['correct']}/{data['total']} ({data['success_rate_pct']:.0f}%)")

    if "top_wrong_guesses" in metrics and metrics["top_wrong_guesses"]:
        print("\nTop incorrect guesses:")
        for item in metrics["top_wrong_guesses"][:5]:
            print(f"  '{item['title']}': {item['count']} times")

    if "remaining_candidates" in metrics:
        rc = metrics["remaining_candidates"]
        if "all_games" in rc:
            print("\nRemaining candidates (all games):")
            print(f"  Average: {rc['all_games']['average']:.1f}")
            print(f"  Median: {rc['all_games']['median']:.0f}")
        if "stumped_only" in rc:
            print("\nRemaining candidates (stumped games):")
            print(f"  Average: {rc['stumped_only']['average']:.1f}")
            print(f"  Median: {rc['stumped_only']['median']:.0f}")

    print("\n" + "=" * 80)

def main():
    parser = argparse.ArgumentParser(
        description="Fetch and analyze live game metrics from Movie Charades"
    )
    parser.add_argument(
        "--key",
        required=True,
        help="Admin key for API access"
    )
    parser.add_argument(
        "--output",
        help="Output file for metrics (JSON)"
    )
    parser.add_argument(
        "--no-print",
        action="store_true",
        help="Don't print metrics to console"
    )

    args = parser.parse_args()

    print("Fetching game data from Movie Charades API...")
    games_response = fetch_games(args.key)

    if not games_response:
        return 1

    metrics = analyze_games(games_response)

    if not args.no_print:
        print_metrics(metrics)

    if args.output:
        output_path = Path(args.output)
        output_path.write_text(json.dumps(metrics, indent=2))
        print(f"\nMetrics saved to {output_path}")

    return 0

if __name__ == "__main__":
    exit(main())
