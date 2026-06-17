#!/usr/bin/env python3
"""
Analyze 2527 Indian films for 5 narrative patterns:
1. has_patriotic_sacrifice - Story centers on sacrifice for nation/duty (death for country, choosing duty over happiness)
2. has_nri_cultural_tension - NRI/expat identity conflict (protagonist torn between two worlds)
3. has_fated_romance - "Meant to be" couples; romance as destiny (lovers cosmically connected, tragic romance)
4. has_patriarchal_resistance - Protagonist challenges rigid authority through emotion (fighting patriarchal/institutional rigidity)
5. has_male_emotional_vulnerability - Male lead's crying/breakdown as strength (trembling, begging, vulnerability as powerful moment)
"""

import json
from pathlib import Path
from typing import Dict, List

# Load films
movies_path = Path("/Users/sandeep.srinivasan/sand-ship/indian-movie-genie/backend/data/movies.json")
with open(movies_path, 'r') as f:
    films = json.load(f)

print(f"Loaded {len(films)} films")

# STRICT Knowledge bases - only high confidence matches

# Pattern 1: PATRIOTIC SACRIFICE - Story centers on sacrifice for nation/duty
# Death for country, choosing duty over happiness, patriotic climax
patriotic_sacrifice_titles = {
    "sholay", "border", "hey ram", "rang de basanti", "lagaan", "bhagat singh",
    "dil diya hai jaan doge", "raees", "lakshya", "jai bhim",
    "partition 1947", "the tashkent files", "sardar udham", "kesari",
    "article 15", "aandhi", "amar akbar anthony", "veer", "mangal pandey",
    "jhansi ki rani", "paathaalam", "samrat prithviraj", "singham",
    "gully boy", "no smoking", "path", "the waterboys",
    "natarang", "kadhaal", "baishe srabon", "udta punjab",
    "haramkhor", "gangs of wasseypur", "jab we met",
    "khula aasmaan", "rann", "khaki", "sinhaasan", "bhaiyya ji",
    "pather panchali", "charulata", "dil se", "roj", "rang de basanti"
}

# Pattern 2: NRI CULTURAL TENSION - NRI/expat identity conflict
# Protagonist torn between two worlds, cultural identity struggle
nri_titles = {
    "dilwale dulhania le jayenge", "ddlj", "kuch kuch hota hai", "kkh",
    "yeh jawaani hai deewani", "karan arjun", "mission china",
    "london dreams", "dostana", "break ke baad", "chandni", "pardes",
    "barsaat", "shaadi ka laddoo", "kabhi haan kabhi naa", "swades",
    "kal ho naa ho", "kabhi khushi kabhie gham", "dil hai betaab",
    "teri meraa pyar", "lucky", "aaj kal", "billu", "jaane tu ya jaane na",
    "roop ki rani choron ka raja", "lamhe", "hera pheri", "dil se",
    "london", "atithi", "namastey london", "dostana 2", "bhindi baazaar",
    "mere brother ki dulhan", "london ishq", "khud dekhi", "agneepath",
    "devdas (london)", "maine dil tanhaa", "dil dole", "hera pheri 2",
    "badhaai do", "drishyam", "aha", "saarangi", "arth"
}

# Pattern 3: FATED ROMANCE - "Meant to be" couples; romance as destiny
# Lovers cosmically connected, tragic romance, impossible love
# KEY: Romance + Drama/Musical + High Rating (tragic love stories)
# NOTE: "Swades" and "Rang De Basanti" have romance but primary theme is patriotic, not romance
fated_romance_titles = {
    "devdas", "umrao jaan", "padmaavat", "hum dil de chuke sanam",
    "jab tak hai jaan", "raanjhanaa", "ae dil hai mushkil", "guzaarish",
    "aashiqui", "aashiqui 2", "sanam teri kasam", "firaaq", "fanaa",
    "pakeezah", "chandni", "dil", "dil ka kya kasoor", "lamhe",
    "prem granth", "shree 420", "alaipayuthey", "kaavalan",
    "madhanolayuthey", "roja", "saarangi", "guru", "raag",
    "baahubali: the beginning", "baahubali 2", "magadheera", "eega",
    "chandni bar", "water", "baishe srabon", "teri meraa pyar",
    "natarang", "khuda haafiz", "geet", "roop ki rani choron ka raja",
    "mughal-e-azam", "kohinoor", "saudagar", "woh lamhe", "dil se"
}

# Exclude from fated_romance: films where romance is secondary
non_fated_romance_secondary = {
    "swades", "rang de basanti", "lagaan", "rang de", "jai bhim"
}

# Pattern 4: PATRIARCHAL RESISTANCE - Protagonist challenges rigid authority through emotion
# Fighting patriarchal/institutional rigidity via emotional persuasion
patriarchal_resistance_titles = {
    "pink", "thappad", "chup", "water", "bandit queen", "piku",
    "alaipayuthey", "taare zameen par", "khuda haafiz", "patralekhaa",
    "badhaai do", "kahani", "natarang", "anand", "post office",
    "ankur", "dangal", "3 idiots", "teri meraa pyar", "neeraj",
    "rang de basanti", "khuda haafiz 2", "raees", "article 15",
    "gully boy", "udta punjab", "dil dole", "kadhaal",
    "haramkhor", "gangs of wasseypur", "baishe srabon",
    "arth", "silsila", "kyun ho gaya na", "do aankhen barah haath",
    "jai bhim", "pather panchali", "charulata", "aandhi",
    "saarangi", "roja", "kaavalan", "madhanolayuthey",
    "khul ja simsim", "bhanja", "krishna", "swades", "kal ho naa ho"
}

# Pattern 5: MALE EMOTIONAL VULNERABILITY - Male lead's crying/breakdown as strength
# Trembling, begging, vulnerability as powerful/climactic moment
male_vulnerability_titles = {
    "anand", "taare zameen par", "post office", "barfi", "bhaag milkha bhaag",
    "haramkhor", "udta punjab", "raag", "khuda haafiz", "guzaarish",
    "khamoshiyan", "bhaiyya ji", "piku", "kadhaal", "teri meraa pyar",
    "hey ram", "devdas", "rang de basanti", "kal ho naa ho", "dil se",
    "roja", "saarangi", "neeraj", "drishyam", "gangs of wasseypur",
    "baishe srabon", "jai bhim", "no smoking", "chandni bar",
    "water", "swades", "lagaan", "dangal", "siddharth",
    "roop ki rani choron ka raja", "natarang", "pather panchali",
    "charulata", "ankur", "aandhi", "khul ja simsim", "arjun", "aashiqui",
    "aashiqui 2", "sanam teri kasam", "lamhe", "woh lamhe"
}

# Actor-based signals (CONSERVATIVE)
patriotic_actors_strong = {
    "amitabh bachchan", "rajesh khanna", "dilip kumar", "sunny deol",
    "ajay devgn", "aamir khan", "salman khan",
    "irrfan khan", "nawazuddin siddiqui", "pankaj tripathi",
    "vicky kaushal", "rajpal yadav", "vidya balan", "kangana ranaut"
}

nri_actors_strong = {
    "shah rukh khan", "kajol", "kareena kapoor khan", "deepika padukone",
    "madhuri dixit", "sridevi", "priyanka chopra", "vidya balan",
    "katrina kaif", "sonam kapoor", "anushka sharma", "aditya roy kapur",
    "sidharth malhotra", "varun dhawan", "dilip kumar", "rajesh khanna",
    "rishi kapoor"
}

emotional_vulnerability_actors_strong = {
    "irrfan khan", "rajpal yadav", "nawazuddin siddiqui", "amol palekar",
    "aamir khan", "ranbir kapoor", "ranveer singh", "rajkummar rao",
    "vicky kaushal", "kartik aaryan", "ayushmann khurrana", "sidharth malhotra",
    "arjun kapoor", "sushant singh rajput", "siddhant chaturvedi", "shahid kapoor"
}

female_resistance_actors_strong = {
    "sridevi", "madhuri dixit", "tabu", "vidya balan", "kangana ranaut",
    "deepika padukone", "priyanka chopra", "katrina kaif", "kareena kapoor khan",
    "sonam kapoor", "anushka sharma", "swara bhasker", "bhumi pednekar",
    "radhika apte", "taapsee pannu", "yami gautam", "kriti sanon",
    "shraddha kapoor", "alia bhatt", "rekha"
}


def analyze_film(film: Dict) -> List[str]:
    """Analyze a single film and return list of detected narrative patterns."""
    patterns = []
    title_lower = film.get("title", "").lower()
    lead_actor = (film.get("lead_actor", "") or "").lower()
    lead_actress = (film.get("lead_actress", "") or "").lower()
    genres = [g.lower() for g in film.get("genres", [])]
    year = film.get("year", 0)

    is_comedy = "comedy" in genres
    is_drama = "drama" in genres
    is_musical = "musical" in genres
    is_historical = film.get("is_historical", False) or "historical" in genres
    is_romance_genre = "romance" in genres or film.get("has_romance", False)
    is_period = film.get("is_period_drama", False)
    has_action = film.get("has_action", False)
    has_social_msg = film.get("has_social_message", False)
    has_class_conflict = film.get("has_class_conflict", False)
    has_romance = film.get("has_romance", False)
    has_love_triangle = film.get("has_love_triangle", False)
    has_forbidden = film.get("has_forbidden_love", False)
    has_parent_child = film.get("has_parent_child_drama", False)
    set_abroad = film.get("is_set_abroad", False)
    imdb = film.get("imdb_rating", 0)
    lead_gender = (film.get("lead_gender", "") or "").lower()

    # ===== PATTERN 1: PATRIOTIC SACRIFICE =====
    # STRICT: Must be about national duty/sacrifice, not just social issues
    if any(t in title_lower for t in patriotic_sacrifice_titles):
        patterns.append("has_patriotic_sacrifice")
    elif lead_actor and any(actor in lead_actor for actor in ["amitabh bachchan", "sunny deol", "ajay devgn", "salman khan"]) and has_social_msg and ("war" in genres or "action" in genres):
        patterns.append("has_patriotic_sacrifice")
    elif is_historical and ("war" in genres or "freedom" in title_lower) and year <= 2000:
        patterns.append("has_patriotic_sacrifice")

    # ===== PATTERN 2: NRI CULTURAL TENSION =====
    # Set abroad + romance + identity conflict OR known NRI title
    if any(t in title_lower for t in nri_titles):
        patterns.append("has_nri_cultural_tension")
    elif set_abroad and has_romance and (has_class_conflict or has_parent_child):
        patterns.append("has_nri_cultural_tension")
    elif lead_actor and any(actor in lead_actor for actor in nri_actors_strong) and set_abroad and has_romance:
        patterns.append("has_nri_cultural_tension")

    # ===== PATTERN 3: FATED ROMANCE =====
    # Romance + Drama/Musical + High Rating (tragic love stories)
    # OR title match, OR period/historical romance
    # NOTE: Exclude films where romance is secondary to patriotic/NRI/patriarchal themes
    if any(t in title_lower for t in fated_romance_titles) and not is_comedy and title_lower not in non_fated_romance_secondary:
        patterns.append("has_fated_romance")
    elif (is_romance_genre and is_period and not is_comedy and title_lower not in non_fated_romance_secondary):
        patterns.append("has_fated_romance")
    elif (is_romance_genre and is_historical and not is_comedy and title_lower not in non_fated_romance_secondary):
        patterns.append("has_fated_romance")
    # Tragic romance: romance + drama/musical + high rating + forbidden/love triangle
    elif (is_romance_genre and (is_drama or is_musical) and imdb >= 7.2 and
          (has_forbidden or has_love_triangle or "tragedy" in genres) and not is_comedy and
          title_lower not in non_fated_romance_secondary):  # Exclude secondary romance stories
        patterns.append("has_fated_romance")
    # Romantic drama with very high rating is often fated (if no action/thriller indicating secondary romance)
    elif (is_romance_genre and is_drama and imdb >= 7.4 and not is_comedy and
          not has_action and not film.get("has_thriller_elements", False) and
          title_lower not in non_fated_romance_secondary):
        patterns.append("has_fated_romance")

    # ===== PATTERN 4: PATRIARCHAL RESISTANCE =====
    # Challenge to rigid authority, emotional overcoming
    if any(t in title_lower for t in patriarchal_resistance_titles):
        patterns.append("has_patriarchal_resistance")
    elif lead_actress and any(actress in lead_actress for actress in female_resistance_actors_strong) and (has_social_msg or has_class_conflict):
        patterns.append("has_patriarchal_resistance")
    elif (has_class_conflict and has_parent_child and is_drama and not ("action" in genres and has_action and imdb < 6.5)):
        patterns.append("has_patriarchal_resistance")
    elif (has_social_msg and has_class_conflict and is_drama):
        patterns.append("has_patriarchal_resistance")

    # ===== PATTERN 5: MALE EMOTIONAL VULNERABILITY =====
    # Male lead's vulnerability/breakdown as strength
    if any(t in title_lower for t in male_vulnerability_titles) and not is_comedy:
        patterns.append("has_male_emotional_vulnerability")
    elif lead_actor and any(actor in lead_actor for actor in emotional_vulnerability_actors_strong) and is_drama:
        patterns.append("has_male_emotional_vulnerability")
    elif (lead_gender == "male" and is_drama and not has_action and not film.get("has_thriller_elements", False) and imdb >= 7.1):
        patterns.append("has_male_emotional_vulnerability")
    elif (lead_gender == "male" and has_parent_child and is_drama and imdb >= 6.9):
        patterns.append("has_male_emotional_vulnerability")

    return list(set(patterns))  # Remove duplicates


# Process all films
results = []
for film in films:
    patterns = analyze_film(film)
    if patterns:  # Only include films with detected patterns
        results.append({
            "title": film.get("title"),
            "patterns": sorted(patterns)  # Sort for consistency
        })

# Save results
output_path = Path("/Users/sandeep.srinivasan/sand-ship/indian-movie-genie/narrative_patterns_analysis.json")
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)

# Summary statistics
print(f"\nAnalysis complete!")
print(f"Total films with patterns detected: {len(results)} / {len(films)}")
print(f"Coverage: {len(results)/len(films)*100:.1f}%")

# Pattern distribution
pattern_counts = {}
for film in results:
    for pattern in film["patterns"]:
        pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1

print("\nPattern distribution:")
for pattern in sorted(pattern_counts.keys()):
    count = pattern_counts[pattern]
    print(f"  {pattern}: {count} films ({count/len(films)*100:.1f}%)")

# Multi-pattern films
multi_pattern_count = sum(1 for f in results if len(f["patterns"]) > 1)
print(f"\nFilms with multiple patterns: {multi_pattern_count} ({multi_pattern_count/len(films)*100:.1f}%)")

print(f"\nResults saved to: {output_path}")
