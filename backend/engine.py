from __future__ import annotations

import json
import math
import random
import uuid
from typing import Optional
from pathlib import Path

from questions import (QUESTION_MAP, Question, LANGUAGE_QUESTION_IDS, ERA_QUESTION_IDS,
                       GENRE_QUESTION_IDS, ENDING_QUESTION_IDS, SETTING_QUESTION_IDS, VILLAIN_QUESTION_IDS)
import questions  # Import module to access QUESTIONS at runtime (for dynamic actor/director Qs)
from reasoning import CotReasoner
from cluster_discrimination import get_discriminator

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
        self.reasoning_log: list[dict] = []  # COT reasoning per turn
        self.strategic_analysis: Optional[dict] = None  # current strategic guidance
        self.maybe_count: int = 0  # Track unsure answers (max 5)
        self.maybe_exhausted: bool = False  # True after 5 maybes
        self.was_stumped: bool = False  # Track if game was already marked stumped

    def remaining_count(self) -> int:
        return len(self.candidates)

    def question_count(self) -> int:
        return len(self.asked)


class GameEngine:
    def __init__(self, movies: list[dict]):
        self.movies = movies
        self._sessions: dict[str, Session] = {}
        self.reasoner = CotReasoner()

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
            "romance": {"q_forbidden_love", "q_reluctant_romance", "q_love_triangle", "q_infidelity"},
            "comedy": {"q_mass_entertainer", "q_protagonist_married", "q_rural_setting", "q_urban_setting", "q_double_role", "q_conman", "q_class_pretense", "q_costar_sanjay_dutt", "q_costar_anil_kapoor", "q_costar_karisma_kapoor"},
            "drama": {"q_patriarchal_resistance", "q_social", "q_male_vulnerability", "q_parent_child", "q_protagonist_married"},
            "horror": {"q_horror"},
        }

        aligned_qids = set()
        for genre in genres:
            aligned_qids.update(genre_to_qids.get(genre, set()))

        return [q for q in unanswered if q.id in aligned_qids]

    # ── strategic reasoning ──────────────────────────────────────────────

    def _should_analyze_strategy(self, session: Session) -> bool:
        """Check if we should trigger strategic analysis (every 5 questions or at transitions)."""
        q_count = len(session.asked)
        c_count = len(session.candidates)

        if q_count in [8, 15, 20, 25]:
            return True
        if c_count <= 10 and c_count % 5 == 0:
            return True
        if not session.strategic_analysis and q_count >= 8:
            return True
        return False

    def _update_strategic_analysis(self, session: Session) -> None:
        """Update strategic guidance based on current game state."""
        if len(session.candidates) <= 1:
            return
        session.strategic_analysis = self.reasoner.analyze_candidate_space(
            candidates=session.candidates,
            answers=session.answers,
            question_count=len(session.asked),
        )
        session.reasoning_log.append({
            "turn": len(session.asked),
            "analysis": session.strategic_analysis,
        })

    # ── core algorithm ───────────────────────────────────────────────────

    def next_question(self, session: Session) -> Optional[Question]:
        if session.question_count() >= MAX_QUESTIONS:
            return None

        # Trigger strategic analysis at key transitions
        if self._should_analyze_strategy(session):
            self._update_strategic_analysis(session)

        asked = set(session.asked)

        if not (asked & LANGUAGE_QUESTION_IDS):
            q = QUESTION_MAP['q_hindi']
            self._log_question_reasoning(session, q, "language anchor (step 1)")
            return q
        if not (asked & ERA_QUESTION_IDS):
            q = QUESTION_MAP['q_classic']
            self._log_question_reasoning(session, q, "era anchor (step 2)")
            return q

        non_anchor = sum(1 for qid in asked
                         if qid not in LANGUAGE_QUESTION_IDS
                         and qid not in ERA_QUESTION_IDS)

        genre_answered = bool(asked & GENRE_QUESTION_IDS)
        if "q_genre_picker" not in asked and non_anchor >= GENRE_HOLDOFF and not genre_answered:
            q = QUESTION_MAP.get("q_genre_picker")
            self._log_question_reasoning(session, q, "genre anchor (step 3)")
            return q

        if "q_multiple_protagonists" not in asked and 2 <= non_anchor < 5:
            q = QUESTION_MAP.get("q_multiple_protagonists")
            self._log_question_reasoning(session, q, "structural question (protagonist count)")
            return q

        cands = session.candidates
        pool_size = len(cands) if cands else len(self.movies)

        # STRATEGIC ROUTING: Adapt question strategy based on remaining pool size
        # This ensures depth questions (actor/director) are prioritized when pool is small
        if pool_size <= 50:
            strategy = "DEPTH_TARGETED"
        elif pool_size <= 500:
            strategy = "MIXED"
        else:
            strategy = "BREADTH"

        # Genre picker joins the natural IG pool — but hold it back until we've
        # asked GENRE_HOLDOFF plot questions first (charades: describe before
        # categorise). Once genre has been answered once, suppress the rest.
        genre_answered = bool(asked & GENRE_QUESTION_IDS)
        suppress_genre = genre_answered or (non_anchor < GENRE_HOLDOFF)

        unanswered = [q for q in questions.QUESTIONS
                      if q.id not in asked
                      and q.id not in LANGUAGE_QUESTION_IDS
                      and q.id not in ERA_QUESTION_IDS
                      and (not suppress_genre or q.id not in GENRE_QUESTION_IDS)
                      and self._is_question_available(q, session.answers)]

        suppress_ending = bool(asked & ENDING_QUESTION_IDS)
        suppress_setting = bool(asked & SETTING_QUESTION_IDS)
        if suppress_ending:
            unanswered = [q for q in unanswered if q.id not in ENDING_QUESTION_IDS]
        if suppress_setting:
            unanswered = [q for q in unanswered if q.id not in SETTING_QUESTION_IDS]

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

        # Filter out genre-gated comparatives that don't match remaining candidates' primary genres
        genres_in_pool = set()
        for film in cands:
            pg = film.get('primary_genre')
            if pg:
                genres_in_pool.add(pg)

        if genres_in_pool:
            filtered = []
            for q in splitting:
                # Keep questions with no genre restriction, or questions whose genres overlap with pool
                if q.genres is None or (genres_in_pool & q.genres):
                    filtered.append(q)
            # Only apply filter if it doesn't eliminate all questions
            if filtered:
                splitting = filtered

        # NOTE: Cast/crew gating was here but removed—it was too aggressive, replacing
        # the entire splitting pool with ONLY actors/directors when pool < 200, which
        # removed all comparatives/tropes. Better to let the actor selection logic
        # (lines 314+) handle prioritization naturally via can_ask_actors gating.

        # Genre-aware prioritization: primary → secondary → primary → generic → discriminating
        # NOTE: Genre preference is soft — if no aligned questions exist, continue to other questions
        established_genres = self._get_established_genres(session)
        genre_question_asked = False
        if established_genres:
            non_anchor_qs = [qid for qid in session.asked
                           if qid not in LANGUAGE_QUESTION_IDS and qid not in ERA_QUESTION_IDS]
            q_count = len(non_anchor_qs)

            # Phase 1 (Q1-5): Primary genre questions
            if q_count < 5:
                aligned = self._get_genre_aligned_questions(established_genres, splitting)
                if aligned:
                    genre_question_asked = True
                    return max(aligned, key=lambda q: self._information_gain(cands, q))

            # Phase 2 (Q5-7): One secondary genre question (if multiple genres confirmed)
            elif q_count < 7 and len(established_genres) > 1:
                # Ask from secondary genres (not the first one)
                primary_genre = next(iter(established_genres))  # Arbitrary "primary"
                secondary_genres = established_genres - {primary_genre}
                secondary_aligned = self._get_genre_aligned_questions(secondary_genres, splitting)
                if secondary_aligned:
                    genre_question_asked = True
                    return max(secondary_aligned, key=lambda q: self._information_gain(cands, q))

            # Phase 3 (Q7-10): Another primary genre question
            elif q_count < 10:
                aligned = self._get_genre_aligned_questions(established_genres, splitting)
                if aligned:
                    genre_question_asked = True
                    return max(aligned, key=lambda q: self._information_gain(cands, q))

        # If genre-aware block found nothing, fall through to other questions (don't return None)

        # SUB-GENRE ROUTING: Once a genre is confirmed, qualify with other genres
        # This establishes the genre blend (romance+action, romance+drama, etc.)
        confirmed_genres = set()
        for qid in GENRE_QUESTION_IDS:
            if session.answers.get(qid) == "yes":
                # Map q_genre_romance → 'romance', q_genre_action → 'action', etc.
                genre = qid.replace("q_genre_", "")
                confirmed_genres.add(genre)

        if confirmed_genres:
            # After any genre is confirmed, ask other genre questions to establish mix
            # This helps route to appropriate comparatives
            unasked_genre_qs = [q for q in splitting
                               if q.id in GENRE_QUESTION_IDS and q.id not in session.asked]
            if unasked_genre_qs and len(confirmed_genres) == 1:
                # Single genre confirmed: ask other genres to establish sub-genre mix
                best_q = max(unasked_genre_qs, key=lambda q: self._information_gain(cands, q))
                self._log_question_reasoning(session, best_q,
                    f"sub-genre qualification (confirmed: {confirmed_genres})")
                return best_q

            # After multiple genres confirmed, prioritize comparatives that match the blend
            if len(confirmed_genres) > 1 and splitting:
                # Find comparatives applicable to the confirmed genre set
                matched_comparatives = []
                for q in splitting:
                    if q.id.startswith("q_comp_"):
                        # Check if question's genres overlap with confirmed genres
                        if q.genres is None or (confirmed_genres & q.genres):
                            matched_comparatives.append(q)

                if matched_comparatives:
                    best_q = max(matched_comparatives, key=lambda q: self._information_gain(cands, q))
                    self._log_question_reasoning(session, best_q,
                        f"comparative for genre blend {confirmed_genres}")
                    return best_q

        # DYNAMIC ACTOR/DIRECTOR GATING: Uses strategic analysis, not fixed Q-numbers
        non_anchor_qs = [qid for qid in session.asked
                         if qid not in LANGUAGE_QUESTION_IDS and qid not in ERA_QUESTION_IDS]

        # Strategic unlock: Ask about actors if:
        # 1. Strategic analysis says so (should_unlock_actors=True)
        # 2. OR pool is small (≤30) and generic questions exhausted
        # 3. OR Q count forces it (Q20+ for actress/director, Q30+ for music)
        should_unlock_strategically = False
        if session.strategic_analysis:
            should_unlock_strategically = session.strategic_analysis.get("should_unlock_actors", False)

        can_ask_actors = (
            should_unlock_strategically or
            len(non_anchor_qs) >= 6
        )

        # Determine phase based on strategic guidance or Q-count
        if session.strategic_analysis and session.strategic_analysis.get("should_unlock_actors"):
            current_phase = 0  # Force actor phase early if strategic
        else:
            current_phase = 0 if len(non_anchor_qs) < 10 else (1 if len(non_anchor_qs) < 20 else 2)

        if current_phase == 0:  # Phase 1: actors take priority
            splitting = [q for q in splitting if not q.id.startswith(("q_actress_", "q_director_", "q_music_"))]
        elif current_phase == 1:  # Phase 2: actress/director (no music)
            splitting = [q for q in splitting if not q.id.startswith("q_music_")]

        # ACTOR SELECTION: Pick from top 3 actors by information gain (once unlocked)
        if can_ask_actors:
            # Only ask actor if we haven't asked one yet (avoid multiple actor Qs in a row)
            actor_asked = any(qid.startswith(("q_actor_", "q_actress_")) for qid in session.asked)
            if not actor_asked:
                actor_qs = [q for q in splitting if q.id.startswith(("q_actor_", "q_actress_"))]
                if actor_qs:
                    # Rank by information gain and pick random from top 3
                    ranked = sorted(actor_qs, key=lambda q: self._information_gain(cands, q), reverse=True)
                    top_n = min(3, len(ranked))
                    best_q = random.choice(ranked[:top_n])
                    self._log_question_reasoning(session, best_q,
                        f"actor from top-{top_n} by information gain ({len(cands)} candidates)")
                    return best_q


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

        # CLUSTER DISCRIMINATION: Inject when candidates cluster in same narrative type
        # This catches stumper patterns (multiple similar films not yet differentiated)
        if 2 <= len(cands) <= 20:
            discriminator = get_discriminator()
            candidate_clusters = discriminator.get_candidate_clusters(cands)

            # If all candidates belong to one cluster, inject discrimination
            if len(candidate_clusters) == 1 and len(candidate_clusters) > 0:
                disc_qs = discriminator.get_cluster_discrimination_questions(cands, asked)
                if disc_qs:
                    # Convert discrimination question JSON to Question-like object
                    disc_q = disc_qs[0]  # Pick first discrimination question
                    self._log_question_reasoning(session, None,
                        f"cluster discrimination (all {len(cands)} candidates in {disc_q['cluster_name']})")
                    # Return a synthetic question object for the discrimination question
                    # This will be handled in main.py with special logic
                    synthetic_q = type('Q', (), {
                        'id': disc_q['question_id'],
                        'text': disc_q['question'],
                        'cluster_based': True,
                        'cluster_id': disc_q['cluster_id'],
                        'cluster_name': disc_q['cluster_name']
                    })()
                    return synthetic_q

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

        # NOTE: Actor selection is handled earlier (lines 288-297) with "1 actor max" rule.
        # This old block is disabled to avoid asking multiple actors.

        # Prefer generic questions before discriminating fields unlocked
        if non_persons:
            best_q = max(non_persons, key=lambda q: self._information_gain(cands, q))
            self._log_question_reasoning(session, best_q, "generic plot/trope question")
            return best_q

        # If we got here, non_persons was empty but splitting might have actors/directors
        # Only reach actor/director questions if generic questions exhausted AND (threshold met OR after Q15)
        # DESPERATE ESCALATION: After Q30, force actors/directors regardless of pool size
        if not can_ask_actors and not directors_enabled:
            if len(non_anchor_qs) >= 30:
                can_ask_actors = True
                directors_enabled = True

        # If actors/directors are still not enabled and we have no generic questions, give up
        if not can_ask_actors and not directors_enabled and not non_persons:
            return None
        consecutive = 0
        for qid in session.asked[::-1]:
            if qid.startswith(("q_actor_", "q_actress_", "q_dir_", "q_music_")):
                consecutive += 1
            else:
                break
        if consecutive >= MAX_CONSECUTIVE_ACTOR_QS:
            return None

        # Safe adaptive boost: after pool stabilizes, prioritize actor questions for sparse films
        if non_anchor >= 5 and 10 < len(cands) <= 100 and consecutive < 1:
            sparse_count = 0
            DENSE_ATTRS = ['is_lost_and_found_child', 'is_love_triangle', 'is_partition_backdrop',
                          'is_dance_heavy', 'has_heist', 'is_sports_film', 'has_courtroom', 'is_sci_fi',
                          'has_wedding_plot', 'is_period_film', 'has_investigation_plot']
            for m in cands[:5]:
                if sum(1 for attr in DENSE_ATTRS if m.get(attr)) <= 2:
                    sparse_count += 1

            if sparse_count >= 4:
                actor_boost = lambda q: (
                    self._information_gain(cands, q) * 1.5
                    if q.id.startswith(('q_rajini', 'q_venkatesh', 'q_chiranjeevi', 'q_kamal_haasan',
                                       'q_vijay', 'q_amitabh', 'q_ajith', 'q_akshay', 'q_shah_rukh',
                                       'q_pawan_kalyan', 'q_sivakarthikeyan', 'q_ravi_teja', 'q_nani',
                                       'q_salman', 'q_dhanush', 'q_suriya', 'q_kajal', 'q_nayanthara'))
                    else self._information_gain(cands, q)
                )
                best_q = max(splitting, key=actor_boost)
                self._log_question_reasoning(session, best_q, "actor question for sparse films")
                return best_q

        # Discriminating field strategy: Priority-ordered placement across 3 phases
        current_non_anchor = len([qid for qid in session.asked
                                 if qid not in LANGUAGE_QUESTION_IDS and qid not in ERA_QUESTION_IDS])
        current_phase = 0 if current_non_anchor < 10 else (1 if current_non_anchor < 20 else 2)

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

        priority_field = None
        if current_phase == 0 and not discrim_asked['actor']:
            priority_field = 'actor'
        elif current_phase == 1 and not discrim_asked['actress'] and not discrim_asked['director']:
            priority_field = 'actress' if not discrim_asked['actress'] else 'director'
        elif current_phase == 2 and not discrim_asked['music']:
            priority_field = 'music'
        elif current_phase == 1 and not discrim_asked['director'] and discrim_asked['actress']:
            priority_field = 'director'
        elif current_phase == 2 and discrim_asked['music']:
            if not discrim_asked['actress']:
                priority_field = 'actress'
            elif not discrim_asked['director']:
                priority_field = 'director'
            elif not discrim_asked['actor']:
                priority_field = 'actor'

        if priority_field and splitting:
            field_map = {
                "actor": lambda q: q.id.startswith("q_actor_"),
                "actress": lambda q: q.id.startswith("q_actress_"),
                "director": lambda q: q.id.startswith("q_dir_"),
                "music": lambda q: q.id.startswith("q_music_"),
            }

            priority_qs = [q for q in splitting if field_map[priority_field](q)]
            if priority_qs:
                best_q = max(priority_qs, key=lambda q: self._information_gain(cands, q))
                self._log_question_reasoning(session, best_q, f"{priority_field} discriminator (phase {current_phase})")
                return best_q

        # Final selection: best information gain from (filtered) pool
        if splitting:
            best_q = max(splitting, key=lambda q: self._information_gain(cands, q))
            self._log_question_reasoning(session, best_q, f"best IG (pool={pool_size}, strategy={strategy})")
            return best_q

        # Fallback if no splitting questions remain: return None to trigger guess
        return None

    def _find_actor_question(self, actor_name: str) -> Optional[Question]:
        """Find a question about a specific actor/actress."""
        # Normalize name for question ID (lowercase, spaces->underscores)
        normalized = actor_name.lower().replace(" ", "_").replace(".", "").replace("'", "")

        # Try different question ID patterns
        patterns = [
            f"q_actor_{normalized}",
            f"q_actress_{normalized}",
            f"q_{normalized}",
        ]

        for qid in patterns:
            if qid in QUESTION_MAP:
                return QUESTION_MAP[qid]

        # Try fuzzy match against all questions
        for q in questions.QUESTIONS:
            if actor_name.lower() in q.text.lower() and q.id.startswith(("q_actor_", "q_actress_")):
                return q

        return None

    def _log_question_reasoning(self, session: Session, question: Question, reason: str) -> None:
        """Log why we selected this question."""
        session.reasoning_log.append({
            "turn": len(session.asked) + 1,
            "question_id": question.id,
            "reasoning": reason,
            "candidates_remaining": len(session.candidates),
        })

    @staticmethod
    def _is_identifying(question: Question) -> bool:
        """Specific 'who made it' questions (heroine/actor/director/music director)
        and sub-genre tropes (weight < 1.0) — the discriminators a human reaches
        for in the endgame."""
        return (question.id.startswith(("q_actor_", "q_actress_", "q_dir_", "q_music_"))
                or getattr(question, "weight", 1.0) < 1.0)

    def apply_answer(self, session: Session, question_id: str, answer: str) -> None:
        """answer: 'yes' | 'no' | 'unsure'
        Limits maybes to 5, then requires yes/no. Auto-clarifies ambiguous maybes with COT."""
        added = [question_id]
        session.asked.append(question_id)

        # Map 'unsure' to 'maybe' for internal consistency
        if answer == "unsure":
            answer = "maybe"

        # Track maybes and handle exhaustion
        if answer == "maybe":
            if session.maybe_count >= 5:
                # Exhausted: force clarification via COT
                q = QUESTION_MAP.get(question_id)
                clarified = self.reasoner.clarify_maybe(
                    question_id=question_id,
                    question_text=q.text if q else "?",
                    existing_answers=session.answers,
                )
                # Use clarified answer instead of maybe
                if clarified in ("yes", "no"):
                    answer = clarified
                    session.reasoning_log.append({
                        "turn": len(session.asked),
                        "type": "maybe_exhausted",
                        "question": question_id,
                        "clarified_to": answer,
                        "reasoning": "Player exhausted 5 maybes; COT disambiguated"
                    })
                else:
                    # Still unclear, use maybe but mark as forced
                    session.maybe_exhausted = True
            else:
                session.maybe_count += 1

        session.answers[question_id] = answer

        if answer == "yes":
            group: Optional[set] = None
            if question_id in LANGUAGE_QUESTION_IDS:
                group = LANGUAGE_QUESTION_IDS
            elif question_id in ERA_QUESTION_IDS:
                group = ERA_QUESTION_IDS
            elif question_id in ENDING_QUESTION_IDS:
                group = ENDING_QUESTION_IDS
            elif question_id in SETTING_QUESTION_IDS:
                group = SETTING_QUESTION_IDS
            if group:
                for sibling_id in group:
                    if sibling_id != question_id and sibling_id not in session.asked:
                        session.asked.append(sibling_id)
                        session.answers[sibling_id] = "no"
                        added.append(sibling_id)


        session.history.append(added)
        self._prune(session)

    def undo_last(self, session: Session) -> bool:
        """Revert the most recent answered turn (and its auto-answered siblings),
        recompute candidates, and report whether anything was undone."""
        if not session.history:
            return False
        last = set(session.history.pop())

        # Decrement maybe_count if we're undoing maybes
        for qid in last:
            if session.answers.get(qid) == "maybe":
                session.maybe_count = max(0, session.maybe_count - 1)

        # Reset exhausted flag if we freed up a maybe slot
        if session.maybe_count < 5:
            session.maybe_exhausted = False

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
        """Adaptive filtering: hard constraints → size-aware soft cutoff → scoring."""
        # Phase 1: Hard eligibility (language, era, genre, lead actor)
        eligible = [m for m in self.movies if self._hard_ok(m, session) and self._genre_ok(m, session)]
        if not eligible:  # contradictory answers — don't wipe the board
            eligible = list(self.movies)

        # Phase 2: Score all eligible films
        scored = [(m, self._score(m, session)) for m in eligible]
        max_score = max((s for _, s in scored), default=0.0)
        if max_score <= 0:
            session.candidates = eligible
            return

        # Adaptive cutoff: stricter as pool shrinks
        pool_size = len(eligible)
        if pool_size > 500:
            keep_ratio = 0.04  # Early game: lenient (2500 → 100)
        elif pool_size > 50:
            keep_ratio = 0.02  # Mid game: moderate (100 → 2)
        else:
            keep_ratio = 0.005  # Late game: aggressive (force disambiguation)

        cutoff = max_score * keep_ratio
        candidates = [m for m, s in scored if s >= cutoff]

        # If cutoff eliminated everything, keep top N to avoid dead end
        if not candidates:
            candidates = [m for m, _ in sorted(scored, key=lambda x: x[1], reverse=True)[:max(5, pool_size // 20)]]

        session.candidates = candidates

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

    def analyze_stumper(self, session: Session, stumped_title: str) -> dict:
        """Analyze why a stumper occurred and what differentiation was missed."""
        discriminator = get_discriminator()
        return discriminator.analyze_stumper(stumped_title, session.candidates, session.last_guesses)

    def _fit(self, movie: dict, session: Session) -> tuple[int, int]:
        """(agreements, answered) over substantive yes/no/unsure answers — excludes
        mutually-exclusive anchor groups, so confidence reflects core discriminating questions."""
        group = (LANGUAGE_QUESTION_IDS | ERA_QUESTION_IDS | GENRE_QUESTION_IDS |
                 ENDING_QUESTION_IDS | SETTING_QUESTION_IDS)
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
        """Bayesian scoring: P(film | answers) using likelihood weighting.

        Each question contributes log-likelihood based on:
        - Whether film matches the question
        - Player's answer (yes/no/maybe)
        - Question weight (hard signal vs soft trope)

        "Don't know" answers are treated as uncertainty (0.5 contribution).
        """
        log_score = 0.0

        for qid, answer in session.answers.items():
            q = QUESTION_MAP.get(qid)
            if not q:
                continue

            match = q.evaluate(movie)
            w = q.weight  # 1.0 = hard signal, 0.3 = soft trope

            # Likelihood ratio: how much does this answer support/refute this film?
            if answer == "yes":
                # Player says YES
                if match:
                    # Film has attribute: strong boost
                    log_score += 1.5 * w
                else:
                    # Film doesn't have attribute: strong penalty
                    log_score -= 1.5 * w

            elif answer == "no":
                # Player says NO
                if not match:
                    # Film doesn't have attribute: strong boost
                    log_score += 1.5 * w
                else:
                    # Film has attribute: strong penalty
                    log_score -= 1.5 * w

            elif answer == "maybe":
                # Player unsure: treat as weak signal
                # Both match and non-match are plausible, but match slightly favored
                if match:
                    log_score += 0.3 * w
                # No penalty if doesn't match when player uncertain

        # Return log-likelihood score (can be negative)
        # Higher scores = better match. Sorting by this in descending order
        # naturally ranks best matches first.
        return log_score

    def _discriminator_power(self, q: Question, candidates: list[dict]) -> float:
        """How well does this question separate THESE specific candidates?

        Returns entropy reduction: how balanced is the split?
        - 50/50 split = max entropy = best discrimination
        - All match or all don't = 0 entropy = useless for this pool
        """
        if not candidates:
            return 0.0

        matches = sum(1 for m in candidates if q.evaluate(m))
        non_matches = len(candidates) - matches

        if matches == 0 or non_matches == 0:
            return 0.0  # Doesn't discriminate

        # Entropy: H(p) = -p*log2(p) - (1-p)*log2(1-p)
        # Maximum at p=0.5 (50/50 split)
        ratio = matches / len(candidates)
        if ratio <= 0 or ratio >= 1:
            return 0.0
        entropy = -ratio * math.log2(ratio) - (1 - ratio) * math.log2(1 - ratio)

        return entropy * q.weight  # Weight by question importance

    def _filter_by_strategy(self, qs: list[Question], strategy: str, session: Session) -> list[Question]:
        """Filter question pool by current game strategy (breadth vs depth)."""
        if strategy == "BREADTH":
            # Prefer: language, era, genre, director (broad discriminators)
            return [q for q in qs if any(
                q.id.startswith(prefix)
                for prefix in ['q_hindi', 'q_tamil', 'q_telugu',
                              'q_classic', 'q_90s', '2000s', 'q_2010s', 'q_2020s',
                              'q_genre_', 'q_director_']
            )]

        elif strategy == "DEPTH_TARGETED":
            # Prefer: actor, actress, director (hard filters with elimination power)
            actor_actress_dir = [q for q in qs if any(
                q.id.startswith(prefix)
                for prefix in ['q_actor_', 'q_actress_', 'q_dir_']
            )]
            return actor_actress_dir if actor_actress_dir else qs  # Fallback to all

        elif strategy == "SURGICAL":
            # Only discriminator questions that actually split remaining candidates
            cands = session.candidates or self.movies
            return [q for q in qs if self._discriminator_power(q, cands) > 0.3]

        # MIXED: use all questions
        return qs

    @staticmethod
    def _infer_intensity(film: dict) -> dict[str, float]:
        """Infer intensity scores (0-10) from existing film fields.

        Maps primary_genre, genres list, and has_* flags to dimensions:
        - Primary genre match: 9
        - In genres list: 6
        - has_* flag set: bumps to at least 6-8
        - Default (not present): 2

        Used for comparative questions: "Is it more X-focused than Y?"
        """
        primary_str = (film.get('primary_genre') or '').lower()
        genres = set(g.lower() for g in (film.get('genres') or []))

        intensity = {
            'action': 2.0,
            'drama': 2.0,
            'war': 2.0,
            'crime': 2.0,
            'romance': 2.0,
            'comedy': 2.0,
            'songs': 2.0,
            'social': 2.0,
            'underdog': 2.0,
            'brotherhood': 2.0,
            'gritty': 2.0,
            'patriotic': 2.0,
            'true_story': 2.0,
            'anti_hero': 2.0,
        }

        # Check genres list (score 6)
        if 'action' in genres or 'thriller' in genres:
            intensity['action'] = 6.0
        if 'drama' in genres:
            intensity['drama'] = 6.0
        if 'war' in genres or 'military' in genres:
            intensity['war'] = 6.0
        if 'crime' in genres:
            intensity['crime'] = 6.0
        if 'romance' in genres or 'love' in genres:
            intensity['romance'] = 6.0
        if 'comedy' in genres:
            intensity['comedy'] = 6.0
        if 'musical' in genres or 'music' in genres:
            intensity['songs'] = 6.0

        # Check primary genre (score 9)
        if 'action' in primary_str or 'thriller' in primary_str:
            intensity['action'] = 9.0
        if 'drama' in primary_str:
            intensity['drama'] = 9.0
        if 'war' in primary_str or 'military' in primary_str:
            intensity['war'] = 9.0
        if 'crime' in primary_str:
            intensity['crime'] = 9.0
        if 'romance' in primary_str or 'love' in primary_str:
            intensity['romance'] = 9.0
        if 'comedy' in primary_str:
            intensity['comedy'] = 9.0
        if 'historical' in primary_str:
            # Historical context suggests drama + possible conflict
            intensity['drama'] = max(intensity['drama'], 7.0)
            intensity['war'] = max(intensity['war'], 7.0)

        # Explicit has_* flags (overrides and enhancements)
        if film.get('has_songs'):
            intensity['songs'] = 9.0
        if film.get('has_social_message'):
            intensity['social'] = 8.0
            intensity['drama'] = max(intensity['drama'], 7.0)

        # Military/war-related flags
        if film.get('has_military_plot') or film.get('is_patriotic_sacrifice'):
            intensity['war'] = max(intensity['war'], 7.0)

        # Crime/gangster-related flags
        if film.get('has_gangster_world') or film.get('has_criminal_underworld'):
            intensity['crime'] = max(intensity['crime'], 8.0)

        # Romance intensity
        if film.get('has_love_triangle') or film.get('has_forbidden_love'):
            intensity['romance'] = max(intensity['romance'], 6.0)

        # Underdog/redemption arc
        if film.get('has_underdog_story') or film.get('has_underdog'):
            intensity['underdog'] = max(intensity['underdog'], 8.0)

        # Brotherhood/camaraderie
        if film.get('has_brothers_in_arms') or film.get('has_buddy_bond'):
            intensity['brotherhood'] = max(intensity['brotherhood'], 7.0)

        # Gritty/dark/cynical tone
        if film.get('has_gritty_realism') or film.get('is_dark_cynical'):
            intensity['gritty'] = max(intensity['gritty'], 8.0)

        # Patriotic/nationalist themes
        if film.get('is_patriotic_film') or film.get('has_patriotic_sacrifice'):
            intensity['patriotic'] = max(intensity['patriotic'], 8.0)

        # True story/biographical
        if film.get('is_based_on_true_story') or film.get('is_biographical'):
            intensity['true_story'] = max(intensity['true_story'], 9.0)

        # Anti-hero protagonist
        if film.get('is_anti_hero') or film.get('has_morally_grey_lead'):
            intensity['anti_hero'] = max(intensity['anti_hero'], 8.0)

        return intensity
