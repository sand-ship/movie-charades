from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class Question:
    id: str
    text: str
    evaluate: Callable[[dict], bool]
    weight: float = 1.0  # 1.0 = hard signal (2×/0.1×), 0.3 = soft trope (1.3×/0.77×)


def _attr_eq(attr: str, value: Any) -> Callable[[dict], bool]:
    return lambda m: m.get(attr) == value


def _attr_gte(attr: str, value: float) -> Callable[[dict], bool]:
    def f(m: dict) -> bool:
        try:
            return float(m.get(attr) or 0) >= value
        except (TypeError, ValueError):
            return False
    return f


QUESTIONS: list[Question] = [
    Question("q_hindi",     "Is it a Hindi film?",                              _attr_eq("language", "hindi")),
    Question("q_tamil",     "Is it a Tamil film?",                              _attr_eq("language", "tamil")),
    Question("q_telugu",    "Is it a Telugu film?",                             _attr_eq("language", "telugu")),
    Question("q_classic",   "Was it released before 1990?",                     _attr_eq("era", "classic")),
    Question("q_90s",       "Was it released in the 90s?",                      _attr_eq("era", "90s")),
    Question("q_2000s",     "Was it released in the 2000s?",                    _attr_eq("era", "2000s")),
    Question("q_2010s",     "Was it released in the 2010s?",                    _attr_eq("era", "2010s")),
    Question("q_2020s",     "Was it released after 2020?",                      _attr_eq("era", "2020s")),
    Question("q_action",    "Is it primarily an action film?",                  _attr_eq("has_action", True)),
    Question("q_comedy",    "Does it have strong comedy elements?",             _attr_eq("has_comedy", True)),
    Question("q_romance",   "Is romance a central theme?",                      _attr_eq("has_romance", True)),
    Question("q_villain",   "Does it feature a memorable villain?",             _attr_eq("has_villain", True)),
    Question("q_songs",     "Are songs/music a key part of the film?",          _attr_eq("has_songs", True)),
    Question("q_female",    "Does it have a female protagonist?",               _attr_eq("lead_gender", "female")),
    Question("q_social",    "Does it carry a strong social message?",           _attr_eq("has_social_message", True)),
    Question("q_true",      "Is it based on a true story?",                     _attr_eq("is_based_on_true_story", True)),
    Question("q_franchise", "Is it part of a series or franchise?",             _attr_eq("is_franchise", True)),
    Question("q_remake",    "Is it a remake of another film?",                  _attr_eq("is_remake", True)),
    Question("q_sports",    "Is it a sports film?",                             _attr_eq("is_sports_film", True)),
    Question("q_historical","Is it set in a historical period?",                _attr_eq("is_historical", True)),
    Question("q_bio",       "Is it a biographical film?",                       _attr_eq("is_biographical", True)),
    Question("q_thriller",  "Does it have thriller or suspense elements?",      _attr_eq("has_thriller_elements", True)),
    Question("q_scifi",     "Does it involve sci-fi or fantasy elements?",      _attr_eq("is_sci_fi", True)),
    Question("q_horror",    "Does it have horror elements?",                    _attr_eq("is_horror", True)),
    Question("q_pan_india",  "Was it a pan-India blockbuster?",                  _attr_eq("is_pan_india_blockbuster", True)),
    Question("q_family",     "Is it a family-friendly film?",                    _attr_eq("is_family_film", True)),
    Question("q_high_rated", "Is it rated 8.3 or above on IMDB?",               _attr_gte("imdb_rating", 8.3)),
    Question("q_anti_hero",      "Is the lead character a morally grey anti-hero?",  _attr_eq("is_anti_hero", True)),
    Question("q_abroad",         "Is the film set significantly outside India?",      _attr_eq("is_set_abroad", True)),
    Question("q_love_triangle",  "Does it feature a love triangle?",                  _attr_eq("has_love_triangle", True)),
    Question("q_revenge",        "Is revenge a central driving force in the plot?",   _attr_eq("has_revenge_plot", True)),
    Question("q_forbidden_love", "Is the romance opposed by family or society?",      _attr_eq("has_forbidden_love", True)),
]

def _in(attr: str, *values: str) -> Callable[[dict], bool]:
    return lambda m: m.get(attr) in values

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
    """Generate actor/director questions for anyone with 3+ films in the active pool."""
    from collections import Counter
    _SKIP = {"", "n/a", "na", "unknown", "none"}
    actors    = Counter(m['lead_actor']     for m in movies if m.get('lead_actor'))
    actresses = Counter(m['lead_actress']   for m in movies if m.get('lead_actress'))
    directors = Counter(m['director']       for m in movies if m.get('director'))
    composers = Counter(m['music_director'] for m in movies if m.get('music_director'))
    qs = []
    for name, n in actors.items():
        if n >= 3:
            safe = name.lower().replace(' ', '_').replace('.', '').replace("'", '')
            qs.append(Question(
                f"q_actor_{safe}",
                f"Does it star {name}?",
                _in('lead_actor', name),
            ))
    for name, n in actresses.items():
        if n >= 3 and name.strip().lower() not in _SKIP:
            safe = name.lower().replace(' ', '_').replace('.', '').replace("'", '')
            qs.append(Question(
                f"q_actress_{safe}",
                f"Does it star the actress {name}?",
                _in('lead_actress', name),
            ))
    for name, n in directors.items():
        if n >= 3 and name.strip().lower() not in _SKIP:
            safe = name.lower().replace(' ', '_').replace('.', '').replace("'", '')
            qs.append(Question(
                f"q_dir_{safe}",
                f"Is it directed by {name}?",
                _in('director', name),
            ))
    for name, n in composers.items():
        if n >= 3 and name.strip().lower() not in _SKIP:
            safe = name.lower().replace(' ', '_').replace('.', '').replace("'", '')
            qs.append(Question(
                f"q_music_{safe}",
                f"Is the music by {name}?",
                _in('music_director', name),
            ))
    return qs


QUESTIONS.extend([
    Question("q_genre_action",   "What is the central theme? (Action)",     _genre_in("action")),
    Question("q_genre_comedy",   "What is the central theme? (Comedy)",     _genre_in("comedy")),
    Question("q_genre_romance",  "What is the central theme? (Romance)",    _genre_in("romance")),
    Question("q_genre_drama",    "What is the central theme? (Drama)",      _genre_in("drama", "family")),
    Question("q_genre_thriller", "What is the central theme? (Thriller)",   _genre_in("thriller", "crime", "mystery")),
    Question("q_genre_other",    "What is the central theme? (Other)",      _genre_in(
        "historical", "horror", "sports", "biopic", "biography", "sci-fi",
        "fantasy", "musical", "social", "western", "war", "adventure", "spy", "tragedy")),
])

def _attr_true(attr: str) -> Callable[[dict], bool]:
    """True only when the field is explicitly True; None/missing → False (untagged treated as no)."""
    return lambda m: m.get(attr) is True


# Soft trope questions (weight=0.3): nudge confidence, never hard-eliminate.
# Fields default to False/None for untagged movies so "no" answers are free.
QUESTIONS.extend([
    Question("q_one_sided_love", "Is the love story primarily one-sided or unrequited?",
             _attr_true("has_one_sided_love"), weight=0.3),
    Question("q_item_number",    "Does it feature a prominent item number / special dance song?",
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
    Question("q_mass_entertainer","Is it a commercial mass masala entertainer?",
             _attr_true("is_mass_entertainer"), weight=0.3),
])

QUESTION_MAP: dict[str, Question] = {q.id: q for q in QUESTIONS}

LANGUAGE_QUESTION_IDS: set[str] = {'q_hindi', 'q_tamil', 'q_telugu'}
ERA_QUESTION_IDS: set[str]      = {'q_classic', 'q_90s', 'q_2000s', 'q_2010s', 'q_2020s'}
GENRE_QUESTION_IDS: set[str]    = {'q_genre_action', 'q_genre_comedy', 'q_genre_romance',
                                    'q_genre_drama', 'q_genre_thriller', 'q_genre_other'}
