"""Merge generated filmography records (/tmp/cover/out/*.json) into movies.json.

Dedups against existing films by (title, year) — existing records always win.
Generates an id, derives era from year, validates genres against the vocabulary,
and coerces booleans. Safe to re-run across sweep waves.

    python scripts/merge_films.py
"""
from __future__ import annotations
import glob, json, re
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data" / "movies.json"
SRC = "/tmp/cover/out/*.json"

GENRE_VOCAB = {"action","comedy","romance","drama","family","thriller","crime","mystery",
    "historical","horror","sports","biopic","sci-fi","fantasy","musical","war","adventure"}
PRIMARY_VOCAB = {"action","comedy","romance","drama","thriller","historical","horror","sports","biopic"}
BOOL = ["has_action","has_comedy","has_romance","has_villain","has_songs","has_thriller_elements",
    "has_social_message","has_love_triangle","has_revenge_plot","has_forbidden_love","is_anti_hero",
    "is_set_abroad","is_family_film","is_based_on_true_story","is_biographical","is_franchise",
    "is_remake","is_sports_film","is_historical","is_horror","is_sci_fi","is_pan_india_blockbuster"]


def era(y):
    try: y = int(y)
    except (TypeError, ValueError): return "2010s"
    return ("classic" if y < 1990 else "90s" if y < 2000 else "2000s"
            if y < 2010 else "2010s" if y < 2020 else "2020s")


def slug(t): return re.sub(r"[^a-z0-9]+", "_", str(t).lower()).strip("_")[:40]


def main():
    ms = json.loads(DATA.read_text())
    seen = {(str(m.get("title","")).strip().lower(), m.get("year")) for m in ms}
    used_ids = {m.get("id") for m in ms}
    added = 0; per_lang = {}
    for f in sorted(glob.glob(SRC)):
        try: arr = json.loads(Path(f).read_text())
        except Exception as e:
            print(f"  skip {Path(f).name}: {e}"); continue
        if not isinstance(arr, list): continue
        for r in arr:
            t, y = r.get("title"), r.get("year")
            if not t or y is None: continue
            try: y = int(y)
            except (TypeError, ValueError): continue
            key = (str(t).strip().lower(), y)
            if key in seen: continue
            seen.add(key)
            lang = (r.get("language") or "hindi").strip().lower()
            g = [x for x in (r.get("genres") or []) if x in GENRE_VOCAB] or ["drama"]
            pg = r.get("primary_genre")
            if pg not in PRIMARY_VOCAB: pg = g[0] if g[0] in PRIMARY_VOCAB else "drama"
            try: rating = float(r.get("imdb_rating"))
            except (TypeError, ValueError): rating = 6.5
            mid = f"{lang[:2]}_{slug(t)}_{y}"; n = 2
            while mid in used_ids: mid = f"{lang[:2]}_{slug(t)}_{y}_{n}"; n += 1
            used_ids.add(mid)
            rec = {"id": mid, "title": str(t).strip(), "year": y, "language": lang,
                   "era": era(y), "director": r.get("director") or "N/A",
                   "lead_actor": r.get("lead_actor") or "N/A",
                   "lead_actress": r.get("lead_actress") or "N/A",
                   "music_director": r.get("music_director") or "N/A",
                   "imdb_rating": rating,
                   "lead_gender": r.get("lead_gender") if r.get("lead_gender") in ("male","female") else "male",
                   "genres": g, "primary_genre": pg,
                   **{b: bool(r.get(b, False)) for b in BOOL}}
            ms.append(rec); added += 1
            per_lang[lang] = per_lang.get(lang, 0) + 1
    DATA.write_text(json.dumps(ms, indent=2, ensure_ascii=False))
    print(f"added {added} new films -> total {len(ms)}")
    print("  by language:", per_lang)


if __name__ == "__main__":
    main()
