#!/usr/bin/env python3
"""
Fetch TMDB IDs for movies.json using TMDB Search API (free, no key required for basic searches).
Adds tmdb_id field to matched movies.
"""

import json
import time
import requests
from pathlib import Path

MOVIES_PATH = Path('backend/data/movies.json')
OUTPUT_PATH = Path('backend/data/movies_with_tmdb.json')
TMDB_SEARCH_URL = 'https://api.themoviedb.org/3/search/movie'

# TMDB API key - you'll need to add this from free signup at themoviedb.org
TMDB_API_KEY = '29ac60742122554fc12f6cef99cd620d'

def load_movies():
    with open(MOVIES_PATH) as f:
        return json.load(f)

def search_tmdb(title, year):
    """Search TMDB for a movie by title and year. Returns tmdb_id or None."""
    if not TMDB_API_KEY:
        return None

    try:
        params = {
            'api_key': TMDB_API_KEY,
            'query': title,
            'year': year,
            'language': 'en',
        }
        resp = requests.get(TMDB_SEARCH_URL, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        if data['results']:
            # Return the first result's ID
            return data['results'][0]['id']
    except Exception as e:
        print(f"Error searching for '{title}' ({year}): {e}")

    return None

def main():
    if not TMDB_API_KEY:
        print("ERROR: Set TMDB_API_KEY in this script first.")
        print("Get a free API key at https://www.themoviedb.org/settings/api")
        return

    movies = load_movies()
    matched = 0
    unmatched = []

    print(f"Processing {len(movies)} movies...")

    for i, movie in enumerate(movies):
        if i % 100 == 0:
            print(f"  {i}/{len(movies)} ({matched} matched so far)")

        if 'tmdb_id' in movie:
            matched += 1
            continue

        tmdb_id = search_tmdb(movie['title'], movie.get('year'))
        if tmdb_id:
            movie['tmdb_id'] = tmdb_id
            matched += 1
        else:
            unmatched.append((movie['title'], movie.get('year'), movie.get('id')))

        time.sleep(0.25)  # Rate limiting: 4 req/sec to avoid throttling

    # Save updated movies
    with open(OUTPUT_PATH, 'w') as f:
        json.dump(movies, f)

    print(f"\n✅ Matched: {matched}/{len(movies)} ({100*matched/len(movies):.1f}%)")
    print(f"📁 Saved to: {OUTPUT_PATH}")

    if unmatched and len(unmatched) <= 20:
        print("\n❌ Unmatched movies:")
        for title, year, mid in unmatched[:20]:
            print(f"  - {title} ({year}) [id: {mid}]")

if __name__ == '__main__':
    main()
