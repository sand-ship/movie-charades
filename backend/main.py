from __future__ import annotations

import datetime
import json
import os
from pathlib import Path
from typing import Optional

import csv
import io
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel

from engine import GameEngine
from questions import LANGUAGE_QUESTION_IDS, ERA_QUESTION_IDS, GENRE_QUESTION_IDS, QUESTION_MAP, make_star_questions

# ── load data ────────────────────────────────────────────────────────────
DATA_PATH = Path(__file__).parent / "data" / "movies.json"
_all_movies = json.loads(DATA_PATH.read_text())
movies = [m for m in _all_movies if m.get("language") in {"hindi", "tamil", "telugu"}]

# Register actor/director questions derived from the active pool
from questions import QUESTIONS
_star_qs = make_star_questions(movies)
QUESTIONS.extend(_star_qs)
for q in _star_qs:
    QUESTION_MAP[q.id] = q

engine = GameEngine(movies)

app = FastAPI(title="Indian Movie Charades", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve the frontend from the same origin so the API can be called with relative
# URLs (no hardcoded host) — this is what makes the deployed app work on mobile.
FRONTEND = Path(__file__).resolve().parent.parent / "frontend"


@app.get("/")
def index():
    return FileResponse(FRONTEND / "index.html")


# ── schemas ──────────────────────────────────────────────────────────────
class AnswerRequest(BaseModel):
    session_id: str
    question_id: str
    answer: str  # "yes" | "no" | "dunno"


class BatchAnswerRequest(BaseModel):
    session_id: str
    answers: list[dict]  # [{question_id: str, answer: str}]


class FeedbackRequest(BaseModel):
    session_id: str
    correct_movie_id: Optional[str] = None
    was_correct: bool


class BackRequest(BaseModel):
    session_id: str


class StumpedRequest(BaseModel):
    session_id: str
    title: str


STUMPERS_LOG = Path(__file__).resolve().parent / "data" / "stumpers.jsonl"
GAMES_LOG    = Path(__file__).resolve().parent / "data" / "games.jsonl"

_SUPA_URL = os.getenv("SUPABASE_URL", "").rstrip("/")
_SUPA_KEY = os.getenv("SUPABASE_ANON_KEY", "")
_SUPA_HEADERS = {
    "apikey": _SUPA_KEY,
    "Authorization": f"Bearer {_SUPA_KEY}",
    "Content-Type": "application/json",
}


def _stumper_insert(record: dict) -> None:
    if _SUPA_URL and _SUPA_KEY:
        try:
            httpx.post(
                f"{_SUPA_URL}/stumpers",
                json={
                    "title": record["title"],
                    "yes_answers": record["yes_answers"],
                    "remaining_candidates": record["remaining_candidates"],
                },
                headers={**_SUPA_HEADERS, "Prefer": "return=minimal"},
                timeout=5.0,
            )
        except Exception:
            pass
    else:
        with STUMPERS_LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def _game_insert(record: dict) -> None:
    if _SUPA_URL and _SUPA_KEY:
        try:
            httpx.post(
                f"{_SUPA_URL}/games",
                json=record,
                headers={**_SUPA_HEADERS, "Prefer": "return=minimal"},
                timeout=5.0,
            )
        except Exception:
            pass
    else:
        with GAMES_LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def _games_list() -> list:
    if _SUPA_URL and _SUPA_KEY:
        try:
            r = httpx.get(
                f"{_SUPA_URL}/games",
                params={"order": "id.desc"},
                headers=_SUPA_HEADERS,
                timeout=5.0,
            )
            return r.json()
        except Exception:
            return []
    else:
        if not GAMES_LOG.exists():
            return []
        return [json.loads(l) for l in GAMES_LOG.read_text().splitlines() if l.strip()]


def _stumper_list() -> list:
    if _SUPA_URL and _SUPA_KEY:
        try:
            r = httpx.get(
                f"{_SUPA_URL}/stumpers",
                params={"order": "id.desc"},
                headers=_SUPA_HEADERS,
                timeout=5.0,
            )
            return r.json()
        except Exception:
            return []
    else:
        if not STUMPERS_LOG.exists():
            return []
        return [json.loads(l) for l in STUMPERS_LOG.read_text().splitlines() if l.strip()]


# ── helpers ──────────────────────────────────────────────────────────────
_LANGUAGE_OPTIONS = [
    {"id": "q_hindi",  "label": "Hindi"},
    {"id": "q_tamil",  "label": "Tamil"},
    {"id": "q_telugu", "label": "Telugu"},
]

_ERA_OPTIONS = [
    {"id": "q_classic", "label": "Before 1990"},
    {"id": "q_90s",     "label": "1990s"},
    {"id": "q_2000s",   "label": "2000s"},
    {"id": "q_2010s",   "label": "2010s"},
    {"id": "q_2020s",   "label": "2020s"},
]

_GENRE_OPTIONS = [
    {"id": "q_genre_action",   "label": "Action"},
    {"id": "q_genre_comedy",   "label": "Comedy"},
    {"id": "q_genre_romance",  "label": "Romance"},
    {"id": "q_genre_drama",    "label": "Drama / Family"},
    {"id": "q_genre_thriller", "label": "Thriller / Crime"},
    {"id": "q_genre_scifi",    "label": "Sci-Fi / Fantasy"},
    {"id": "q_genre_other",    "label": "Historical / Biopic / Horror / Sports"},
]


def _question_payload(q) -> dict:
    if q.id in LANGUAGE_QUESTION_IDS:
        return {"id": q.id, "text": "What language is the film in?",
                "group": "language", "options": _LANGUAGE_OPTIONS}
    if q.id in ERA_QUESTION_IDS:
        return {"id": q.id, "text": "Which era was it released in?",
                "group": "era", "options": _ERA_OPTIONS}
    if q.id in GENRE_QUESTION_IDS:
        return {"id": q.id, "text": "What is the central theme?",
                "group": "genre", "options": _GENRE_OPTIONS}
    return {"id": q.id, "text": q.text, "group": None, "options": None}


def _session_state(session) -> dict:
    return {
        "session_id": session.id,
        "question_count": session.question_count(),
        "remaining_candidates": session.remaining_count(),
        "can_go_back": len(session.history) > 0,
    }


# ── routes ───────────────────────────────────────────────────────────────
@app.post("/game/start")
def start_game():
    session = engine.new_session()
    question = engine.next_question(session)
    return {
        **_session_state(session),
        "question": _question_payload(question) if question else None,
    }


@app.post("/game/answer")
def answer_question(req: AnswerRequest):
    session = engine.get_session(req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if req.answer not in ("yes", "no", "dunno"):
        raise HTTPException(status_code=422, detail="answer must be 'yes', 'no', or 'dunno'")

    engine.apply_answer(session, req.question_id, req.answer)

    if engine.should_guess(session):
        guesses = engine.top_guesses(session)
        return {
            **_session_state(session),
            "phase": "guess",
            "guesses": guesses,
            "question": None,
        }

    question = engine.next_question(session)
    if question is None:
        # Ran out of questions — make best guess
        return {
            **_session_state(session),
            "phase": "guess",
            "guesses": engine.top_guesses(session),
            "question": None,
        }
    return {
        **_session_state(session),
        "phase": "question",
        "question": _question_payload(question),
        "guesses": None,
    }


@app.post("/game/batch-answer")
def batch_answer(req: BatchAnswerRequest):
    from questions import QUESTION_MAP as QM
    session = engine.get_session(req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    for a in req.answers:
        qid, ans = a.get("question_id"), a.get("answer")
        if qid and ans and qid in QM and qid not in session.asked:
            engine.apply_answer(session, qid, ans)
    if engine.should_guess(session):
        return {**_session_state(session), "phase": "guess",
                "guesses": engine.top_guesses(session), "question": None}
    q = engine.next_question(session)
    return {**_session_state(session), "phase": "question",
            "question": _question_payload(q) if q else None, "guesses": None}


@app.post("/game/back")
def go_back(req: BackRequest):
    session = engine.get_session(req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    engine.undo_last(session)
    question = engine.next_question(session)
    return {
        **_session_state(session),
        "phase": "question",
        "question": _question_payload(question) if question else None,
        "guesses": None,
    }


@app.post("/game/stumped")
def stumped(req: StumpedRequest):
    """Log a title the genie failed to guess — a coverage-gap signal (the film
    may be missing from the catalog, or mislabeled). Records the player's picks
    so we can tell which."""
    title = (req.title or "").strip()
    if not title:
        return {"status": "empty"}
    session = engine.get_session(req.session_id)
    yes_answers = sorted(q for q, a in (session.answers.items() if session else [])
                         if a == "yes")
    record = {
        "ts": datetime.datetime.utcnow().isoformat() + "Z",
        "title": title,
        "yes_answers": yes_answers,
        "remaining_candidates": session.remaining_count() if session else None,
    }
    _stumper_insert(record)
    return {"status": "ok"}


@app.get("/admin/stumpers")
def list_stumpers():
    """Read-only view of films the genie couldn't guess — your coverage-gap feed."""
    entries = _stumper_list()
    return {"count": len(entries), "entries": entries}


@app.post("/game/feedback")
def submit_feedback(req: FeedbackRequest):
    session = engine.get_session(req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    top = session.last_guesses[0] if session.last_guesses else {}
    yes_answers = sorted(q for q, a in session.answers.items() if a == "yes")
    _game_insert({
        "ts": datetime.datetime.utcnow().isoformat() + "Z",
        "outcome": "correct" if req.was_correct else "wrong_guess",
        "guessed_movie_id": top.get("id"),
        "guessed_movie_title": top.get("title"),
        "correct_movie_id": req.correct_movie_id,
        "yes_answers": yes_answers,
        "all_answers": dict(session.answers),
        "questions_asked": list(session.asked),
        "remaining_candidates": session.remaining_count(),
        "question_count": session.question_count(),
    })
    return {"status": "ok", "was_correct": req.was_correct}


@app.get("/admin/games")
def list_games():
    """All completed game outcomes — correct guesses and wrong guesses."""
    entries = _games_list()
    return {"count": len(entries), "entries": entries}


@app.get("/game/session/{session_id}")
def get_session(session_id: str):
    session = engine.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return _session_state(session)


@app.get("/movies")
def list_movies(language: Optional[str] = None):
    result = movies
    if language:
        result = [m for m in movies if m["language"] == language]
    return {"count": len(result), "movies": result}


@app.get("/movies/export.csv")
def export_csv():
    COLS = [
        "id", "title", "year", "language", "era", "primary_genre",
        "director", "lead_actor", "lead_gender", "imdb_rating",
        "has_action", "has_comedy", "has_romance", "has_songs", "has_villain",
        "has_thriller_elements", "has_social_message",
        "is_anti_hero", "is_set_abroad",
        "has_love_triangle", "has_revenge_plot", "has_forbidden_love",
        "is_family_film", "is_based_on_true_story", "is_biographical",
        "is_franchise", "is_remake", "is_sports_film", "is_historical",
        "is_horror", "is_sci_fi", "is_pan_india_blockbuster",
    ]
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=COLS, extrasaction="ignore")
    writer.writeheader()
    for m in sorted(_all_movies, key=lambda x: (x["language"], x.get("year", 0))):
        writer.writerow({c: m.get(c, "") for c in COLS})
    buf.seek(0)
    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=movies.csv"},
    )


@app.get("/health")
def health():
    return {"status": "ok", "movie_count": len(movies)}
