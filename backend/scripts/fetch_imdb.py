"""
Builds the Indian movie dataset using:
  1. Wikidata SPARQL  — country_of_origin=India, gives film+language+genre+director+year
  2. IMDB ratings    — joins on IMDB ID for vote counts and ratings
  3. Optional Wikipedia enrichment — true-story / remake / franchise flags

Usage:
    python scripts/fetch_imdb.py --out data/movies.json --min-votes 5000 --limit 500
    python scripts/fetch_imdb.py --out data/movies.json --min-votes 2000 --limit 1000 --enrich-wikipedia
"""

from __future__ import annotations

import argparse
import gzip
import json
import re
import shutil
import time
from pathlib import Path
from typing import Optional

import pandas as pd
import requests

SPARQL_URL = "https://query.wikidata.org/sparql"
IMDB_BASE  = "https://datasets.imdbws.com"
WIKI_API   = "https://en.wikipedia.org/w/api.php"

HEADERS = {"User-Agent": "IndianMovieGenie/1.0 (game dataset builder)"}

LANGUAGE_MAP = {
    "Q11051":  "hindi",
    "Q5885":   "tamil",
    "Q8097":   "telugu",
    "Q36236":  "malayalam",
    "Q33673":  "kannada",
    "Q9610":   "bengali",
    "Q1571":   "marathi",
    "Q58635":  "punjabi",
    "Q33965":  "odia",
    "Q33549":  "gujarati",
    "Q33810":  "assamese",
    "Q36049":  "bhojpuri",
}

GENRE_MAP = {
    "Q188473": "action",
    "Q157394": "comedy",
    "Q130232": "drama",
    "Q1054574":"romance",
    "Q2484376":"crime",
    "Q200092": "horror",
    "Q211723": "thriller",
    "Q622291": "sports",
    "Q52162261":"biography",
    "Q859369": "biography",
    "Q24869":  "musical",
    "Q1341051":"musical",
    "Q471839": "sci-fi",
    "Q157394": "comedy",
    "Q2297927":"historical",
    "Q80930":  "fantasy",
    "Q496523": "family",
}


# ── Wikidata ──────────────────────────────────────────────────────────────

def sparql(query: str, timeout: int = 60) -> list[dict]:
    try:
        r = requests.get(SPARQL_URL, params={"query": query, "format": "json"},
                         headers=HEADERS, timeout=timeout)
        r.raise_for_status()
        return r.json()["results"]["bindings"]
    except Exception as e:
        print(f"    SPARQL error: {e}")
        return []


def fetch_all_wikidata() -> dict[str, dict]:
    """Phase 1: year-by-year lightweight queries → {wikidata_id: {title, imdb_id, year}}."""
    films: dict[str, dict] = {}
    for year in range(2025, 1949, -1):
        q = f"""
SELECT ?film ?filmLabel ?imdbId WHERE {{
  ?film wdt:P31 wd:Q11424 ; wdt:P495 wd:Q668 ; wdt:P577 ?d .
  FILTER(YEAR(?d) = {year})
  OPTIONAL {{ ?film wdt:P345 ?imdbId . }}
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en" . }}
}} LIMIT 500"""
        rows = sparql(q)
        for row in rows:
            wid   = row["film"]["value"].rsplit("/", 1)[-1]
            title = row.get("filmLabel", {}).get("value", "")
            imdb  = row.get("imdbId", {}).get("value", "")
            if title and not title.startswith("Q"):
                films[wid] = {"wikidata_id": wid, "title": title,
                              "imdb_id": imdb, "year": year,
                              "director": "", "language": "", "genres": []}
        if rows:
            print(f"  {year}: {len(rows)} films  (total {len(films)})")
        time.sleep(0.5)
    return films


def enrich_wikidata_details(wids: list[str]) -> dict[str, dict]:
    """Phase 2: batch fetch director/language/genre for qualifying films."""
    details: dict[str, dict] = {}
    batch_size = 80
    for i in range(0, len(wids), batch_size):
        batch = wids[i:i + batch_size]
        values = " ".join(f"wd:{w}" for w in batch)
        q = f"""
SELECT ?film ?directorLabel ?langLabel ?genreLabel WHERE {{
  VALUES ?film {{ {values} }}
  OPTIONAL {{ ?film wdt:P57 ?director . }}
  OPTIONAL {{ ?film wdt:P364 ?lang . }}
  OPTIONAL {{ ?film wdt:P136 ?genre . }}
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en" . }}
}}"""
        rows = sparql(q)
        for row in rows:
            wid = row["film"]["value"].rsplit("/", 1)[-1]
            if wid not in details:
                details[wid] = {"director": "", "language": "", "genres": set()}
            d = details[wid]
            director  = row.get("directorLabel",  {}).get("value", "")
            lang      = row.get("langLabel",      {}).get("value", "")
            genre_raw = row.get("genreLabel",     {}).get("value", "")
            if director and not d["director"]:
                d["director"] = director
            if lang and not d["language"]:
                lang_lower = lang.lower()
                for key in LANGUAGE_MAP.values():
                    if key in lang_lower:
                        d["language"] = key
                        break
            if genre_raw:
                genre_lower = genre_raw.lower()
                for mapped in ("action","comedy","drama","romance","crime","horror",
                               "thriller","sports","biography","musical","sci-fi",
                               "fantasy","historical","family"):
                    if mapped in genre_lower:
                        d["genres"].add(mapped)
        time.sleep(0.3)
        print(f"  Detail batch {i//batch_size+1}/{(len(wids)-1)//batch_size+1} done")
    for d in details.values():
        d["genres"] = sorted(d["genres"])
    return details


# ── IMDB ratings ──────────────────────────────────────────────────────────

def download_tsv(name: str, dest: Path) -> Path:
    url      = f"{IMDB_BASE}/{name}.tsv.gz"
    gz_path  = dest / f"{name}.tsv.gz"
    tsv_path = dest / f"{name}.tsv"
    if tsv_path.exists():
        print(f"  [cached] {name}.tsv")
        return tsv_path
    print(f"  Downloading {url} …")
    with requests.get(url, stream=True, timeout=300, headers=HEADERS) as r:
        r.raise_for_status()
        total = int(r.headers.get("content-length", 0))
        done  = 0
        with open(gz_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=1 << 20):
                f.write(chunk)
                done += len(chunk)
                if total:
                    print(f"\r    {done/1e6:.0f} / {total/1e6:.0f} MB", end="", flush=True)
    print()
    with gzip.open(gz_path, "rb") as fi, open(tsv_path, "wb") as fo:
        shutil.copyfileobj(fi, fo)
    gz_path.unlink()
    return tsv_path


def load_imdb_ratings(cache_dir: Path, imdb_ids: set[str], min_votes: int) -> dict[str, dict]:
    path = download_tsv("title.ratings", cache_dir)
    df   = pd.read_csv(path, sep="\t", na_values="\\N")
    df   = df[df["tconst"].isin(imdb_ids) & (df["numVotes"] >= min_votes)]
    return {
        row["tconst"]: {"imdb_rating": round(float(row["averageRating"]), 1),
                        "num_votes":   int(row["numVotes"])}
        for _, row in df.iterrows()
    }


# ── attribute inference ───────────────────────────────────────────────────

def era_from_year(year: int) -> str:
    if year < 1990: return "classic"
    if year < 2000: return "90s"
    if year < 2010: return "2000s"
    if year < 2020: return "2010s"
    return "2020s"


def infer_attributes(genres: list[str], num_votes: int) -> dict:
    g = set(genres)
    return {
        "has_action":            "action" in g,
        "has_comedy":            "comedy" in g,
        "has_romance":           "romance" in g,
        "has_thriller_elements": any(x in g for x in ("thriller", "crime", "mystery")),
        "has_songs":             True,
        "is_biographical":       "biography" in g,
        "is_sports_film":        "sports" in g,
        "is_sci_fi":             any(x in g for x in ("sci-fi", "fantasy")),
        "is_horror":             "horror" in g,
        "is_historical":         any(x in g for x in ("historical", "history", "period")),
        "is_family_film":        "family" in g,
        "is_pan_india_blockbuster": num_votes > 200_000,
        # Manual / enrichment fields
        "lead_gender":           "male",
        "has_villain":           True,
        "has_social_message":    False,
        "is_based_on_true_story": False,
        "is_remake":             False,
        "is_franchise":          False,
    }


# ── Wikipedia enrichment ──────────────────────────────────────────────────

def fetch_wikipedia_attrs(title: str, year: int) -> dict:
    params = {
        "action": "query", "format": "json",
        "list": "search",
        "srsearch": f"{title} {year} Indian film",
        "srlimit": 1,
    }
    try:
        r = requests.get(WIKI_API, params=params, headers=HEADERS, timeout=10)
        results = r.json().get("query", {}).get("search", [])
        if not results:
            return {}
        snippet = re.sub(r"<[^>]+>", "", results[0].get("snippet", "")).lower()
        out: dict = {}
        if any(w in snippet for w in ("true story", "based on", "real events", "autobiography")):
            out["is_based_on_true_story"] = True
        if any(w in snippet for w in ("remake", "adapted from", "adaptation of")):
            out["is_remake"] = True
        if any(w in snippet for w in ("sequel", "franchise", "part 2", "chapter 2", "series")):
            out["is_franchise"] = True
        if any(w in snippet for w in ("female lead", "woman", "actress stars", "she leads")):
            out["lead_gender"] = "female"
        if any(w in snippet for w in ("social", "awareness", "message", "inequality", "justice", "caste")):
            out["has_social_message"] = True
        return out
    except Exception:
        return {}


# ── merge ────────────────────────────────────────────────────────────────

def merge_with_existing(new_records: list[dict], out_path: Path) -> list[dict]:
    if not out_path.exists():
        return new_records
    existing     = json.loads(out_path.read_text())
    existing_ids = {m["id"] for m in existing}
    added = [m for m in new_records if m["id"] not in existing_ids]
    print(f"  Existing: {len(existing)}  |  New: {len(added)}")
    return existing + added


# ── main ──────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out",              default="data/movies.json")
    parser.add_argument("--cache-dir",        default=".imdb_cache")
    parser.add_argument("--min-votes",        type=int, default=5000)
    parser.add_argument("--limit",            type=int, default=500)
    parser.add_argument("--enrich-wikipedia", action="store_true")
    args = parser.parse_args()

    cache_dir = Path(args.cache_dir)
    cache_dir.mkdir(exist_ok=True)
    out_path  = Path(args.out)
    out_path.parent.mkdir(exist_ok=True)

    # ── 1. Phase 1: year-by-year film list ───────────────────────────────
    print("=== Step 1: Wikidata year-by-year scan ===")
    wikidata_films = fetch_all_wikidata()
    print(f"Total Indian films found: {len(wikidata_films)}")

    with_imdb = {
        wid: f for wid, f in wikidata_films.items()
        if f["imdb_id"].startswith("tt")
    }
    print(f"With IMDB IDs: {len(with_imdb)}")

    # ── 2. Filter by IMDB ratings ────────────────────────────────────────
    print(f"\n=== Step 2: IMDB ratings (min_votes={args.min_votes}) ===")
    imdb_id_set = {f["imdb_id"] for f in with_imdb.values()}
    ratings     = load_imdb_ratings(cache_dir, imdb_id_set, args.min_votes)
    print(f"Films passing vote threshold: {len(ratings)}")

    # Sort by votes descending, cap at limit
    qualified = sorted(
        [(wid, f) for wid, f in with_imdb.items() if f["imdb_id"] in ratings],
        key=lambda x: ratings[x[1]["imdb_id"]]["num_votes"],
        reverse=True,
    )[:args.limit]
    print(f"Taking top {len(qualified)} by vote count")

    # ── 3. Phase 2: enrich with director/language/genre ──────────────────
    print(f"\n=== Step 3: Wikidata detail enrichment ===")
    qualifying_wids = [wid for wid, _ in qualified]
    details = enrich_wikidata_details(qualifying_wids)

    # ── 4. Build records ──────────────────────────────────────────────────
    print(f"\n=== Step 4: Building records ===")
    records = []
    for i, (wid, film) in enumerate(qualified):
        rating_info = ratings[film["imdb_id"]]
        d = details.get(wid, {})
        genres   = d.get("genres", [])
        attrs    = infer_attributes(genres, rating_info["num_votes"])
        language = d.get("language") or film.get("language") or "hindi"
        director = d.get("director") or film.get("director") or ""

        record: dict = {
            "id":          film["imdb_id"],
            "title":       film["title"],
            "year":        film["year"],
            "language":    language,
            "era":         era_from_year(film["year"]),
            "genres":      genres,
            "director":    director,
            "lead_actor":  "",
            "imdb_rating": rating_info["imdb_rating"],
            **attrs,
        }

        if args.enrich_wikipedia:
            updates = fetch_wikipedia_attrs(film["title"], film["year"])
            record.update(updates)
            time.sleep(0.25)

        records.append(record)
        if (i + 1) % 100 == 0:
            print(f"  … {i+1} done")

    # ── 4. Merge and save ─────────────────────────────────────────────────
    print(f"\n=== Step 4: Merging with existing ===")
    merged = merge_with_existing(records, out_path)
    out_path.write_text(json.dumps(merged, indent=2, ensure_ascii=False))
    print(f"\nSaved {len(merged)} total movies → {out_path}")

    # Summary
    from collections import Counter
    imdb_new = [m for m in merged if m["id"].startswith("tt")]
    langs    = Counter(m["language"] for m in imdb_new)
    print("Language breakdown:", dict(sorted(langs.items(), key=lambda x: -x[1])))


if __name__ == "__main__":
    main()
