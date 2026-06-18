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
movies = [m for m in _all_movies if m.get("language") in {"Hindi", "Tamil", "Telugu"}]

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
    answer: str  # "yes" | "no" | "maybe" | "dunno"


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
    all_answers: Optional[dict] = None  # Full answer history from frontend
    questions_asked: Optional[list] = None  # Questions asked from frontend
    remaining_candidates: Optional[int] = None


STUMPERS_LOG = Path(__file__).resolve().parent / "data" / "stumpers.jsonl"
GAMES_LOG    = Path(__file__).resolve().parent / "data" / "games.jsonl"

_SUPA_URL = os.getenv("SUPABASE_URL", "").rstrip("/")
_SUPA_KEY = os.getenv("SUPABASE_ANON_KEY", "")
_SUPA_HEADERS = {
    "apikey": _SUPA_KEY,
    "Authorization": f"Bearer {_SUPA_KEY}",
    "Content-Type": "application/json",
}

_ADMIN_KEY = os.getenv("ADMIN_KEY", "")

def _require_admin_key(key: Optional[str] = None) -> None:
    if not _ADMIN_KEY or key != _ADMIN_KEY:
        raise HTTPException(status_code=403, detail="Unauthorized")


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
            r = httpx.post(
                f"{_SUPA_URL}/games",
                json=record,
                headers={**_SUPA_HEADERS, "Prefer": "return=minimal"},
                timeout=5.0,
            )
            if r.status_code >= 400:
                print(f"⚠️ Supabase games insert failed: {r.status_code} {r.text}", flush=True)
                # Fallback to local
                with GAMES_LOG.open("a", encoding="utf-8") as f:
                    f.write(json.dumps(record, ensure_ascii=False) + "\n")
        except Exception as e:
            print(f"⚠️ Supabase games insert error: {e}", flush=True)
            # Fallback to local
            with GAMES_LOG.open("a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
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
    {"id": "q_genre_action",     "label": "Action/Thriller/Adventure"},
    {"id": "q_genre_comedy",     "label": "Comedy"},
    {"id": "q_genre_romance",    "label": "Romance (Love Stories)"},
    {"id": "q_genre_drama",      "label": "Drama (Personal/Family)"},
    {"id": "q_genre_social",     "label": "Social/Political"},
    {"id": "q_genre_historical", "label": "Historical/Biopic"},
    {"id": "q_genre_horror",     "label": "Horror/Supernatural"},
    {"id": "q_genre_scifi",      "label": "Sci-Fi/Fantasy"},
]


def _question_payload(q) -> dict:
    if q.id in LANGUAGE_QUESTION_IDS:
        return {"id": q.id, "text": "What language is the film in?",
                "group": "language", "options": _LANGUAGE_OPTIONS}
    if q.id in ERA_QUESTION_IDS:
        return {"id": q.id, "text": "Which era was it released in?",
                "group": "era", "options": _ERA_OPTIONS}
    if q.id == "q_genre_picker":
        return {"id": q.id, "text": "What's the core genre?",
                "group": "genre", "options": _GENRE_OPTIONS}
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

    # Handle genre picker: convert picker selection to genre answer
    if req.question_id == "q_genre_picker":
        # req.answer is the selected genre ID (e.g., 'q_genre_action')
        selected_genre = req.answer
        if selected_genre not in GENRE_QUESTION_IDS:
            raise HTTPException(status_code=422, detail=f"Invalid genre selection: {selected_genre}")
        # Record that this genre was selected (answers=yes)
        engine.apply_answer(session, selected_genre, "yes")
        # Mark picker as asked so it doesn't appear again
        session.asked.append("q_genre_picker")
    else:
        if req.answer not in ("yes", "no", "maybe", "dunno"):
            raise HTTPException(status_code=422, detail="answer must be 'yes', 'no', 'maybe', or 'dunno'")
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

    # Use frontend-provided data if session is expired/missing
    all_answers = req.all_answers if req.all_answers else (dict(session.answers) if session else {})
    questions_asked = req.questions_asked if req.questions_asked else (list(session.asked) if session else [])
    remaining_candidates = req.remaining_candidates if req.remaining_candidates is not None else (session.remaining_count() if session else None)
    question_count = len(questions_asked)

    yes_answers = sorted(q for q, a in all_answers.items() if a == "yes")

    record = {
        "ts": datetime.datetime.utcnow().isoformat() + "Z",
        "title": title,
        "yes_answers": yes_answers,
        "all_answers": all_answers,
        "questions_asked": questions_asked,
        "remaining_candidates": remaining_candidates,
        "question_count": question_count,
    }
    _stumper_insert(record)

    # Also log to games table as a stumped outcome
    if session:
        top = session.last_guesses[0] if session.last_guesses else {}
        _game_insert({
            "ts": datetime.datetime.utcnow().isoformat() + "Z",
            "outcome": "stumped",
            "guessed_movie_id": top.get("id"),
            "guessed_movie_title": top.get("title"),
            "correct_movie_id": None,  # unknown until player submits
            "yes_answers": yes_answers,
            "all_answers": dict(session.answers),
            "questions_asked": list(session.asked),
            "remaining_candidates": session.remaining_count(),
            "question_count": session.question_count(),
        })

    return {"status": "ok"}


@app.get("/admin/stumpers")
def list_stumpers(key: Optional[str] = None):
    """Read-only view of films the genie couldn't guess — your coverage-gap feed."""
    _require_admin_key(key)
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
def list_games(key: Optional[str] = None):
    """All completed game outcomes — correct guesses and wrong guesses."""
    _require_admin_key(key)
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


@app.get("/admin/analyze-stumpers")
def analyze_stumpers(key: Optional[str] = None, verbose: bool = False):
    """Analyze stumpers to find label mismatches and missing films.

    Returns findings grouped by category:
    - missing: films not in catalog
    - mismatched: films in catalog with label mismatches
    - ok: films with consistent data
    """
    _require_admin_key(key)
    import difflib

    STRUCTURAL = {
        "q_hindi", "q_tamil", "q_telugu",
        "q_classic", "q_90s", "q_2000s", "q_2010s", "q_2020s",
        "q_genre_action", "q_genre_comedy", "q_genre_romance",
        "q_genre_drama", "q_genre_thriller", "q_genre_scifi", "q_genre_other",
    }

    def fuzzy_match(title: str) -> dict | None:
        title_lo = title.strip().lower()
        for m in movies:
            if m["title"].lower() == title_lo:
                return m
        if len(title_lo) >= 4:
            for m in movies:
                mt = m["title"].lower()
                if len(mt) >= 4 and (title_lo in mt or mt in title_lo):
                    return m
        titles = [m["title"].lower() for m in movies]
        close = difflib.get_close_matches(title_lo, titles, n=1, cutoff=0.85)
        if close:
            return next((m for m in movies if m["title"].lower() == close[0]), None)
        return None

    stumpers = _stumper_list()

    missing, mismatched, ok = [], [], []

    for entry in stumpers:
        title = entry.get("title", "").strip()
        yes_answers = set(entry.get("yes_answers", []))

        film = fuzzy_match(title)
        if film is None:
            missing.append({"title": title, "yes_answers": sorted(yes_answers)})
            continue

        mismatches = []
        for qid in sorted(yes_answers):
            if qid in STRUCTURAL:
                continue
            q = QUESTION_MAP.get(qid)
            if q is None:
                continue
            actual = q.evaluate(film)
            if not actual:
                mismatches.append({
                    "question_id": qid,
                    "question_text": q.text if q else "?",
                })

        hidden = []
        if verbose:
            for qid, q in QUESTION_MAP.items():
                if qid in STRUCTURAL or qid in yes_answers:
                    continue
                if qid.startswith(("q_actor_", "q_actress_", "q_dir_", "q_music_")):
                    continue
                if q.evaluate(film):
                    hidden.append(qid)

        if mismatches or hidden:
            mismatched.append({
                "title": title,
                "matched_to": film["title"],
                "film_id": film["id"],
                "mismatches": mismatches,
                "hidden": hidden,
            })
        else:
            ok.append({"title": title, "matched_to": film["title"]})

    return {
        "missing_count": len(missing),
        "mismatched_count": len(mismatched),
        "ok_count": len(ok),
        "total_analyzed": len(stumpers),
        "missing": missing,
        "mismatched": mismatched,
        "ok": ok,
    }


@app.get("/health")
def health():
    return {"status": "ok", "movie_count": len(movies)}
