#!/usr/bin/env python3
"""
Analyze 2527 Indian films for 7 key attributes:
1. has_happy_ending — Satisfying, romantic, or triumphant conclusion
2. has_tragic_ending — Sad, tragic, or bittersweet conclusion
3. has_ambiguous_ending — Unclear, open-ended, or uncertain conclusion
4. is_yrf_style — Yash Raj Films aesthetic: grand, romantic, feel-good
5. has_gritty_realism — Dark, gritty, urban-realistic style
6. is_intimate_indie — Intimate, personal, or indie style (NOT big-budget)
7. has_suspense_thriller — Tension through suspense or cat-and-mouse plot
"""

import json
import os
from collections import defaultdict

# Load the movies data
movies_path = "/Users/sandeep.srinivasan/sand-ship/indian-movie-genie/backend/data/movies.json"
with open(movies_path, 'r') as f:
    movies = json.load(f)

print(f"Loaded {len(movies)} films")

# ============================================================================
# PART 1: Build Knowledge Base of Famous/Pivot Films
# ============================================================================

famous_films_knowledge = {
    # Classic era golden age - happy endings
    "Dilwale Dulhania Le Jayenge": {
        "attributes": ["has_happy_ending", "is_yrf_style"],
        "reason": "Iconic Bollywood romance, grand wedding finale, iconic YRF feel"
    },
    "Sholay": {
        "attributes": ["has_happy_ending", "has_suspense_thriller"],
        "reason": "Climactic villain showdown with happy resolution, suspense-driven"
    },
    "Mughal-E-Azam": {
        "attributes": ["has_tragic_ending"],
        "reason": "Forbidden love ends in tragedy - lovers separate"
    },
    "Awara": {
        "attributes": ["has_happy_ending"],
        "reason": "Redemption arc with satisfying conclusion"
    },

    # Modern era - YRF style films
    "Rab Ne Bana Di Jodi": {
        "attributes": ["has_happy_ending", "is_yrf_style"],
        "reason": "Romantic transformation, grand YRF production feel"
    },
    "Veer Zaara": {
        "attributes": ["has_happy_ending", "is_yrf_style"],
        "reason": "Epic romance across borders, YRF grandeur, triumphant ending"
    },
    "Jab Tak Hai Jaan": {
        "attributes": ["has_happy_ending", "is_yrf_style"],
        "reason": "Romantic climax, large-scale YRF production"
    },

    # Gritty realism films
    "Gangs of Wasseypur": {
        "attributes": ["has_tragic_ending", "has_gritty_realism"],
        "reason": "Ultra-realistic crime saga ending in death, urban grit"
    },
    "Satya": {
        "attributes": ["has_tragic_ending", "has_gritty_realism"],
        "reason": "Dark underworld film, protagonist dies, realistic Mumbai"
    },
    "Company": {
        "attributes": ["has_gritty_realism"],
        "reason": "Realistic crime drama, urban underworld"
    },
    "Jai Bhim": {
        "attributes": ["has_happy_ending", "has_gritty_realism"],
        "reason": "Social realism with triumphant justice ending"
    },

    # Intimate/indie style
    "Masaan": {
        "attributes": ["has_ambiguous_ending", "is_intimate_indie"],
        "reason": "Personal stories, indie aesthetic, uncertain futures"
    },
    "Article 15": {
        "attributes": ["is_intimate_indie", "has_gritty_realism"],
        "reason": "Personal investigation film, realistic social commentary"
    },
    "Udaan": {
        "attributes": ["is_intimate_indie"],
        "reason": "Coming-of-age indie drama, personal story"
    },
    "The Girl in Yellow Boots": {
        "attributes": ["has_ambiguous_ending", "is_intimate_indie"],
        "reason": "Art-house indie film, open-ended narrative"
    },

    # Suspense/thriller films
    "Drishyam": {
        "attributes": ["has_suspense_thriller"],
        "reason": "Cat-and-mouse game with police, high tension"
    },
    "Badla": {
        "attributes": ["has_suspense_thriller"],
        "reason": "Twisty cat-and-mouse legal thriller"
    },
    "Kahaani": {
        "attributes": ["has_suspense_thriller"],
        "reason": "Mystery thriller with constant tension"
    },
    "Natarang": {
        "attributes": ["has_tragic_ending"],
        "reason": "Tragic fall of protagonist, dark ending"
    },
    "Rang De Basanti": {
        "attributes": ["has_happy_ending"],
        "reason": "Activists achieve social change despite sacrifice"
    },
    "Hera Pheri": {
        "attributes": ["has_happy_ending"],
        "reason": "Comedy caper with happy resolution"
    },
    "The Lunchbox": {
        "attributes": ["is_intimate_indie"],
        "reason": "Intimate, understated indie love story"
    },
    "Gulaal": {
        "attributes": ["has_gritty_realism"],
        "reason": "Realistic political corruption drama"
    },
    "Dev D": {
        "attributes": ["has_tragic_ending", "has_gritty_realism"],
        "reason": "Dark modern tragedy, gritty Delhi setting"
    },
    "Piku": {
        "attributes": ["has_happy_ending"],
        "reason": "Heartwarming family drama with satisfying resolution"
    }
}

# ============================================================================
# PART 2: Create Heuristic Analyzer
# ============================================================================

class FilmAttributeAnalyzer:
    def __init__(self, knowledge_base):
        self.knowledge_base = knowledge_base
        self.yrf_directors = {
            "Yash Chopra", "Aditya Chopra", "Sooraj Barjatya", "Rajkumar Hirani",
            "Farah Khan", "Kabir Khan"
        }
        self.gritty_directors = {
            "Anurag Kashyap", "Neeraj Pandey", "Dibakar Banerjee", "Vishal Bharwani",
            "Srijit Mukherji", "Navdeep Singh", "Abhishek Chaubey", "Tigmanshu Dhulia"
        }
        self.indie_directors = {
            "Neeraj Ghaywan", "Abhijit Das", "Nitesh Tiwari", "Girish Kasaravalli",
            "Ravi Ruia", "Ashwiny Iyer Tiwari", "Brijmohan Lal"
        }

    def analyze(self, film):
        """Analyze a single film for all 7 attributes"""
        attributes = []

        # First check if it's in the knowledge base
        title = film.get("title", "").strip()
        if title in self.knowledge_base:
            return self.knowledge_base[title]["attributes"]

        # Apply heuristics
        # 1. has_happy_ending
        if self._has_happy_ending(film):
            attributes.append("has_happy_ending")

        # 2. has_tragic_ending
        if self._has_tragic_ending(film):
            attributes.append("has_tragic_ending")

        # 3. has_ambiguous_ending
        if self._has_ambiguous_ending(film):
            attributes.append("has_ambiguous_ending")

        # 4. is_yrf_style
        if self._is_yrf_style(film):
            attributes.append("is_yrf_style")

        # 5. has_gritty_realism
        if self._has_gritty_realism(film):
            attributes.append("has_gritty_realism")

        # 6. is_intimate_indie
        if self._is_intimate_indie(film):
            attributes.append("is_intimate_indie")

        # 7. has_suspense_thriller
        if self._has_suspense_thriller(film):
            attributes.append("has_suspense_thriller")

        return attributes

    def _has_happy_ending(self, film):
        """Detect happy endings"""
        # Romance films without tragic markers
        if film.get("has_romance") and not film.get("has_forbidden_love"):
            # Most romantic films have happy endings
            if film.get("primary_genre") in ["romance", "drama"]:
                if not film.get("is_anti_hero"):
                    return True

        # Family films typically have happy endings
        if film.get("is_family_film") and film.get("imdb_rating", 0) > 6.5:
            return True

        # Mass entertainers with positive themes
        if film.get("is_mass_entertainer") and not film.get("has_social_message"):
            return True

        # Underdog stories usually have happy endings
        if film.get("has_underdog_story"):
            return True

        # Romantic films with high ratings
        if (film.get("has_romance") and
            film.get("primary_genre") in ["romance", "comedy"] and
            film.get("imdb_rating", 0) > 7.0):
            return True

        # Films with "lost and found child" resolved
        if film.get("is_lost_and_found_child"):
            return True

        # Films with patriotic/sacrifice themes often end happily
        if film.get("has_patriotic_sacrifice") and not film.get("is_anti_hero"):
            return True

        return False

    def _has_tragic_ending(self, film):
        """Detect tragic endings"""
        # Anti-hero films often have tragic endings
        if film.get("is_anti_hero"):
            return True

        # Gangster/crime films with dark themes
        if film.get("has_gangster_world") and film.get("has_gritty_realism"):
            return True

        # Period dramas with forbidden love
        if film.get("is_period_drama") and film.get("has_forbidden_love"):
            return True

        # Historical films sometimes have tragic endings
        if (film.get("is_historical") and
            film.get("lead_gender") == "male" and
            film.get("imdb_rating", 0) > 7.0):
            # Check for serious themes
            if "tragedy" in str(film.get("genres", [])).lower():
                return True

        # Arthouse/indie films can have tragic endings
        if film.get("year", 2000) > 2010:
            if film.get("is_historical") or film.get("has_social_message"):
                if film.get("imdb_rating", 0) > 7.0:
                    return True

        return False

    def _has_ambiguous_ending(self, film):
        """Detect ambiguous/open-ended endings"""
        # Art house and indie films often have ambiguous endings
        if film.get("year", 2000) > 2014:
            if film.get("has_social_message") and not film.get("is_family_film"):
                return True

        # Psychological/drama films with complex themes
        if (film.get("primary_genre") in ["drama", "psychological"] and
            film.get("imdb_rating", 0) > 7.2):
            if not (film.get("has_revenge_plot") or film.get("has_romance")):
                return True

        return False

    def _is_yrf_style(self, film):
        """Detect Yash Raj Films aesthetic"""
        director = film.get("director", "")

        # Check director
        if director in self.yrf_directors:
            return True

        # YRF characteristics: romantic, grand, feel-good
        if (film.get("has_romance") and
            film.get("is_mass_entertainer") and
            film.get("has_songs") and
            not film.get("is_anti_hero") and
            film.get("imdb_rating", 0) > 6.5):
            return True

        # Large scale romance films
        if (film.get("has_romance") and
            film.get("is_pan_india_blockbuster") and
            film.get("has_comedy") and
            not film.get("is_set_in_slums")):
            return True

        return False

    def _has_gritty_realism(self, film):
        """Detect gritty realism aesthetic"""
        director = film.get("director", "")

        # Check director
        if director in self.gritty_directors:
            return True

        # Characteristics: crime, underworld, slums, dark
        if film.get("has_gangster_world") or film.get("is_set_in_slums"):
            return True

        # Urban crime dramas
        if (film.get("primary_genre") in ["crime", "drama"] and
            film.get("has_social_message") and
            not film.get("has_songs")):
            return True

        # Dark, realistic films
        if (film.get("is_anti_hero") and
            film.get("primary_genre") in ["crime", "thriller", "drama"]):
            return True

        return False

    def _is_intimate_indie(self, film):
        """Detect intimate/indie style"""
        director = film.get("director", "")

        # Check director
        if director in self.indie_directors:
            return True

        # Intimate characteristics: not mass entertainer, personal stories
        if (not film.get("is_pan_india_blockbuster") and
            not film.get("is_mass_entertainer") and
            film.get("primary_genre") in ["drama", "romance"] and
            film.get("year", 2000) > 2010):
            return True

        # Small budget, character-driven
        if (film.get("has_social_message") and
            not film.get("has_songs") and
            not film.get("has_item_number") and
            film.get("imdb_rating", 0) > 7.0):
            return True

        # Art house sensibility
        if (not film.get("has_action") and
            not film.get("has_villain") and
            film.get("year", 2000) > 2012 and
            film.get("primary_genre") in ["drama", "romance"]):
            return True

        return False

    def _has_suspense_thriller(self, film):
        """Detect suspense/thriller elements"""
        # Direct genre indicators
        if film.get("primary_genre") in ["thriller", "suspense", "crime"]:
            return True

        # Thriller elements
        if film.get("has_thriller_elements"):
            return True

        # Mystery/crime with specific elements
        if (film.get("has_police_or_law") and
            film.get("primary_genre") in ["crime", "drama", "thriller"]):
            return True

        # Cat and mouse plots
        if (film.get("has_revenge_plot") and
            "thriller" in str(film.get("genres", [])).lower()):
            return True

        return False

# ============================================================================
# PART 3: Run Analysis
# ============================================================================

analyzer = FilmAttributeAnalyzer(famous_films_knowledge)
results = []
attribute_counts = defaultdict(int)

print("\nAnalyzing all films...")
for i, film in enumerate(movies):
    if i % 500 == 0:
        print(f"  Processed {i}/{len(movies)}...")

    attributes = analyzer.analyze(film)

    if attributes:  # Only include films with at least one attribute
        results.append({
            "title": film.get("title", "Unknown"),
            "attributes": attributes
        })

        for attr in attributes:
            attribute_counts[attr] += 1

# ============================================================================
# PART 4: Output Results
# ============================================================================

output_path = "/Users/sandeep.srinivasan/sand-ship/indian-movie-genie/film_attributes_analysis.json"
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"\n✓ Analysis complete!")
print(f"  Total films analyzed: {len(movies)}")
print(f"  Films with attributes: {len(results)}")
print(f"  Output file: {output_path}")

print("\nAttribute Distribution:")
for attr in sorted(attribute_counts.keys()):
    count = attribute_counts[attr]
    pct = (count / len(results) * 100) if results else 0
    print(f"  {attr}: {count} films ({pct:.1f}%)")

print(f"\nTotal attribute assignments: {sum(attribute_counts.values())}")
print(f"Average attributes per film: {sum(attribute_counts.values()) / len(results):.2f}" if results else "N/A")
