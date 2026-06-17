#!/usr/bin/env python3
"""
Test the API by playing several games and analyzing the results.
"""
import json
import httpx
import time
import random
from pathlib import Path

BASE_URL = "https://movie-charades.onrender.com"

def start_game():
    """Start a new game."""
    try:
        r = httpx.post(f"{BASE_URL}/game/start", timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"Error starting game: {e}")
        return None

def answer_question(session_id, question_id, answer):
    """Answer a question."""
    try:
        r = httpx.post(
            f"{BASE_URL}/game/answer",
            json={
                "session_id": session_id,
                "question_id": question_id,
                "answer": answer
            },
            timeout=10
        )
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"Error answering question: {e}")
        return None

def play_random_game(num_moves=10):
    """Play a game with random answers."""
    game = start_game()
    if not game:
        return None

    session_id = game.get("session_id")
    print(f"Started game: {session_id}")

    game_record = {
        "session_id": session_id,
        "questions_asked": 0,
        "answers": [],
        "final_state": None
    }

    for move in range(num_moves):
        state = game
        if state.get("phase") == "guess":
            guesses = state.get("guesses", [])
            print(f"  Game reached guess phase after {game_record['questions_asked']} questions")
            print(f"  Top guesses: {[g.get('title') for g in guesses[:3]]}")
            game_record["final_state"] = "guessed"
            game_record["final_guesses"] = guesses
            return game_record

        question = state.get("question")
        if not question:
            print(f"  No more questions available")
            game_record["final_state"] = "no_questions"
            return game_record

        q_id = question.get("id")
        answer = random.choice(["yes", "no", "maybe"])

        print(f"  Q{move+1}: {question.get('text')[:60]}... -> {answer}")
        game_record["questions_asked"] += 1
        game_record["answers"].append({"id": q_id, "answer": answer})

        game = answer_question(session_id, q_id, answer)
        if not game:
            break

        time.sleep(0.1)  # Small delay to be nice to the server

    return game_record

def main():
    print("=" * 80)
    print("TESTING MOVIE CHARADES API")
    print("=" * 80)
    print()

    # Test a few games
    num_games = 3
    game_records = []

    for i in range(num_games):
        print(f"Playing game {i+1}/{num_games}...")
        game = play_random_game(num_moves=15)
        if game:
            game_records.append(game)
        print()

    # Analyze results
    print("=" * 80)
    print("GAME STATISTICS")
    print("=" * 80)
    print(f"Games played: {len(game_records)}")
    if game_records:
        avg_questions = sum(g["questions_asked"] for g in game_records) / len(game_records)
        print(f"Average questions per game: {avg_questions:.1f}")

        guessed_count = sum(1 for g in game_records if g.get("final_state") == "guessed")
        print(f"Games that reached guess phase: {guessed_count}/{len(game_records)}")

if __name__ == "__main__":
    main()
