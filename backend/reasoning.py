"""
Chain-of-Thought reasoning for intelligent question selection.

The engine uses LLM reasoning to understand the candidate space and pick
strategic questions, not just locally-optimal ones.
"""
import json
from typing import Optional
from pathlib import Path


class CotReasoner:
    """Generates chain-of-thought reasoning for question selection."""

    def __init__(self, model_name: str = "claude-opus-4-8"):
        self.model_name = model_name
        self.reasoning_history = []
        try:
            import anthropic
            self.client = anthropic.Anthropic()
        except ImportError:
            self.client = None

    def analyze_candidate_space(self, candidates: list, answers: dict, question_count: int) -> dict:
        """
        Analyze the candidate film space to understand what varies and what discriminates.
        Includes genre-aware analysis and actor/director distribution.

        Returns: {
            'patterns': str,
            'discriminators': list,
            'strategy': str,
            'genre_analysis': str,     # What varies WITHIN the genre?
            'actor_discriminators': list, # Which actors discriminate most?
            'should_unlock_actors': bool, # Time to ask actor Qs?
            'reasoning': str,
        }
        """
        if not self.client or len(candidates) > 50:
            return self._fallback_analysis(candidates, answers, question_count)

        candidate_titles = [f"{m.get('title')} ({m.get('year')})" for m in candidates[:12]]
        known_answers = {k: v for k, v in answers.items() if v == "yes"}

        # Analyze actor/director distribution
        actors_freq = {}
        directors_freq = {}
        for m in candidates:
            for actor in (m.get('lead_actors') or []):
                actors_freq[actor] = actors_freq.get(actor, 0) + 1
            for actor in ([m.get('lead_actor')] if m.get('lead_actor') else []):
                actors_freq[actor] = actors_freq.get(actor, 0) + 1
            dir_name = m.get('director')
            if dir_name:
                directors_freq[dir_name] = directors_freq.get(dir_name, 0) + 1

        top_actors = sorted(actors_freq.items(), key=lambda x: -x[1])[:5]
        top_directors = sorted(directors_freq.items(), key=lambda x: -x[1])[:3]

        prompt = f"""Analyze this film selection space strategically.

CANDIDATES ({len(candidates)} films):
{', '.join(candidate_titles)}

KNOWN FACTS (YES answers):
{json.dumps(known_answers, indent=2)}

QUESTIONS ASKED: {question_count}

Your task: Identify what VARIES WITHIN the known constraints.

1. GENRE-AWARE PATTERNS: What differs between these films?
   (E.g., if all action: military vs crime vs romance-action?)
   (E.g., if all 2020s Hindi: patriotic vs crime vs romantic?)

2. CONTRADICTIONS: Do any YES answers conflict?
   (E.g., patriotic + gangster is unusual — they occupy different spaces)

3. SEQUENCE: Should we unlock actor questions NOW or wait?
   - Pool > 100: ask plot/trope questions first
   - Pool 30-100: ready for actor questions
   - Pool < 30: endgame — final discriminators

Be specific: name films and explain what separates them."""

        try:
            response = self.client.messages.create(
                model=self.model_name,
                max_tokens=800,
                messages=[{"role": "user", "content": prompt}],
            )
            reasoning = response.content[0].text

            analysis = {
                "full_reasoning": reasoning,
                "patterns": self._extract_section(reasoning, "GENRE-AWARE", 2),
                "genre_analysis": self._extract_section(reasoning, "varies WITHIN", 3),
                "strategy": self._extract_section(reasoning, "SEQUENCE STRATEGY", 3),
            }
            self.reasoning_history.append({"turn": question_count, "analysis": analysis})
            return analysis
        except Exception as e:
            print(f"⚠️ COT reasoning failed: {e}")
            return self._fallback_analysis(candidates, answers, question_count)

    def score_question_strategically(
        self, question_id: str, question_text: str, candidates: list, answers: dict
    ) -> Optional[dict]:
        """
        Generate reasoning for why a specific question is strategic given the current state.

        Returns: {
            'question_id': str,
            'reasoning': str,           # Why ask this question?
            'discriminative_power': int, # 1-10 scale
            'strategic_alignment': int, # How well does it advance our strategy?
        }
        """
        if not self.client or len(candidates) > 40:
            return None

        candidate_titles = [m.get('title') for m in candidates[:8]]

        prompt = f"""Rate this question strategically for this game state.

QUESTION: {question_text}
QUESTION_ID: {question_id}

CURRENT CANDIDATES ({len(candidates)}):
{', '.join(candidate_titles)}

WHAT WE KNOW:
{json.dumps({k: v for k, v in answers.items() if v == "yes"}, indent=2)}

Evaluate:
1. How well would this discriminate the current candidates?
2. What would "yes" vs "no" tell us?
3. How does this advance finding the actual film?
4. Is this a high-ROI question or a side exploration?
5. Rate 1-10: discriminative power

Format your response as:
DISCRIMINATIVE_POWER: X
STRATEGIC_VALUE: Y (also 1-10)
REASONING: [2-3 sentences on why this question matters]"""

        try:
            response = self.client.messages.create(
                model=self.model_name,
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}],
            )
            text = response.content[0].text

            return {
                "question_id": question_id,
                "reasoning": text,
                "scored": True,
            }
        except Exception:
            return None

    def clarify_maybe(self, question_id: str, question_text: str, existing_answers: dict) -> str:
        """
        When player exhausts maybes (5 used), disambiguate with COT.
        Returns: "yes" or "no" based on contradiction analysis.
        """
        if not self.client:
            return "maybe"  # Fallback

        yes_answers = {k: v for k, v in existing_answers.items() if v == "yes"}
        maybe_answers = {k: v for k, v in existing_answers.items() if v == "maybe"}

        prompt = f"""Player has used 5 unsure answers and is now forced to decide on this one.

QUESTION: {question_text}
QUESTION_ID: {question_id}

THEIR YES ANSWERS (confident):
{json.dumps(yes_answers, indent=2)}

THEIR MAYBE ANSWERS (uncertain):
{json.dumps(maybe_answers, indent=2)}

Based on what they ARE confident about, would they most likely answer YES or NO to this question?

Consider: If they said YES to [list], they probably mean YES/NO to this question.

ANSWER ONLY: YES or NO (not maybe)"""

        try:
            response = self.client.messages.create(
                model=self.model_name,
                max_tokens=100,
                messages=[{"role": "user", "content": prompt}],
            )
            text = response.content[0].text.strip().upper()
            return "yes" if "YES" in text else "no"
        except Exception:
            return "maybe"

    def reflect_on_answer(self, question_id: str, answer: str, expected: Optional[str], candidates_before: int, candidates_after: int) -> dict:
        """
        Reflect on an answer: Was it expected? What does it mean?

        Returns reasoning about what the answer revealed.
        """
        if expected and answer != expected:
            surprise_level = "MAJOR"
        elif len(candidates_after) / max(1, candidates_before) > 0.8:
            surprise_level = "MINOR"
        else:
            surprise_level = "EXPECTED"

        prompt = f"""Reflect on this answer in the game.

QUESTION: {question_id}
ANSWER: {answer}
EXPECTED: {expected or 'Unknown'}
SURPRISE: {surprise_level}

CANDIDATE REDUCTION: {candidates_before} → {candidates_after}

What does this tell us? What was surprising? What does it imply about the film?
(1-2 sentences)"""

        try:
            response = self.client.messages.create(
                model=self.model_name,
                max_tokens=150,
                messages=[{"role": "user", "content": prompt}],
            )
            return {
                "answer": answer,
                "surprise": surprise_level,
                "reflection": response.content[0].text,
            }
        except Exception:
            return {"answer": answer, "surprise": surprise_level}

    @staticmethod
    def _extract_section(text: str, keyword: str, sentences: int = 2) -> str:
        """Extract a section of reasoning containing keyword."""
        lines = text.split("\n")
        for i, line in enumerate(lines):
            if keyword.lower() in line.lower():
                return "\n".join(lines[i : i + sentences])
        return ""

    @staticmethod
    def _extract_actor_name(text: str) -> Optional[str]:
        """Try to extract recommended actor name from reasoning."""
        # Look for patterns like "ask about [Actor Name]" or "[Actor] would split"
        import re
        patterns = [
            r"ask about ([A-Z][a-z]+ [A-Z][a-z]+)",
            r"([A-Z][a-z]+ [A-Z][a-z]+) would.*split",
            r"TARGET.*?([A-Z][a-z]+ [A-Z][a-z]+)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        return None

    @staticmethod
    def _fallback_analysis(candidates: list, answers: dict, question_count: int) -> dict:
        """Fallback when LLM is unavailable."""
        return {
            "full_reasoning": f"Analyzing {len(candidates)} candidates after {question_count} questions",
            "patterns": "Multiple candidates match current answers",
            "discriminators": "Need targeted plot/trope questions",
            "genre_analysis": "Analyzing genre-specific variations",
            "actor_discriminators": "Actor distribution being analyzed",
            "should_unlock_actors": len(candidates) < 100,
            "strategy": "Focus on story elements that vary across remaining films",
        }
