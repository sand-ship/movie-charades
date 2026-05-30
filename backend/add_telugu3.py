#!/usr/bin/env python3
"""Add more Telugu films (batch 3) and fix Tamil count to 500."""
import json, re
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

def ta(id, title, year, era, genre, director, actor, gender, imdb,
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
        id=id, title=title, year=year, language="tamil", era=era, primary_genre=genre,
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
    # ── Classic era ───────────────────────────────────────────────────────
    te("te_tenali_ramakrishna_1956", "Tenali Ramakrishna", 1956, "classic", "comedy",
       "B. Vittalacharya", "N.T. Rama Rao", "male", 7.2, comedy=True),
    te("te_bhookailas_1958", "Bhookailas", 1958, "classic", "mythology",
       "B. Vittalacharya", "N.T. Rama Rao", "male", 7.5, action=True),
    te("te_gundamma_katha_1962", "Gundamma Katha", 1962, "classic", "comedy",
       "L.V. Prasad", "N.T. Rama Rao", "male", 8.1, comedy=True, romance=True),
    te("te_lava_kusa_1963", "Lava Kusa", 1963, "classic", "mythology",
       "Kadiri Venkata Reddy", "N.T. Rama Rao", "male", 7.8, action=True),
    te("te_nartanasala_1963", "Nartanasala", 1963, "classic", "romance",
       "B. Vittalacharya", "N.T. Rama Rao", "male", 7.3, romance=True),
    te("te_sri_krishnarjuna_yuddham_1963", "Sri Krishnarjuna Yuddham", 1963, "classic", "action",
       "Kadiri Venkata Reddy", "N.T. Rama Rao", "male", 7.4, action=True),
    te("te_mooga_manasulu_1964", "Mooga Manasulu", 1964, "classic", "drama",
       "Adurthi Subba Rao", "Akkineni Nageswara Rao", "male", 7.8, romance=True, social=True),
    te("te_bhale_mastaru_1969", "Bhale Mastaru", 1969, "classic", "comedy",
       "B.V. Prasad", "Akkineni Nageswara Rao", "male", 7.0, comedy=True),
    te("te_annadammula_anubandham_1972", "Annadammula Anubandham", 1972, "classic", "drama",
       "Bapu", "Akkineni Nageswara Rao", "male", 7.2, family=True),
    te("te_o_seeta_katha_1974", "O Seeta Katha", 1974, "classic", "drama",
       "Bapu", "Shyam", "male", 7.5, romance=True, social=True),
    te("te_anthuleni_katha_1976", "Anthuleni Katha", 1976, "classic", "drama",
       "K. Viswanath", "Akkineni Nageswara Rao", "male", 7.8, social=True),
    te("te_siri_siri_muvva_1976", "Siri Siri Muvva", 1976, "classic", "romance",
       "K. Viswanath", "Chandra Mohan", "male", 7.4, romance=True),
    te("te_premabhishekam_1981", "Premabhishekam", 1981, "classic", "romance",
       "Dasari Narayana Rao", "Akkineni Nageswara Rao", "male", 7.5, romance=True),
    te("te_subhalekha_1982", "Subhalekha", 1982, "classic", "drama",
       "K. Viswanath", "Chandra Mohan", "male", 7.6, social=True),
    te("te_sitaara_1984", "Sitaara", 1984, "classic", "drama",
       "K. Viswanath", "Bhanupriya", "female", 7.7, social=True),
    te("te_sirivennela_1986", "Sirivennela", 1986, "classic", "drama",
       "K. Viswanath", "Sarvadaman D. Banerjee", "male", 7.9, social=True),
    te("te_swathi_mutyam_1986", "Swathi Mutyam", 1986, "classic", "drama",
       "K. Viswanath", "Kamal Haasan", "male", 8.1, social=True, family=True),

    # ── 90s ──────────────────────────────────────────────────────────────
    te("te_rowdy_alludu_1991", "Rowdy Alludu", 1991, "90s", "action",
       "A. Kodandarami Reddy", "Chiranjeevi", "male", 6.8, action=True, villain=True),
    te("te_seetharamaiah_gari_manavaralu_1991", "Seetharamaiah Gari Manavaralu", 1991, "90s", "drama",
       "Madhusudhana Rao", "Akkineni Nageswara Rao", "male", 7.8, family=True, social=True),
    te("te_golimaar_1992", "Golimaar", 1992, "90s", "action",
       "A. Kodandarami Reddy", "Chiranjeevi", "male", 7.0, action=True, villain=True),
    te("te_srimannarayana_1992", "Srimannarayana", 1992, "90s", "action",
       "Kodi Ramakrishna", "Balakrishna", "male", 6.8, action=True),
    te("te_gharana_bullodu_1994", "Gharana Bullodu", 1994, "90s", "action",
       "A. Kodandarami Reddy", "Chiranjeevi", "male", 6.9, action=True, comedy=True),
    te("te_allari_alludu_1994", "Allari Alludu", 1994, "90s", "comedy",
       "Kovelamudi Raghavendra Rao", "Chiranjeevi", "male", 6.5, comedy=True),
    te("te_preminchukundam_raa_1994", "Preminchukundam Raa", 1994, "90s", "romance",
       "S.V. Krishna Reddy", "Venkatesh", "male", 7.2, romance=True, comedy=True),
    te("te_kondapalli_raja_1994", "Kondapalli Raja", 1994, "90s", "action",
       "Suresh Krishna", "Venkatesh", "male", 7.3, action=True, villain=True),
    te("te_ninne_pelladatha_1996", "Ninne Pelladatha", 1996, "90s", "romance",
       "M. Raju", "Nagarjuna Akkineni", "male", 7.5, romance=True),
    te("te_suryavamsam_1997", "Suryavamsam", 1997, "90s", "drama",
       "K. Raghavendra Rao", "Venkatesh", "male", 7.6, family=True, social=True),
    te("te_choodalani_undi_1998", "Choodalani Undi", 1998, "90s", "romance",
       "Puri Jagannadh", "Nagarjuna Akkineni", "male", 7.0, romance=True, comedy=True),
    te("te_abhimanyu_1999", "Abhimanyu", 1999, "90s", "romance",
       "Puri Jagannadh", "Tarun", "male", 7.3, romance=True, comedy=True),
    te("te_ravoyi_chandamama_1999", "Ravoyi Chandamama", 1999, "90s", "comedy",
       "S.V. Krishna Reddy", "Nagarjuna Akkineni", "male", 7.4, comedy=True, romance=True),
    te("te_samarasimha_reddy_1999", "Samarasimha Reddy", 1999, "90s", "action",
       "S.V. Krishna Reddy", "Balakrishna", "male", 7.4, action=True, villain=True, revenge=True),
    te("te_president_gari_pellam_1990", "President Gari Pellam", 1990, "90s", "comedy",
       "P. Chandrasekhar Reddy", "Mohan Babu", "male", 7.2, comedy=True),

    # ── 2000s ─────────────────────────────────────────────────────────────
    te("te_narasimha_naidu_2001", "Narasimha Naidu", 2001, "2000s", "action",
       "S.V. Krishna Reddy", "Balakrishna", "male", 7.1, action=True, villain=True),
    te("te_nuvve_nuvve_2002", "Nuvve Nuvve", 2002, "2000s", "romance",
       "Trivikram Srinivas", "Tarun", "male", 7.3, romance=True, comedy=True),
    te("te_jayam_2002", "Jayam", 2002, "2000s", "action",
       "Teja", "Nithin", "male", 7.2, action=True, romance=True),
    te("te_tagore_2003", "Tagore", 2003, "2000s", "action",
       "V.V. Vinayak", "Chiranjeevi", "male", 7.1, action=True, social=True),
    te("te_sye_2004", "Sye", 2004, "2000s", "sports",
       "S.S. Rajamouli", "Nithin", "male", 7.6, sports=True, action=True),
    te("te_pournami_2006", "Pournami", 2006, "2000s", "romance",
       "S.S. Rajamouli", "Prabhas", "male", 7.1, romance=True, action=True),
    te("te_annavaram_2006", "Annavaram", 2006, "2000s", "action",
       "Vasu Varma", "Pawan Kalyan", "male", 7.3, action=True, social=True),
    te("te_ashok_2006", "Ashok", 2006, "2000s", "action",
       "S.S. Rajamouli", "Jr. NTR", "male", 7.3, action=True, romance=True),
    te("te_chirutha_2007", "Chirutha", 2007, "2000s", "action",
       "Puri Jagannadh", "Ram Charan", "male", 7.1, action=True, romance=True),
    te("te_tulasi_2007", "Tulasi", 2007, "2000s", "drama",
       "Boyapati Srinu", "Venkatesh", "male", 7.4, action=True, family=True),
    te("te_lakshyam_2007", "Lakshyam", 2007, "2000s", "action",
       "Boyapati Srinu", "Gopichand", "male", 7.3, action=True, villain=True),
    te("te_kantri_2008", "Kantri", 2008, "2000s", "action",
       "Meher Ramesh", "Jr. NTR", "male", 6.9, action=True, comedy=True),
    te("te_bujjigadu_2008", "Bujjigadu", 2008, "2000s", "comedy",
       "Puri Jagannadh", "Prabhas", "male", 6.9, comedy=True, action=True),
    te("te_kick_2009", "Kick", 2009, "2000s", "action",
       "Surender Reddy", "Ravi Teja", "male", 7.5, action=True, comedy=True),
    te("te_naa_istam_2009", "Naa Istam", 2009, "2000s", "romance",
       "Srinivas Avasarala", "Rana Daggubati", "male", 7.0, romance=True, comedy=True),

    # ── 2010s ─────────────────────────────────────────────────────────────
    te("te_ye_maaya_chesave_2010", "Ye Maaya Chesave", 2010, "2010s", "romance",
       "Gautham Vasudev Menon", "Naga Chaitanya", "male", 8.0, romance=True),
    te("te_badrinath_2011", "Badrinath", 2011, "2010s", "action",
       "V.V. Vinayak", "Allu Arjun", "male", 6.5, action=True, romance=True),
    te("te_mirapakay_2011", "Mirapakay", 2011, "2010s", "action",
       "Gopichand Malineni", "Ravi Teja", "male", 6.8, action=True, comedy=True),
    te("te_oosaravelli_2011", "Oosaravelli", 2011, "2010s", "action",
       "Surender Reddy", "Jr. NTR", "male", 6.9, action=True, romance=True),
    te("te_eega_2012", "Eega", 2012, "2010s", "fantasy",
       "S.S. Rajamouli", "Nani", "male", 8.1, action=True, romance=True, sci_fi=True, revenge=True),
    te("te_dammu_2012", "Dammu", 2012, "2010s", "action",
       "Srinu Vaitla", "Jr. NTR", "male", 6.6, action=True, comedy=True),
    te("te_nippu_2012", "Nippu", 2012, "2010s", "action",
       "Srikanth Addala", "Ravi Teja", "male", 6.8, action=True),
    te("te_ongole_gitta_2013", "Ongole Gitta", 2013, "2010s", "action",
       "Y. Sai Babu", "Ram", "male", 6.7, action=True, romance=True),
    te("te_ramayya_vasthavayya_2013", "Ramayya Vasthavayya", 2013, "2010s", "action",
       "Harish Shankar", "Jr. NTR", "male", 7.1, action=True, romance=True),
    te("te_iddarammayilatho_2013", "Iddarammayilatho", 2013, "2010s", "romance",
       "Puri Jagannadh", "Allu Arjun", "male", 6.9, romance=True, action=True),
    te("te_govindudu_andarivadele_2014", "Govindudu Andarivadele", 2014, "2010s", "drama",
       "Krishna Vamsi", "Ram Charan", "male", 6.6, family=True, action=True),
    te("te_rabhasa_2015", "Rabhasa", 2015, "2010s", "action",
       "Santosh Srinivas", "Jr. NTR", "male", 6.5, action=True, romance=True, comedy=True),
    te("te_sarrainodu_2016", "Sarrainodu", 2016, "2010s", "action",
       "Boyapati Srinu", "Allu Arjun", "male", 7.2, action=True, romance=True, villain=True),
    te("te_dhruva_2016", "Dhruva", 2016, "2010s", "thriller",
       "Surender Reddy", "Ram Charan", "male", 6.9, thriller=True, action=True),
    te("te_gentleman_2016", "Gentleman", 2016, "2010s", "romance",
       "Mohan Krishna Indraganti", "Nani", "male", 7.2, romance=True, thriller=True),
    te("te_rarandoi_veduka_chudham_2016", "Rarandoi Veduka Chudham", 2016, "2010s", "romance",
       "Kalyan Krishna", "Naga Chaitanya", "male", 6.8, romance=True, comedy=True),
    te("te_ninnu_kori_2017", "Ninnu Kori", 2017, "2010s", "romance",
       "Shiva Nirvana", "Nani", "male", 7.5, romance=True, family=True),
    te("te_mca_2017", "MCA Middle Class Abbayi", 2017, "2010s", "comedy",
       "Venu Sriram", "Nani", "male", 7.4, comedy=True, action=True, romance=True),
    te("te_spyder_2017", "Spyder", 2017, "2010s", "thriller",
       "A.R. Murugadoss", "Mahesh Babu", "male", 6.5, thriller=True, action=True),
    te("te_guru_2017", "Guru", 2017, "2010s", "drama",
       "Sudha Kongara", "Venkatesh", "male", 7.0, social=True),
    te("te_nenu_local_2017", "Nenu Local", 2017, "2010s", "comedy",
       "Trinadha Rao Nakkina", "Nani", "male", 7.2, comedy=True, romance=True),
    te("te_oxygen_2017", "Oxygen", 2017, "2010s", "thriller",
       "Mani Sharma", "Gopichand", "male", 6.5, thriller=True, action=True),
    te("te_amar_akbar_anthony_2018", "Amar Akbar Anthony", 2018, "2010s", "comedy",
       "Srinu Vaitla", "Ravi Teja", "male", 6.7, comedy=True, action=True),
    te("te_tholi_prema_2018", "Tholi Prema", 2018, "2010s", "romance",
       "Venky Atluri", "Varun Tej", "male", 7.7, romance=True),
    te("te_krishnarjuna_yuddham_2018", "Krishnarjuna Yuddham", 2018, "2010s", "action",
       "Merlapaka Gandhi", "Nani", "male", 6.9, action=True, comedy=True, romance=True),
    te("te_bichagadu_2016", "Bichagadu", 2016, "2010s", "thriller",
       "Deekay", "Vijay Antony", "male", 7.3, thriller=True, action=True),
    te("te_majili_2019", "Majili", 2019, "2010s", "romance",
       "Shiva Nirvana", "Naga Chaitanya", "male", 7.5, romance=True),
    te("te_gang_leader_2019", "Gang Leader", 2019, "2010s", "thriller",
       "Vikram Kumar", "Nani", "male", 7.1, thriller=True, comedy=True),

    # ── 2020s ─────────────────────────────────────────────────────────────
    te("te_jathi_ratnalu_2021", "Jathi Ratnalu", 2021, "2020s", "comedy",
       "Anudeep KV", "Naveen Polishetty", "male", 8.1, comedy=True),
    te("te_kondapolam_2021", "Kondapolam", 2021, "2020s", "drama",
       "Krish Jagarlamudi", "Vaisshnav Tej", "male", 7.5, social=True, romance=True),
    te("te_naandhi_2021", "Naandhi", 2021, "2020s", "drama",
       "Vijay Kumar Konda", "Allari Naresh", "male", 8.1, social=True, thriller=True, songs=False),
    te("te_sreekaram_2021", "Sreekaram", 2021, "2020s", "drama",
       "Kishore Tirumala", "Sharwanand", "male", 7.8, social=True),
    te("te_narappa_2021", "Narappa", 2021, "2020s", "drama",
       "Srikanth Addala", "Venkatesh", "male", 7.3, social=True, true_story=True, action=True, remake=True),
    te("te_maestro_2021", "Maestro", 2021, "2020s", "thriller",
       "Merlapaka Gandhi", "Nithiin", "male", 6.5, thriller=True, remake=True),
    te("te_karthikeya_2_2022", "Karthikeya 2", 2022, "2020s", "action",
       "Chandoo Mondeti", "Nikhil Siddharth", "male", 7.6, action=True, historical=True),
    te("te_liger_2022", "Liger", 2022, "2020s", "sports",
       "Puri Jagannadh", "Vijay Deverakonda", "male", 3.1, sports=True, action=True),
    te("te_the_ghost_2022", "The Ghost", 2022, "2020s", "action",
       "Praveen Sattaru", "Nagarjuna Akkineni", "male", 4.8, action=True, thriller=True),
    te("te_kushi_2023", "Kushi", 2023, "2020s", "romance",
       "Shiva Nirvana", "Vijay Deverakonda", "male", 5.7, romance=True, comedy=True),
    te("te_custody_2023", "Custody", 2023, "2020s", "action",
       "Venkat Prabhu", "Naga Chaitanya", "male", 4.5, action=True, thriller=True),
    te("te_tiger_nageswara_rao_2023", "Tiger Nageswara Rao", 2023, "2020s", "action",
       "Vamsee", "Ravi Teja", "male", 6.8, action=True, historical=True, true_story=True),
    te("te_agent_2023", "Agent", 2023, "2020s", "action",
       "Surender Reddy", "Akhil Akkineni", "male", 4.2, action=True, thriller=True, abroad=True),
    te("te_saindhav_2024", "Saindhav", 2024, "2020s", "action",
       "Sailesh Kolanu", "Venkatesh", "male", 6.5, action=True, thriller=True),
    te("te_eagle_2024", "Eagle", 2024, "2020s", "action",
       "Karthik Gattamneni", "Ravi Teja", "male", 5.8, action=True, thriller=True),
    te("te_kalki_2898_ad_2024", "Kalki 2898 AD", 2024, "2020s", "sci_fi",
       "Nag Ashwin", "Prabhas", "male", 6.2, sci_fi=True, action=True, historical=True, pan_india=True),
    te("te_saripodhaa_sanivaaram_2024", "Saripodhaa Sanivaaram", 2024, "2020s", "action",
       "Vivek Athreya", "Nani", "male", 7.8, action=True, thriller=True, anti_hero=True),
    te("te_double_ismart_2024", "Double iSmart", 2024, "2020s", "action",
       "Puri Jagannadh", "Ram Pothineni", "male", 5.2, action=True, comedy=True),

    # ── Tamil fix: +1 film to restore count to 500 ────────────────────────
    ta("ta_raatchasan_2018", "Ratchasan", 2018, "2010s", "thriller",
       "Ram Kumar", "Vishnu Vishal", "male", 8.4, thriller=True, villain=True, songs=False),
]

existing = {f"{m['title'].lower()}_{m['year']}" for m in movies}
to_add = [m for m in new if f"{m['title'].lower()}_{m['year']}" not in existing]

movies.extend(to_add)

# Global dedup by title_year
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
