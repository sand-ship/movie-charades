"""Fill missing trope fields for the ~999 films that were added after the
initial labeling pass. Only touches the 8 fields that are None for those
films — leaves all other fields (genres, lead_gender, existing booleans) alone.

Fields filled:
  has_village_setting     — significant portion set in a village / rural area
  has_parent_child_drama  — parent-child relationship is a central emotional thread
  has_police_or_law       — protagonist is a cop, lawyer, or judge
  has_double_role         — lead actor plays a double role
  has_item_number         — prominent item number / special dance song
  has_one_sided_love      — love story is primarily unrequited / one-sided
  is_college_film         — significant portion set in college / university
  is_mass_entertainer     — commercial mass-masala entertainer

Usage:
    python scripts/fill_tropes.py --dry-run 5
    python scripts/fill_tropes.py --run
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import anthropic

MODEL = "claude-haiku-4-5-20251001"   # fast + cheap for a simple boolean fill
DATA = Path(__file__).resolve().parent.parent / "data" / "movies.json"

TROPE_FIELDS = [
    "has_village_setting",
    "has_parent_child_drama",
    "has_police_or_law",
    "has_double_role",
    "has_item_number",
    "has_one_sided_love",
    "is_college_film",
    "is_mass_entertainer",
]

SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {f: {"type": "boolean"} for f in TROPE_FIELDS},
    "required": TROPE_FIELDS,
}

SYSTEM = [{
    "type": "text",
    "text": (
        "You label Indian films with trope attributes for a charades-style "
        "guessing game. Use your knowledge of the specific film. "
        "Set each boolean True or False honestly — never default to False.\n\n"
        "Field definitions:\n"
        "- has_village_setting: a significant portion of the film is set in a "
        "village or rural area (not a city).\n"
        "- has_parent_child_drama: the relationship between a parent and child "
        "is a central emotional thread (not just a background detail).\n"
        "- has_police_or_law: the protagonist (or a key lead) is a cop, "
        "police officer, lawyer, or judge.\n"
        "- has_double_role: the lead actor plays two distinct roles / characters.\n"
        "- has_item_number: the film features a prominent item number or "
        "special guest-appearance dance song.\n"
        "- has_one_sided_love: the romantic storyline is primarily one-sided "
        "or unrequited (one person loves, the other does not, for most of the film).\n"
        "- is_college_film: a significant portion of the story is set in a "
        "college or university.\n"
        "- is_mass_entertainer: a commercial mass-masala entertainer with broad "
        "popular appeal (high-energy action/comedy/drama mix aimed at mass audience)."
    ),
    "cache_control": {"type": "ephemeral"},
}]

OUTPUT_CONFIG = {"format": {"type": "json_schema", "schema": SCHEMA}}


def _user_text(m: dict) -> str:
    return (
        f"Title: {m['title']}\n"
        f"Year: {m.get('year', '?')}\n"
        f"Language: {m.get('language', '?')}\n"
        f"Director: {m.get('director', '?')}\n"
        f"Lead actor: {m.get('lead_actor', '?')}"
    )


def _needs_fill(m: dict) -> bool:
    return m.get("has_village_setting") is None


def label_one(client: anthropic.Anthropic, m: dict) -> dict:
    resp = client.messages.create(
        model=MODEL,
        max_tokens=256,
        system=SYSTEM,
        output_config=OUTPUT_CONFIG,
        messages=[{"role": "user", "content": _user_text(m)}],
    )
    text = next(b.text for b in resp.content if b.type == "text")
    return json.loads(text)


def dry_run(movies: list[dict], n: int) -> None:
    client = anthropic.Anthropic()
    sample = [m for m in movies if _needs_fill(m)][:n]
    for m in sample:
        labels = label_one(client, m)
        print(f"\n{m['title']} ({m.get('year')}, {m.get('language')})")
        for f in TROPE_FIELDS:
            print(f"  {f:<26} {labels[f]}")


def full_run(movies: list[dict]) -> None:
    from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
    from anthropic.types.messages.batch_create_params import Request

    client = anthropic.Anthropic()
    to_fill = [(i, m) for i, m in enumerate(movies) if _needs_fill(m)]
    print(f"Films to label: {len(to_fill)}")

    requests = [
        Request(
            custom_id=str(i),
            params=MessageCreateParamsNonStreaming(
                model=MODEL,
                max_tokens=256,
                system=SYSTEM,
                output_config=OUTPUT_CONFIG,
                messages=[{"role": "user", "content": _user_text(m)}],
            ),
        )
        for i, m in to_fill
    ]

    print(f"Submitting batch of {len(requests)} requests ({MODEL})…")
    batch = client.messages.batches.create(requests=requests)
    print(f"Batch {batch.id} submitted — polling every 30s…")

    while True:
        batch = client.messages.batches.retrieve(batch.id)
        if batch.processing_status == "ended":
            break
        rc = batch.request_counts
        print(f"  {batch.processing_status}: processing={rc.processing} "
              f"succeeded={rc.succeeded} errored={rc.errored}")
        time.sleep(30)

    rc = batch.request_counts
    print(f"Done: succeeded={rc.succeeded} errored={rc.errored}")

    labels_by_idx: dict[int, dict] = {}
    errors = 0
    for result in client.messages.batches.results(batch.id):
        if result.result.type == "succeeded":
            idx = int(result.custom_id)
            try:
                text = next(b.text for b in result.result.message.content if b.type == "text")
                labels_by_idx[idx] = json.loads(text)
            except Exception as e:
                errors += 1
                print(f"  parse error idx={result.custom_id}: {e}")
        else:
            errors += 1
            print(f"  idx={result.custom_id}: {result.result.type}")

    print(f"Parsed {len(labels_by_idx)}/{len(to_fill)} (errors: {errors})")

    bak = DATA.with_suffix(".json.tropes.bak")
    bak.write_text(DATA.read_text())
    print(f"Backed up → {bak.name}")

    out = list(movies)
    for idx, labels in labels_by_idx.items():
        m = dict(out[idx])
        for f in TROPE_FIELDS:
            m[f] = bool(labels[f])
        out[idx] = m

    DATA.write_text(json.dumps(out, indent=2, ensure_ascii=False))
    print(f"Wrote {DATA} — {len(labels_by_idx)} films updated.")


def main() -> None:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", type=int, metavar="N",
                   help="Label first N unlabeled films synchronously, print only")
    g.add_argument("--run", action="store_true",
                   help="Full Batch API run; writes movies.json")
    args = ap.parse_args()

    movies = json.loads(DATA.read_text())
    if args.run:
        full_run(movies)
    else:
        dry_run(movies, args.dry_run)


if __name__ == "__main__":
    main()
