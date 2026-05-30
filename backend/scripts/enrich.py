"""
Enriches existing movies.json with Wikipedia-derived attributes.
Runs in-place: reads movies.json, enriches, saves back.

Usage:
    python scripts/enrich.py --data data/movies.json --batch-size 50
"""

from __future__ import annotations

import argparse
import json
import re
import time
from pathlib import Path

import requests

WIKI_API = "https://en.wikipedia.org/w/api.php"
HEADERS  = {"User-Agent": "IndianMovieGenie/1.0 (enrichment)"}


def fetch_wikipedia_snippet(title: str, year: int) -> str:
    params = {
        "action": "query", "format": "json",
        "list": "search",
        "srsearch": f"{title} {year} Indian film",
        "srlimit": 1,
    }
    try:
        r = requests.get(WIKI_API, params=params, headers=HEADERS, timeout=10)
        r.raise_for_status()
        results = r.json().get("query", {}).get("search", [])
        if not results:
            return ""
        return re.sub(r"<[^>]+>", "", results[0].get("snippet", "")).lower()
    except Exception:
        return ""


def infer_from_snippet(snippet: str, movie: dict) -> dict:
    updates: dict = {}

    if not movie.get("is_based_on_true_story"):
        if any(w in snippet for w in ("true story", "based on the life", "real-life",
                                      "true events", "autobiography", "inspired by")):
            updates["is_based_on_true_story"] = True

    if not movie.get("is_remake"):
        if any(w in snippet for w in ("remake of", "adapted from", "adaptation of",
                                      "remake", "remade")):
            updates["is_remake"] = True

    if not movie.get("is_franchise"):
        if any(w in snippet for w in ("sequel", "franchise", "series", "part 2",
                                      "chapter 2", "second part", "third part")):
            updates["is_franchise"] = True

    if movie.get("lead_gender") != "female":
        if any(w in snippet for w in ("female lead", "woman in the lead",
                                      "actress in the lead", "female protagonist",
                                      "woman-centric", "led by a woman")):
            updates["lead_gender"] = "female"

    if not movie.get("has_social_message"):
        if any(w in snippet for w in ("social issue", "social message", "awareness",
                                      "caste discrimination", "gender inequality",
                                      "social commentary", "socially relevant")):
            updates["has_social_message"] = True

    if not movie.get("has_romance"):
        if any(w in snippet for w in ("love story", "romantic", "romance", "love interest",
                                      "falls in love", "love triangle")):
            updates["has_romance"] = True

    if not movie.get("has_comedy"):
        if any(w in snippet for w in ("comedy", "comic", "humour", "humor",
                                      "slapstick", "satirical")):
            updates["has_comedy"] = True

    if not movie.get("has_action"):
        if any(w in snippet for w in ("action film", "action sequences", "action-packed",
                                      "martial arts", "stunt")):
            updates["has_action"] = True

    if not movie.get("has_thriller_elements"):
        if any(w in snippet for w in ("thriller", "suspense", "mystery", "whodunit",
                                      "psychological")):
            updates["has_thriller_elements"] = True

    if not movie.get("is_biographical"):
        if any(w in snippet for w in ("biographical", "biopic", "life of ", "based on the life of")):
            updates["is_biographical"] = True

    if not movie.get("is_historical"):
        if any(w in snippet for w in ("historical", "period film", "set in the",
                                      "colonial", "medieval", "ancient")):
            updates["is_historical"] = True

    return updates


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data",       default="data/movies.json")
    parser.add_argument("--batch-size", type=int, default=50,
                        help="Save progress every N films")
    parser.add_argument("--only-imdb",  action="store_true",
                        help="Only enrich IMDB-sourced films (skip hand-tagged)")
    args = parser.parse_args()

    data_path = Path(args.data)
    movies    = json.loads(data_path.read_text())

    to_enrich = [m for m in movies if not args.only_imdb or m["id"].startswith("tt")]
    skip_set  = set() if not args.only_imdb else {m["id"] for m in movies if not m["id"].startswith("tt")}

    print(f"Enriching {len(to_enrich)} films via Wikipedia…")
    print(f"(saving every {args.batch_size} films)\n")

    total_updates = 0
    for i, movie in enumerate(movies):
        if movie["id"] in skip_set:
            continue

        snippet = fetch_wikipedia_snippet(movie["title"], movie["year"])
        if not snippet:
            time.sleep(0.3)
            continue

        updates = infer_from_snippet(snippet, movie)
        if updates:
            movie.update(updates)
            total_updates += len(updates)
            changed = ", ".join(f"{k}→{v}" for k, v in updates.items())
            print(f"  [{i+1:>4}] {movie['title']} ({movie['year']}): {changed}")

        time.sleep(0.3)

        if (i + 1) % args.batch_size == 0:
            data_path.write_text(json.dumps(movies, indent=2, ensure_ascii=False))
            print(f"  … saved at {i+1} films ({total_updates} attribute updates so far)")

    data_path.write_text(json.dumps(movies, indent=2, ensure_ascii=False))
    print(f"\nDone. {total_updates} attribute updates across {len(to_enrich)} films → {data_path}")


if __name__ == "__main__":
    main()
