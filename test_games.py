import sys
import json
sys.path.insert(0, 'backend')
from engine import GameEngine

# Load stumpers
with open('backend/data/stumpers.jsonl', 'r') as f:
    lines = f.readlines()
    stumper_games = [json.loads(line) for line in lines if line.strip()]

# Test a few stumper games
test_indices = [30, 32, 34]  # Games 31, 33, 35 (0-indexed)

for idx in test_indices:
    if idx < len(stumper_games):
        game = stumper_games[idx]
        title = game['film_title']
        
        # Create engine and run game
        engine = GameEngine()
        session = engine.start_session()
        
        # Simulate answering yes/no randomly for all questions until convergence
        q_count = 0
        remaining = len(engine.movies)
        
        while remaining > 1 and q_count < 30:
            q = engine.next_question(session)
            if not q:
                break
            
            # Answer based on film attributes (simulate perfect play)
            film = next((m for m in engine.movies if m['title'] == title), None)
            if film:
                answer = "yes" if film.get(q.filter_attr) else "no"
            else:
                answer = "yes"
            
            session.answers[q.id] = answer
            session.asked.append(q.id)
            
            remaining = len(engine.get_candidates(session))
            q_count += 1
        
        print(f"Game {idx+1} ({title}): {remaining} remaining after {q_count} questions")
