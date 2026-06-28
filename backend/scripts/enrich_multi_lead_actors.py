#!/usr/bin/env python3
"""
Enrich lead_actors field for multi-lead films.
Uses collaboration graph, ensemble tags, and manual mappings to populate lead_actors properly.

Usage:
    python scripts/enrich_multi_lead_actors.py --dry-run
    python scripts/enrich_multi_lead_actors.py --apply
"""

import json
import argparse
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set

DATA_DIR = Path(__file__).parent.parent / "data"
MOVIES_FILE = DATA_DIR / "movies.json"
COLLAB_FILE = DATA_DIR / "collaboration_graph.json"

# Manual mappings for known multi-lead films: (title, year, language) -> [actors]
KNOWN_MULTI_LEADS = {
    ("Seethamma Vakitlo Sirimalle Chettu", 2013, "Telugu"): ["Venkatesh", "Mahesh Babu", "Anjali", "Samantha Ruth Prabhu"],
    ("Dil Chahta Hai", 2001, "Hindi"): ["Aamir Khan", "Saif Ali Khan", "Akshay Khanna"],
    ("3 Idiots", 2009, "Hindi"): ["Aamir Khan", "R. Madhavan", "Sharman Joshi"],
    ("Rang De Basanti", 2006, "Hindi"): ["Aamir Khan", "Siddharth Narayan", "Kunal Kapoor", "Soha Ali Khan"],
    ("Hera Pheri", 2000, "Hindi"): ["Akshay Kumar", "Suniel Shetty", "Paresh Rawal"],
    ("Welcome", 2007, "Hindi"): ["Akshay Kumar", "Anil Kapoor", "Nana Patekar"],
    ("Golmaal Again", 2017, "Hindi"): ["Ajay Devgn", "Parineeti Chopra", "Arshad Warsi", "Tusshar Kapoor"],
    ("Andhadhun", 2018, "Hindi"): ["Ayushmann Khurrana", "Tabu", "Radhika Apte"],
    ("Chak De! India", 2007, "Hindi"): ["Shah Rukh Khan"],  # Single lead, ensemble cast
    ("Jab Tak Hai Jaan", 2012, "Hindi"): ["Shah Rukh Khan", "Katrina Kaif"],
}

def load_data():
    """Load movies and collaboration graph."""
    with open(MOVIES_FILE) as f:
        movies = json.load(f)
    with open(COLLAB_FILE) as f:
        collab_graph = json.load(f)
    return movies, collab_graph

def infer_from_collaboration_graph(movie: dict, collab_graph: dict) -> List[str]:
    """
    Infer additional leads from collaboration graph.
    If a director frequently works with multiple actors, those are likely leads.
    """
    director = movie.get("director")
    if not director:
        return []

    # Get director's actor pool from collaboration graph
    director_data = collab_graph.get("director_to_actors", {}).get(director, {})
    if not director_data:
        return []

    # Find frequent collaborators of this director
    # (actors who appear in 3+ films with this director)
    frequent_actors = [
        actor for actor, count in director_data.items()
        if count >= 3
    ]

    return sorted(frequent_actors)

def normalize_name(name: str) -> str:
    """Normalize actor names for comparison (remove prefixes, standardize)."""
    return name.strip().lower()

def enrich_movie(movie: dict, collab_graph: dict) -> tuple:
    """
    Enrich a single movie's lead_actors field.
    Returns (old_leads, new_leads, enrichment_type, changed).
    """
    title = movie.get("title", "")
    year = movie.get("year")
    language = movie.get("language", "")
    current_leads = movie.get("lead_actors", []) or [movie.get("lead_actor")] if movie.get("lead_actor") else []

    # Check manual mappings first (highest priority)
    key = (title, year, language)
    if key in KNOWN_MULTI_LEADS:
        enriched = KNOWN_MULTI_LEADS[key]
        current_normalized = {normalize_name(n) for n in current_leads if n}
        enriched_normalized = {normalize_name(n) for n in enriched}

        if enriched_normalized != current_normalized:
            return current_leads, enriched, "manual_mapping", True
        return current_leads, current_leads, "unchanged", False

    # If already has multiple leads, keep them
    if len(current_leads) > 1:
        return current_leads, current_leads, "already_multi", False

    # Check if tagged as ensemble or has brotherhood
    is_ensemble = movie.get("is_ensemble_cast", False)
    has_brothers = movie.get("has_brothers_in_arms", False)

    if not (is_ensemble or has_brothers):
        return current_leads, current_leads, "single_lead", False

    # Try to infer from collaboration graph
    inferred = infer_from_collaboration_graph(movie, collab_graph)

    if inferred and len(inferred) > 1:
        # Combine with existing lead(s)
        enriched = list(dict.fromkeys(current_leads + inferred[:3]))  # Max 3 leads, preserve order
        if set(enriched) != set(current_leads):
            return current_leads, enriched, "collaboration_graph", True

    return current_leads, current_leads, "unchanged", False

def main():
    parser = argparse.ArgumentParser(description="Enrich lead_actors for multi-lead films")
    parser.add_argument("--dry-run", action="store_true", help="Show changes without writing")
    parser.add_argument("--apply", action="store_true", help="Apply changes to movies.json")
    args = parser.parse_args()

    if not args.dry_run and not args.apply:
        parser.print_help()
        return

    print("Loading data...")
    movies, collab_graph = load_data()

    enriched_count = 0
    changes_by_type = defaultdict(int)

    print(f"\nEnriching {len(movies)} films...")
    enriched_movies = []

    for i, movie in enumerate(movies):
        old_leads, new_leads, enrichment_type, changed = enrich_movie(movie, collab_graph)

        if changed:
            movie_copy = dict(movie)
            movie_copy["lead_actors"] = new_leads
            enriched_count += 1
            changes_by_type[enrichment_type] += 1

            title = movie.get("title")
            print(f"\n  [{i}] {title} ({movie.get('year')})")
            print(f"      {old_leads} → {new_leads}")

            enriched_movies.append(movie_copy)
        else:
            enriched_movies.append(movie)

    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  Total films enriched: {enriched_count}/{len(movies)}")
    for enrichment_type, count in sorted(changes_by_type.items()):
        print(f"    {enrichment_type}: {count}")

    if args.apply:
        # Backup original
        backup_path = MOVIES_FILE.with_suffix(".json.lead_actors.bak")
        with open(backup_path, 'w') as f:
            json.dump(movies, f, indent=2, ensure_ascii=False)
        print(f"\n✓ Backed up original → {backup_path}")

        # Write enriched
        with open(MOVIES_FILE, 'w') as f:
            json.dump(enriched_movies, f, indent=2, ensure_ascii=False)
        print(f"✓ Wrote enriched movies.json ({enriched_count} films updated)")
        print(f"\nNext step: rebuild collaboration_graph.json")
        print(f"  python backend/build_collaboration_graph.py")

if __name__ == "__main__":
    main()
