from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class Question:
    id: str
    text: str
    evaluate: Callable[[dict], bool]
    weight: float = 1.0  # 1.0 = hard signal (2×/0.1×), 0.3 = soft trope (1.3×/0.77×)
    requires: tuple[str, str] | list[tuple[str, str]] | None = None  # Single (q_id, answer) or list with OR logic


def _attr_eq(attr: str, value: Any) -> Callable[[dict], bool]:
    return lambda m: m.get(attr) == value


def _attr_gte(attr: str, value: float) -> Callable[[dict], bool]:
    def f(m: dict) -> bool:
        try:
            return float(m.get(attr) or 0) >= value
        except (TypeError, ValueError):
            return False
    return f


def _has_multiple_protagonists(m: dict) -> bool:
    """Check if film has multiple prominent leads (co-leads, ensemble)."""
    lead_actors = m.get('lead_actors') or []
    return len(lead_actors) >= 2


def _in(attr: str, *values: str) -> Callable[[dict], bool]:
    return lambda m: m.get(attr) in values


def _actor_appears(name: str) -> Callable[[dict], bool]:
    """Check if actor/actress is a lead (stars in film, not just cameo/supporting)."""
    return lambda m: (m.get('lead_actor') == name or
                     m.get('lead_actress') == name or
                     name in (m.get('lead_actors') or []) or
                     name in (m.get('lead_actresses') or []))


QUESTIONS: list[Question] = [
    Question("q_hindi",     "Is it a Hindi film?",                              _attr_eq("language", "Hindi")),
    Question("q_tamil",     "Is it a Tamil film?",                              _attr_eq("language", "Tamil")),
    Question("q_telugu",    "Is it a Telugu film?",                             _attr_eq("language", "Telugu")),
    Question("q_classic",   "Was it released before 1990?",                     _attr_eq("era", "classic")),
    Question("q_90s",       "Was it released in the 90s?",                      _attr_eq("era", "90s")),
    Question("q_2000s",     "Was it released in the 2000s?",                    _attr_eq("era", "2000s")),
    Question("q_2010s",     "Was it released in the 2010s?",                    _attr_eq("era", "2010s")),
    Question("q_2020s",     "Was it released after 2020?",                      _attr_eq("era", "2020s")),
    Question("q_multiple_protagonists", "Does it have multiple protagonists?", _has_multiple_protagonists, weight=1.0),
    Question("q_villain",          "Does it feature a memorable villain?",                           _attr_eq("has_villain", True)),
    Question("q_strict_antagonist","Is the main conflict driven by a strict but well-meaning character\n(overprotective parent/sibling, authority figure) rather than a villain?",
             _attr_eq("has_strict_antagonist", True), requires=("q_villain", "no")),
    Question("q_songs",     "Are songs/music a key part of the film?",          _attr_eq("has_songs", True)),
    Question("q_female",    "Is the main character female?",                    _attr_eq("lead_gender", "female")),
    Question("q_social",    "Does it carry a strong social message?",           _attr_eq("has_social_message", True)),
    Question("q_true",      "Is it based on a true story or biography?",        lambda m: m.get('is_based_on_true_story') or m.get('is_biographical')),
    Question("q_franchise", "Is it part of a series or franchise?",             _attr_eq("is_franchise", True)),
    Question("q_remake",    "Is it a remake of another film?",                  _attr_eq("is_remake", True)),
    Question("q_sports",    "Is it a sports film?",                             _attr_eq("is_sports_film", True)),
    Question("q_historical","Is it set in a historical period?",                _attr_eq("is_historical", True)),
    Question("q_horror",    "Does it have horror elements?",                    _attr_eq("is_horror", True)),
    Question("q_pan_india",  "Was it a pan-India blockbuster?",                  _attr_eq("is_pan_india_blockbuster", True)),
    Question("q_family",     "Is it a family-friendly film?",                    _attr_eq("is_family_film", True)),
    Question("q_anti_hero",      "Is the lead character a morally grey anti-hero?",  _attr_eq("is_anti_hero", True)),
    Question("q_abroad",         "Is the film set significantly outside India?",      _attr_eq("is_set_abroad", True)),
    Question("q_love_triangle",  "Does it feature a love triangle?",                  _attr_eq("has_love_triangle", True)),
    Question("q_revenge",        "Is revenge a central driving force in the plot?",   _attr_eq("has_revenge_plot", True)),
    Question("q_forbidden_love", "Is the romance opposed by family or society?",      _attr_eq("has_forbidden_love", True)),
    Question("q_protagonist_married", "Is the protagonist married?",                  _attr_eq("is_protagonist_married", True)),
    Question("q_infidelity",     "Does it involve infidelity or an affair?",          _attr_eq("has_infidelity", True)),
    Question("q_rural_setting",  "Is it set in a rural area?",                        _attr_eq("has_rural_setting", True)),
    Question("q_urban_setting",  "Is the story set in a city or metropolitan area?",  _attr_eq("has_urban_setting", True)),
    Question("q_conman",         "Does the plot involve conmen or con artists?",      _attr_eq("has_conman", True)),
    Question("q_class_pretense", "Does the protagonist pretend to be from a different class/background?", _attr_eq("has_class_pretense", True)),
    Question("q_costar_sanjay_dutt", "Does Sanjay Dutt appear in the film?", _actor_appears("Sanjay Dutt")),
    Question("q_costar_anil_kapoor", "Does Anil Kapoor appear in the film?", _actor_appears("Anil Kapoor")),
    Question("q_costar_karisma_kapoor", "Does Karisma Kapoor appear in the film?", _actor_appears("Karisma Kapoor")),
]

def _genre_in(*tokens: str) -> Callable[[dict], bool]:
    """Match a theme against ANY of a movie's genres (multi-genre films
    qualify under each of their genres), falling back to primary_genre."""
    toks = set(tokens)
    def f(m: dict) -> bool:
        if set(m.get('genres') or []) & toks:
            return True
        return m.get('primary_genre') in toks
    return f


def make_star_questions(movies: list[dict]) -> list["Question"]:
    """Generate actor/director/music questions for anyone meeting the min-film threshold.
    For Telugu/Tamil/Kannada, use lower thresholds (8+ films) for top regional actors."""
    from collections import Counter
    _SKIP = {"", "n/a", "na", "unknown", "none"}
    actors    = Counter(m['lead_actor']      for m in movies if m.get('lead_actor'))
    actresses = Counter(m['lead_actress']    for m in movies if m.get('lead_actress'))
    directors = Counter(m['director']        for m in movies if m.get('director'))
    music     = Counter(m['music_director']  for m in movies if m.get('music_director'))

    # Identify language distribution
    language_films = Counter(m.get('language') for m in movies if m.get('language'))
    has_regional = 'Telugu' in language_films or 'Tamil' in language_films or 'Kannada' in language_films

    qs = []
    for name, n in actors.items():
        if name.strip().lower() in _SKIP:
            continue
        # Regional threshold (8+) if we have Telugu/Tamil/Kannada films, else global (15+)
        threshold = 8 if has_regional else 15
        if n >= threshold:
            safe = name.lower().replace(' ', '_').replace('.', '').replace("'", '')
            qs.append(Question(f"q_actor_{safe}", f"Does it star {name}?", _actor_appears(name)))

    for name, n in actresses.items():
        if name.strip().lower() in _SKIP:
            continue
        threshold = 8 if has_regional else 15
        if n >= threshold:
            safe = name.lower().replace(' ', '_').replace('.', '').replace("'", '')
            qs.append(Question(f"q_actress_{safe}", f"Does it star the actress {name}?", _actor_appears(name)))

    for name, n in directors.items():
        if name.strip().lower() in _SKIP:
            continue
        # Lower director threshold (1+ instead of 2+) for more discrimination
        if n >= 1:
            safe = name.lower().replace(' ', '_').replace('.', '').replace("'", '')
            qs.append(Question(f"q_dir_{safe}", f"Is it directed by {name}?", _in('director', name)))

    for name, n in music.items():
        if name.strip().lower() in _SKIP:
            continue
        if n >= 8:
            safe = name.lower().replace(' ', '_').replace('.', '').replace("'", '')
            qs.append(Question(f"q_music_{safe}", f"Is the music by {name}?", _in('music_director', name)))
    return qs


QUESTIONS.extend([
    Question("q_genre_picker",        "What's the core genre?",                          lambda m: True, weight=1.0),  # Picker UI sentinel
    Question("q_genre_action",        "Is it Action/Thriller/Adventure?",                _genre_in("action", "thriller", "adventure")),
    Question("q_genre_comedy",        "Is it Comedy?",                                   _genre_in("comedy")),
    Question("q_genre_romance",       "Is it Romance (Love Stories)?",                   _genre_in("romance")),
    Question("q_genre_drama",         "Is it Drama (Personal/Family)?",                  _genre_in("drama", "family")),
    Question("q_genre_social",        "Is it Social/Political?",                         _attr_eq("has_social_message", True)),
    Question("q_genre_historical",    "Is it Historical/Biopic?",                        lambda m: m.get('is_historical') or m.get('is_biographical')),
    Question("q_genre_horror",        "Is it Horror/Supernatural?",                      _attr_eq("is_horror", True)),
    Question("q_genre_scifi",         "Is it Sci-Fi/Fantasy?",                           _attr_eq("is_sci_fi", True)),
])

def _attr_true(attr: str) -> Callable[[dict], bool]:
    """True only when the field is explicitly True; None/missing → False (untagged treated as no)."""
    return lambda m: m.get(attr) is True


# Soft trope questions (weight=0.3): nudge confidence, never hard-eliminate.
# Fields default to False/None for untagged movies so "no" answers are free.
QUESTIONS.extend([
    Question("q_one_sided_love", "Is the love story primarily one-sided or unrequited?",
             _attr_true("has_one_sided_love"), weight=0.3),
    Question("q_item_number",    "Does it feature a famous dance/item number?",
             _attr_true("has_item_number"), weight=0.3),
    Question("q_double_role",    "Does the lead actor play a double role?",
             _attr_true("has_double_role"), weight=0.3),
    Question("q_college_film",   "Is a significant part of the film set in college or university?",
             _attr_true("is_college_film"), weight=0.3),
    Question("q_parent_child",   "Is the parent-child relationship a central emotional thread?",
             _attr_true("has_parent_child_drama"), weight=0.3),
    Question("q_cop_or_law",     "Is the protagonist a cop, lawyer, or judge?",
             _attr_true("has_police_or_law"), weight=0.3),
    Question("q_village_setting","Is the film primarily set in a village or rural area?",
             _attr_true("has_village_setting"), weight=0.3),

    # Otherworldly / mythology / superpowers
    Question("q_supernatural",  "Does it involve gods, supernatural beings, or the afterlife?",
             _attr_true("has_supernatural"), weight=0.3),
    Question("q_superpowers",   "Does a character have superhuman or magical powers?",
             _attr_true("has_superpowers"), weight=0.3),
    Question("q_mythology",     "Is it based on or inspired by Hindu mythology?",
             _attr_true("is_mythology_based"), weight=0.3),

    # Kids / child protagonist
    Question("q_child_protag",  "Is a child the central character or hero of the story?",
             _attr_true("has_child_protagonist"), weight=0.3),

    # More narrative tropes
    Question("q_multiple_stories", "Does it follow multiple parallel storylines or characters?",
             _attr_true("has_multiple_storylines"), weight=0.3),
    Question("q_underdog",      "Is the lead an underdog fighting against the system or odds?",
             _attr_true("has_underdog_story"), weight=0.3),
    Question("q_heist",         "Does it involve a heist, con, or elaborate plan?",
             _attr_true("has_heist"), weight=0.3),
    Question("q_period_drama",  "Is it a period film set more than 50 years before its release?",
             _attr_true("is_period_drama"), weight=0.3),
    Question("q_courtroom",     "Does it feature a significant courtroom or trial scene?",
             _attr_true("has_courtroom"), weight=0.3),
    Question("q_flashback",     "Is a major portion of the story told through flashbacks?",
             _attr_true("has_major_flashback"), weight=0.3),

    # Storyline / narrative tropes
    Question("q_mentor",        "Does the lead have a mentor or guru who shapes their journey?",
             _attr_true("has_mentor_figure"), weight=0.3),
    Question("q_betrayal",      "Is a close friendship destroyed by betrayal?",
             _attr_true("has_friendship_betrayal"), weight=0.3),
    Question("q_mistaken_identity", "Does the plot hinge on mistaken identity or impersonation?",
             _attr_true("has_mistaken_identity"), weight=0.3),
    Question("q_class_conflict","Is the clash between social classes a central theme?",
             _attr_true("has_class_conflict"), weight=0.3),
    Question("q_gangster_world","Is the story set in or driven by the criminal underworld?",
             _attr_true("has_gangster_world"), weight=0.3),
    Question("q_slums",         "Is the film primarily set in slums or very poor urban areas?",
             _attr_true("is_set_in_slums"), weight=0.3),
    Question("q_brotherhood",   "Is male friendship or brotherhood the central emotional thread?",
             _attr_true("has_brothers_in_arms"), weight=0.3),
    Question("q_enemy_friend",  "Does an enemy become a friend (or a friend become an enemy)?",
             _attr_true("has_enemy_turned_friend"), weight=0.3),
    Question("q_patriotic",     "Does the film have strong patriotic or nationalist themes?",
             _attr_true("is_patriotic_film"), weight=0.3),

    # Phase 2.2: Wider coverage for Hindi/Tamil/Telugu disambiguation
    Question("q_separated_family", "Are the main characters searching for separated or lost family members?",
             _attr_true("is_lost_and_found_child"), weight=0.3),
    Question("q_love_triangle",    "Is there a love triangle where multiple characters pursue the same person?",
             _attr_true("is_love_triangle"), weight=0.3),
    Question("q_reluctant_romance", "Is the main romance about one person pursuing a reluctant partner?",
             _attr_true("is_unrequited_love_turnaround"), weight=0.3),
    Question("q_reincarnation",    "Does the plot involve ghosts, spirits, or reincarnation?",
             _attr_true("is_reincarnation_rebirth"), weight=0.3),
    Question("q_partition_era",    "Is this set in pre-1947 British-ruled India (colonial or partition era)?",
             _attr_true("is_partition_backdrop"), weight=0.3),
    Question("q_dance_heavy",      "Does the film heavily feature elaborate dance sequences or musical numbers?",
             _attr_true("is_dance_heavy"), weight=0.3),
    Question("q_sibling_rivalry",  "Is sibling or brother rivalry a central plot element?",
             _attr_true("is_brother_conflict"), weight=0.3),
    Question("q_sacrifice_ending", "Does the climax involve a significant sacrifice or tragic ending?",
             _attr_true("is_sacrifice_ending"), weight=0.3),

    # Phase 3: Additional discrimination questions (5 more — removed duplicates)
    Question("q_scifi_fantasy",      "Does the film involve sci-fi, fantasy, or supernatural worlds?",
             _attr_true("is_sci_fi"), weight=0.3),
    Question("q_single_protagonist", "Is the story tightly focused on one main character's journey?",
             _attr_true("has_single_protagonist"), weight=0.3),
    Question("q_female_lead",        "Is the protagonist or central character female?",
             _attr_true("has_female_lead"), weight=0.3),
    Question("q_ensemble_large",     "Does the film have a large ensemble cast with multiple major characters?",
             _attr_true("is_ensemble_cast"), weight=0.3),

    # Phase 4: Tier 2 discrimination (9 questions targeting mid-rated film distinctions)
    Question("q_wedding_marriage",   "Is a wedding, marriage, or engagement a major plot point?",
             _attr_true("has_wedding_plot"), weight=0.3),
    Question("q_crime_protagonist",  "Is the protagonist a criminal, gangster, or morally grey character?",
             _attr_true("has_anti_hero_protagonist"), weight=0.3),
    Question("q_investigation",      "Does the film involve a murder, investigation, or mystery to solve?",
             _attr_true("has_investigation_plot"), weight=0.3),
    Question("q_friendship_focus",   "Is friendship or brotherhood the emotional core (rather than romance)?",
             _attr_true("has_friendship_focus"), weight=0.3),
    Question("q_parent_child",       "Are parent-child relationships central to the plot?",
             _attr_true("has_parent_child_arc"), weight=0.3),
    Question("q_supernatural_magic", "Does the film involve ghosts, magic, or the supernatural (beyond reincarnation)?",
             _attr_true("has_supernatural_elements"), weight=0.3),
    Question("q_sequel_franchise",   "Is this a sequel, prequel, or part of a film franchise/series?",
             _attr_true("is_sequel_or_franchise"), weight=0.3),

    # Phase 5: Actor & Director recommendations for Tier 2 (endgame discrimination)
    Question("q_rajini",              "Does it star Rajinikanth?",
             _actor_appears("Rajinikanth"), weight=1.0),
    Question("q_venkatesh",           "Does it star Venkatesh?",
             _actor_appears("Venkatesh"), weight=1.0),
    Question("q_chiranjeevi",         "Does it star Chiranjeevi?",
             _actor_appears("Chiranjeevi"), weight=1.0),
    Question("q_kamal_haasan",        "Does it star Kamal Haasan?",
             _actor_appears("Kamal Haasan"), weight=1.0),
    Question("q_vijay",               "Does it star Vijay?",
             _actor_appears("Vijay"), weight=1.0),
    Question("q_amitabh",             "Does it star Amitabh Bachchan?",
             _actor_appears("Amitabh Bachchan"), weight=1.0),
    Question("q_ajith",               "Does it star Ajith Kumar?",
             _actor_appears("Ajith Kumar"), weight=1.0),
    Question("q_akshay",              "Does it star Akshay Kumar?",
             _actor_appears("Akshay Kumar"), weight=1.0),
    Question("q_kajal",               "Does it star Kajal Aggarwal?",
             _actor_appears("Kajal Aggarwal"), weight=1.0),
    Question("q_nayanthara",          "Does it star Nayanthara?",
             _actor_appears("Nayanthara"), weight=1.0),
    Question("q_dir_balachander",     "Is it directed by K. Balachander?",
             _attr_eq("director", "K. Balachander"), weight=1.0),
    Question("q_dir_muthuraman",      "Is it directed by S. P. Muthuraman?",
             _attr_eq("director", "S. P. Muthuraman"), weight=1.0),
    Question("q_dir_puri",            "Is it directed by Puri Jagannadh?",
             _attr_eq("director", "Puri Jagannadh"), weight=1.0),
    Question("q_dir_mani_ratnam",     "Is it directed by Mani Ratnam?",
             _attr_eq("director", "Mani Ratnam"), weight=1.0),

    # Phase 6: Additional prolific actors (identified from failure analysis)
    Question("q_pawan_kalyan",        "Does it star Pawan Kalyan?",
             _actor_appears("Pawan Kalyan"), weight=1.0),
    Question("q_sivakarthikeyan",     "Does it star Sivakarthikeyan?",
             _actor_appears("Sivakarthikeyan"), weight=1.0),
    Question("q_shah_rukh",           "Does it star Shah Rukh Khan?",
             _actor_appears("Shah Rukh Khan"), weight=1.0),
    Question("q_ravi_teja",           "Does it star Ravi Teja?",
             _actor_appears("Ravi Teja"), weight=1.0),
    Question("q_nani",                "Does it star Nani?",
             _actor_appears("Nani"), weight=1.0),
    Question("q_salman",              "Does it star Salman Khan?",
             _actor_appears("Salman Khan"), weight=1.0),
    Question("q_dhanush",             "Does it star Dhanush?",
             _actor_appears("Dhanush"), weight=1.0),
    Question("q_suriya",              "Does it star Suriya?",
             _actor_appears("Suriya"), weight=1.0),

    # ACTOR-HIERARCHICAL SUB-QUESTIONS (only asked after actor confirmed)
    # Focus on SPECIFIC plot elements & characterization, NOT era/genre (already asked in main Qs)
    # Chiranjeevi-specific: revenge-driven roles vs family/comedy
    Question("q_chiranjeevi_revenge",   "Does the film center on revenge or an underdog struggle?",
             _attr_true("has_revenge_plot"), weight=0.5, requires=("q_chiranjeevi", "yes")),
    Question("q_chiranjeevi_comedy",    "Is it primarily a comedy or lighthearted entertainer?",
             _genre_in("comedy"), weight=0.5, requires=("q_chiranjeevi", "yes")),

    # Vijay-specific: mass vs romantic
    Question("q_vijay_mass",           "Is it a mass-appeal action entertainer?",
             _attr_true("is_mass_entertainer"), weight=0.5, requires=("q_vijay", "yes")),
    Question("q_vijay_romantic",       "Is romance central to the plot?",
             _attr_true("has_romance"), weight=0.5, requires=("q_vijay", "yes")),

    # Amitabh-specific: villain/grey vs righteous
    Question("q_amitabh_anti_hero",    "Does he play an anti-hero or morally grey character?",
             _attr_true("is_anti_hero"), weight=0.5, requires=("q_amitabh", "yes")),
    Question("q_amitabh_family",       "Is family drama central to the story?",
             _attr_true("is_family_film"), weight=0.5, requires=("q_amitabh", "yes")),

    # Shah Rukh-specific: patriarchal resistance vs romantic
    Question("q_shah_rukh_patriarchy", "Does it center on resistance to patriarchal/family pressure?",
             _attr_true("has_patriarchal_resistance"), weight=0.5, requires=("q_shah_rukh", "yes")),
    Question("q_shah_rukh_vulnerability", "Does the lead show emotional vulnerability or breaking?",
             _attr_true("has_male_vulnerability"), weight=0.5, requires=("q_shah_rukh", "yes")),

    # Salman-specific: comedy vs thriller
    Question("q_salman_comedy_focused", "Is it primarily a comedy?",
             _genre_in("comedy"), weight=0.5, requires=("q_salman", "yes")),
    Question("q_salman_romance_subplot", "Does it have a romance subplot?",
             _attr_true("has_romance"), weight=0.5, requires=("q_salman", "yes")),

    # Ajith-specific: action-heavy vs balanced
    Question("q_ajith_intense",        "Is it an intense, hard-hitting action thriller?",
             _genre_in("thriller", "crime"), weight=0.5, requires=("q_ajith", "yes")),
    Question("q_ajith_family_theme",   "Does it have family or relationship elements?",
             _attr_true("is_family_film"), weight=0.5, requires=("q_ajith", "yes")),

    # Nayanthara-specific: heroine-led vs ensemble
    Question("q_nayanthara_led",       "Is she the central protagonist/heroine?",
             _attr_eq("lead_gender", "female"), weight=0.5, requires=("q_nayanthara", "yes")),
    Question("q_nayanthara_action_heavy", "Is it action or thriller-heavy?",
             _genre_in("action", "thriller", "crime"), weight=0.5, requires=("q_nayanthara", "yes")),

    # Rajini-specific: stylish vs gritty
    Question("q_rajini_stylish",       "Is it a stylish, high-octane action film?",
             _attr_true("is_mass_entertainer"), weight=0.5, requires=("q_rajini", "yes")),
    Question("q_rajini_social_message", "Does it have a social or patriotic message?",
             _attr_true("has_patriotic_sacrifice"), weight=0.5, requires=("q_rajini", "yes")),

    # SRK narrative patterns (applicable across languages and actors)
    Question("q_patriarchal_resistance", "Does emotion become the way the protagonist resists authority?",
             _attr_true("has_patriarchal_resistance"), weight=0.3),
    Question("q_male_vulnerability",     "Does the male lead show emotional vulnerability or breakdown?",
             _attr_true("has_male_emotional_vulnerability"), weight=0.3),
    Question("q_nri_values_tension",     "Does the protagonist balance Western lifestyle with traditional Indian values?",
             _attr_true("has_nri_cultural_tension"), weight=0.3),
    Question("q_military_plot",          "Does the plot involve the military, army, navy, or intelligence agencies?",
             _attr_true("has_military_plot"), weight=0.3),
    Question("q_patriotic_sacrifice",    "Does the story center on sacrifice for nation or patriotic duty?",
             _attr_true("has_patriotic_sacrifice"), weight=0.3),

    # Ending type
    Question("q_happy_ending",           "Does it have a happy or satisfying ending?",
             _attr_true("has_happy_ending"), weight=0.3),
    Question("q_tragic_ending",          "Does it have a sad, tragic, or bittersweet ending?",
             _attr_true("has_tragic_ending"), weight=0.3),
    Question("q_ambiguous_ending",       "Does it have an ambiguous or open-ended ending?",
             _attr_true("has_ambiguous_ending"), weight=0.3),

    # Director/production style
    Question("q_yrf_style",              "Does it have a Yash Raj Films aesthetic (grand, romantic, feel-good)?",
             _attr_true("is_yrf_style"), weight=0.3),
    Question("q_gritty_realism",         "Is it dark, gritty, or urban-realistic in style?",
             _attr_true("has_gritty_realism"), weight=0.3),
    Question("q_intimate_indie",         "Is it intimate, personal, or indie in style (not a big-budget spectacle)?",
             _attr_true("is_intimate_indie"), weight=0.3),

    # Suspense
    Question("q_suspense_thriller",      "Does it build tension through suspense or a cat-and-mouse plot?",
             _attr_true("has_suspense_thriller"), weight=0.3),
])

QUESTION_MAP: dict[str, Question] = {q.id: q for q in QUESTIONS}

LANGUAGE_QUESTION_IDS: set[str] = {'q_hindi', 'q_tamil', 'q_telugu'}
ERA_QUESTION_IDS: set[str]      = {'q_classic', 'q_90s', 'q_2000s', 'q_2010s', 'q_2020s'}
GENRE_QUESTION_IDS: set[str]    = {'q_genre_action', 'q_genre_comedy', 'q_genre_romance',
                                    'q_genre_drama', 'q_genre_social', 'q_genre_historical',
                                    'q_genre_horror', 'q_genre_scifi'}
ENDING_QUESTION_IDS: set[str]   = {'q_happy_ending', 'q_tragic_ending', 'q_ambiguous_ending'}
SETTING_QUESTION_IDS: set[str]  = {'q_rural_setting', 'q_urban_setting', 'q_abroad'}
VILLAIN_QUESTION_IDS: set[str]  = {'q_villain', 'q_strict_antagonist'}
