"""Batch-label has_strict_antagonist for all films in movies.json.

has_strict_antagonist = True when the main conflict is driven by a strict
but well-meaning authority figure (overprotective parent/sibling, conservative
patriarch, institution) who opposes the protagonist — NOT because they are
evil, but out of protectiveness or duty. Classic examples: overprotective
brother in PKTDK, strict father in DDLJ, Paresh Rawal's patriarch roles.
Set False if the antagonist is a clear villain, if there is no real antagonist,
or if the conflict is external/societal rather than a specific character.

Usage:
    python scripts/label_strict_antagonist.py --dry-run 8
    python scripts/label_strict_antagonist.py --titles "Pyaar Kiya To Darna Kya,DDLJ"
    python scripts/label_strict_antagonist.py --run
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

SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "has_strict_antagonist": {"type": "boolean"},
    },
    "required": ["has_strict_antagonist"],
}

SYSTEM = [
    {
        "type": "text",
        "text": (
            "You label Indian films for an Akinator-style guessing game.\n\n"
            "Label the single field has_strict_antagonist:\n"
            "  True  — the main conflict is primarily driven by a STRICT BUT WELL-MEANING "
            "character who opposes the protagonist out of protectiveness, duty, or conservative "
            "values — NOT because they are evil. Examples: overprotective father or brother who "
            "disapproves of a romance, a strict patriarch who wants to control family decisions, "
            "a conservative institution that blocks the hero's goals, a mentor who clashes with "
            "the lead. The key test: would the audience sympathise with this character's "
            "intentions even while rooting against them?\n"
            "  False — the antagonist is a clear villain (evil/criminal/corrupt), OR there is no "
            "significant antagonist, OR the main conflict is purely internal/external without a "
            "specific well-meaning character driving it.\n\n"
            "Use your knowledge of the specific film. Answer True or False only."
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
        f"Lead actor: {m.get('lead_actor')}"
    )


def _parse(message) -> dict:
    text = next(b.text for b in message.content if b.type == "text")
    return json.loads(text)


def label_one(client, m: dict) -> dict:
    resp = client.messages.create(
        model=MODEL,
        max_tokens=64,
        system=SYSTEM,
        output_config=OUTPUT_CONFIG,
        messages=[{"role": "user", "content": _user_text(m)}],
    )
    return _parse(resp)


def dry_run(sample: list[dict]) -> None:
    client = anthropic.Anthropic()
    for m in sample:
        labels = label_one(client, m)
        current = m.get("has_strict_antagonist", "<unset>")
        flag = "  <-- changed" if current != labels["has_strict_antagonist"] else ""
        print(f"{m['title']:45s} ({m['year']})  {str(current):8s} -> {labels['has_strict_antagonist']}{flag}")


def full_run(movies: list[dict]) -> None:
    from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
    from anthropic.types.messages.batch_create_params import Request

    client = anthropic.Anthropic()
    requests = [
        Request(
            custom_id=f"m{i}",
            params=MessageCreateParamsNonStreaming(
                model=MODEL,
                max_tokens=64,
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

    labels_by_idx: dict[int, bool] = {}
    errors = 0
    for result in client.messages.batches.results(batch.id):
        if result.result.type == "succeeded":
            idx = int(result.custom_id[1:])
            try:
                labels_by_idx[idx] = _parse(result.result.message)["has_strict_antagonist"]
            except Exception as e:
                errors += 1
                print(f"  parse error {result.custom_id}: {e}")
        else:
            errors += 1
            print(f"  {result.custom_id}: {result.result.type}")

    labeled = sum(1 for i in range(len(movies)) if i in labels_by_idx)
    print(f"Labeled {labeled}/{len(movies)} (errors: {errors})")

    bak = DATA.with_suffix(".json.strict_antagonist.bak")
    bak.write_text(json.dumps(movies, indent=2, ensure_ascii=False))
    print(f"Backed up → {bak}")

    out = []
    for i, m in enumerate(movies):
        m2 = dict(m)
        if i in labels_by_idx:
            m2["has_strict_antagonist"] = labels_by_idx[i]
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
