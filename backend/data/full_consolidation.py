#!/usr/bin/env python3
"""
Complete consolidation: merge all cluster data into movies.json
and generate discrimination questions for all clusters.
"""

import json
from pathlib import Path
from collections import defaultdict
from typing import List, Dict, Any

def load_cluster_json(file_path: str) -> List[Dict]:
    """Load cluster JSON from file."""
    try:
        with open(file_path) as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: Could not load {file_path}: {e}")
        return []

def merge_clusters_into_movies(movies: List[Dict], clusters: List[Dict]) -> int:
    """
    Merge cluster data into movies.json.
    Returns count of matched films.
    """
    # Create (title, year, language) -> movie lookup
    movie_lookup = {}
    for m in movies:
        key = (m.get("title", "").strip().lower(), m.get("year"), m.get("language", "").strip().lower())
        movie_lookup[key] = m

    matched = 0
    for cluster in clusters:
        key = (
            cluster.get("title", "").strip().lower(),
            cluster.get("year"),
            cluster.get("language", "").strip().lower()
        )
        if key in movie_lookup:
            movie = movie_lookup[key]
            movie["cluster_id"] = cluster.get("cluster_id")
            movie["cluster_name"] = cluster.get("cluster_name")
            movie["cluster_differentiation_key"] = cluster.get("cluster_differentiation_key")
            if "tags" in cluster:
                movie["cluster_tags"] = cluster["tags"]
            matched += 1

    return matched

def generate_discrimination_questions(movies: List[Dict]) -> List[Dict]:
    """
    Generate 2-3 discrimination questions per cluster based on
    cluster differentiation keys and film attributes.
    """
    # Group by cluster
    clusters_map = defaultdict(lambda: {
        "name": None,
        "diff_key": None,
        "films": []
    })

    for movie in movies:
        if "cluster_id" in movie:
            cluster_id = movie["cluster_id"]
            clusters_map[cluster_id]["name"] = movie.get("cluster_name")
            clusters_map[cluster_id]["diff_key"] = movie.get("cluster_differentiation_key")
            clusters_map[cluster_id]["films"].append(movie)

    questions = []
    question_id = 1

    for cluster_id, cluster_data in sorted(clusters_map.items()):
        if not cluster_data["films"]:
            continue

        cluster_name = cluster_data["name"] or cluster_id
        diff_key = cluster_data["diff_key"] or ""
        films = cluster_data["films"]

        # Q1: Identify cluster by narrative/thematic marker
        if diff_key:
            questions.append({
                "question_id": f"DISC_{question_id:04d}",
                "question_type": "cluster_identification",
                "cluster_id": cluster_id,
                "cluster_name": cluster_name,
                "question": f"Which cluster is characterized by: {diff_key}",
                "difficulty": "medium",
                "example_films": [f["title"] for f in films[:3]]
            })
            question_id += 1

        # Q2: Attribute-based discrimination
        if len(films) >= 2:
            sample = films[0]
            attrs = []
            if sample.get("cluster_tags", {}).get("has_action_scenes") == "yes":
                attrs.append("explicit action sequences")
            if sample.get("cluster_tags", {}).get("has_villain") == "yes":
                attrs.append("antagonistic villain force")
            if attrs:
                questions.append({
                    "question_id": f"DISC_{question_id:04d}",
                    "question_type": "attribute_discrimination",
                    "cluster_id": cluster_id,
                    "cluster_name": cluster_name,
                    "question": f"Films in {cluster_name} typically feature: {', '.join(attrs)}",
                    "difficulty": "easy",
                    "example_films": [f["title"] for f in films[:2]]
                })
                question_id += 1

        # Q3: Comparative vs adjacent clusters (will be populated post-consolidation)
        if len(cluster_name) > 0:
            questions.append({
                "question_id": f"DISC_{question_id:04d}",
                "question_type": "cluster_discrimination",
                "cluster_id": cluster_id,
                "cluster_name": cluster_name,
                "question": f"Distinguish {cluster_name} from other action clusters by: {diff_key[:80]}...",
                "difficulty": "hard",
                "example_films": [f["title"] for f in films[:3]]
            })
            question_id += 1

    return questions

def main():
    data_dir = Path("/Users/sandeep.srinivasan/sand-ship/indian-movie-genie/backend/data")
    movies_path = data_dir / "movies.json"

    # Load existing movies
    print("Loading movies.json...")
    with open(movies_path) as f:
        movies = json.load(f)
    print(f"Loaded {len(movies)} films")

    # Load all cluster data
    print("\nLoading cluster data...")
    all_clusters = []

    # Hindi clusters (will be populated by agent)
    hindi_90s_path = data_dir / "hindi_clusters_90s.json"
    hindi_2000s_path = data_dir / "hindi_clusters_2000s.json"
    hindi_2010s_path = data_dir / "hindi_clusters_2010s.json"

    # Telugu/Tamil clusters (from /tmp)
    telugu_tamil_files = [
        "/tmp/telugu_action_90s.json",
        "/tmp/telugu_action_2000s.json",
        "/tmp/telugu_action_2010s.json",
        "/tmp/telugu_romance.json",
        "/tmp/telugu_comedy.json",
        "/tmp/tamil_action_90s.json",
        "/tmp/tamil_action_2000s.json",
        "/tmp/tamil_action_2010s.json",
        "/tmp/tamil_romance.json",
        "/tmp/tamil_comedy.json",
    ]

    # Try to load Hindi cluster files (will exist after agent extraction)
    for path in [hindi_90s_path, hindi_2000s_path, hindi_2010s_path]:
        clusters = load_cluster_json(str(path))
        all_clusters.extend(clusters)
        if clusters:
            print(f"  ✓ Loaded {len(clusters)} from {path.name}")

    # Try to load Telugu/Tamil files
    for path in telugu_tamil_files:
        clusters = load_cluster_json(path)
        all_clusters.extend(clusters)
        if clusters:
            print(f"  ✓ Loaded {len(clusters)} from {Path(path).name}")

    print(f"\nTotal cluster records loaded: {len(all_clusters)}")

    # Merge clusters into movies
    print("\nMerging cluster metadata into movies...")
    matched = merge_clusters_into_movies(movies, all_clusters)
    print(f"  ✓ Matched {matched} films with cluster data")

    # Save updated movies.json
    output_path = data_dir / "movies.json"
    with open(output_path, 'w') as f:
        json.dump(movies, f, indent=2)
    print(f"  ✓ Saved {len(movies)} films to movies.json")

    # Generate discrimination questions
    print("\nGenerating discrimination questions...")
    questions = generate_discrimination_questions(movies)
    print(f"  ✓ Generated {len(questions)} discrimination questions")

    # Save questions
    questions_path = data_dir / "discrimination_questions.json"
    with open(questions_path, 'w') as f:
        json.dump(questions, f, indent=2)
    print(f"  ✓ Saved to discrimination_questions.json")

    # Summary
    clustered = sum(1 for m in movies if "cluster_id" in m)
    print(f"\n=== Summary ===")
    print(f"Total films in movies.json: {len(movies)}")
    print(f"Films with cluster metadata: {clustered}")
    print(f"Discrimination questions: {len(questions)}")

if __name__ == "__main__":
    main()
