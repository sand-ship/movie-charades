"""Batch-label 9 storyline attributes for all films in movies.json.

New attributes:
  has_mentor_figure       — a mentor/guru shapes the protagonist's arc
  has_friendship_betrayal — a close friendship ends in betrayal
  has_mistaken_identity   — plot hinges on mistaken identity / impersonation
  has_class_conflict      — clash between social classes is a central theme
  has_gangster_world      — story set in or driven by the criminal underworld
  is_set_in_slums         — film primarily set in slums / very poor urban areas
  has_rural_vs_urban      — tension between rural and urban life is a key theme
  has_brothers_in_arms    — male brotherhood/camaraderie is a central emotional thread
  has_enemy_turned_friend — an enemy becomes an ally (or a friend turns enemy)

Usage:
    python scripts/label_storylines.py --dry-run 8
    python scripts/label_storylines.py --titles "Thalapathi,Welcome,Satya"
    python scripts/label_storylines.py --run
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import anthropic

MODEL = "claude-sonnet-4-6"
DATA  = Path(__file__).resolve().parent.parent / "data" / "movies.json"

FIELDS = [
    "has_mentor_figure",
    "has_friendship_betrayal",
    "has_mistaken_identity",
    "has_class_conflict",
    "has_gangster_world",
    "is_set_in_slums",
    "has_rural_vs_urban",
    "has_brothers_in_arms",
    "has_enemy_turned_friend",
]

SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {f: {"type": "boolean"} for f in FIELDS},
    "required": FIELDS,
}

SYSTEM = [
    {
        "type": "text",
        "text": (
            "You label Indian films for an Akinator-style guessing game.\n\n"
            "Label these 9 boolean fields based on the film's actual storyline:\n\n"
            "  has_mentor_figure       — True if a mentor, guru, or senior figure plays a "
            "significant role in shaping the protagonist's journey or values. Must be a "
            "recurring character, not a one-scene cameo.\n\n"
            "  has_friendship_betrayal — True if a close friendship or brotherhood is central "
            "to the plot AND ends in (or is threatened by) betrayal or a serious falling-out. "
            "Includes friends who become enemies, not just mild disagreements.\n\n"
            "  has_mistaken_identity   — True if the plot significantly depends on a character "
            "being mistaken for someone else, impersonating another person, or hiding their "
            "true identity in a comic or dramatic way.\n\n"
            "  has_class_conflict      — True if the clash between rich and poor, high caste "
            "and low caste, or social class divisions is a central theme — not just backdrop.\n\n"
            "  has_gangster_world      — True if the story is substantially set in or driven by "
            "the criminal underworld: gangsters, dons, organised crime, mafia-like factions. "
            "A single villain is not enough; the underworld must be part of the world of the film.\n\n"
            "  is_set_in_slums         — True if slums, chawls, or very poor urban settlements "
            "are the primary setting for a significant portion of the film.\n\n"
            "  has_rural_vs_urban      — True if the tension between village/rural life and "
            "city/urban life is a meaningful theme — e.g. country boy comes to city, city girl "
            "goes to village, or a character torn between both worlds.\n\n"
            "  has_brothers_in_arms    — True if male friendship, brotherhood, or a band-of-brothers "
            "bond is the central emotional thread of the film. The bond must be between the lead "
            "character and at least one other male character, and must drive the story.\n\n"
            "  has_enemy_turned_friend — True if a character who starts as an adversary or rival "
            "meaningfully becomes a friend or ally by the end (or vice versa: a trusted friend "
            "becomes an enemy). Must be a significant arc, not a brief reconciliation.\n\n"
            "Use your knowledge of the specific film. Set each field True or False."
        ),
        "cache_control": {"type": "ephemeral"},
    }
]

OUTPUT_CONFIG = {"format": {"type": "json_schema", "schema": SCHEMA}}


def _user_text(m: dict) -> str:
    return (
        f"Title: {m.get('title')}\n"
        f"Year: {m.get('year')}\n"
        f"Language: {m.get('language')}\n"
        f"Director: {m.get('director')}\n"
        f"Lead actor: {m.get('lead_actor')}\n"
        f"Genres: {', '.join(m.get('genres') or [])}"
    )


def _parse(message) -> dict:
    text = next(b.text for b in message.content if b.type == "text")
    return json.loads(text)


def label_one(client, m: dict) -> dict:
    resp = client.messages.create(
        model=MODEL,
        max_tokens=256,
        system=SYSTEM,
        output_config=OUTPUT_CONFIG,
        messages=[{"role": "user", "content": _user_text(m)}],
    )
    return _parse(resp)


def dry_run(sample: list[dict]) -> None:
    client = anthropic.Anthropic()
    for m in sample:
        labels = label_one(client, m)
        print(f"\n{m['title']} ({m['year']})")
        for f in FIELDS:
            current = m.get(f, "<unset>")
            new = labels[f]
            flag = "  <-- changed" if current != new else ""
            print(f"  {f:35s} {str(current):8s} -> {new}{flag}")


def full_run(movies: list[dict]) -> None:
    from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
    from anthropic.types.messages.batch_create_params import Request

    client = anthropic.Anthropic()
    requests = [
        Request(
            custom_id=f"m{i}",
            params=MessageCreateParamsNonStreaming(
                model=MODEL,
                max_tokens=256,
                system=SYSTEM,
                output_config=OUTPUT_CONFIG,
                messages=[{"role": "user", "content": _user_text(m)}],
            ),
        )
        for i, m in enumerate(movies)
    ]
    print(f"Submitting batch of {len(requests)} requests ({MODEL})…")
    batch = client.messages.batches.create(requests=requests)
    print(f"Batch {batch.id} — polling…")
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
                labels_by_idx[idx] = _parse(result.result.message)
            except Exception as e:
                errors += 1
                print(f"  parse error {result.custom_id}: {e}")
        else:
            errors += 1
            print(f"  {result.custom_id}: {result.result.type}")

    labeled = sum(1 for i in range(len(movies)) if i in labels_by_idx)
    print(f"Labeled {labeled}/{len(movies)} (errors: {errors})")

    bak = DATA.with_suffix(".json.storylines.bak")
    bak.write_text(json.dumps(movies, indent=2, ensure_ascii=False))
    print(f"Backed up → {bak}")

    out = []
    for i, m in enumerate(movies):
        m2 = dict(m)
        if i in labels_by_idx:
            m2.update(labels_by_idx[i])
        out.append(m2)

    DATA.write_text(json.dumps(out, indent=2, ensure_ascii=False))
    print(f"Wrote {DATA}")


def main() -> None:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", type=int, metavar="N",
                   help="Label first N films synchronously, print only")
    g.add_argument("--titles", type=str,
                   help="Comma-separated titles, synchronously, print only")
    g.add_argument("--run", action="store_true",
                   help="Full Batch API run, writes movies.json")
    args = ap.parse_args()

    movies = json.loads(DATA.read_text())

    if args.run:
        full_run(movies)
    elif args.titles:
        wanted = {t.strip().lower() for t in args.titles.split(",")}
        sample = [m for m in movies if m.get("title", "").lower() in wanted]
        if not sample:
            print("No matching titles.", file=sys.stderr)
            sys.exit(1)
        dry_run(sample)
    else:
        dry_run(movies[:args.dry_run])


if __name__ == "__main__":
    main()
