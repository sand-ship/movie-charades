"""
Cluster-based discrimination for stumper prevention.

Loads cluster metadata and discrimination questions, then uses them to:
1. Detect when candidates belong to similar clusters
2. Inject cluster differentiation questions at the right time
3. Analyze stumper patterns to identify weak discrimination points
"""

import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from collections import defaultdict


class ClusterDiscriminator:
    def __init__(self):
        self.movies_by_cluster: Dict[str, List[Dict]] = defaultdict(list)
        self.cluster_metadata: Dict[str, Dict] = {}
        self.discrimination_questions: List[Dict] = []
        self.language_clusters: Dict[str, set] = defaultdict(set)
        self._load_data()

    def _load_data(self):
        """Load cluster data and discrimination questions."""
        data_dir = Path(__file__).parent / "data"

        try:
            # Load consolidated clusters
            with open(data_dir / "all_clusters_consolidated.json") as f:
                clusters = json.load(f)

            for cluster in clusters:
                cid = cluster.get("cluster_id")
                lang = cluster.get("language", "unknown")

                if cid:
                    self.movies_by_cluster[cid].append(cluster)
                    self.language_clusters[lang].add(cid)

                    # Store metadata once per cluster
                    if cid not in self.cluster_metadata:
                        self.cluster_metadata[cid] = {
                            "name": cluster.get("cluster_name"),
                            "language": lang,
                            "diff_key": cluster.get("cluster_differentiation_key", ""),
                            "tags": cluster.get("tags", {}),
                            "film_count": 0
                        }
                    self.cluster_metadata[cid]["film_count"] += 1
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Warning: Could not load cluster data: {e}")

        try:
            # Load discrimination questions
            with open(data_dir / "discrimination_questions.json") as f:
                self.discrimination_questions = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Warning: Could not load discrimination questions: {e}")

    def get_candidate_clusters(self, candidates: List[Dict]) -> Dict[str, int]:
        """
        Count how many candidates belong to each cluster.
        Returns {cluster_id: count} for clusters represented in candidates.
        """
        clusters_in_candidates = defaultdict(int)
        for movie in candidates:
            cid = movie.get("cluster_id")
            if cid:
                clusters_in_candidates[cid] += 1
        return clusters_in_candidates

    def should_inject_discrimination_questions(self, candidates: List[Dict],
                                              asked_questions: List[str]) -> bool:
        """
        Check if candidates are clustering (multiple films in same cluster).
        Returns True if we should inject discrimination questions.
        """
        if len(candidates) > 10:
            # Only consider discrimination when pool is small
            return False

        candidate_clusters = self.get_candidate_clusters(candidates)
        if not candidate_clusters:
            return False

        # If more than 1 cluster is represented, no discrimination needed yet
        if len(candidate_clusters) > 1:
            return False

        # If all candidates are in the same cluster, inject discrimination
        dominant_cluster = list(candidate_clusters.keys())[0]
        return True

    def get_cluster_discrimination_questions(self, candidates: List[Dict],
                                           asked_questions: List[str],
                                           limit: int = 3) -> List[Dict]:
        """
        Return discrimination questions for the dominant cluster in candidates.
        """
        candidate_clusters = self.get_candidate_clusters(candidates)
        if not candidate_clusters or len(candidate_clusters) > 1:
            return []

        dominant_cluster = list(candidate_clusters.keys())[0]
        cluster_info = self.cluster_metadata.get(dominant_cluster)
        if not cluster_info:
            return []

        # Find discrimination questions for this cluster
        relevant = [q for q in self.discrimination_questions
                   if q.get("cluster_id") == dominant_cluster
                   and q.get("question_id") not in asked_questions]

        return relevant[:limit]

    def analyze_stumper(self, stumped_title: str, final_candidates: List[Dict],
                       top_guesses: List[Dict]) -> Dict[str, Any]:
        """
        Analyze a stumper to identify which cluster differentiation was missed.
        """
        analysis = {
            "stumper_title": stumped_title,
            "reason": "unknown",
            "similar_candidates": [],
            "missing_discriminations": [],
            "cluster_id": None
        }

        # Find the stumper in final candidates
        stumper = None
        for movie in final_candidates:
            if movie.get("title") == stumped_title:
                stumper = movie
                break

        if not stumper:
            analysis["reason"] = "stumper_not_in_final_candidates"
            return analysis

        stumper_cluster = stumper.get("cluster_id")
        analysis["cluster_id"] = stumper_cluster

        if not stumper_cluster:
            analysis["reason"] = "stumper_has_no_cluster"
            return analysis

        # Find similar candidates in same cluster
        similar = [m for m in final_candidates
                   if m.get("cluster_id") == stumper_cluster
                   and m.get("title") != stumped_title]
        analysis["similar_candidates"] = [m.get("title") for m in similar]

        # Find which discrimination questions would have helped
        relevant_qs = [q for q in self.discrimination_questions
                      if q.get("cluster_id") == stumper_cluster]
        analysis["missing_discriminations"] = [
            {
                "question_id": q.get("question_id"),
                "question": q.get("question")
            }
            for q in relevant_qs[:3]
        ]

        if similar:
            analysis["reason"] = "cluster_candidates_not_differentiated"
        else:
            analysis["reason"] = "cluster_alone_in_pool"

        return analysis

    def get_cluster_hint(self, candidates: List[Dict]) -> Optional[str]:
        """
        Return a subtle hint about the dominant cluster if candidates cluster together.
        """
        candidate_clusters = self.get_candidate_clusters(candidates)
        if len(candidate_clusters) != 1:
            return None

        cid = list(candidate_clusters.keys())[0]
        cluster_info = self.cluster_metadata.get(cid)
        if not cluster_info:
            return None

        # Return the differentiation key as a hint
        return cluster_info.get("diff_key")


# Global instance
_discriminator: Optional[ClusterDiscriminator] = None


def get_discriminator() -> ClusterDiscriminator:
    """Get or create the global cluster discriminator instance."""
    global _discriminator
    if _discriminator is None:
        _discriminator = ClusterDiscriminator()
    return _discriminator
