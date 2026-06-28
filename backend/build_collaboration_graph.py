#!/usr/bin/env python3
"""Build actor-director collaboration graph from movies.json"""

import json
from pathlib import Path
from collections import defaultdict

# Load movies
with open(Path(__file__).parent / 'data' / 'movies.json', 'r') as f:
    movies = json.load(f)

# Build collaboration indices
actor_director_collabs = defaultdict(lambda: defaultdict(lambda: {'count': 0, 'films': []}))
director_actor_collabs = defaultdict(lambda: defaultdict(lambda: {'count': 0, 'films': []}))

# Track unique actor-director pairs per film to avoid double-counting
processed_pairs = set()

for movie in movies:
    film_id = movie.get('id') or movie.get('cluster_id')
    if not film_id:
        continue
    director = movie.get('director')

    if not director:
        continue

    # Get all actors (from both singular and plural fields, with fallback to alternative names)
    actors = set()
    if movie.get('lead_actor'):
        actors.add(movie['lead_actor'])
    elif movie.get('actor_starring'):  # fallback for alternate naming
        actors.add(movie['actor_starring'])
    if movie.get('lead_actress'):
        actors.add(movie['lead_actress'])
    elif movie.get('actress_starring'):  # fallback for alternate naming
        actors.add(movie['actress_starring'])
    if movie.get('lead_actors'):
        actors.update(movie['lead_actors'])

    # Record each actor-director pair
    for actor in actors:
        if not actor:
            continue

        pair_key = (actor, director, film_id)
        if pair_key not in processed_pairs:
            processed_pairs.add(pair_key)

            actor_director_collabs[actor][director]['count'] += 1
            actor_director_collabs[actor][director]['films'].append(film_id)

            director_actor_collabs[director][actor]['count'] += 1
            director_actor_collabs[director][actor]['films'].append(film_id)

# Convert defaultdicts to regular dicts
collaboration_graph = {
    'actor_director': {
        actor: {
            director: {
                'count': data['count'],
                'films': data['films']
            }
            for director, data in collabs.items()
        }
        for actor, collabs in actor_director_collabs.items()
    },
    'director_actor': {
        director: {
            actor: {
                'count': data['count'],
                'films': data['films']
            }
            for actor, data in collabs.items()
        }
        for director, collabs in director_actor_collabs.items()
    },
    'metadata': {
        'total_movies': len(movies),
        'total_unique_actors': len(actor_director_collabs),
        'total_unique_directors': len(director_actor_collabs),
        'total_unique_collaborations': sum(
            len(collabs) for collabs in actor_director_collabs.values()
        )
    }
}

# Save to file
output_path = Path(__file__).parent / 'data' / 'collaboration_graph.json'
with open(output_path, 'w') as f:
    json.dump(collaboration_graph, f, indent=2)

print(f"✓ Collaboration graph built")
print(f"  Total actors: {collaboration_graph['metadata']['total_unique_actors']}")
print(f"  Total directors: {collaboration_graph['metadata']['total_unique_directors']}")
print(f"  Total unique actor-director pairs: {collaboration_graph['metadata']['total_unique_collaborations']}")
print(f"  Saved to: {output_path}")

# Print top collaborators
print("\nTop 10 most-collaborated director-actor pairs:")
pairs = []
for actor, directors in actor_director_collabs.items():
    for director, data in directors.items():
        if data['count'] > 1:
            pairs.append((actor, director, data['count']))

pairs.sort(key=lambda x: x[2], reverse=True)
for actor, director, count in pairs[:10]:
    print(f"  {actor} × {director}: {count} films")
