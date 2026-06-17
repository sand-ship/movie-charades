#!/usr/bin/env python3
"""
Live game monitoring dashboard for Indian Movie Charades
Fetches latest games from Supabase and analyzes patterns
"""

import subprocess
import json
import sys
from datetime import datetime
from collections import Counter

SUPABASE_URL = "https://vhppdcdpqaqkupakqjgb.supabase.co/rest/v1"
ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZocHBkY2RwcWFxa3VwYWtxamdiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTc2NTAzODgsImV4cCI6MTczMzIwMjM4OH0.ePxbvFO-KhNvFEzHzG5WMVt-8QO0M9ZvCNaVxMw7YDA"

def fetch_games(limit=50):
    """Fetch latest games from Supabase"""
    try:
        result = subprocess.run([
            'curl', '-s',
            f'{SUPABASE_URL}/games?order=id.desc&limit={limit}',
            '-H', f'apikey: {ANON_KEY}'
        ], capture_output=True, text=True, timeout=10)

        if result.stdout.strip():
            return json.loads(result.stdout)
        return []
    except Exception as e:
        print(f"Error fetching games: {e}")
        return []

def analyze_games(games):
    """Analyze game patterns"""
    if not games:
        print("No games available")
        return

    print("\n" + "=" * 90)
    print(f"LIVE GAME MONITORING - {len(games)} GAMES")
    print("=" * 90)
    print(f"Timestamp: {datetime.now().isoformat()}\n")

    # Outcome distribution
    by_outcome = Counter(g.get('outcome') for g in games)
    total = len(games)

    print("OUTCOME SUMMARY:")
    for outcome in ['correct', 'wrong_guess', 'stumped']:
        count = by_outcome.get(outcome, 0)
        pct = 100 * count / total if total > 0 else 0
        print(f"  {outcome:12}: {count:3}/{total} ({pct:5.1f}%)")

    # Recent games table
    print("\nRECENT GAMES (latest 15):\n")
    print(f"{'Row':<4} {'Outcome':<12} {'Yes #':<6} {'Questions':<11} {'Target':<35}")
    print("-" * 80)

    for i, g in enumerate(games[:15], 1):
        outcome = g.get('outcome', '?')[:8]
        yes_count = len(g.get('yes_answers', []))
        q_count = g.get('question_count', 0)
        target = g.get('correct_movie_title', 'N/A')[:33]

        print(f"{g.get('idx', '?'):<4} {outcome:<12} {yes_count:<6} {q_count:<11} {target:<35}")

    # Performance by yes_answer count
    print("\n\nPERFORMANCE BY YES_ANSWER COUNT:")
    yes_counts = Counter()
    outcome_by_yes = {}

    for g in games:
        yes_c = len(g.get('yes_answers', []))
        yes_counts[yes_c] += 1
        if yes_c not in outcome_by_yes:
            outcome_by_yes[yes_c] = Counter()
        outcome_by_yes[yes_c][g.get('outcome')] += 1

    for yes_c in sorted(yes_counts.keys(), reverse=True)[:10]:
        outcomes = outcome_by_yes[yes_c]
        correct = outcomes.get('correct', 0)
        total_c = yes_counts[yes_c]
        pct = 100 * correct / total_c if total_c > 0 else 0
        print(f"  {yes_c:2} yes answers: {total_c:3} games | {correct} correct ({pct:5.1f}%)")

    # Hierarchical sub-Q adoption
    print("\n\nHIERARCHICAL SUB-QUESTION ADOPTION:")
    hierarchical_games = 0
    sub_q_freq = Counter()

    for g in games:
        yes_answers = g.get('yes_answers', [])
        for q in yes_answers:
            if any(q.endswith(suffix) for suffix in ['_action', '_80s90s', '_recent', '_comedy', '_romance']):
                hierarchical_games += 1
                sub_q_freq[q] += 1
                break

    pct = 100 * hierarchical_games / len(games) if games else 0
    print(f"  Games using hierarchical sub-Qs: {hierarchical_games}/{len(games)} ({pct:.1f}%)")

    if sub_q_freq:
        print(f"\n  Top hierarchical sub-Qs used:")
        for q, count in sub_q_freq.most_common(5):
            print(f"    {q}: {count}x")

    # Most common stumpers
    print("\n\nMOST COMMON STUMPERS:")
    stumpers = [g.get('guessed_movie_title') for g in games if g.get('outcome') == 'stumped']
    stumper_freq = Counter(stumpers)

    for film, count in stumper_freq.most_common(5):
        print(f"  {film}: {count}x")

    print("\n" + "=" * 90)

def main():
    games = fetch_games(limit=50)
    analyze_games(games)

if __name__ == '__main__':
    main()
