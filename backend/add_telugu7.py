#!/usr/bin/env python3
"""Final Telugu top-up: target 500. Also remove Salaar duplicate."""
import json
from pathlib import Path

DATA = Path(__file__).parent / "data" / "movies.json"
movies = json.loads(DATA.read_text())

# Fix: "Salaar" and "Salaar: Part 1" are the same 2023 film — keep the longer title
movies = [m for m in movies if not (m.get('title') == 'Salaar' and m.get('year') == 2023 and m.get('language') == 'telugu')]

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
    te("te_geetanjali_1989", "Geetanjali", 1989, "classic", "romance",
       "Ram Gopal Varma", "Nagarjuna Akkineni", "male", 8.1, romance=True),

    # 2000s
    te("te_amma_nanna_o_tamila_ammayi_2003", "Amma Nanna O Tamila Ammayi", 2003, "2000s", "romance",
       "Puri Jagannadh", "Ravi Teja", "male", 7.8, romance=True, comedy=True, action=True),
    te("te_dhee_2007", "Dhee", 2007, "2000s", "action",
       "Srinu Vaitla", "Allu Arjun", "male", 7.3, action=True, comedy=True),
    te("te_oye_2009", "Oye!", 2009, "2000s", "romance",
       "Anand Ranga", "Siddharth", "male", 7.3, romance=True, comedy=True),
    te("te_murari_2001b", "Murari", 2001, "2000s", "drama",
       "Krishna Vamsi", "Mahesh Babu", "male", 7.7, romance=True, family=True),
    te("te_takkari_donga_2002", "Takkari Donga", 2002, "2000s", "romance",
       "Nandini Reddi", "Mahesh Babu", "male", 7.1, romance=True, comedy=True, abroad=True),

    # 2010s
    te("te_100percent_love_2011", "100% Love", 2011, "2010s", "romance",
       "Sukumar", "Naga Chaitanya", "male", 7.5, romance=True),
    te("te_srirama_rajyam_2011", "Srirama Rajyam", 2011, "2010s", "historical",
       "Bapu", "Balakrishna", "male", 7.2, historical=True),
    te("te_andala_rakshasi_2012", "Andala Rakshasi", 2012, "2010s", "romance",
       "Vasu Varma", "Naveen Polishetty", "male", 7.6, romance=True, comedy=True),
    te("te_sahasam_2013", "Sahasam", 2013, "2010s", "action",
       "Chandra Sekhar Yeleti", "Prashanth", "male", 7.0, action=True, thriller=True),
    te("te_ra_ra_krishnayya_2014", "Ra Ra Krishnayya", 2014, "2010s", "comedy",
       "G. Nageswara Reddy", "Sundeep Kishan", "male", 7.4, comedy=True, action=True),
    te("te_pilla_nuvvu_leni_jeevitham_2014", "Pilla Nuvvu Leni Jeevitham", 2014, "2010s", "romance",
       "A. Karunakaran", "Sai Dharam Tej", "male", 7.2, romance=True, family=True),
    te("te_babu_bangaram_2016", "Babu Bangaram", 2016, "2010s", "comedy",
       "Maruthi Dasari", "Venkatesh", "male", 7.1, comedy=True, romance=True, action=True),
    te("te_nenu_rowdy_ne_2016", "Nenu Rowdy Ne", 2016, "2010s", "romance",
       "Kishore Tirumala", "Vijay Deverakonda", "male", 7.4, romance=True, comedy=True),
    te("te_nenu_nanna_abbayi_2016", "Nenu Nanna Abbayi", 2016, "2010s", "comedy",
       "Maruthi Dasari", "Raj Tarun", "male", 7.0, comedy=True, romance=True),
    te("te_hyper_2016", "Hyper", 2016, "2010s", "action",
       "Santosh Srinivas", "Ram Pothineni", "male", 6.5, action=True, romance=True, comedy=True),
    te("te_krishnashtami_2016", "Krishnashtami", 2016, "2010s", "comedy",
       "Vasu Varma", "Sunil", "male", 7.2, comedy=True, action=True),
    te("te_malli_raava_2017", "Malli Raava", 2017, "2010s", "romance",
       "Gautham Tinnanuri", "Sumanth", "male", 7.7, romance=True),
    te("te_mahanubhavudu_2017", "Mahanubhavudu", 2017, "2010s", "comedy",
       "Maruthi Dasari", "Sharwanand", "male", 7.6, comedy=True, action=True, romance=True),
    te("te_sammohanam_2018", "Sammohanam", 2018, "2010s", "romance",
       "Mohan Krishna Indraganti", "Sudheer Babu", "male", 7.7, romance=True),
    te("te_ee_nagaraniki_emaindi_2018", "Ee Nagaraniki Emaindi", 2018, "2010s", "comedy",
       "Tharun Bhascker", "Vishwak Sen", "male", 7.6, comedy=True, romance=True, abroad=True),
    te("te_devadas_2018", "Devadas", 2018, "2010s", "comedy",
       "Sriram Aditya", "Nagarjuna Akkineni", "male", 6.8, comedy=True, action=True),
    te("te_ntr_mahanayakudu_2019", "NTR: Mahanayakudu", 2019, "2010s", "historical",
       "Krish Jagarlamudi", "Balakrishna", "male", 6.8, historical=True, bio=True, true_story=True),
    te("te_gentleman_2016c", "Gentleman", 2023, "2020s", "action",
       "Mohan Krishna Indraganti", "Nithiin", "male", 6.5, action=True, romance=True),

    # 2020s
    te("te_middle_class_melodies_2020", "Middle Class Melodies", 2020, "2020s", "comedy",
       "Vinod Anantoju", "Anand Deverakonda", "male", 8.0, comedy=True, family=True, social=True),
    te("te_orey_bujjiga_2020", "Orey Bujjiga", 2020, "2020s", "comedy",
       "Vasu Varma", "Raj Tarun", "male", 7.3, comedy=True, romance=True),
    te("te_adipurush_2023", "Adipurush", 2023, "2020s", "historical",
       "Om Raut", "Prabhas", "male", 2.8, historical=True, action=True, pan_india=True),
    te("te_raja_raja_chora_2022", "Raja Raja Chora", 2022, "2020s", "comedy",
       "Srinivas Avasarala", "Sree Vishnu", "male", 7.4, comedy=True, romance=True, thriller=True),
    te("te_thellavarithe_guruvaram_2022", "Thellavarithe Guruvaram", 2022, "2020s", "romance",
       "Srinivas Naidu", "Satyadev Kancharana", "male", 7.1, romance=True),
    te("te_hit_3_2023", "HIT: The Third Case", 2023, "2020s", "thriller",
       "Sailesh Kolanu", "Nani", "male", 7.5, thriller=True, songs=False, franchise=True),
    te("te_bichagadu_2_2023", "Bichagadu 2", 2023, "2020s", "thriller",
       "Deekay", "Vijay Antony", "male", 6.5, thriller=True, action=True),
    te("te_james_2022", "James", 2022, "2020s", "action",
       "Chethan Kumar", "Puneeth Rajkumar", "male", 7.0, action=True),
    te("te_dasara_2023c", "Dasara", 2023, "2020s", "drama",
       "Srikanth Odela", "Nani", "male", 7.7, action=True, social=True, anti_hero=True),
    te("te_mem_famous_2022b", "Mem Famous", 2022, "2020s", "comedy",
       "Sumanth Prabhas", "Suhas", "male", 7.8, comedy=True),
    te("te_COLOR_photo_2020c", "Colour Photo", 2020, "2020s", "romance",
       "Mohan Krishna Indraganti", "Suhas", "male", 8.4, romance=True, social=True),
    te("te_karthikeya2_2022c", "Karthikeya 2", 2022, "2020s", "action",
       "Chandoo Mondeti", "Nikhil Siddharth", "male", 7.6, action=True, historical=True),
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
