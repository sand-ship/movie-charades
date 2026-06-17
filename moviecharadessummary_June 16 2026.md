# Movie Charades — Codebase Summary

## What it does

Akinator-style (20 questions) guessing game for Hindi, Tamil, and Telugu films. Users answer yes/no questions; the backend narrows down a target movie from a database of ~4,000 films.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11 + FastAPI + Uvicorn |
| Frontend | Single-file vanilla HTML/CSS/JS (cinema-themed, retro UI) |
| Mobile | Flutter (`/mobile`) |
| Deployment | Docker — targets Render / Hugging Face Spaces |

## Key Files

| File | Role |
|------|------|
| `backend/main.py` | FastAPI entry point; serves API + frontend from same origin |
| `backend/engine.py` | Core game logic — session management, candidate filtering, question selection |
| `backend/questions.py` | 50+ questions with evaluation logic (dynamic actor/director questions) |
| `backend/data/movies.json` | ~4,000+ movies with metadata attributes |
| `frontend/index.html` | Single-page UI with film reel animations |
| `Dockerfile` | Builds and runs the whole app |

## Architecture Notes

- **Monolithic deployment:** Backend serves the frontend — no hardcoded URLs, easy single-service deploy
- **Game algorithm:** Scoring uses `SOFT_KEEP_RATIO=0.04` to prune candidate movies across 20+ attributes per answer
- **Question flow:** Hard ceiling of 42 questions; minimum 12 before a guess; actor/director questions reserved for endgame
- **Data enrichment:** Scripts in `scripts/` and `add_telugu*.py` maintain and label the movie database

## GitHub Repo

https://github.com/sand-ship/movie-charades

## Note on Context Size

The `backend/data/movies.json` file (~4,000 movies) is very large. Avoid adding the raw JSON to Claude project context — it will consume ~380% of the context window. Use this summary instead, and query specific movie subsets only when needed.
