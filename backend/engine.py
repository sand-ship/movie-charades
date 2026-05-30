from __future__ import annotations

import math
import uuid
from typing import Optional

from questions import QUESTIONS, QUESTION_MAP, Question, LANGUAGE_QUESTION_IDS, ERA_QUESTION_IDS, GENRE_QUESTION_IDS

MAX_QUESTIONS = 42  # hard ceiling (incl. ~6 auto-answered siblings → ~36 real questions)
MIN_NON_GROUP_QUESTIONS = 10        # fallback when not all 3 group pickers answered
MIN_NON_GROUP_AFTER_ALL_PICKERS = 15 # ask at least 15 real questions — builds suspense,
                                     # gives tropes room to fire before the guess
ENDGAME_POOL = 25  # at/under this many candidates, switch to *identifying* questions
                   # (heroine / actor / director / music director / sub-genre tropes).
                   # Raised from 12 — classic-era pools stay larger (many similar films)
                   # and need the actor/director question earlier to break ties.

# Sub-genres folded into the catch-all "Other" theme picker — asked up front to
# disambiguate it when the user picks Other.
OTHER_SUBGENRES = {"q_historical", "q_horror", "q_sports", "q_bio"}

# Each mismatched answer scores 0.05x relative to a perfect match (see _score:
# 0.1 vs 2.0). A cutoff of 0.04 keeps any movie within ONE disagreement of the
# best and prunes those that disagree on two or more — tight enough that strong
# signals (language, lead actor/actress) stay decisive and the pool actually
# converges, while still tolerating a single label error or off-answer. (0.002 /
# two-disagreement tolerance was tried and left hundreds of candidates that
# never narrowed.) "Ask more before guessing" is handled by the min-question
# floor + honest confidence below, not by loosening this.
SOFT_KEEP_RATIO = 0.04


class Session:
    def __init__(self, movies: list[dict]):
        self.id = str(uuid.uuid4())
        self.candidates: list[dict] = list(movies)
        self.asked: list[str] = []
        self.answers: dict[str, str] = {}  # question_id -> yes/no/dunno
        self.history: list[list[str]] = []  # per-turn qids added (for Back/undo)

    def remaining_count(self) -> int:
        return len(self.candidates)

    def question_count(self) -> int:
        return len(self.asked)


class GameEngine:
    def __init__(self, movies: list[dict]):
        self.movies = movies
        self._sessions: dict[str, Session] = {}

    # ── session management ──────────────────────────────────────────────

    def new_session(self) -> Session:
        s = Session(self.movies)
        self._sessions[s.id] = s
        return s

    def get_session(self, session_id: str) -> Optional[Session]:
        return self._sessions.get(session_id)

    # ── core algorithm ───────────────────────────────────────────────────

    def next_question(self, session: Session) -> Optional[Question]:
        if session.question_count() >= MAX_QUESTIONS:
            return None

        asked = set(session.asked)
        lang_asked  = bool(asked & LANGUAGE_QUESTION_IDS)
        era_asked   = bool(asked & ERA_QUESTION_IDS)
        genre_asked = bool(asked & GENRE_QUESTION_IDS)

        # Always ask language → era → genre as group pickers before free questions
        if not lang_asked:
            return QUESTION_MAP['q_hindi']       # sentinel; frontend renders full picker
        if not era_asked:
            return QUESTION_MAP['q_classic']     # sentinel; frontend renders full picker
        if not genre_asked:
            return QUESTION_MAP['q_genre_action'] # sentinel; frontend renders full picker

        unanswered = [q for q in QUESTIONS
                      if q.id not in asked
                      and q.id not in LANGUAGE_QUESTION_IDS
                      and q.id not in ERA_QUESTION_IDS
                      and q.id not in GENRE_QUESTION_IDS]
        cands = session.candidates
        # Only ask questions that actually split the remaining pool — a question
        # all candidates answer the same way teaches us nothing.
        splitting = [q for q in unanswered
                     if 0 < sum(1 for m in cands if q.evaluate(m)) < len(cands)]

        # When pool == 1 and we haven't hit the question minimum yet, keep asking
        # confirming questions about the sole candidate — builds suspense and lets
        # the player verify the answer themselves before we reveal it.
        asked_set = set(session.asked)
        non_group = sum(1 for qid in asked_set
                        if qid not in LANGUAGE_QUESTION_IDS
                        and qid not in ERA_QUESTION_IDS
                        and qid not in GENRE_QUESTION_IDS)
        all_pickers_done = (bool(asked_set & LANGUAGE_QUESTION_IDS) and
                            bool(asked_set & ERA_QUESTION_IDS) and
                            bool(asked_set & GENRE_QUESTION_IDS))
        min_q = MIN_NON_GROUP_AFTER_ALL_PICKERS if all_pickers_done else MIN_NON_GROUP_QUESTIONS

        if not splitting and non_group < min_q and len(cands) == 1:
            # Ask interesting confirming questions about the one remaining film
            confirm = [q for q in unanswered
                       if not q.id.startswith(("q_actor_", "q_actress_", "q_dir_", "q_music_"))
                       and q.id not in LANGUAGE_QUESTION_IDS
                       and q.id not in ERA_QUESTION_IDS
                       and q.id not in GENRE_QUESTION_IDS]
            if confirm:
                # Prefer questions the film answers "yes" to — more interesting for the player
                yes_qs = [q for q in confirm if q.evaluate(cands[0])]
                pool = yes_qs if yes_qs else confirm
                return pool[0]

        if not splitting:
            return None  # nothing left discriminates → caller will guess

        # The "Other" theme is a catch-all (historical/horror/sports/sci-fi/biopic
        # ~400 films) so it barely narrows. If the user picked it, immediately
        # disambiguate with the sub-genre questions before anything else — these
        # are low-prevalence so information gain would otherwise never ask them.
        if session.answers.get("q_genre_other") == "yes":
            subs = [q for q in splitting if q.id in OTHER_SUBGENRES]
            if subs:
                return max(subs, key=lambda q: self._information_gain(cands, q))

        # Endgame: once the pool is small, broad 50/50 tropes (action? songs?)
        # stop helping. What a human asks now is *identifying* — the heroine,
        # hero, director — plus sub-genre tropes. Prefer those; information gain
        # alone never picks them because they're low-prevalence. Music director
        # is deprioritized (many players don't know the composer) — asked only
        # when nothing else can separate the finalists.
        if len(cands) <= ENDGAME_POOL:
            identifying = [q for q in splitting if self._is_identifying(q)]
            non_music = [q for q in identifying if not q.id.startswith("q_music_")]
            preferred = non_music or identifying
            if preferred:
                return max(preferred, key=lambda q: self._information_gain(cands, q))
        return max(splitting, key=lambda q: self._information_gain(cands, q))

    @staticmethod
    def _is_identifying(question: Question) -> bool:
        """Specific 'who made it' questions (heroine/actor/director/music director)
        and sub-genre tropes (weight < 1.0) — the discriminators a human reaches
        for in the endgame."""
        return (question.id.startswith(("q_actor_", "q_actress_", "q_dir_", "q_music_"))
                or getattr(question, "weight", 1.0) < 1.0)

    def apply_answer(self, session: Session, question_id: str, answer: str) -> None:
        """answer: 'yes' | 'no' | 'dunno'"""
        added = [question_id]
        session.asked.append(question_id)
        session.answers[question_id] = answer

        # Auto-answer "no" to siblings of mutually-exclusive groups. A film has
        # exactly one language and one era, so those siblings are safe to settle.
        # Genre is NOT mutually exclusive (a film can be comedy AND drama), so we
        # never auto-no genre siblings — that was eliminating multi-genre films.
        if answer == "yes":
            group: Optional[set] = None
            if question_id in LANGUAGE_QUESTION_IDS:
                group = LANGUAGE_QUESTION_IDS
            elif question_id in ERA_QUESTION_IDS:
                group = ERA_QUESTION_IDS
            if group:
                for sibling_id in group:
                    if sibling_id != question_id and sibling_id not in session.asked:
                        session.asked.append(sibling_id)
                        session.answers[sibling_id] = "no"
                        added.append(sibling_id)

        session.history.append(added)  # record this turn so Back can undo it
        # Soft pruning: rescore the whole pool and keep every movie within one
        # disagreement of the best fit. No single answer permanently removes a
        # candidate, so a movie wrongly demoted early can recover later.
        self._prune(session)

    def undo_last(self, session: Session) -> bool:
        """Revert the most recent answered turn (and its auto-answered siblings),
        recompute candidates, and report whether anything was undone."""
        if not session.history:
            return False
        last = set(session.history.pop())
        session.asked = [q for q in session.asked if q not in last]
        for qid in last:
            session.answers.pop(qid, None)
        self._prune(session)
        return True

    @staticmethod
    def _is_decisive(qid: str) -> bool:
        # Categorical facts a user is sure about: a "yes" here is a hard filter.
        return (qid in LANGUAGE_QUESTION_IDS or qid in ERA_QUESTION_IDS
                or qid.startswith(("q_actor_", "q_actress_", "q_dir_")))

    def _hard_ok(self, movie: dict, session: Session) -> bool:
        """A movie is eligible only if it satisfies every decisive 'yes' answer
        (language / era / lead actor / lead actress / director). 'no' answers on
        these stay soft — a user may be unsure or the label may be wrong."""
        for qid, ans in session.answers.items():
            if ans == "yes" and self._is_decisive(qid):
                q = QUESTION_MAP.get(qid)
                if q and not q.evaluate(movie):
                    return False
        return True

    def _prune(self, session: Session) -> None:
        # Hard constraints first (decisive facts), then soft scoring within them.
        eligible = [m for m in self.movies if self._hard_ok(m, session)]
        if not eligible:  # contradictory answers — don't wipe the board
            eligible = list(self.movies)
        scored = [(m, self._score(m, session)) for m in eligible]
        max_score = max((s for _, s in scored), default=0.0)
        if max_score <= 0:
            session.candidates = eligible
            return
        cutoff = max_score * SOFT_KEEP_RATIO
        session.candidates = [m for m, s in scored if s >= cutoff]

    def should_guess(self, session: Session) -> bool:
        if session.question_count() >= MAX_QUESTIONS or session.remaining_count() == 0:
            return True
        asked_set = set(session.asked)
        non_group = sum(
            1 for qid in asked_set
            if qid not in LANGUAGE_QUESTION_IDS
            and qid not in ERA_QUESTION_IDS
            and qid not in GENRE_QUESTION_IDS
        )
        all_pickers_done = (
            bool(asked_set & LANGUAGE_QUESTION_IDS) and
            bool(asked_set & ERA_QUESTION_IDS) and
            bool(asked_set & GENRE_QUESTION_IDS)
        )
        min_q = MIN_NON_GROUP_AFTER_ALL_PICKERS if all_pickers_done else MIN_NON_GROUP_QUESTIONS
        if non_group < min_q:
            return False
        # Even when the pool is 1 we keep asking confirming questions until the
        # minimum is met — the player should feel properly interrogated, not rushed.
        # next_question will keep generating questions about the single candidate
        # (confirming tropes, songs, lead actress, director) until it runs out,
        # at which point it returns None and main.py triggers the guess.
        # MAX_QUESTIONS is the hard backstop.
        return False

    def top_guesses(self, session: Session, n: int = 3) -> list[dict]:
        candidates = session.candidates or self.movies
        scored = [
            {**m, "_score": self._score(m, session)}
            for m in candidates
        ]
        scored.sort(key=lambda x: x["_score"], reverse=True)
        top = scored[:n]

        result = []
        for i, m in enumerate(top):
            agree, answered = self._fit(m, session)
            if answered:
                # Absolute fit: what fraction of the substantive answers this
                # film actually matches. A poorly-matching best guess (e.g. the
                # real film isn't in the catalog) reads as low confidence, not 100%.
                conf = round(100 * agree / answered)
            else:
                conf = 100 - i * 20  # only pickers answered — rank-based fallback
            result.append({
                "id": m["id"], "title": m["title"], "year": m["year"],
                "language": m["language"], "director": m["director"],
                "lead_actor": m["lead_actor"], "imdb_rating": m["imdb_rating"],
                "confidence": conf,
            })
        return result

    def _fit(self, movie: dict, session: Session) -> tuple[int, int]:
        """(agreements, answered) over substantive yes/no answers — excludes
        'dunno' and the language/era/genre pickers, so confidence reflects the
        discriminating questions rather than easy auto-answered constraints."""
        group = LANGUAGE_QUESTION_IDS | ERA_QUESTION_IDS | GENRE_QUESTION_IDS
        agree = answered = 0
        for qid, ans in session.answers.items():
            if ans == "dunno" or qid in group:
                continue
            q = QUESTION_MAP.get(qid)
            if not q:
                continue
            answered += 1
            match = q.evaluate(movie)
            if (ans == "yes" and match) or (ans == "no" and not match):
                agree += 1
        return agree, answered

    # ── information gain ─────────────────────────────────────────────────

    def _information_gain(self, candidates: list[dict], question: Question) -> float:
        n = len(candidates)
        if n == 0:
            return 0.0
        yes = [m for m in candidates if question.evaluate(m)]
        no = [m for m in candidates if not question.evaluate(m)]
        p_yes, p_no = len(yes) / n, len(no) / n
        gain = self._entropy(n) - (p_yes * self._entropy(len(yes)) + p_no * self._entropy(len(no)))
        # penalise questions that split trivially (all yes or all no)
        if len(yes) == 0 or len(no) == 0:
            return -1.0
        return gain

    @staticmethod
    def _entropy(n: int) -> float:
        return math.log2(n) if n > 1 else 0.0

    def _score(self, movie: dict, session: Session) -> float:
        score = 1.0
        for qid, answer in session.answers.items():
            q = QUESTION_MAP.get(qid)
            if not q:
                continue
            match = q.evaluate(movie)
            w = q.weight           # 1.0 = hard signal, 0.3 = soft trope
            pos = 1.0 + w          # weight 1.0 → 2.0,  weight 0.3 → 1.3
            neg = 1.0 - w * 0.9   # weight 1.0 → 0.1,  weight 0.3 → 0.73
            if answer == "yes" and match:
                score *= pos
            elif answer == "no" and not match:
                score *= pos
            elif answer == "yes" and not match:
                score *= neg
            elif answer == "no" and match:
                score *= neg
        return score
