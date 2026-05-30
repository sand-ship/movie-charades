"""Merge subagent-produced label slices into movies.json.

Reads /tmp/relabel/out/slice_*.json (each a JSON array of {id, ...labels}),
applies them to data/movies.json keyed by `id`, and reports coverage. Identity
/ factual fields are preserved; `era` is derived from `year`.

    python scripts/merge_labels.py            # report coverage only (no write)
    python scripts/merge_labels.py --write    # back up + write movies.json
"""
from __future__ import annotations
import argparse, glob, json, sys
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data" / "movies.json"
OUT = Path("/tmp/relabel/out")

GENRE_VOCAB = {"action","comedy","romance","drama","family","thriller","crime",
    "mystery","historical","horror","sports","biopic","sci-fi","fantasy",
    "musical","war","adventure"}
PRIMARY_VOCAB = {"action","comedy","romance","drama","thriller","historical",
    "horror","sports","biopic"}
BOOL_FIELDS = ["has_action","has_comedy","has_romance","has_villain","has_songs",
    "has_thriller_elements","has_social_message","has_love_triangle",
    "has_revenge_plot","has_forbidden_love","is_anti_hero","is_set_abroad",
    "is_family_film","is_based_on_true_story","is_biographical","is_franchise",
    "is_remake","is_sports_film","is_historical","is_horror","is_sci_fi",
    "is_pan_india_blockbuster"]


def _era(year):
    try: y = int(year)
    except (TypeError, ValueError): return "2010s"
    return ("classic" if y < 1990 else "90s" if y < 2000 else "2000s"
            if y < 2010 else "2010s" if y < 2020 else "2020s")


def load_labels() -> dict:
    labels = {}
    bad = 0
    for f in sorted(glob.glob(str(OUT / "slice_*.json"))):
        try:
            arr = json.loads(Path(f).read_text())
        except Exception as e:  # noqa: BLE001
            print(f"  skip {Path(f).name}: invalid JSON ({e})"); continue
        for rec in arr:
            rid = rec.get("id")
            if not rid:
                bad += 1; continue
            # validate / sanitize
            genres = [g for g in (rec.get("genres") or []) if g in GENRE_VOCAB]
            pg = rec.get("primary_genre")
            if pg not in PRIMARY_VOCAB:
                pg = (genres[0] if genres else "drama")
            lg = rec.get("lead_gender") if rec.get("lead_gender") in ("male","female") else "male"
            clean = {"genres": genres or ["drama"], "primary_genre": pg, "lead_gender": lg}
            for b in BOOL_FIELDS:
                clean[b] = bool(rec.get(b, False))
            labels[rid] = clean
    if bad: print(f"  {bad} records had no id (skipped)")
    return labels


def apply(m: dict, lab: dict) -> dict:
    out = dict(m)
    out["genres"] = lab["genres"]
    out["primary_genre"] = lab["primary_genre"]
    out["lead_gender"] = lab["lead_gender"]
    for b in BOOL_FIELDS:
        out[b] = lab[b]
    out["era"] = _era(m.get("year"))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    movies = json.loads(DATA.read_text())
    labels = load_labels()
    have = [m for m in movies if m.get("id") in labels]
    missing = [m for m in movies if m.get("id") not in labels]
    print(f"movies={len(movies)}  labeled={len(have)}  missing={len(missing)}")
    if missing:
        print("  missing ids (first 15):", [m.get("id") for m in missing[:15]])

    if not args.write:
        print("\n(dry run — pass --write to apply)")
        return
    if missing:
        print(f"\nREFUSING to write: {len(missing)} films unlabeled. "
              "Re-run the missing slices first.", file=sys.stderr)
        sys.exit(1)

    bak = DATA.with_suffix(".json.prelabel.bak")
    bak.write_text(json.dumps(movies, indent=2, ensure_ascii=False))
    out = [apply(m, labels[m["id"]]) for m in movies]
    DATA.write_text(json.dumps(out, indent=2, ensure_ascii=False))
    print(f"backed up -> {bak}\nwrote {DATA} ({len(out)} movies). Restart the backend.")


if __name__ == "__main__":
    main()
