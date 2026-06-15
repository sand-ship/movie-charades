"""Analyze the stumpers log to surface two failure modes:

  1. MISSING  — film not in the catalog at all (coverage gap).
  2. MISMATCH — film is in the catalog but a question the player
                answered 'yes' evaluates to False on that film's data,
                meaning the label is wrong or the question definition
                is ambiguous.

Usage:
    # analyze the local log
    python scripts/analyze_stumpers.py

    # pull live data from deployed server
    python scripts/analyze_stumpers.py --url https://movie-charades.onrender.com

    # also show questions the player never got asked but which are True
    # on the film (hidden signals — may explain why the pool didn't narrow)
    python scripts/analyze_stumpers.py --verbose
"""
from __future__ import annotations

import argparse
import difflib
import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "movies.json"
STUMPERS = ROOT / "data" / "stumpers.jsonl"

# Question groups that are structural (language/era/genre picker) —
# mismatches here are expected and not labeling errors.
STRUCTURAL = {
    "q_hindi", "q_tamil", "q_telugu",
    "q_classic", "q_90s", "q_2000s", "q_2010s", "q_2020s",
    "q_genre_action", "q_genre_comedy", "q_genre_romance",
    "q_genre_drama", "q_genre_thriller", "q_genre_scifi", "q_genre_other",
}


def _load_question_map(movies):
    sys.path.insert(0, str(ROOT))
    from questions import QUESTIONS, QUESTION_MAP, make_star_questions
    star_qs = make_star_questions(movies)
    QUESTIONS.extend(star_qs)
    for q in star_qs:
        QUESTION_MAP[q.id] = q
    return QUESTION_MAP


def _fuzzy_match(title: str, movies: list[dict]) -> dict | None:
    title_lo = title.strip().lower()
    # 1. exact (case-insensitive)
    for m in movies:
        if m["title"].lower() == title_lo:
            return m
    # 2. one is a substring of the other — only when both are long enough
    if len(title_lo) >= 4:
        for m in movies:
            mt = m["title"].lower()
            if len(mt) >= 4 and (title_lo in mt or mt in title_lo):
                return m
    # 3. difflib close match — high cutoff to avoid false positives
    titles = [m["title"].lower() for m in movies]
    close = difflib.get_close_matches(title_lo, titles, n=1, cutoff=0.85)
    if close:
        return next(m for m in movies if m["title"].lower() == close[0])
    return None


def _fetch_stumpers(url: str) -> list[dict]:
    req = urllib.request.urlopen(f"{url.rstrip('/')}/admin/stumpers", timeout=10)
    data = json.loads(req.read())
    return data.get("entries", [])


def _load_local_stumpers() -> list[dict]:
    if not STUMPERS.exists():
        return []
    return [json.loads(l) for l in STUMPERS.read_text().splitlines() if l.strip()]


def analyze(stumpers: list[dict], movies: list[dict], qmap: dict, verbose: bool) -> None:
    if not stumpers:
        print("No stumpers to analyze.")
        return

    print(f"Analyzing {len(stumpers)} stumped game(s)...\n")
    missing, mismatched, ok = [], [], []

    for entry in stumpers:
        title = entry.get("title", "").strip()
        yes_answers = set(entry.get("yes_answers", []))
        ts = entry.get("ts", "")[:10]

        film = _fuzzy_match(title, movies)
        if film is None:
            missing.append({"title": title, "ts": ts, "yes_answers": sorted(yes_answers)})
            continue

        # Find data mismatches: player said yes → data says False/None
        mismatches = []
        for qid in sorted(yes_answers):
            if qid in STRUCTURAL:
                continue
            q = qmap.get(qid)
            if q is None:
                continue  # removed/renamed question — skip
            actual = q.evaluate(film)
            if not actual:
                mismatches.append(qid)

        # Optionally: find True fields that were never asked (hidden signals)
        hidden = []
        if verbose:
            for qid, q in qmap.items():
                if qid in STRUCTURAL or qid in yes_answers:
                    continue
                if qid.startswith(("q_actor_", "q_actress_", "q_dir_")):
                    continue
                if q.evaluate(film):
                    hidden.append(qid)

        if mismatches or hidden:
            mismatched.append({
                "title": title, "matched_to": film["title"],
                "film_id": film["id"], "ts": ts,
                "mismatches": mismatches, "hidden": hidden,
            })
        else:
            ok.append({"title": title, "matched_to": film["title"], "ts": ts})

    # ── Report ────────────────────────────────────────────────────────────

    if missing:
        print(f"{'─'*60}")
        print(f"MISSING FROM CATALOG ({len(missing)} film(s)) — add these")
        print(f"{'─'*60}")
        for e in missing:
            print(f"  [{e['ts']}] \"{e['title']}\"")
            signals = [q for q in e['yes_answers'] if q not in STRUCTURAL]
            if signals:
                print(f"    Player yes-answers: {', '.join(signals)}")
        print()

    if mismatched:
        print(f"{'─'*60}")
        print(f"LABEL MISMATCHES ({len(mismatched)} film(s)) — fix the data")
        print(f"{'─'*60}")
        for e in mismatched:
            match_note = (f" (matched to \"{e['matched_to']}\")"
                          if e['title'].lower() != e['matched_to'].lower() else "")
            print(f"  [{e['ts']}] \"{e['title']}\"{match_note}  id={e['film_id']}")
            for qid in e["mismatches"]:
                q = qmap.get(qid)
                print(f"    ✗ player said YES to [{qid}]  \"{q.text if q else '?'}\"")
                print(f"      → data says False — set to true in movies.json")
            if e["hidden"]:
                print(f"    ℹ hidden True fields never asked: {', '.join(e['hidden'][:6])}")
            print()

    if ok:
        print(f"{'─'*60}")
        print(f"OK — data looks consistent ({len(ok)} film(s))")
        print(f"{'─'*60}")
        for e in ok:
            print(f"  [{e['ts']}] \"{e['title']}\"")

    print(f"\nSummary: {len(missing)} missing, {len(mismatched)} mismatched, {len(ok)} ok")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default=None,
                    help="Fetch stumpers from live server (e.g. https://movie-charades.onrender.com)")
    ap.add_argument("--verbose", action="store_true",
                    help="Also show True fields on the film that were never asked")
    args = ap.parse_args()

    movies_all = json.loads(DATA.read_text())
    movies = [m for m in movies_all if m.get("language") in {"hindi", "tamil", "telugu"}]
    qmap = _load_question_map(movies)

    if args.url:
        print(f"Fetching stumpers from {args.url}...")
        stumpers = _fetch_stumpers(args.url)
    else:
        stumpers = _load_local_stumpers()

    analyze(stumpers, movies, qmap, verbose=args.verbose)


if __name__ == "__main__":
    main()
