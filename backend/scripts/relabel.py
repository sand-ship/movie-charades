"""Batch re-labeling of movies.json attributes using Claude (Sonnet 4.6).

The Wikipedia-snippet enrichment (enrich.py) only ever flips flags to True and
misses most attributes, leaving records like "Student of the Year" (a romance)
tagged comedy-only with has_romance=False. This relabels every film's
descriptive attributes from Claude's own knowledge, correcting flags in BOTH
directions, so the genie's questions actually match the films.

Identity / factual fields are NEVER touched: id, title, year, language,
director, lead_actor, imdb_rating. `era` is derived deterministically from
`year`. Everything else (genres, primary_genre, lead_gender, and the boolean
attributes) is relabeled.

Usage:
    python scripts/relabel.py --dry-run 8     # label a sample synchronously, print, no write
    python scripts/relabel.py --titles "PK,Sanju"   # label specific titles, print, no write
    python scripts/relabel.py --run            # full Batch API run, writes movies.json

Safe to re-run. --run backs up movies.json to movies.json.relabel.bak first.
Do NOT --run while another process is writing movies.json.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import anthropic

MODEL = "claude-sonnet-4-6"
DATA = Path(__file__).resolve().parent.parent / "data" / "movies.json"

# Controlled vocabulary — must stay aligned with questions.py (_genre_in tokens
# and the GENRE_QUESTION_IDS theme picker) so labels drive the right questions.
GENRE_VOCAB = [
    "action", "comedy", "romance", "drama", "family", "thriller", "crime",
    "mystery", "historical", "horror", "sports", "biopic", "sci-fi", "fantasy",
    "musical", "war", "adventure",
]
PRIMARY_GENRE_VOCAB = [
    "action", "comedy", "romance", "drama", "thriller", "historical",
    "horror", "sports", "biopic",
]
BOOL_FIELDS = [
    "has_action", "has_comedy", "has_romance", "has_villain", "has_songs",
    "has_thriller_elements", "has_social_message", "has_love_triangle",
    "has_revenge_plot", "has_forbidden_love", "is_anti_hero", "is_set_abroad",
    "is_family_film", "is_based_on_true_story", "is_biographical", "is_franchise",
    "is_remake", "is_sports_film", "is_historical", "is_horror", "is_sci_fi",
    "is_pan_india_blockbuster",
]

# JSON schema for structured outputs (single source of truth for sync + batch).
SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "genres": {
            "type": "array",
            "items": {"type": "string", "enum": GENRE_VOCAB},
        },
        "primary_genre": {"type": "string", "enum": PRIMARY_GENRE_VOCAB},
        "lead_gender": {"type": "string", "enum": ["male", "female"]},
        **{f: {"type": "boolean"} for f in BOOL_FIELDS},
    },
    "required": ["genres", "primary_genre", "lead_gender", *BOOL_FIELDS],
}

SYSTEM = [
    {
        "type": "text",
        "text": (
            "You label Indian films (Hindi/Tamil/Telugu/etc.) with structured "
            "attributes for an Akinator-style guessing game. Use your knowledge "
            "of the specific film identified by title + year + language + "
            "director + lead actor. If you are unsure of the exact film, infer "
            "from the most likely film matching those fields. Label honestly and "
            "completely — set each boolean True or False based on the actual "
            "film, never default everything to False.\n\n"
            "Field definitions:\n"
            "- genres: ALL applicable genres from the vocabulary (a film is "
            "often 2-4 genres; e.g. a romantic comedy-drama is "
            "[romance, comedy, drama]).\n"
            "- primary_genre: the single most central genre.\n"
            "- lead_gender: gender of the primary protagonist.\n"
            "- has_action/has_comedy/has_romance: prominent action / comedy / "
            "romance content.\n"
            "- has_villain: a clear memorable antagonist.\n"
            "- has_songs: song-and-dance numbers (true for most mainstream "
            "Indian films).\n"
            "- has_thriller_elements: suspense/thriller/mystery beats.\n"
            "- has_social_message: a clear social/political message.\n"
            "- has_love_triangle: a romantic triangle between three characters.\n"
            "- has_revenge_plot: revenge is a central driver.\n"
            "- has_forbidden_love: romance opposed by family/society/class/caste.\n"
            "- is_anti_hero: morally grey lead.\n"
            "- is_set_abroad: significant portions set outside India.\n"
            "- is_family_film: family-friendly / family drama.\n"
            "- is_based_on_true_story / is_biographical: based on real events / a "
            "biopic of a real person (a biopic is always based on a true story).\n"
            "- is_franchise: part of a series/franchise.\n"
            "- is_remake: a remake of an earlier film.\n"
            "- is_sports_film / is_historical / is_horror / is_sci_fi: the film is "
            "centrally a sports / period-historical / horror / sci-fi-or-fantasy "
            "film.\n"
            "- is_pan_india_blockbuster: a major cross-region blockbuster.\n"
        ),
        "cache_control": {"type": "ephemeral"},
    }
]

OUTPUT_CONFIG = {"format": {"type": "json_schema", "schema": SCHEMA}}


def _era(year) -> str:
    try:
        y = int(year)
    except (TypeError, ValueError):
        return "2010s"
    if y < 1990:
        return "classic"
    if y < 2000:
        return "90s"
    if y < 2010:
        return "2000s"
    if y < 2020:
        return "2010s"
    return "2020s"


def _user_text(m: dict) -> str:
    return (
        f"Title: {m.get('title')}\n"
        f"Year: {m.get('year')}\n"
        f"Language: {m.get('language')}\n"
        f"Director: {m.get('director')}\n"
        f"Lead actor: {m.get('lead_actor')}"
    )


def _apply(m: dict, labels: dict) -> dict:
    """Merge LLM labels into a movie dict; keep identity/factual fields."""
    out = dict(m)
    out["genres"] = labels["genres"]
    out["primary_genre"] = labels["primary_genre"]
    out["lead_gender"] = labels["lead_gender"]
    for f in BOOL_FIELDS:
        out[f] = bool(labels[f])
    out["era"] = _era(m.get("year"))  # deterministic, not from the LLM
    return out


def _parse_labels(message) -> dict:
    text = next(b.text for b in message.content if b.type == "text")
    return json.loads(text)


def label_one(client, m: dict) -> dict:
    resp = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        thinking={"type": "disabled"},
        system=SYSTEM,
        output_config=OUTPUT_CONFIG,
        messages=[{"role": "user", "content": _user_text(m)}],
    )
    return _parse_labels(resp)


# ── modes ─────────────────────────────────────────────────────────────────

def dry_run(movies: list[dict], sample: list[dict]) -> None:
    client = anthropic.Anthropic()
    show = ["genres", "primary_genre", "lead_gender", "has_romance", "has_comedy",
            "has_love_triangle", "is_biographical", "is_based_on_true_story",
            "has_villain", "is_sports_film"]
    for m in sample:
        labels = label_one(client, m)
        merged = _apply(m, labels)
        print(f"\n=== {m.get('title')} ({m.get('year')}, {m.get('language')}) ===")
        for k in show:
            before, after = m.get(k), merged.get(k)
            flag = "  <-- changed" if before != after else ""
            print(f"  {k:24s} {str(before):28s} -> {after}{flag}")


def full_run(movies: list[dict]) -> None:
    from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
    from anthropic.types.messages.batch_create_params import Request

    client = anthropic.Anthropic()
    requests = [
        Request(
            custom_id=f"m{i}",
            params=MessageCreateParamsNonStreaming(
                model=MODEL,
                max_tokens=1024,
                thinking={"type": "disabled"},
                system=SYSTEM,
                output_config=OUTPUT_CONFIG,
                messages=[{"role": "user", "content": _user_text(m)}],
            ),
        )
        for i, m in enumerate(movies)
    ]
    print(f"Submitting batch of {len(requests)} labeling requests ({MODEL})…")
    batch = client.messages.batches.create(requests=requests)
    print(f"Batch {batch.id} — polling (most finish < 1h)…")
    while True:
        batch = client.messages.batches.retrieve(batch.id)
        if batch.processing_status == "ended":
            break
        rc = batch.request_counts
        print(f"  {batch.processing_status}: processing={rc.processing} "
              f"succeeded={rc.succeeded} errored={rc.errored}")
        time.sleep(30)

    labels_by_idx: dict[int, dict] = {}
    errors = 0
    for result in client.messages.batches.results(batch.id):
        if result.result.type == "succeeded":
            idx = int(result.custom_id[1:])
            try:
                labels_by_idx[idx] = _parse_labels(result.result.message)
            except Exception as e:  # noqa: BLE001
                errors += 1
                print(f"  parse error {result.custom_id}: {e}")
        else:
            errors += 1
            print(f"  {result.custom_id}: {result.result.type}")

    relabeled = sum(1 for i in range(len(movies)) if i in labels_by_idx)
    print(f"Labeled {relabeled}/{len(movies)} (errors: {errors})")

    bak = DATA.with_suffix(".json.relabel.bak")
    bak.write_text(json.dumps(movies, indent=2, ensure_ascii=False))
    print(f"Backed up original → {bak}")

    out = [
        _apply(m, labels_by_idx[i]) if i in labels_by_idx else m
        for i, m in enumerate(movies)
    ]
    DATA.write_text(json.dumps(out, indent=2, ensure_ascii=False))
    print(f"Wrote {DATA}. Restart the backend to load the relabeled catalog.")


def main() -> None:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", type=int, metavar="N",
                   help="Label first N films synchronously, print, do not write")
    g.add_argument("--titles", type=str,
                   help="Comma-separated titles to label synchronously, print, no write")
    g.add_argument("--run", action="store_true",
                   help="Full Batch API run; writes movies.json")
    args = ap.parse_args()

    movies = json.loads(DATA.read_text())

    if args.run:
        full_run(movies)
    elif args.titles:
        wanted = {t.strip().lower() for t in args.titles.split(",")}
        sample = [m for m in movies if m.get("title", "").lower() in wanted]
        if not sample:
            print("No matching titles found.", file=sys.stderr)
            sys.exit(1)
        dry_run(movies, sample)
    else:
        dry_run(movies, movies[: args.dry_run])


if __name__ == "__main__":
    main()
