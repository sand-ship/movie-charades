from __future__ import annotations

import json
import math
import uuid
from typing import Optional
from pathlib import Path

from questions import QUESTIONS, QUESTION_MAP, Question, LANGUAGE_QUESTION_IDS, ERA_QUESTION_IDS, GENRE_QUESTION_IDS

# Load engine hints for adaptive questioning strategy
try:
    with open(Path(__file__).parent / 'data' / 'engine_hints.json', 'r') as f:
        ENGINE_HINTS = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    ENGINE_HINTS = {}

MAX_QUESTIONS = 35   # hard ceiling for game length (raised to accommodate director Qs)
MAX_CONSECUTIVE_ACTOR_QS = 2  # limit actor Qs to 2 in a row to avoid battery effect
MIN_QUESTIONS = 12   # minimum non-language/era questions before guessing
GENRE_HOLDOFF = 3    # ask at least this many plot questions before the genre picker fires
ENDGAME_POOL = 8     # at/under this many candidates, prefer soft tropes over IG ordering

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
        self.last_guesses: list[dict] = []  # most recent top_guesses() output

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

    @staticmethod
    def _is_question_available(question: Question, answered: dict) -> bool:
        """Check if a question's requires conditions are met (OR logic for multiple)."""
        if question.requires is None:
            return True
        # Handle both old format (tuple) and new format (list of tuples)
        if isinstance(question.requires, tuple):
            # Single requirement: (question_id, answer)
            return answered.get(question.requires[0]) == question.requires[1]
        else:
            # Multiple requirements (list): OR logic - any condition met = available
            return any(answered.get(cond[0]) == cond[1] for cond in question.requires)

    # ── core algorithm ───────────────────────────────────────────────────

    def next_question(self, session: Session) -> Optional[Question]:
        if session.question_count() >= MAX_QUESTIONS:
            return None

        asked = set(session.asked)

        # Language and era are the only mandatory anchors — they're things the
        # player knows for certain (what language, roughly when).
        if not (asked & LANGUAGE_QUESTION_IDS):
            return QUESTION_MAP['q_hindi']    # sentinel; frontend renders full picker
        if not (asked & ERA_QUESTION_IDS):
            return QUESTION_MAP['q_classic']  # sentinel; frontend renders full picker

        # Count non-language/era questions asked so far (genre counts here now).
        non_anchor = sum(1 for qid in asked
                         if qid not in LANGUAGE_QUESTION_IDS
                         and qid not in ERA_QUESTION_IDS)

        cands = session.candidates

        # Genre picker joins the natural IG pool — but hold it back until we've
        # asked GENRE_HOLDOFF plot questions first (charades: describe before
        # categorise). Once genre has been answered once, suppress the rest.
        genre_answered = bool(asked & GENRE_QUESTION_IDS)
        suppress_genre = genre_answered or (non_anchor < GENRE_HOLDOFF)

        unanswered = [q for q in QUESTIONS
                      if q.id not in asked
                      and q.id not in LANGUAGE_QUESTION_IDS
                      and q.id not in ERA_QUESTION_IDS
                      and (not suppress_genre or q.id not in GENRE_QUESTION_IDS)
                      and self._is_question_available(q, session.answers)]

        splitting = [q for q in unanswered
                     if 0 < sum(1 for m in cands if q.evaluate(m)) < len(cands)]

        # If the last answer was "maybe", ask a confirmation question to convert to yes/no
        # This pins down uncertain answers and reduces candidate pool drift
        if session.asked:
            last_qid = session.asked[-1]
            last_ans = session.answers.get(last_qid)
            if last_ans == "maybe":
                confirm = [q for q in splitting
                          if not q.id.startswith(("q_actor_", "q_actress_", "q_dir_", "q_music_"))
                          and q.id not in GENRE_QUESTION_IDS
                          and q.id != last_qid]

                # Language-specific confirmation routing for better disambiguation
                lang = cands[0].get('language', '') if cands else ''
                if lang == 'Telugu' and last_qid in ['q_genre_romance', 'q_genre_drama']:
                    # Telugu films are 89% romance-heavy: ask about comedy/action distinction
                    lang_specific = [q for q in confirm if q.id in ['q_genre_comedy', 'q_genre_action', 'q_mass_entertainer']]
                    confirm = lang_specific + confirm if lang_specific else confirm
                elif lang == 'Tamil' and 'class' in last_qid.lower():
                    # Tamil films have high class-conflict signal: use it
                    lang_specific = [q for q in confirm if q.id in ['q_class_conflict', 'q_social', 'q_patriotic']]
                    confirm = lang_specific + confirm if lang_specific else confirm
                elif lang == 'Hindi' and last_qid in ['q_genre_romance', 'q_genre_drama']:
                    # Hindi films need thriller distinction
                    lang_specific = [q for q in confirm if q.id in ['q_genre_thriller', 'q_investigation', 'q_crime_protagonist']]
                    confirm = lang_specific + confirm if lang_specific else confirm

                if confirm:
                    # Prefer questions that align with the maybe-answer
                    aligned = [q for q in confirm if q.evaluate(cands[0]) if len(cands) > 0]
                    pool = aligned if aligned else confirm
                    return max(pool, key=lambda q: self._information_gain(cands, q))

        # After actor question gets "yes", lock in hierarchical sub-questions
        # This ensures Chiranjeevi/Vijay/etc. are immediately disambiguated by era/genre
        if session.asked:
            last_qid = session.asked[-1]
            last_ans = session.answers.get(last_qid)
            is_actor_q = last_qid.startswith(('q_actor_', 'q_actress_', 'q_rajini', 'q_chiranjeevi',
                                             'q_vijay', 'q_amitabh', 'q_shah_rukh', 'q_salman',
                                             'q_ajith', 'q_nayanthara', 'q_venkatesh', 'q_kamal_haasan'))
            if is_actor_q and last_ans == "yes":
                # Find hierarchical sub-questions that require this actor=yes
                sub_qs = [q for q in splitting if q.requires == (last_qid, "yes")]
                if sub_qs:
                    return max(sub_qs, key=lambda q: self._information_gain(cands, q))

        # When pool == 1 and we haven't hit the minimum yet, ask confirming
        # questions — builds suspense, lets the player verify before the reveal.
        if not splitting and non_anchor < MIN_QUESTIONS and len(cands) == 1:
            confirm = [q for q in unanswered
                       if not q.id.startswith(("q_actor_", "q_actress_", "q_dir_"))
                       and q.id not in GENRE_QUESTION_IDS]
            if confirm:
                yes_qs = [q for q in confirm if q.evaluate(cands[0])]
                pool = yes_qs if yes_qs else confirm
                return pool[0]

        if not splitting:
            return None  # nothing left discriminates → caller will guess

        # "Other" genre is a broad catch-all — immediately disambiguate with
        # sub-genre questions (historical / horror / sports / bio) before anything else.
        if session.answers.get("q_genre_other") == "yes":
            subs = [q for q in splitting if q.id in OTHER_SUBGENRES]
            if subs:
                return max(subs, key=lambda q: self._information_gain(cands, q))

        # Endgame: once pool is small, exhaust soft tropes first — they describe
        # the film's personality better than a name ever could.
        if len(cands) <= ENDGAME_POOL:
            tropes = [q for q in splitting
                      if getattr(q, "weight", 1.0) < 1.0
                      and not q.id.startswith(("q_actor_", "q_actress_", "q_dir_", "q_music_"))
                      and q.id not in GENRE_QUESTION_IDS]
            if tropes:
                return max(tropes, key=lambda q: self._information_gain(cands, q))

        # Guard: Actor/director questions only when generic questions have failed.
        # Only ask actor Qs if: (first 5 Qs all no) OR (5+ of first 10 are maybe/dunno)
        # EXCEPTION: After Q25, enable director/music questions for disambiguation
        non_anchor_qs = [qid for qid in session.asked
                        if qid not in LANGUAGE_QUESTION_IDS and qid not in ERA_QUESTION_IDS]

        # After 25 questions, director/actress/music questions become available
        # (actress is more memorable to players than music director)
        if len(non_anchor_qs) >= 25:
            directors_enabled = True
            non_persons = [q for q in splitting
                          if not q.id.startswith(("q_actor_",))]  # Keep q_actress_, q_dir_, q_music_
        else:
            directors_enabled = False
            non_persons = [q for q in splitting
                          if not q.id.startswith(("q_actor_", "q_actress_", "q_dir_", "q_music_"))]

        # Calculate when to unlock actor questions
        can_ask_actors = False
        if len(non_anchor_qs) >= 5:
            # Check if first 5 questions are all "no"
            first_five = non_anchor_qs[:5]
            if all(session.answers.get(qid) == "no" for qid in first_five):
                can_ask_actors = True
            # OR check if 5+ of first 10 are "maybe" or "dunno"
            first_ten = non_anchor_qs[:10]
            uncertain = sum(1 for qid in first_ten if session.answers.get(qid) in ("maybe", "dunno"))
            if uncertain >= 5:
                can_ask_actors = True

        # Prefer generic questions unless actor threshold is met
        if non_persons:
            return max(non_persons, key=lambda q: self._information_gain(cands, q))

        # Only reach actor/director questions if generic questions exhausted AND (threshold met OR after Q25)
        if not can_ask_actors and not directors_enabled:
            return None  # Give up rather than ask actor Qs without threshold
        consecutive = 0
        for qid in session.asked[::-1]:
            if qid.startswith(("q_actor_", "q_actress_", "q_dir_", "q_music_")):
                consecutive += 1
            else:
                break
        if consecutive >= MAX_CONSECUTIVE_ACTOR_QS:
            return None  # enough name questions — trigger guess

        # Safe adaptive boost: after pool stabilizes, prioritize actor questions for sparse films
        # Only apply if: past stabilization point (non_anchor >= 5) AND pool still large AND low density
        if non_anchor >= 5 and 10 < len(cands) <= 100 and consecutive < 1:
            # Quick density check: count narrative attributes in first 5 candidates
            sparse_count = 0
            DENSE_ATTRS = ['is_lost_and_found_child', 'is_love_triangle', 'is_partition_backdrop',
                          'is_dance_heavy', 'has_heist', 'is_sports_film', 'has_courtroom', 'is_sci_fi',
                          'has_wedding_plot', 'is_period_film', 'has_investigation_plot']
            for m in cands[:5]:
                if sum(1 for attr in DENSE_ATTRS if m.get(attr)) <= 2:
                    sparse_count += 1

            # If 4+ of top 5 candidates are sparse, boost actor question scoring
            if sparse_count >= 4:
                actor_boost = lambda q: (
                    self._information_gain(cands, q) * 1.5
                    if q.id.startswith(('q_rajini', 'q_venkatesh', 'q_chiranjeevi', 'q_kamal_haasan',
                                       'q_vijay', 'q_amitabh', 'q_ajith', 'q_akshay', 'q_shah_rukh',
                                       'q_pawan_kalyan', 'q_sivakarthikeyan', 'q_ravi_teja', 'q_nani',
                                       'q_salman', 'q_dhanush', 'q_suriya', 'q_kajal', 'q_nayanthara'))
                    else self._information_gain(cands, q)
                )
                return max(splitting, key=actor_boost)

        # Discriminating field strategy: Priority-ordered placement across 3 phases
        # Phase 1 (Q1-10): Actor | Phase 2 (Q10-20): Actress/Director | Phase 3 (Q20-30): Music Director
        # Rotate based on what's not been asked yet

        # Count non-anchor Qs to determine phase
        current_non_anchor = len([qid for qid in session.asked
                                 if qid not in LANGUAGE_QUESTION_IDS and qid not in ERA_QUESTION_IDS])
        current_phase = 0 if current_non_anchor < 10 else (1 if current_non_anchor < 20 else 2)

        # Check which discrim fields have been asked
        discrim_asked = {'actor': False, 'actress': False, 'director': False, 'music': False}
        for qid in session.asked:
            if qid.startswith("q_actor_"):
                discrim_asked['actor'] = True
            elif qid.startswith("q_actress_"):
                discrim_asked['actress'] = True
            elif qid.startswith("q_dir_"):
                discrim_asked['director'] = True
            elif qid.startswith("q_music_"):
                discrim_asked['music'] = True

        # Determine which field to ask based on phase and priority
        priority_field = None
        if current_phase == 0 and not discrim_asked['actor']:  # Phase 1: Priority is actor
            priority_field = 'actor'
        elif current_phase == 1 and not discrim_asked['actress'] and not discrim_asked['director']:  # Phase 2: actress or director
            priority_field = 'actress' if not discrim_asked['actress'] else 'director'
        elif current_phase == 2 and not discrim_asked['music']:  # Phase 3: music director
            priority_field = 'music'
        elif current_phase == 1 and not discrim_asked['director'] and discrim_asked['actress']:  # Phase 2 fallback: director if actress done
            priority_field = 'director'
        elif current_phase == 2 and discrim_asked['music']:  # Phase 3 rotation: go back to earlier fields if music done
            # Rotate through actress, director, actor in that order
            if not discrim_asked['actress']:
                priority_field = 'actress'
            elif not discrim_asked['director']:
                priority_field = 'director'
            elif not discrim_asked['actor']:
                priority_field = 'actor'

        # If we have a priority field, filter to it
        if priority_field and splitting:
            field_map = {
                "actor": lambda q: q.id.startswith("q_actor_"),
                "actress": lambda q: q.id.startswith("q_actress_"),
                "director": lambda q: q.id.startswith("q_dir_"),
                "music": lambda q: q.id.startswith("q_music_"),
            }

            priority_qs = [q for q in splitting if field_map[priority_field](q)]
            if priority_qs:
                return max(priority_qs, key=lambda q: self._information_gain(cands, q))

        return max(splitting, key=lambda q: self._information_gain(cands, q))

    @staticmethod
    def _is_identifying(question: Question) -> bool:
        """Specific 'who made it' questions (heroine/actor/director/music director)
        and sub-genre tropes (weight < 1.0) — the discriminators a human reaches
        for in the endgame."""
        return (question.id.startswith(("q_actor_", "q_actress_", "q_dir_", "q_music_"))
                or getattr(question, "weight", 1.0) < 1.0)

    def apply_answer(self, session: Session, question_id: str, answer: str) -> None:
        """answer: 'yes' | 'no' | 'maybe' | 'dunno'
        'dunno' is tracked as asked but not scored (doesn't affect candidate filtering).
        'maybe' is recorded and scored as weak 'yes'."""
        added = [question_id]
        session.asked.append(question_id)

        # Dunno: mark as asked (so we don't ask again) but don't score it
        if answer == "dunno":
            session.history.append(added)
            return

        session.answers[question_id] = answer

        # Auto-answer "no" to siblings of mutually-exclusive groups. A film has
        # exactly one language, one era, and one lead music director.
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
        non_anchor = sum(1 for qid in asked_set
                         if qid not in LANGUAGE_QUESTION_IDS
                         and qid not in ERA_QUESTION_IDS)
        if non_anchor < MIN_QUESTIONS:
            return False
        # next_question returning None drives the actual guess trigger.
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
        session.last_guesses = result
        return result

    def _fit(self, movie: dict, session: Session) -> tuple[int, int]:
        """(agreements, answered) over substantive yes/no/maybe answers — excludes
        the language/era/genre pickers, so confidence reflects discriminating questions.
        'maybe' answers count as half-agreement when they match."""
        group = LANGUAGE_QUESTION_IDS | ERA_QUESTION_IDS | GENRE_QUESTION_IDS
        agree = answered = 0
        for qid, ans in session.answers.items():
            if qid in group:
                continue
            q = QUESTION_MAP.get(qid)
            if not q:
                continue
            answered += 1
            match = q.evaluate(movie)
            if (ans == "yes" and match) or (ans == "no" and not match):
                agree += 1
            elif ans == "maybe" and match:
                agree += 0.5  # weak agreement
        return int(agree), answered

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
            w = q.weight  # 1.0 = hard signal, 0.3 = soft trope
            # Strong answers (yes/no): full weight
            pos_strong = 1.0 + w
            neg_strong = 1.0 - w * 0.9
            # Maybe: weak yes (0.5 strength positive, no penalty)
            pos_maybe = 1.0 + w * 0.5
            neg_maybe = 1.0  # no penalty when wrong
            if answer == "yes" and match:
                score *= pos_strong
            elif answer == "yes" and not match:
                score *= neg_strong
            elif answer == "no" and not match:
                score *= pos_strong
            elif answer == "no" and match:
                score *= neg_strong
            elif answer == "maybe" and match:
                score *= pos_maybe
            elif answer == "maybe" and not match:
                score *= neg_maybe
        return score
