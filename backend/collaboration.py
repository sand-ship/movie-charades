"""Query and analyze actor-director collaboration networks"""

import json
from pathlib import Path
from typing import Optional, Dict, List, Set


class CollaborationGraph:
    def __init__(self):
        try:
            with open(Path(__file__).parent / 'data' / 'collaboration_graph.json', 'r') as f:
                self.graph = json.load(f)
        except FileNotFoundError:
            self.graph = {'actor_director': {}, 'director_actor': {}, 'metadata': {}}

    def get_actor_directors(self, actor: str) -> Dict[str, dict]:
        """Return all directors this actor has worked with, with counts and film lists"""
        return self.graph['actor_director'].get(actor, {})

    def get_director_actors(self, director: str) -> Dict[str, dict]:
        """Return all actors this director has worked with, with counts and film lists"""
        return self.graph['director_actor'].get(director, {})

    def collaboration_count(self, actor: str, director: str) -> int:
        """Return number of films actor and director have done together"""
        return self.graph['actor_director'].get(actor, {}).get(director, {}).get('count', 0)

    def collaboration_films(self, actor: str, director: str) -> List[str]:
        """Return list of film IDs for this actor-director pair"""
        return self.graph['actor_director'].get(actor, {}).get(director, {}).get('films', [])

    def has_collaborated(self, actor: str, director: str) -> bool:
        """Check if actor and director have worked together"""
        return self.collaboration_count(actor, director) > 0

    def frequent_collaborators(self, actor: str, min_films: int = 2) -> Dict[str, int]:
        """Return directors this actor has frequently worked with (min_films or more)"""
        directors = self.get_actor_directors(actor)
        return {d: data['count'] for d, data in directors.items() if data['count'] >= min_films}

    def actor_pool_by_director(self, director: str, candidate_films: List[str]) -> Set[str]:
        """Return actors who have worked with this director in the candidate films"""
        director_actors = self.get_director_actors(director)
        result = set()
        for actor, data in director_actors.items():
            if any(film_id in data['films'] for film_id in candidate_films):
                result.add(actor)
        return result

    def actor_pool_by_collaboration(self, actor: str, candidate_films: List[str]) -> Set[str]:
        """Return directors who have worked with this actor in the candidate films"""
        actor_directors = self.get_actor_directors(actor)
        result = set()
        for director, data in actor_directors.items():
            if any(film_id in data['films'] for film_id in candidate_films):
                result.add(director)
        return result


# Singleton instance
_graph = None

def get_graph() -> CollaborationGraph:
    global _graph
    if _graph is None:
        _graph = CollaborationGraph()
    return _graph
