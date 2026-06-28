#!/usr/bin/env python3
"""Build narrative cluster membership index from existing cluster_id/cluster_name fields.
Maps films to their narrative archetypes for stumper discrimination."""

import json
from pathlib import Path
from collections import defaultdict, Counter

# Load movies
with open(Path(__file__).parent / 'data' / 'movies.json', 'r') as f:
    movies = json.load(f)

# Extract narrative archetypes from cluster names
# Cluster names like "HI_10_ACT_06: Mass Action Hero/Comedy" contain the archetype info
narrative_archetypes = defaultdict(list)  # archetype_id -> [film_ids]
cluster_metadata = {}  # archetype_id -> {name, count, sample_films}

# Pattern-based archetype extraction from cluster names
def extract_archetype_from_cluster(cluster_name: str) -> str:
    """Extract core narrative archetype from cluster name.
    E.g., 'Mass Action Hero/Comedy' → 'mass_action_hero_comedy'"""
    if not cluster_name:
        return "unknown"
    # Take the descriptive part after the colon
    if ':' in cluster_name:
        desc = cluster_name.split(':', 1)[1].strip()
    else:
        desc = cluster_name
    # Normalize to archetype ID
    archetype_id = desc.lower().replace(' / ', '_').replace(' ', '_').replace('-', '_')
    return archetype_id

# Map films to archetypes
film_to_archetypes = {}  # film_id -> list of archetype_ids

for movie in movies:
    film_id = movie.get('id') or movie.get('cluster_id')
    if not film_id:
        continue

    archetypes = []

    # Extract from explicit cluster_id/cluster_name
    if movie.get('cluster_id') and movie.get('cluster_name'):
        archetype = extract_archetype_from_cluster(movie['cluster_name'])
        archetypes.append(archetype)
        narrative_archetypes[archetype].append(film_id)

    # Also extract from primary genre and era (creates meta-archetypes)
    primary_genre = movie.get('primary_genre', 'unknown').lower()
    era = movie.get('era', '').lower()

    if primary_genre != 'unknown':
        # Genre-era archetype: e.g., 'action_2000s', 'romance_classic'
        if era:
            meta_archetype = f"{primary_genre}_{era}"
            archetypes.append(meta_archetype)
            narrative_archetypes[meta_archetype].append(film_id)
        else:
            narrative_archetypes[primary_genre].append(film_id)
            archetypes.append(primary_genre)

    film_to_archetypes[film_id] = archetypes

# Build metadata for each archetype
for archetype_id, film_ids in narrative_archetypes.items():
    cluster_metadata[archetype_id] = {
        'film_count': len(film_ids),
        'films': film_ids[:10],  # Sample of first 10 films
        'is_explicit_cluster': any(
            extract_archetype_from_cluster(m.get('cluster_name', '')) == archetype_id
            for m in movies if m.get('id') in film_ids or m.get('cluster_id') in film_ids
        )
    }

# Save indices
narrative_index = {
    'archetype_to_films': {k: v for k, v in narrative_archetypes.items() if len(v) > 0},
    'film_to_archetypes': film_to_archetypes,
    'archetype_metadata': cluster_metadata,
    'statistics': {
        'total_films': len(film_to_archetypes),
        'total_archetypes': len(narrative_archetypes),
        'explicit_clusters': sum(1 for m in cluster_metadata.values() if m.get('is_explicit_cluster')),
    }
}

output_path = Path(__file__).parent / 'data' / 'narrative_clusters.json'
with open(output_path, 'w') as f:
    json.dump(narrative_index, f, indent=2)

print(f"✓ Narrative cluster index built")
print(f"  Total films indexed: {narrative_index['statistics']['total_films']}")
print(f"  Total archetypes: {narrative_index['statistics']['total_archetypes']}")
print(f"  Explicit narrative clusters: {narrative_index['statistics']['explicit_clusters']}")
print(f"  Saved to: {output_path}")

# Print top archetypes
print("\nTop 15 narrative archetypes:")
sorted_archetypes = sorted(narrative_archetypes.items(), key=lambda x: len(x[1]), reverse=True)
for archetype_id, film_ids in sorted_archetypes[:15]:
    is_explicit = cluster_metadata[archetype_id]['is_explicit_cluster']
    marker = "●" if is_explicit else "○"
    print(f"  {marker} {archetype_id}: {len(film_ids)} films")
