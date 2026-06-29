#!/usr/bin/env python3
"""
Intelligent cluster extension for unclustered films.

Uses existing cluster taxonomy to assign remaining 1,361 films to clusters
based on genre, lead actor, era, and thematic markers.
"""

import json
from pathlib import Path
from collections import defaultdict
from typing import Optional, List, Dict, Any, Tuple

# Load reference data
MOVIES_PATH = Path(__file__).parent / "movies.json"
CLUSTERS_PATH = Path(__file__).parent / "all_clusters_consolidated.json"

def load_data():
    """Load movies and cluster reference data."""
    with open(MOVIES_PATH) as f:
        movies = json.load(f)
    with open(CLUSTERS_PATH) as f:
        all_clusters = json.load(f)
    return movies, all_clusters

def build_cluster_reference(clusters: List[Dict]) -> Dict[str, Dict]:
    """Build lookup of cluster definitions with examples and characteristics."""
    reference = defaultdict(lambda: {
        "name": None, "diff_key": None, "examples": [],
        "language": None, "genres": defaultdict(int), "actors": defaultdict(int)
    })

    for c in clusters:
        cid = c.get("cluster_id")
        if cid:
            meta = reference[cid]
            if not meta["name"]:
                meta["name"] = c.get("cluster_name")
                meta["language"] = c.get("language")
                meta["diff_key"] = c.get("cluster_differentiation_key")

            meta["examples"].append(c.get("title"))

            # Collect genre/actor patterns (would need additional data)

    return dict(reference)

def get_cluster_candidates_by_language_genre(
    cluster_ref: Dict[str, Dict],
    language: str,
    primary_genre: str
) -> List[Tuple[str, float]]:
    """
    Find clusters matching language and genre.
    Returns list of (cluster_id, match_score).
    """
    candidates = []

    for cid, meta in cluster_ref.items():
        # Match language
        if meta.get("language") != language:
            continue

        # Score by genre hint in cluster name
        name_lower = (meta.get("name", "") or "").lower()
        diff_key_lower = (meta.get("diff_key", "") or "").lower()

        score = 0.5  # Base score for language match

        # Boost for genre matches in name/diff_key
        if primary_genre.lower() in name_lower or primary_genre.lower() in diff_key_lower:
            score += 0.3

        # Exact genre matches
        genre_keywords = {
            "action": ["action", "heist", "cop", "military", "patriotic", "vigilante"],
            "drama": ["drama", "family", "emotional", "character", "institutional"],
            "romance": ["romance", "love", "melodrama", "obsessive", "relationship"],
            "comedy": ["comedy", "masala", "slapstick", "deception"],
            "thriller": ["thriller", "suspense", "crime", "mystery"],
            "historical": ["historical", "period", "epic", "war"],
            "biopic": ["biopic", "life", "story", "true story"],
        }

        if primary_genre.lower() in genre_keywords:
            for keyword in genre_keywords[primary_genre.lower()]:
                if keyword in name_lower or keyword in diff_key_lower:
                    score += 0.1
                    break

        if score > 0:
            candidates.append((cid, min(score, 1.0)))

    return sorted(candidates, key=lambda x: x[1], reverse=True)

def extend_clusters(
    movies: List[Dict],
    cluster_ref: Dict[str, Dict],
    confidence_threshold: float = 0.75
) -> Tuple[List[Dict], List[Dict], List[Dict]]:
    """
    Extend cluster coverage:
    1. Auto-assign high-confidence matches (>threshold)
    2. Group uncertain films for user review
    3. Handle language/decade priorities

    Returns: (auto_assigned, review_candidates, unchanged)
    """
    auto_assigned = []
    review_candidates = []
    unchanged = []

    # Priority: Hindi 90s-2010s, Tamil/Telugu 2010s+, then others
    def get_priority(m):
        year = m.get("year", 0)
        lang = m.get("language", "unknown")
        if lang == "Hindi" and 1990 <= year <= 2019:
            return 0
        elif lang in ["Tamil", "Telugu"] and 2010 <= year <= 2019:
            return 1
        elif lang in ["Tamil", "Telugu"] and 1990 <= year <= 2009:
            return 2
        elif lang in ["Hindi", "Tamil", "Telugu"] and 1990 <= year:
            return 3
        else:
            return 999

    unclustered = [m for m in movies if not m.get("cluster_id")]
    unclustered.sort(key=get_priority)

    for movie in unclustered:
        lang = movie.get("language", "unknown")
        genre = movie.get("primary_genre", "other").lower()

        # Skip languages without cluster taxonomy
        if lang not in ["Hindi", "Tamil", "Telugu"]:
            unchanged.append(movie)
            continue

        # Find matching clusters
        candidates = get_cluster_candidates_by_language_genre(
            cluster_ref, lang, genre
        )

        if not candidates:
            review_candidates.append({
                "movie": movie,
                "reason": f"No matching clusters found for {lang} {genre}"
            })
            continue

        best_cluster_id, score = candidates[0]

        if score >= confidence_threshold:
            # Auto-assign high-confidence matches
            movie["cluster_id"] = best_cluster_id
            movie["cluster_name"] = cluster_ref[best_cluster_id]["name"]
            movie["cluster_differentiation_key"] = cluster_ref[best_cluster_id]["diff_key"]
            auto_assigned.append(movie)
        else:
            # Flag uncertain films for review
            review_candidates.append({
                "movie": movie,
                "suggestions": [
                    {
                        "cluster_id": cid,
                        "cluster_name": cluster_ref[cid]["name"],
                        "score": score,
                        "examples": cluster_ref[cid]["examples"][:2]
                    }
                    for cid, score in candidates[:3]
                ]
            })

    return auto_assigned, review_candidates, unchanged

def main():
    print("=== CLUSTER EXTENSION ===\n")

    movies, all_clusters = load_data()
    cluster_ref = build_cluster_reference(all_clusters)

    print(f"Loaded {len(movies)} films")
    print(f"Cluster reference: {len(cluster_ref)} clusters")

    unclustered_before = sum(1 for m in movies if not m.get("cluster_id"))
    print(f"Unclustered films: {unclustered_before}\n")

    # Extend
    auto_assigned, review_candidates, unchanged = extend_clusters(
        movies, cluster_ref, confidence_threshold=0.75
    )

    print(f"Results:")
    print(f"  Auto-assigned (>75% confidence): {len(auto_assigned)}")
    print(f"  Review needed: {len(review_candidates)}")
    print(f"  Skipped (no taxonomy): {len(unchanged)}")
    print(f"  Total coverage now: {unclustered_before - len(review_candidates) - len(unchanged)}")

    # Show samples
    if auto_assigned:
        print(f"\nSample auto-assignments:")
        for m in auto_assigned[:3]:
            print(f"  • {m['title']} ({m['year']}) → {m['cluster_id']}")

    if review_candidates:
        print(f"\nSample review candidates:")
        for item in review_candidates[:3]:
            m = item["movie"]
            sug = item.get("suggestions", [{}])[0]
            if "reason" in item:
                print(f"  • {m['title']} ({m['year']}) - {item['reason']}")
            else:
                print(f"  • {m['title']} ({m['year']})")
                if sug:
                    print(f"    → Suggest: {sug.get('cluster_name')} ({sug.get('score'):.2f})")

    # Save results
    clustered = [m for m in movies if m.get("cluster_id")]
    clustered.extend(auto_assigned)

    with open(MOVIES_PATH, 'w') as f:
        json.dump(movies, f, indent=2)

    print(f"\n✓ Updated movies.json")
    print(f"  Final coverage: {len(clustered)}/{len(movies)} ({100*len(clustered)/len(movies):.1f}%)")

    # Save review list for user
    review_path = Path(__file__).parent / "cluster_extension_review.json"
    with open(review_path, 'w') as f:
        json.dump(review_candidates, f, indent=2)
    print(f"✓ Saved review candidates to cluster_extension_review.json ({len(review_candidates)} films)")

if __name__ == "__main__":
    main()
