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
MAX_CONSECUTIVE_ACTOR_QS = 1  # limit actor Qs to 1 in a row for breathing room (force plot after each)
MIN_QUESTIONS = 12   # minimum non-language/era questions before guessing
GENRE_HOLDOFF = 0    # genre picker fires immediately after language/era for early pool narrowing
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
        self.answers: dict[str, str] = {}  # question_id -> yes/no/maybe
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

    def _get_established_genres(self, session: Session) -> set[str]:
        """Return genres the player has already confirmed (via YES answers to genre Qs)."""
        genres = set()
        if session.answers.get("q_genre_scifi") == "yes":
            genres.add("scifi")
        if session.answers.get("q_genre_action") == "yes":
            genres.add("action")
        if session.answers.get("q_genre_romance") == "yes":
            genres.add("romance")
        if session.answers.get("q_genre_comedy") == "yes":
            genres.add("comedy")
        if session.answers.get("q_genre_drama") == "yes":
            genres.add("drama")
        if session.answers.get("q_genre_horror") == "yes":
            genres.add("horror")
        return genres

    def _get_genre_aligned_questions(self, genres: set[str], unanswered: list[Question]) -> list[Question]:
        """Return questions aligned to the established genres (primary + secondary)."""
        if not genres:
            return []

        genre_to_qids = {
            "scifi": {"q_superpowers", "q_scifi_fantasy"},
            "action": {"q_villain", "q_revenge", "q_betrayal"},
            "romance": {"q_forbidden_love", "q_reluctant_romance", "q_love_triangle"},
            "comedy": {"q_mass_entertainer"},
            "drama": {"q_patriarchal_resistance", "q_social", "q_male_vulnerability", "q_parent_child"},
            "horror": {"q_horror"},
        }

        aligned_qids = set()
        for genre in genres:
            aligned_qids.update(genre_to_qids.get(genre, set()))

        return [q for q in unanswered if q.id in aligned_qids]

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

        # Force structural question by Q5 for early discriminating field unlock
        non_anchor = sum(1 for qid in asked
                         if qid not in LANGUAGE_QUESTION_IDS
                         and qid not in ERA_QUESTION_IDS)

        # Genre picker: return it when holdoff is satisfied and no genre answered yet
        # (With GENRE_HOLDOFF=0, this fires immediately after language/era)
        genre_answered = bool(asked & GENRE_QUESTION_IDS)
        if "q_genre_picker" not in asked and non_anchor >= GENRE_HOLDOFF and not genre_answered:
            return QUESTION_MAP.get("q_genre_picker")

        if "q_multiple_protagonists" not in asked and 2 <= non_anchor < 5:
            return QUESTION_MAP.get("q_multiple_protagonists")

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

        # Suppress questions incompatible with confirmed genre
        # Comedy films don't have: patriarchy, gritty, crime, gangster themes
        if session.answers.get("q_genre_comedy") == "yes":
            incompatible_with_comedy = {"q_patriarchal_resistance", "q_gritty_realism", "q_crime_protagonist",
                                       "q_gangster_world", "q_suspense_thriller", "q_investigation"}
            unanswered = [q for q in unanswered if q.id not in incompatible_with_comedy]

        # Limit music director questions (ask max 2, they're rarely discriminating)
        music_asked = sum(1 for qid in session.asked if qid.startswith("q_music_"))
        if music_asked >= 2:
            unanswered = [q for q in unanswered if not q.id.startswith("q_music_")]

        splitting = [q for q in unanswered
                     if 0 < sum(1 for m in cands if q.evaluate(m)) < len(cands)]

        # Genre-aware prioritization: primary → secondary → primary → generic → discriminating
        established_genres = self._get_established_genres(session)
        if established_genres:
            non_anchor_qs = [qid for qid in session.asked
                           if qid not in LANGUAGE_QUESTION_IDS and qid not in ERA_QUESTION_IDS]
            q_count = len(non_anchor_qs)

            # Phase 1 (Q1-5): Primary genre questions
            if q_count < 5:
                aligned = self._get_genre_aligned_questions(established_genres, splitting)
                if aligned:
                    return max(aligned, key=lambda q: self._information_gain(cands, q))

            # Phase 2 (Q5-7): One secondary genre question (if multiple genres confirmed)
            elif q_count < 7 and len(established_genres) > 1:
                # Ask from secondary genres (not the first one)
                primary_genre = next(iter(established_genres))  # Arbitrary "primary"
                secondary_genres = established_genres - {primary_genre}
                secondary_aligned = self._get_genre_aligned_questions(secondary_genres, splitting)
                if secondary_aligned:
                    return max(secondary_aligned, key=lambda q: self._information_gain(cands, q))

            # Phase 3 (Q7-10): Another primary genre question
            elif q_count < 10:
                aligned = self._get_genre_aligned_questions(established_genres, splitting)
                if aligned:
                    return max(aligned, key=lambda q: self._information_gain(cands, q))

        # Enforce phase gating: restrict discriminating questions by phase
        # Phase 1 (Q1-10): Actor only | Phase 2 (Q10-20): Actress/Director | Phase 3 (Q20+): Music
        non_anchor_qs = [qid for qid in session.asked
                         if qid not in LANGUAGE_QUESTION_IDS and qid not in ERA_QUESTION_IDS]
        current_phase = 0 if len(non_anchor_qs) < 10 else (1 if len(non_anchor_qs) < 20 else 2)

        if current_phase == 0:  # Phase 1: only actor Qs
            splitting = [q for q in splitting if not q.id.startswith(("q_actress_", "q_director_", "q_music_"))]
        elif current_phase == 1:  # Phase 2: actress/director only (no music yet)
            splitting = [q for q in splitting if not q.id.startswith("q_music_")]

        # ACTOR UNLOCK: Relax gating for regional cinema where actors discriminate well
        can_ask_actors = False

        # Unlock actors at Q6+ if: 3+ NOs (rare film) OR 2-3 unsures (ambiguous film)
        if len(non_anchor_qs) >= 5:
            first_five = non_anchor_qs[:5]
            nos = sum(1 for qid in first_five if session.answers.get(qid) == "no")
            unsures = sum(1 for qid in first_five if session.answers.get(qid) == "maybe")
            if nos >= 3 or 2 <= unsures <= 3:
                can_ask_actors = True

        # Force actor at Q10 if not asked yet
        if len(non_anchor_qs) >= 10:
            actor_asked = any(qid.startswith(("q_actor_", "q_actress_")) for qid in session.asked)
            if not actor_asked:
                actor_qs = [q for q in splitting if q.id.startswith(("q_actor_", "q_actress_"))]
                if actor_qs:
                    return max(actor_qs, key=lambda q: self._information_gain(cands, q))


        # After person question YES, suppress all person Qs for 1-2 turns for breathing room
        if session.asked:
            last_qid = session.asked[-1]
            last_ans = session.answers.get(last_qid)
            is_person_q = last_qid.startswith(("q_actor_", "q_actress_", "q_director_", "q_music_",
                                             "q_rajini", "q_chiranjeevi", "q_vijay", "q_amitabh",
                                             "q_shah_rukh", "q_salman", "q_ajith", "q_nayanthara",
                                             "q_venkatesh", "q_kamal_haasan", "q_pawan_kalyan",
                                             "q_sivakarthikeyan", "q_ravi_teja", "q_nani",
                                             "q_dhanush", "q_suriya", "q_kajal", "q_akshay"))
            if is_person_q and last_ans == "yes":
                # Count only GENERIC questions since last person YES (skip all person Qs including sub-Qs)
                generic_since_person_yes = 0
                for qid in session.asked[::-1]:
                    if qid.startswith(("q_actor_", "q_actress_", "q_director_", "q_music_",
                                      "q_rajini", "q_chiranjeevi", "q_vijay", "q_amitabh",
                                      "q_shah_rukh", "q_salman", "q_ajith", "q_nayanthara",
                                      "q_venkatesh", "q_kamal_haasan", "q_pawan_kalyan",
                                      "q_sivakarthikeyan", "q_ravi_teja", "q_nani",
                                      "q_dhanush", "q_suriya", "q_kajal", "q_akshay")):
                        break  # Stop counting at ANY person Q (including sub-Qs)
                    generic_since_person_yes += 1

                # If < 2 generic questions: suppress ALL person Qs (actors, sub-Qs, director, music)
                if generic_since_person_yes < 2:
                    generic_qs = [q for q in splitting
                                 if not q.id.startswith(("q_actor_", "q_actress_", "q_director_", "q_music_"))
                                 and not q.id.startswith(("q_rajini", "q_chiranjeevi", "q_vijay", "q_amitabh",
                                                         "q_shah_rukh", "q_salman", "q_ajith", "q_nayanthara",
                                                         "q_venkatesh", "q_kamal_haasan", "q_pawan_kalyan",
                                                         "q_sivakarthikeyan", "q_ravi_teja", "q_nani",
                                                         "q_dhanush", "q_suriya", "q_kajal", "q_akshay"))]
                    if generic_qs:
                        return max(generic_qs, key=lambda q: self._information_gain(cands, q))
                # If 2+ generic questions: FORCE director/music (best discriminators for overlaps)
                else:
                    director_music = [q for q in splitting
                                     if q.id.startswith(("q_director_", "q_music_"))]
                    if director_music:
                        return max(director_music, key=lambda q: self._information_gain(cands, q))

        # If the last answer was "unsure", ask a confirmation question to convert to yes/no
        # This pins down uncertain answers and reduces candidate pool drift
        if session.asked:
            last_qid = session.asked[-1]
            last_ans = session.answers.get(last_qid)
            if last_ans == "maybe":
                # Ask clarifying questions specifically for the uncertain attribute
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
                    # Prefer questions that align with the maybe-answer to push toward yes/no
                    aligned = [q for q in confirm if q.evaluate(cands[0]) if len(cands) > 0]
                    pool = aligned if aligned else confirm
                    return max(pool, key=lambda q: self._information_gain(cands, q))
                # If no follow-up clarification possible, force actor question to break tie
                if can_ask_actors:
                    all_actors = [q for q in unanswered if q.id.startswith(("q_actor_", "q_actress_"))]
                    if all_actors:
                        return max(all_actors, key=lambda q: self._information_gain(cands, q))

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
        # Only ask actor Qs if: (first 5 Qs all no) OR (5+ of first 10 are unsure)
        # EXCEPTION: After Q25, enable director/music questions for disambiguation
        non_anchor_qs = [qid for qid in session.asked
                        if qid not in LANGUAGE_QUESTION_IDS and qid not in ERA_QUESTION_IDS]

        # After 15 questions, director/actress/music questions become available
        # (earlier than Q25 to ensure escalation if pool still large)
        if len(non_anchor_qs) >= 15:
            directors_enabled = True
            non_persons = [q for q in splitting
                          if not q.id.startswith(("q_actor_",))]  # Keep q_actress_, q_dir_, q_music_
        else:
            directors_enabled = False
            non_persons = [q for q in splitting
                          if not q.id.startswith(("q_actor_", "q_actress_", "q_dir_", "q_music_"))]

        # Actor discrimination enabled early (Q5+, 15+ candidates)?
        # But respect consecutive actor limit (breathe with plot questions between)
        if can_ask_actors:
            # Check consecutive actor limit BEFORE asking actors
            consecutive = 0
            for qid in session.asked[::-1]:
                if qid.startswith(("q_actor_", "q_actress_", "q_director_", "q_music_")):
                    consecutive += 1
                else:
                    break

            # Only ask actor if not at consecutive limit
            if consecutive < MAX_CONSECUTIVE_ACTOR_QS:
                actors_in_splitting = [q for q in splitting if q.id.startswith(("q_actor_", "q_actress_"))]
                if actors_in_splitting:
                    return max(actors_in_splitting, key=lambda q: self._information_gain(cands, q))
                # If no actors split, ask ANY unanswered actor question (direct identification)
                all_actors = [q for q in unanswered if q.id.startswith(("q_actor_", "q_actress_"))]
                if all_actors:
                    return max(all_actors, key=lambda q: self._information_gain(cands, q))

        # Prefer generic questions before discriminating fields unlocked
        if non_persons:
            return max(non_persons, key=lambda q: self._information_gain(cands, q))

        # Only reach actor/director questions if generic questions exhausted AND (threshold met OR after Q15)
        # DESPERATE ESCALATION: After Q30, force actors/directors regardless of pool size
        if not can_ask_actors and not directors_enabled:
            if len(non_anchor_qs) >= 30:
                can_ask_actors = True  # Desperate: ask actors in endgame
                directors_enabled = True  # Also enable directors
            else:
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
        """answer: 'yes' | 'no' | 'unsure'
        'unsure' is recorded and scored as weak signal (0.5x weight compared to hard yes/no)."""
        added = [question_id]
        session.asked.append(question_id)

        # Map 'unsure' to 'maybe' for internal consistency with scoring logic
        if answer == "unsure":
            answer = "maybe"

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

    def _genre_ok(self, movie: dict, session: Session) -> bool:
        """Hard-gate on genre: if player says YES to a genre, only keep films with that genre."""
        genre_answers = {qid: ans for qid, ans in session.answers.items() if qid.startswith("q_genre_")}

        for qid, ans in genre_answers.items():
            if ans == "yes":
                q = QUESTION_MAP.get(qid)
                if q and not q.evaluate(movie):
                    return False  # Film doesn't match the genre player selected
        return True

    def _prune(self, session: Session) -> None:
        # Hard constraints first (decisive facts + genre), then soft scoring within them.
        eligible = [m for m in self.movies if self._hard_ok(m, session) and self._genre_ok(m, session)]
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
        """(agreements, answered) over substantive yes/no/unsure answers — excludes
        the language/era/genre pickers, so confidence reflects discriminating questions.
        'unsure' answers count as half-agreement when they match."""
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
