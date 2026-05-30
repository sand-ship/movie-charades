# 🎬 Indian Movie Charades

An Akinator-style guessing game for Indian (Hindi / Tamil / Telugu) films. FastAPI
backend + a single-file cinema-themed frontend, served from one origin.

## Run locally
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --port 8000
# open http://localhost:8000
```

## Deploy (free, mobile-accessible)
The repo is a single Docker service — FastAPI serves both the API and the UI, so
there's no separate frontend host and no hardcoded API URL.

### Render (recommended)
1. Push this repo to GitHub.
2. Render → **New → Web Service** → connect the repo.
3. Render auto-detects the `Dockerfile`. Leave the start command empty (the
   Dockerfile's `CMD` runs uvicorn on `$PORT`).
4. Instance type: **Free**. Deploy → you get a public `https://…onrender.com` URL
   that works on mobile. (Free tier sleeps when idle; first hit cold-starts ~30s.)

### Hugging Face Spaces (alternative)
Create a **Docker** Space from the repo; add `app_port: 8000` to the Space's
README frontmatter.

## Layout
- `backend/` — FastAPI app (`main.py`), game engine (`engine.py`), questions
  (`questions.py`), data (`data/movies.json`), labeling scripts (`scripts/`).
- `frontend/index.html` — the cinema-themed UI (served at `/`).
