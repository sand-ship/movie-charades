"""Query and analyze narrative cluster memberships"""

import json
from pathlib import Path
from typing import List, Set, Dict


class NarrativeClusters:
    def __init__(self):
        try:
            with open(Path(__file__).parent / 'data' / 'narrative_clusters.json', 'r') as f:
                self.index = json.load(f)
        except FileNotFoundError:
            self.index = {'archetype_to_films': {}, 'film_to_archetypes': {}, 'archetype_metadata': {}}

    def film_archetypes(self, film_id: str) -> List[str]:
        """Return all narrative archetypes this film belongs to"""
        return self.index.get('film_to_archetypes', {}).get(film_id, [])

    def archetype_films(self, archetype_id: str) -> List[str]:
        """Return all films in this narrative archetype"""
        return self.index.get('archetype_to_films', {}).get(archetype_id, [])

    def films_in_archetypes(self, archetype_ids: List[str]) -> Set[str]:
        """Return films that belong to ANY of the given archetypes (union)"""
        result = set()
        for archetype_id in archetype_ids:
            result.update(self.archetype_films(archetype_id))
        return result

    def films_in_all_archetypes(self, archetype_ids: List[str]) -> Set[str]:
        """Return films that belong to ALL of the given archetypes (intersection)"""
        if not archetype_ids:
            return set()
        result = None
        for archetype_id in archetype_ids:
            archetype_films = set(self.archetype_films(archetype_id))
            if result is None:
                result = archetype_films
            else:
                result = result & archetype_films
        return result or set()

    def shared_archetypes(self, film_ids: List[str]) -> Dict[str, int]:
        """Return archetypes shared by multiple films, with count of how many films have them"""
        from collections import Counter
        archetype_counts = Counter()
        for film_id in film_ids:
            for archetype in self.film_archetypes(film_id):
                archetype_counts[archetype] += 1
        # Return archetypes shared by multiple films
        return {a: count for a, count in archetype_counts.items() if count > 1}

    def most_specific_archetype(self, film_id: str) -> str:
        """Return the most specific (likely explicit cluster) archetype for a film"""
        archetypes = self.film_archetypes(film_id)
        if not archetypes:
            return None
        # Prefer explicit clusters (usually longer, more specific names)
        explicit = [a for a in archetypes
                   if self.index.get('archetype_metadata', {}).get(a, {}).get('is_explicit_cluster')]
        if explicit:
            return max(explicit, key=len)  # Longest = most specific
        return archetypes[0]  # Fall back to first archetype

    def is_narrative_similar(self, film_a: str, film_b: str, min_shared: int = 1) -> bool:
        """Check if two films share narrative archetypes"""
        archetypes_a = set(self.film_archetypes(film_a))
        archetypes_b = set(self.film_archetypes(film_b))
        return len(archetypes_a & archetypes_b) >= min_shared

    def narrative_pool_overlap(self, candidate_films: List[str], sample_film: str) -> int:
        """Return count of candidates that share archetypes with sample film"""
        sample_archetypes = set(self.film_archetypes(sample_film))
        if not sample_archetypes:
            return 0
        count = 0
        for film_id in candidate_films:
            if self.is_narrative_similar(film_id, sample_film):
                count += 1
        return count

    def cluster_concentration(self, candidate_films: List[str]) -> Dict[str, float]:
        """For each archetype, what % of candidates belong to it?
        Useful for detecting when candidates are concentrated in one narrative type."""
        from collections import Counter
        archetype_counts = Counter()
        for film_id in candidate_films:
            for archetype in self.film_archetypes(film_id):
                archetype_counts[archetype] += 1

        total = len(candidate_films)
        if total == 0:
            return {}

        return {a: count / total for a, count in archetype_counts.items()}


# Singleton instance
_clusters = None

def get_clusters() -> NarrativeClusters:
    global _clusters
    if _clusters is None:
        _clusters = NarrativeClusters()
    return _clusters
