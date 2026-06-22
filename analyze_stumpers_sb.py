#!/usr/bin/env python3
"""
Analyze recent stumped games from Supabase.
Shows stumper names vs what the genie guessed, with the options that were presented.
"""
import json
import os
from datetime import datetime
from pathlib import Path
from collections import defaultdict
import requests
import sys

# Supabase credentials
SUPABASE_URL = "https://ciwopsvjasfustqjspqm.supabase.co/rest/v1"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNpd29wc3ZqYXNmdXN0cWpzcHFtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODE1MzMxOTksImV4cCI6MjA5NzEwOTE5OX0.S3cOJS1J6HFAUIL8Ypfg6Q73JrITLfpdksVpRUx1pLk"
ADMIN_KEY = "ushermein114!"

def fetch_stumped_games(limit=20):
    """Fetch recent stumped games from Supabase."""
    try:
        headers = {
            "apikey": SUPABASE_ANON_KEY,
            "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
            "Content-Type": "application/json"
        }

        # Fetch stumped games ordered by created_at DESC
        url = f"{SUPABASE_URL}/games?outcome=eq.stumped&order=created_at.desc&limit={limit}"

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        return response.json()
    except Exception as e:
        print(f"Error fetching stumped games: {e}", file=sys.stderr)
        return []

def print_table_view(games):
    """Print stumpers in a clean table format."""
    if not games:
        print("No stumped games found.")
        return

    print("\n" + "=" * 120)
    print(f"RECENT STUMPERS ({len(games)} games)")
    print("=" * 120)
    print()

    print(f"{'#':<3} {'Stumper Name':<35} {'Genie Guessed':<35} {'Questions':<5} {'Remaining':<10}")
    print("-" * 120)

    for i, game in enumerate(games, 1):
        stumper_name = (game.get('stumper_name') or game.get('guessed_movie_title') or '?')[:33]
        guessed = (game.get('guessed_movie_title') or '?')[:33]
        questions = game.get('question_count', 0)
        remaining = game.get('remaining_candidates', '?')

        print(f"{i:<3} {stumper_name:<35} {guessed:<35} {questions:<5} {remaining:<10}")

    print()

def print_detailed_view(games, limit_details=5):
    """Print detailed view of first N stumpers."""
    print("=" * 120)
    print(f"DETAILED ANALYSIS (First {min(limit_details, len(games))} stumpers)")
    print("=" * 120)
    print()

    for i, game in enumerate(games[:limit_details], 1):
        stumper_name = game.get('stumper_name') or game.get('guessed_movie_title') or 'Unknown'
        guessed = game.get('guessed_movie_title') or 'Unknown'
        ts = game.get('created_at', game.get('ts', '?'))
        questions = game.get('question_count', 0)
        remaining = game.get('remaining_candidates', '?')

        print(f"{i}. STUMPER: '{stumper_name}'")
        print(f"   Created: {ts}")
        print(f"   Genie guessed: '{guessed}'")
        print(f"   Questions asked: {questions}")
        print(f"   Remaining candidates: {remaining}")

        # Show yes answers
        yes_answers = game.get('yes_answers', [])
        if yes_answers:
            print(f"   Yes answers: {', '.join(yes_answers[:5])}")
            if len(yes_answers) > 5:
                print(f"               ... and {len(yes_answers) - 5} more")

        # Show options presented (if available)
        options = game.get('options_presented', [])
        if options:
            print(f"   Options presented ({len(options)} films):")
            for opt in options[:3]:
                print(f"     - {opt}")
            if len(options) > 3:
                print(f"     ... and {len(options) - 3} more")
        print()

def print_summary_stats(games):
    """Print summary statistics."""
    if not games:
        return

    print("=" * 120)
    print("SUMMARY STATISTICS")
    print("=" * 120)
    print()

    question_counts = [g.get('question_count', 0) for g in games if g.get('question_count') is not None]
    remaining_counts = [g.get('remaining_candidates') for g in games if g.get('remaining_candidates') is not None]

    print(f"Total stumped games analyzed: {len(games)}")
    print()

    if question_counts:
        import statistics
        print("Questions asked per stumper:")
        print(f"  Average: {statistics.mean(question_counts):.1f}")
        print(f"  Median: {statistics.median(question_counts):.0f}")
        print(f"  Range: {min(question_counts)}-{max(question_counts)}")
        print()

    if remaining_counts:
        import statistics
        print("Remaining candidates when stumped:")
        print(f"  Average: {statistics.mean(remaining_counts):.1f}")
        print(f"  Median: {statistics.median(remaining_counts):.0f}")
        print(f"  Range: {min(remaining_counts)}-{max(remaining_counts)}")
        print()

    # Most common stumpers (repeated)
    stumper_counts = defaultdict(int)
    for game in games:
        stumper = game.get('stumper_name') or game.get('guessed_movie_title')
        if stumper:
            stumper_counts[stumper] += 1

    repeated = [s for s, c in stumper_counts.items() if c > 1]
    if repeated:
        print(f"Stumpers that came up multiple times:")
        for stumper, count in sorted([(s, stumper_counts[s]) for s in repeated], key=lambda x: -x[1]):
            print(f"  '{stumper}': {count} times")
        print()

def generate_admin_link():
    """Generate admin link."""
    print("\n" + "=" * 120)
    print("ADMIN LINK")
    print("=" * 120)
    link = f"https://movie-charades.onrender.com/admin?key={ADMIN_KEY}"
    print(f"Admin Dashboard: {link}")
    print()

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Analyze recent stumped games from Supabase"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Number of recent stumpers to fetch (default 20)"
    )
    parser.add_argument(
        "--details",
        type=int,
        default=5,
        help="Number of stumpers to show detailed analysis for (default 5)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )
    parser.add_argument(
        "--csv",
        action="store_true",
        help="Output as CSV"
    )

    args = parser.parse_args()

    games = fetch_stumped_games(limit=args.limit)

    if args.json:
        print(json.dumps(games, indent=2))
    elif args.csv:
        import csv
        import io
        output = io.StringIO()
        if games:
            writer = csv.DictWriter(output, fieldnames=games[0].keys())
            writer.writeheader()
            writer.writerows(games)
        print(output.getvalue())
    else:
        # Terminal display
        print_table_view(games)
        print_detailed_view(games, limit_details=args.details)
        print_summary_stats(games)
        generate_admin_link()

if __name__ == "__main__":
    main()
