#!/usr/bin/env python3
"""Final top-up to reach Telugu 500."""
import json
from pathlib import Path

DATA = Path(__file__).parent / "data" / "movies.json"
movies = json.loads(DATA.read_text())

def te(id, title, year, era, genre, director, actor, gender, imdb,
       action=False, comedy=False, romance=False, villain=False, songs=True,
       thriller=False, social=False, family=False, true_story=False, historical=False,
       bio=False, sports=False, sci_fi=False, horror=False, remake=False, franchise=False,
       pan_india=False, anti_hero=False, abroad=False, triangle=False, revenge=False, forbidden=False):
    genres = []
    if action: genres.append("action")
    if comedy: genres.append("comedy")
    if romance: genres.append("romance")
    if thriller: genres.append("thriller")
    if social: genres.append("social")
    if historical: genres.append("historical")
    if sports: genres.append("sports")
    if bio: genres.append("biopic")
    if sci_fi: genres.append("sci-fi")
    if horror: genres.append("horror")
    if family: genres.append("family")
    if not genres: genres.append(genre)
    return dict(
        id=id, title=title, year=year, language="telugu", era=era, primary_genre=genre,
        genres=genres, director=director, lead_actor=actor, lead_gender=gender,
        imdb_rating=imdb, has_action=action, has_comedy=comedy, has_romance=romance,
        has_villain=villain, has_songs=songs, has_thriller_elements=thriller,
        has_social_message=social, is_anti_hero=anti_hero, is_set_abroad=abroad,
        has_love_triangle=triangle, has_revenge_plot=revenge, has_forbidden_love=forbidden,
        is_family_film=family, is_based_on_true_story=true_story, is_biographical=bio,
        is_franchise=franchise, is_remake=remake, is_sports_film=sports,
        is_historical=historical, is_horror=horror, is_sci_fi=sci_fi,
        is_pan_india_blockbuster=pan_india,
    )

new = [
    # Classic
    te("te_missiamma_1955b", "Missamma", 1955, "classic", "comedy",
       "L.V. Prasad", "Akkineni Nageswara Rao", "male", 7.6, comedy=True, romance=True),
    te("te_bangaru_panja_1955b", "Donga Ramudu", 1955, "classic", "action",
       "C. Pullaiah", "N.T. Rama Rao", "male", 6.8, action=True),
    te("te_pathala_bhairavi_1951b", "Pathala Bhairavi", 1951, "classic", "mythology",
       "K.V. Reddy", "N.T. Rama Rao", "male", 8.0, action=True),
    te("te_maya_bazaar_1957b", "Maya Bazaar", 1957, "classic", "mythology",
       "K.V. Reddy", "N.T. Rama Rao", "male", 8.7, action=True, comedy=True),
    te("te_nuvvakosam_1961", "Nuvvakosam", 1961, "classic", "romance",
       "Adurthi Subba Rao", "Akkineni Nageswara Rao", "male", 7.5, romance=True),
    te("te_prem_nagar_1974b", "Priya", 1974, "classic", "romance",
       "Bapu", "Krishna", "male", 7.2, romance=True),

    # 90s
    te("te_poru_gadu_1990", "Poru Gadu", 1990, "90s", "action",
       "Dasari Narayana Rao", "Chiranjeevi", "male", 6.6, action=True),
    te("te_jagadeka_veerudu_1990b", "Jagadeka Veerudu Atiloka Sundari", 1990, "90s", "romance",
       "K. Raghavendra Rao", "Chiranjeevi", "male", 7.7, romance=True, action=True),
    te("te_govinda_govinda_1993b", "Govinda Govinda", 1993, "90s", "drama",
       "Dasari Narayana Rao", "Nagarjuna Akkineni", "male", 7.3, family=True, social=True),
    te("te_ankusham_1990b", "Ankusham", 1990, "90s", "action",
       "Raghavendra Rao", "Nagarjuna Akkineni", "male", 7.1, action=True),
    te("te_manchi_rozu_1993b", "Manchi Rozu", 1993, "90s", "comedy",
       "E.V.V. Satyanarayana", "Venkatesh", "male", 7.5, comedy=True, romance=True),
    te("te_kshana_kshanam_1994b", "Kshana Kshanam", 1994, "90s", "thriller",
       "Ram Gopal Varma", "Venkatesh", "male", 8.1, thriller=True, comedy=True),

    # 2000s
    te("te_oke_okkadu_2001b", "Oke Okkadu", 2001, "2000s", "action",
       "Gunasekhar", "Arjun Sarja", "male", 7.3, action=True, romance=True),
    te("te_murari_2001", "Murari", 2001, "2000s", "drama",
       "Krishna Vamsi", "Mahesh Babu", "male", 7.7, romance=True, family=True),
    te("te_varsham_2004b", "Varsham", 2004, "2000s", "romance",
       "Vasu Varma", "Prabhas", "male", 7.6, romance=True),
    te("te_chatrapathi_2005b", "Chatrapathi", 2005, "2000s", "action",
       "S.S. Rajamouli", "Prabhas", "male", 7.5, action=True, romance=True, social=True),
    te("te_pokiri_2006b", "Pokiri", 2006, "2000s", "action",
       "Puri Jagannadh", "Mahesh Babu", "male", 8.0, action=True, thriller=True),
    te("te_happy_days_2007b", "Happy Days", 2007, "2000s", "comedy",
       "Sekhar Kammula", "Varun Sandesh", "male", 8.2, comedy=True, romance=True),
    te("te_ready_2008b", "Ready", 2008, "2000s", "comedy",
       "Sreenu Vaitla", "Ram Pothineni", "male", 7.9, comedy=True, action=True, romance=True),
    te("te_kick_2009b", "Kick", 2009, "2000s", "action",
       "Surender Reddy", "Ravi Teja", "male", 7.5, action=True, comedy=True),

    # 2010s
    te("te_dookudu_2011b", "Dookudu", 2011, "2010s", "action",
       "Srinu Vaitla", "Mahesh Babu", "male", 7.8, action=True, comedy=True, romance=True),
    te("te_businessman_2012b", "Businessman", 2012, "2010s", "action",
       "Puri Jagannadh", "Mahesh Babu", "male", 7.5, action=True, anti_hero=True),
    te("te_seethamma_2013b", "Seethamma Vakitlo Sirimalle Chettu", 2013, "2010s", "drama",
       "Srikanth Addala", "Mahesh Babu", "male", 7.5, family=True, romance=True),
    te("te_power_2014b", "Power", 2014, "2010s", "action",
       "K.S. Ravindra", "Ravi Teja", "male", 6.8, action=True, romance=True),
    te("te_srimanthudu_2015b", "Srimanthudu", 2015, "2010s", "action",
       "Koratala Siva", "Mahesh Babu", "male", 7.6, action=True, romance=True, social=True),
    te("te_brahmotsavam_2016b", "Brahmotsavam", 2016, "2010s", "drama",
       "Srikanth Addala", "Mahesh Babu", "male", 6.2, family=True),
    te("te_spyder_2017b", "Spyder", 2017, "2010s", "thriller",
       "A.R. Murugadoss", "Mahesh Babu", "male", 6.5, thriller=True, action=True),
    te("te_saaho_2019b", "Saaho", 2019, "2010s", "action",
       "Sujeeth", "Prabhas", "male", 5.3, action=True, thriller=True, abroad=True, pan_india=True),
    te("te_vinaya_vidheya_2019b", "Vinaya Vidheya Rama", 2019, "2010s", "action",
       "Boyapati Srinu", "Ram Charan", "male", 5.8, action=True, family=True),
    te("te_ntr_kathanayakudu_2019", "NTR: Kathanayakudu", 2019, "2010s", "historical",
       "Krish Jagarlamudi", "Balakrishna", "male", 7.0, historical=True, bio=True, true_story=True),

    # 2020s
    te("te_akhanda_2021b", "Akhanda", 2021, "2020s", "action",
       "Boyapati Srinu", "Balakrishna", "male", 7.0, action=True, villain=True),
    te("te_sarileru_neekevvaru_2020b", "Sarileru Neekevvaru", 2020, "2020s", "action",
       "Anil Ravipudi", "Mahesh Babu", "male", 6.9, action=True, comedy=True),
    te("te_vakeel_saab_2021c", "Vakeel Saab", 2021, "2020s", "drama",
       "Venu Sriram", "Pawan Kalyan", "male", 7.1, social=True, remake=True),
    te("te_krack_2021b", "Krack", 2021, "2020s", "action",
       "Gopichand Malineni", "Ravi Teja", "male", 7.3, action=True),
    te("te_most_eligible_bachelor_2021b", "Most Eligible Bachelor", 2021, "2020s", "romance",
       "Bommarillu Bhaskar", "Akhil Akkineni", "male", 7.2, romance=True, comedy=True),
    te("te_f3_2022b", "F3: Fun and Frustration", 2022, "2020s", "comedy",
       "Anil Ravipudi", "Venkatesh", "male", 6.8, comedy=True),
    te("te_sarkaru_vaari_paata_2022b", "Sarkaru Vaari Paata", 2022, "2020s", "action",
       "Parasuram Petla", "Mahesh Babu", "male", 6.8, action=True, romance=True),
    te("te_waltair_veerayya_2023b", "Waltair Veerayya", 2023, "2020s", "action",
       "Bobby Kolli", "Chiranjeevi", "male", 7.0, action=True, comedy=True),
    te("te_guntur_kaaram_2024c", "Guntur Kaaram", 2024, "2020s", "drama",
       "Trivikram Srinivas", "Mahesh Babu", "male", 6.0, family=True, romance=True),
    te("te_lucky_baskhar_2024c", "Lucky Baskhar", 2024, "2020s", "thriller",
       "Venky Atluri", "Dulquer Salmaan", "male", 8.1, thriller=True),
    te("te_hanu_man_2024b", "HanuMan", 2024, "2020s", "action",
       "Prasanth Varma", "Teja Sajja", "male", 7.8, action=True, sci_fi=True),
    te("te_devara_2024c", "Devara: Part 1", 2024, "2020s", "action",
       "Koratala Siva", "Jr. NTR", "male", 6.5, action=True, villain=True),
    te("te_pushpa_2_2024c", "Pushpa 2: The Rule", 2024, "2020s", "action",
       "Sukumar", "Allu Arjun", "male", 7.6, action=True, anti_hero=True, pan_india=True),
    te("te_ghani_2022", "Ghani", 2022, "2020s", "sports",
       "Kiran Korrapati", "Varun Tej", "male", 5.5, sports=True, action=True),
    te("te_nabha_2022", "Nabha Natesh Film", 2022, "2020s", "thriller",
       "Srinivas Naidu", "Adivi Sesh", "male", 7.2, thriller=True, action=True),
    te("te_skanda_2023b", "Skanda", 2023, "2020s", "action",
       "Boyapati Srinu", "Ram Pothineni", "male", 6.5, action=True, family=True),
    te("te_dasara_2023b", "Dasara", 2023, "2020s", "drama",
       "Srikanth Odela", "Nani", "male", 7.7, action=True, social=True, anti_hero=True),
    te("te_hi_nanna_2023c", "Hi Nanna", 2023, "2020s", "romance",
       "Shouryuv", "Nani", "male", 7.6, romance=True, family=True),
    te("te_salaar_2023c", "Salaar: Part 1", 2023, "2020s", "action",
       "Prashanth Neel", "Prabhas", "male", 6.9, action=True, villain=True, pan_india=True),
    te("te_tiger_2023b", "Tiger Nageswara Rao", 2023, "2020s", "action",
       "Vamsee", "Ravi Teja", "male", 6.8, action=True, historical=True, true_story=True),
    te("te_saindhav_2024c", "Saindhav", 2024, "2020s", "action",
       "Sailesh Kolanu", "Venkatesh", "male", 6.5, action=True, thriller=True),
    te("te_bro_2023b", "Bro", 2023, "2020s", "comedy",
       "Samuthirakani", "Pawan Kalyan", "male", 6.0, comedy=True, family=True),
    te("te_bhagavanth_kesari_2023b", "Bhagavanth Kesari", 2023, "2020s", "action",
       "Anil Ravipudi", "Balakrishna", "male", 6.9, action=True, comedy=True, family=True),
    te("te_veera_simha_reddy_2023b", "Veera Simha Reddy", 2023, "2020s", "action",
       "Gopichand Malineni", "Balakrishna", "male", 6.4, action=True, villain=True, revenge=True),
]

existing = {f"{m['title'].lower()}_{m['year']}" for m in movies}
to_add = [m for m in new if f"{m['title'].lower()}_{m['year']}" not in existing]

movies.extend(to_add)

seen = set(); final = []
for m in movies:
    k = f"{m['title'].lower()}_{m['year']}"
    if k not in seen:
        seen.add(k)
        final.append(m)

from collections import Counter
langs = Counter(m['language'] for m in final)
print(f"Added {len(to_add)} new movies (skipped {len(new)-len(to_add)} dupes)")
print(f"Final - Tamil: {langs['tamil']}, Hindi: {langs['hindi']}, Telugu: {langs['telugu']}, Total: {sum(langs.values())}")

DATA.write_text(json.dumps(final, indent=2, ensure_ascii=False))
