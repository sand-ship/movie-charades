#!/usr/bin/env python3
"""
Extract cluster_differentiation_key patterns and add as specific attributes to movies.json
Maps thematic/plot archetypes to queryable attributes for better discrimination.
"""

import json
from pathlib import Path

MOVIES_PATH = Path('backend/data/movies.json')

# Mapping: keyword patterns → attribute name
DIFFERENTIATOR_PATTERNS = {
    'romantic_fugitive': [
        'eloping romantic couple',
        'romantic couple fleeing',
        'class divide romantic',
    ],
    'lookalike_twin_deception': [
        'lookalike deceptions',
        'identical twins',
        'multi-role frameworks',
        'identical lookalikes',
    ],
    'cop_protagonist': [
        'operates within official law enforcement',
        'law enforcement system',
        'police procedural',
        'cop identity',
    ],
    'frontier_elements': [
        'horse-chase mechanics',
        'bounty hunts',
        'cowboy',
        'frontier',
        'western action',
    ],
    'neighborhood_brotherhood': [
        'neighborhood camaraderie',
        'street justice',
        'brotherhood',
        'family assassination setups',
    ],
    'vigilante_justice': [
        'rogue persona',
        'single-handedly dismantle',
        'stepping outside',
        'systemic cleanse',
    ],
    'faction_feud': [
        'multi-generational blood feuds',
        'land oppression',
        'regional power struggles',
        'rayalaseema revenge',
    ],
    'counter_terrorism': [
        'military units',
        'state intelligence',
        'cross-border infiltration',
        'security networks',
    ],
    'divine_intervention': [
        'divine intervention',
        'magical artifacts',
        'celestial entities',
        'yamaloka',
        'mythological',
    ],
    'fan_service_masala': [
        'fan-service packaging',
        'signature punchlines',
        'mass hero blockbuster',
    ],
}

def extract_differentiators(text):
    """Return list of matched differentiator attributes for a text."""
    if not text:
        return []

    text_lower = text.lower()
    matched = []

    for attr, patterns in DIFFERENTIATOR_PATTERNS.items():
        for pattern in patterns:
            if pattern.lower() in text_lower:
                matched.append(attr)
                break  # Only match once per attribute

    return matched

def main():
    with open(MOVIES_PATH) as f:
        movies = json.load(f)

    print(f"Processing {len(movies)} movies...")

    updated = 0
    for movie in movies:
        # Check cluster_differentiation_key
        diff_key = movie.get('cluster_differentiation_key', '')

        # Check genre for additional clues
        genre = movie.get('genre', '')

        # Combined text to search
        search_text = f"{diff_key} {genre}"

        # Extract differentiators
        attrs = extract_differentiators(search_text)

        if attrs:
            for attr in attrs:
                movie[f'has_{attr}'] = True
            updated += 1

    # Save updated
    with open(MOVIES_PATH, 'w') as f:
        json.dump(movies, f)

    print(f"✅ Updated {updated} movies with differentiator attributes")

    # Show examples
    print("\nExample: Kodama Simham")
    kodama = next((m for m in movies if m.get('title') == 'Kodama Simham'), None)
    if kodama:
        for k, v in kodama.items():
            if k.startswith('has_') and v:
                print(f"  {k}: {v}")

if __name__ == '__main__':
    main()
