#!/usr/bin/env python3
"""
Production Database Cleanup & Validation Script
Validates and cleans up backend/data/movies.json for production readiness
"""

import json
import sys
from collections import defaultdict, Counter
from pathlib import Path

def load_db():
    """Load the production database"""
    path = Path('backend/data/movies.json')
    with open(path, 'r') as f:
        return json.load(f)

def validate_and_clean(movies):
    """Validate and clean the database"""
    issues = {
        'empty_strings': [],
        'null_values': [],
        'missing_fields': [],
        'invalid_ratings': [],
        'duplicate_titles': [],
        'missing_actors': [],
        'invalid_languages': [],
        'fixed_issues': []
    }

    seen_titles = {}
    valid_languages = {'Hindi', 'Tamil', 'Telugu', 'Kannada', 'Malayalam'}

    cleaned_movies = []

    for i, film in enumerate(movies):
        title = film.get('title', '')

        # Check for duplicates
        if title in seen_titles:
            issues['duplicate_titles'].append({
                'title': title,
                'index': i,
                'previous_index': seen_titles[title]
            })
            continue
        seen_titles[title] = i

        # Clean empty strings
        for key in ['title', 'director', 'language']:
            if key in film and film[key] == '':
                issues['empty_strings'].append(f"Film {i}: {key} is empty string")
                film[key] = None

        # Validate required fields
        required = ['title', 'year', 'language', 'imdb_rating']
        for field in required:
            if field not in film:
                issues['missing_fields'].append(f"Film {i} ({title}): missing {field}")

        # Validate language
        if 'language' in film and film['language'] and film['language'] not in valid_languages:
            issues['invalid_languages'].append({
                'title': title,
                'language': film['language']
            })
            # Try to fix common issues
            lang_lower = film['language'].lower()
            if lang_lower == 'hindi':
                film['language'] = 'Hindi'
                issues['fixed_issues'].append(f"Fixed language case: {title}")
            elif lang_lower == 'tamil':
                film['language'] = 'Tamil'
                issues['fixed_issues'].append(f"Fixed language case: {title}")
            elif lang_lower == 'telugu':
                film['language'] = 'Telugu'
                issues['fixed_issues'].append(f"Fixed language case: {title}")

        # Validate IMDb rating
        rating = film.get('imdb_rating')
        if rating is not None:
            try:
                rating_num = float(rating)
                if rating_num < 0 or rating_num > 10:
                    issues['invalid_ratings'].append({
                        'title': title,
                        'rating': rating
                    })
            except (ValueError, TypeError):
                issues['invalid_ratings'].append({
                    'title': title,
                    'rating': rating,
                    'error': 'Cannot convert to float'
                })

        # Ensure arrays are properly formatted
        if 'lead_actors' not in film or not isinstance(film.get('lead_actors'), list):
            issues['missing_actors'].append(f"Film {i}: {title} missing lead_actors array")
            film['lead_actors'] = [film.get('lead_actor', 'Unknown')] if film.get('lead_actor') else []

        if 'lead_actresses' not in film or not isinstance(film.get('lead_actresses'), list):
            film['lead_actresses'] = [film.get('lead_actress', 'Unknown')] if film.get('lead_actress') else []

        # Ensure genres is array
        if 'genres' not in film or not isinstance(film.get('genres'), list):
            film['genres'] = []

        if film.get('title'):  # Only include films with valid title
            cleaned_movies.append(film)

    return cleaned_movies, issues

def generate_report(movies, issues):
    """Generate comprehensive database report"""

    print("\n" + "="*100)
    print("PRODUCTION DATABASE CLEANUP REPORT")
    print("="*100)
    print()

    # Summary stats
    print("DATABASE STATISTICS")
    print("-"*100)
    print(f"Total films after cleanup: {len(movies)}")
    print()

    # Language distribution
    lang_dist = Counter(m.get('language', 'Unknown') for m in movies)
    print("Language Distribution:")
    for lang, count in lang_dist.most_common():
        pct = (count / len(movies)) * 100
        print(f"  {lang:15s}: {count:4d} ({pct:5.1f}%)")
    print()

    # Rating distribution
    print("Rating Distribution (Tiers):")
    tier1 = sum(1 for m in movies if (m.get('imdb_rating') or 0) >= 7.5)
    tier2 = sum(1 for m in movies if 7.0 <= (m.get('imdb_rating') or 0) < 7.5)
    tier3 = sum(1 for m in movies if (m.get('imdb_rating') or 0) < 7.0)

    print(f"  Tier 1 (≥7.5):      {tier1:4d} ({100*tier1/len(movies):5.1f}%)")
    print(f"  Tier 2 (7.0-7.5):   {tier2:4d} ({100*tier2/len(movies):5.1f}%)")
    print(f"  Tier 3 (<7.0):      {tier3:4d} ({100*tier3/len(movies):5.1f}%)")
    print()

    # Attribute coverage
    print("Core Attribute Coverage:")
    attrs = ['has_comedy', 'has_thriller_elements', 'is_family_film', 'has_class_conflict', 'has_romance']
    for attr in attrs:
        count = sum(1 for m in movies if m.get(attr))
        pct = (count / len(movies)) * 100
        print(f"  {attr:30s}: {count:4d} ({pct:5.1f}%)")
    print()

    # Issues summary
    print("CLEANUP ISSUES FOUND")
    print("-"*100)

    total_issues = sum(len(v) for v in issues.values())
    print(f"Total issues identified: {total_issues}")
    print()

    if issues['empty_strings']:
        print(f"✗ Empty strings: {len(issues['empty_strings'])}")
        for issue in issues['empty_strings'][:5]:
            print(f"    {issue}")
        if len(issues['empty_strings']) > 5:
            print(f"    ... and {len(issues['empty_strings']) - 5} more")
        print()

    if issues['invalid_languages']:
        print(f"✗ Invalid languages: {len(issues['invalid_languages'])}")
        for issue in issues['invalid_languages'][:5]:
            print(f"    {issue['title']}: {issue['language']}")
        if len(issues['invalid_languages']) > 5:
            print(f"    ... and {len(issues['invalid_languages']) - 5} more")
        print()

    if issues['invalid_ratings']:
        print(f"✗ Invalid ratings: {len(issues['invalid_ratings'])}")
        for issue in issues['invalid_ratings'][:5]:
            print(f"    {issue['title']}: {issue.get('rating')}")
        if len(issues['invalid_ratings']) > 5:
            print(f"    ... and {len(issues['invalid_ratings']) - 5} more")
        print()

    if issues['duplicate_titles']:
        print(f"✗ Duplicate titles: {len(issues['duplicate_titles'])}")
        for issue in issues['duplicate_titles'][:5]:
            print(f"    {issue['title']} (indices {issue['index']}, {issue['previous_index']})")
        if len(issues['duplicate_titles']) > 5:
            print(f"    ... and {len(issues['duplicate_titles']) - 5} more")
        print()

    if issues['missing_actors']:
        print(f"⚠ Missing actor arrays: {len(issues['missing_actors'])}")
        for issue in issues['missing_actors'][:3]:
            print(f"    {issue}")
        print()

    if issues['fixed_issues']:
        print(f"✓ Issues fixed: {len(issues['fixed_issues'])}")
        for fix in issues['fixed_issues'][:5]:
            print(f"    {fix}")
        if len(issues['fixed_issues']) > 5:
            print(f"    ... and {len(issues['fixed_issues']) - 5} more")
        print()

    print("="*100)

def main():
    print("Loading production database...")
    movies = load_db()
    print(f"Loaded {len(movies)} films")
    print()

    print("Validating and cleaning...")
    cleaned_movies, issues = validate_and_clean(movies)
    print(f"After cleanup: {len(cleaned_movies)} films")
    print()

    # Generate report
    generate_report(cleaned_movies, issues)

    # Save cleaned database
    output_path = Path('backend/data/movies.json')
    print(f"\nSaving cleaned database to {output_path}")
    with open(output_path, 'w') as f:
        json.dump(cleaned_movies, f, indent=2)
    print("✓ Database saved")

    return 0 if len(issues['invalid_ratings']) == 0 and len(issues['invalid_languages']) == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
