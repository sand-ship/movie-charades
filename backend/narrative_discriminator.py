"""Suggest discrimination questions for narrative-similar stumpers"""

from typing import List, Optional, Dict
from narrative_clusters import get_clusters
from collaboration import get_graph
from questions import QUESTION_MAP

NARRATIVE_ARCHETYPE_DISCRIMINATORS = {
    # Mass Action Hero films: distinguish by tone/style
    'mass_action_hero/comedy': {
        'dimensions': ['comedy_focus', 'villain_intensity', 'romance_subplot'],
        'questions': ['q_genre_comedy', 'q_villain', 'has_romance'],
    },
    # Cop/Police Action: distinguish by corruption level, political elements
    'cop/police_action': {
        'dimensions': ['corruption_theme', 'political_angle', 'vigilante_justice'],
        'questions': ['q_crime_protagonist', 'q_political_corruption', 'q_investigation'],
    },
    # Romance/Melodrama: distinguish by resolution, family role
    'romantic_melodrama_domestic_hybrid': {
        'dimensions': ['family_role', 'ending_type', 'secondary_plot'],
        'questions': ['has_family_approval_conflict', 'q_happy_ending', 'q_forbidden_love'],
    },
    # Institutional Romance: distinguish by setting, conflict type
    'institutional/ideological_romance': {
        'dimensions': ['setting_type', 'conflict_source', 'character_arc'],
        'questions': ['q_college_film', 'q_class_conflict', 'q_forbidden_love'],
    },
}


def suggest_narrative_discriminators(candidates: List[dict]) -> Optional[Dict]:
    """Suggest discrimination questions when candidates are narrative-similar stumpers.

    Returns dict with:
    - shared_archetype: the common archetype
    - discriminator_dimensions: what distinguishes films within this archetype
    - suggested_questions: which questions to ask
    - narrative_type: description of the common narrative pattern
    """
    if len(candidates) < 2:
        return None

    clusters = get_clusters()

    # Find shared archetypes
    shared = clusters.shared_archetypes([m.get('id') or m.get('cluster_id') for m in candidates if m.get('id') or m.get('cluster_id')])

    if not shared:
        return None

    # Find the dominant shared archetype (most films in it)
    dominant_archetype = max(shared.items(), key=lambda x: x[1])[0] if shared else None

    if not dominant_archetype:
        return None

    concentration = shared[dominant_archetype] / len(candidates)

    # Only suggest if 50%+ of candidates share this archetype (stumper indicator)
    if concentration < 0.5:
        return None

    discriminators = NARRATIVE_ARCHETYPE_DISCRIMINATORS.get(dominant_archetype, {})

    return {
        'shared_archetype': dominant_archetype,
        'concentration': concentration,
        'num_in_archetype': shared[dominant_archetype],
        'dimensions': discriminators.get('dimensions', []),
        'suggested_questions': discriminators.get('questions', []),
        'narrative_type': 'narrative_stumper',
    }


def get_most_specific_narrative_features(film: dict, num_features: int = 3) -> List[str]:
    """Get the most specific/distinctive narrative features of a film for narrowing.
    Combines explicit cluster + key boolean attributes."""
    features = []

    clusters = get_clusters()
    film_id = film.get('id') or film.get('cluster_id')

    if film_id:
        # Get most specific archetype
        specific = clusters.most_specific_archetype(film_id)
        if specific:
            features.append(f"archetype:{specific}")

    # Add key boolean narrative attributes
    key_attrs = [
        'has_revenge_plot', 'has_friendship_focus', 'has_forbidden_love',
        'has_class_conflict', 'has_gangster_world', 'is_anti_hero_protagonist',
        'has_brothers_in_arms', 'has_family_approval_conflict',
    ]

    for attr in key_attrs:
        if film.get(attr) is True:
            features.append(f"attr:{attr}")
            if len(features) >= num_features:
                break

    return features[:num_features]
