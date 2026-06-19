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

        Returns: {
            'patterns': str,           # Key patterns observed across candidates
            'discriminators': list,    # Features that vary significantly
            'strategy': str,           # Strategic direction for next questions
            'reasoning': str,          # Full chain-of-thought
        }
        """
        if not self.client or len(candidates) > 50:
            return self._fallback_analysis(candidates, answers, question_count)

        candidate_titles = [f"{m.get('title')} ({m.get('year')})" for m in candidates[:12]]
        known_answers = {k: v for k, v in answers.items() if v == "yes"}

        prompt = f"""Analyze this film selection space strategically.

REMAINING CANDIDATES ({len(candidates)} films):
{', '.join(candidate_titles)}

WHAT WE KNOW (YES answers):
{json.dumps(known_answers, indent=2) if known_answers else 'Only anchor questions answered'}

QUESTIONS ASKED SO FAR: {question_count}

Your task: Identify what VARIES across these candidates and what would DISCRIMINATE them best.

Think through:
1. What's similar about all these films? (anchors our search)
2. What differs between them? (what we're trying to discriminate)
3. What questions would best separate them into distinct groups?
4. What chains of reasoning would narrow the pool most efficiently?
5. What assumptions might we be making that are wrong?

Be specific: name actual films and explain why a question matters for THIS exact set."""

        try:
            response = self.client.messages.create(
                model=self.model_name,
                max_tokens=600,
                messages=[{"role": "user", "content": prompt}],
            )
            reasoning = response.content[0].text

            # Parse the reasoning into structured parts
            analysis = {
                "full_reasoning": reasoning,
                "patterns": self._extract_section(reasoning, "similar", 2),
                "discriminators": self._extract_section(reasoning, "differ", 3),
                "strategy": self._extract_section(reasoning, "best separate", 3),
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
    def _fallback_analysis(candidates: list, answers: dict, question_count: int) -> dict:
        """Fallback when LLM is unavailable."""
        return {
            "full_reasoning": f"Analyzing {len(candidates)} candidates after {question_count} questions",
            "patterns": "Multiple candidates match current answers",
            "discriminators": "Need targeted plot/trope questions",
            "strategy": "Focus on story elements that vary across remaining films",
        }
