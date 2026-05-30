#!/usr/bin/env python3
"""Idempotent data-quality pass for data/movies.json.

Safe to re-run any time — in particular AFTER the enrichment task rewrites the
dataset, since enrichment may reintroduce the same genre/flag contradictions.

What it does:
  1. Coerces numeric-looking imdb_rating strings to floats.
  2. Repairs known column-shifted records (currently: the "Iraivi" row).
  3. Syncs boolean flags ON from each movie's `genres` list (one-directional —
     never turns a flag OFF, since genre lists can be incomplete). This fixes
     the Sanju-class bug where a biopic had is_biographical=false.
  4. Replaces bogus primary_genre values (e.g. an era string that leaked in).

Run:  python scripts/fix_data.py        (from the backend/ directory)
"""
from __future__ import annotations
import json
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data" / "movies.json"

# genre token -> boolean flags it implies
GENRE_FLAG = {
    "comedy": ["has_comedy"], "romance": ["has_romance"], "action": ["has_action"],
    "thriller": ["has_thriller_elements"], "horror": ["is_horror"],
    "sports": ["is_sports_film"], "historical": ["is_historical"],
    "musical": ["has_songs"], "family": ["is_family_film"],
    "sci-fi": ["is_sci_fi"], "fantasy": ["is_sci_fi"],
    "biography": ["is_biographical", "is_based_on_true_story"],
    "biopic": ["is_biographical", "is_based_on_true_story"],
}
ERAS = {"classic", "90s", "2000s", "2010s", "2020s"}

# Curated corrections for records we've hand-verified as mislabeled by the
# auto-enrichment (e.g. genres too sparse to imply the right flags). Keyed by
# (title, year). `add_genres` are merged into the genres list (so the flag sync
# below then turns the implied booleans on); `set` overrides specific flags that
# no genre implies (love triangle, villain, ...). Add entries here as testing
# surfaces more — the real fix belongs upstream in enrichment.
KNOWN_FIXES = {
    ("Student of the Year", 2012): {
        "add_genres": ["romance", "drama"],
        "set": {"has_romance": True, "has_love_triangle": True, "has_villain": False},
    },
}


def fix(movies: list[dict]) -> dict:
    counts = {"rating_coerced": 0, "repaired": 0, "flags": 0, "primary_genre": 0, "curated": 0}

    for m in movies:
        # 0. curated per-title corrections (run before flag sync so added genres
        #    also propagate to their implied flags)
        cf = KNOWN_FIXES.get((m.get("title"), m.get("year")))
        if cf:
            for g in cf.get("add_genres", []):
                m.setdefault("genres", [])
                if g not in m["genres"]:
                    m["genres"].append(g)
            for k, v in cf.get("set", {}).items():
                m[k] = v
            counts["curated"] += 1

        # 1. numeric rating stored as string
        r = m.get("imdb_rating")
        if isinstance(r, str):
            try:
                m["imdb_rating"] = float(r)
                counts["rating_coerced"] += 1
            except ValueError:
                pass  # genuinely non-numeric (corrupted) — left for step 2

        # 2. known column-shifted record: the Tamil film "Iraivi" (2016)
        if m.get("title") == "Lady Superstar" and m.get("imdb_rating") == "male":
            m.update({
                "id": "ta_iraivi_2016", "title": "Iraivi", "year": 2016,
                "language": "tamil", "era": "2010s", "primary_genre": "drama",
                "director": "Karthik Subbaraj", "lead_actor": "S. J. Suryah",
                "lead_gender": "male", "imdb_rating": 7.9, "has_action": False,
            })
            m.setdefault("genres", [])
            if "drama" not in m["genres"]:
                m["genres"].append("drama")
            counts["repaired"] += 1

        # 3. sync flags ON from genres
        for g in (m.get("genres") or []):
            for flag in GENRE_FLAG.get(g, []):
                if m.get(flag) is not True:
                    m[flag] = True
                    counts["flags"] += 1

        # 4. bogus primary_genre (e.g. an era leaked in)
        if m.get("primary_genre") in ERAS:
            m["primary_genre"] = (m.get("genres") or ["drama"])[0]
            counts["primary_genre"] += 1

    return counts


def main() -> None:
    movies = json.loads(DATA.read_text())
    counts = fix(movies)
    DATA.write_text(json.dumps(movies, indent=2, ensure_ascii=False))
    print(f"fixed {DATA} ({len(movies)} movies)")
    for k, v in counts.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
