#!/usr/bin/env python3
"""Add final Telugu films (batch 5) to reach 500."""
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
    # ── Classic ──────────────────────────────────────────────────────────
    te("te_manadesam_1949", "Manadesam", 1949, "classic", "drama",
       "B.N. Reddi", "N.T. Rama Rao", "male", 7.0, social=True),
    te("te_palletoori_pilla_1950", "Palletoori Pilla", 1950, "classic", "drama",
       "B.N. Reddi", "N.T. Rama Rao", "male", 7.1, social=True, family=True),
    te("te_shavukaru_1950", "Shavukaru", 1950, "classic", "comedy",
       "B.N. Reddi", "N.T. Rama Rao", "male", 7.3, comedy=True, romance=True),
    te("te_bangaru_panjaram_1955", "Bangaru Panjaram", 1955, "classic", "drama",
       "B.N. Reddi", "Akkineni Nageswara Rao", "male", 7.0, family=True),
    te("te_guptacharudu_1967", "Guptacharudu", 1967, "classic", "action",
       "B. Vittalacharya", "N.T. Rama Rao", "male", 6.9, action=True),

    # ── 90s ──────────────────────────────────────────────────────────────
    te("te_bangaru_bullodu_1993", "Bangaru Bullodu", 1993, "90s", "comedy",
       "K. Raghavendra Rao", "Chiranjeevi", "male", 6.8, comedy=True, romance=True),
    te("te_rajendrudu_gajendrudu_1993", "Rajendrudu Gajendrudu", 1993, "90s", "comedy",
       "E.V.V. Satyanarayana", "Rajendra Prasad", "male", 7.4, comedy=True),
    te("te_akkada_ammayi_ikkada_abbayi_1996", "Akkada Ammayi Ikkada Abbayi", 1996, "90s", "comedy",
       "E.V.V. Satyanarayana", "Pawan Kalyan", "male", 7.1, comedy=True, romance=True),
    te("te_aayana_1997", "Aayana", 1997, "90s", "drama",
       "A. Karunakaran", "Akkineni Nageswara Rao", "male", 7.2, family=True, social=True),
    te("te_mondi_mogudu_penki_pellam_1997", "Mondi Mogudu Penki Pellam", 1997, "90s", "comedy",
       "A. Karunakaran", "Rajendra Prasad", "male", 7.5, comedy=True),
    te("te_muddhamandaram_1993", "Muddhamandaram", 1993, "90s", "romance",
       "K. Raghavendra Rao", "Nagarjuna Akkineni", "male", 7.0, romance=True, action=True),
    te("te_oka_chinna_maata_1984", "Oka Chinna Maata", 1984, "classic", "romance",
       "K. Viswanath", "Venkatesh", "male", 7.3, romance=True),
    te("te_inti_guttu_1987", "Inti Guttu", 1987, "classic", "drama",
       "Dasari Narayana Rao", "Balakrishna", "male", 7.0, family=True, social=True),

    # ── 2000s ─────────────────────────────────────────────────────────────
    te("te_santhosham_2002", "Santhosham", 2002, "2000s", "comedy",
       "N. Shankar", "Nagarjuna Akkineni", "male", 7.2, comedy=True, family=True),
    te("te_samba_2004", "Samba", 2004, "2000s", "action",
       "S.S. Rajamouli", "Jr. NTR", "male", 7.0, action=True, romance=True),
    te("te_venky_2004", "Venky", 2004, "2000s", "action",
       "Surender Reddy", "Ravi Teja", "male", 7.4, action=True, comedy=True),
    te("te_malliswari_2004", "Malliswari", 2004, "2000s", "romance",
       "S.S. Rajamouli", "Venkatesh", "male", 7.5, romance=True, comedy=True, historical=True),
    te("te_nuvvu_naaku_nachav_2001", "Nuvvu Naaku Nachav", 2001, "2000s", "comedy",
       "E.V.V. Satyanarayana", "Venkatesh", "male", 7.3, comedy=True, romance=True),
    te("te_nenunnanu_2004", "Nenunnanu", 2004, "2000s", "romance",
       "A. Karunakaran", "Nagarjuna Akkineni", "male", 6.8, romance=True),
    te("te_shankar_dada_mbbs_2004", "Shankar Dada MBBS", 2004, "2000s", "comedy",
       "Dasari Narayana Rao", "Chiranjeevi", "male", 6.6, comedy=True, remake=True),
    te("te_gowri_2004", "Gowri", 2004, "2000s", "romance",
       "K. Raghavendra Rao", "Tarun", "male", 6.7, romance=True),
    te("te_lakshmi_narasimha_2004", "Lakshmi Narasimha", 2004, "2000s", "action",
       "S.V. Krishna Reddy", "Balakrishna", "male", 6.7, action=True, villain=True),
    te("te_oka_oorilo_2005", "Oka Oorilo", 2005, "2000s", "comedy",
       "Priyadarshan", "Ravi Teja", "male", 7.1, comedy=True, romance=True),
    te("te_saradaga_kasepu_2009", "Saradaga Kasepu", 2009, "2000s", "comedy",
       "Brahmanandam", "Allari Naresh", "male", 7.0, comedy=True),

    # ── 2010s ─────────────────────────────────────────────────────────────
    te("te_oh_my_friend_2011", "Oh My Friend", 2011, "2010s", "comedy",
       "Vasu Varma", "Siddharth", "male", 7.2, comedy=True, romance=True),
    te("te_manam_2014", "Manam", 2014, "2010s", "drama",
       "Vikram Kumar", "Nagarjuna Akkineni", "male", 8.2, romance=True, family=True),
    te("te_swamy_ra_ra_2013", "Swamy Ra Ra", 2013, "2010s", "comedy",
       "Sudheer Varma", "Nikhil Siddharth", "male", 7.6, comedy=True, thriller=True),
    te("te_gunde_jaari_gallanthayyinde_2013", "Gunde Jaari Gallanthayyinde", 2013, "2010s", "romance",
       "Virinchi Varma", "Nithiin", "male", 7.5, romance=True, comedy=True),
    te("te_pesarattu_2012", "Pesarattu", 2012, "2010s", "action",
       "V.V. Vinayak", "Manchu Vishnu", "male", 6.8, action=True, comedy=True),
    te("te_julayi_2012b", "Julayi", 2012, "2010s", "action",
       "Trivikram Srinivas", "Allu Arjun", "male", 7.5, action=True, comedy=True, romance=True),
    te("te_malli_malli_idi_rani_roju_2015", "Malli Malli Idi Rani Roju", 2015, "2010s", "romance",
       "Kranthi Madhav", "Sharwanand", "male", 7.9, romance=True),
    te("te_kerintha_2015b", "Kerintha", 2015, "2010s", "romance",
       "G. Nageswara Reddy", "Sumanth Ashwin", "male", 7.0, romance=True, comedy=True),
    te("te_saahasam_2016", "Saahasam", 2016, "2010s", "thriller",
       "Sriwass", "Prashanth", "male", 7.0, thriller=True, romance=True),
    te("te_speedunnodu_2016", "Speedunnodu", 2016, "2010s", "comedy",
       "N. Shankar", "Manchu Vishnu", "male", 6.5, comedy=True, action=True),
    te("te_premam_telugu_2016", "Premam", 2016, "2010s", "romance",
       "Chandoo Mondeti", "Naga Chaitanya", "male", 7.6, romance=True, remake=True),
    te("te_jyo_achyutananda_2016", "Jyo Achyutananda", 2016, "2010s", "thriller",
       "G.V. Raghunath", "Naga Shaurya", "male", 7.4, thriller=True, comedy=True),
    te("te_winner_2017b", "Winner", 2017, "2010s", "action",
       "G. Nageswara Reddy", "Rakul Preet Singh", "female", 6.3, action=True, sports=True),
    te("te_keshava_2017", "Keshava", 2017, "2010s", "thriller",
       "Sudheer Varma", "Nikhil Siddharth", "male", 7.5, thriller=True, romance=True),
    te("te_lovers_2018", "Lovers", 2018, "2010s", "romance",
       "Vijay Kumar Konda", "Sumanth Ashwin", "male", 7.0, romance=True),
    te("te_savaari_2019", "Savaari", 2019, "2010s", "comedy",
       "G.V. Raghunath", "Naga Shaurya", "male", 7.5, comedy=True, romance=True),
    te("te_oh_baby_2019", "Oh! Baby", 2019, "2010s", "comedy",
       "B.V. Nandini Reddi", "Samantha", "female", 7.6, comedy=True, remake=True, family=True),
    te("te_valmiki_2019", "Valmiki", 2019, "2010s", "action",
       "Harish Shankar", "Varun Tej", "male", 7.1, action=True, romance=True),
    te("te_ala_vaikunthapurramuloo_2020_2010", "Ala Vaikunthapurramuloo", 2020, "2020s", "action",
       "Trivikram Srinivas", "Allu Arjun", "male", 7.3, action=True, comedy=True, family=True),
    te("te_rx_100_2018b", "RX 100", 2018, "2010s", "romance",
       "Ajay Bhupathi", "Karthikeya Gummakonda", "male", 7.7, romance=True, thriller=True, anti_hero=True),
    te("te_taxiwaala_2018b", "Taxiwaala", 2018, "2010s", "thriller",
       "Rahul Sankrityan", "Vijay Deverakonda", "male", 7.0, thriller=True, horror=True),
    te("te_kousalya_supraja_2018", "Kousalya Supraja Rama", 2018, "2010s", "comedy",
       "Srinivas Avasarala", "Srinivas Avasarala", "male", 7.8, comedy=True, family=True),
    te("te_evaru_2019", "Evaru", 2019, "2010s", "thriller",
       "Venkat Ramji", "Adivi Sesh", "male", 7.9, thriller=True, remake=True, villain=True),
    te("te_hello_2017", "Hello!", 2017, "2010s", "romance",
       "Vikram Kumar", "Akhil Akkineni", "male", 6.4, romance=True),
    te("te_mr_majnu_2019b", "Mr. Majnu", 2019, "2010s", "romance",
       "Venky Atluri", "Akhil Akkineni", "male", 6.8, romance=True, comedy=True),
    te("te_lie_2017", "LIE", 2017, "2010s", "thriller",
       "Hanu Raghavapudi", "Nithiin", "male", 6.6, thriller=True, action=True),

    # ── 2020s ─────────────────────────────────────────────────────────────
    te("te_uma_maheshwara_ugra_2020", "Uma Maheshwara Ugra Roopasya", 2020, "2020s", "thriller",
       "Venkatesh Maha", "Satyadev Kancharana", "male", 7.8, thriller=True, songs=False),
    te("te_zombie_reddy_2021", "Zombie Reddy", 2021, "2020s", "horror",
       "Prashanth Varma", "Teja Sajja", "male", 7.1, horror=True, comedy=True),
    te("te_check_2021", "Check", 2021, "2020s", "thriller",
       "Chandra Sekhar Yeleti", "Nithiin", "male", 7.0, thriller=True),
    te("te_maha_samudram_2021", "Maha Samudram", 2021, "2020s", "action",
       "Ajay Bhupathi", "Sharwanand", "male", 6.6, action=True, romance=True),
    te("te_paagal_2021", "Paagal", 2021, "2020s", "romance",
       "Naresh Kuppili", "Vishwak Sen", "male", 6.4, romance=True, comedy=True),
    te("te_konda_polam_2021b", "Konda Polam", 2021, "2020s", "drama",
       "Krish Jagarlamudi", "Vaisshnav Tej", "male", 7.5, social=True, romance=True),
    te("te_vimanam_2022", "Vimanam", 2022, "2020s", "comedy",
       "Srinivas Avasarala", "Sree Vishnu", "male", 6.8, comedy=True, family=True),
    te("te_ori_devuda_2022b", "Ori Devuda", 2022, "2020s", "comedy",
       "Ashwath Marimuthu", "Vishwak Sen", "male", 6.3, comedy=True, romance=True),
    te("te_das_ka_dhamki_2023", "Das Ka Dhamki", 2023, "2020s", "comedy",
       "Vishwak Sen", "Vishwak Sen", "male", 6.8, comedy=True, action=True),
    te("te_ravanasura_2023", "Ravanasura", 2023, "2020s", "thriller",
       "Sudheer Varma", "Ravi Teja", "male", 6.9, thriller=True, action=True, anti_hero=True),
    te("te_naa_saami_ranga_2023", "Naa Saami Ranga", 2023, "2020s", "comedy",
       "Vijay Binni", "Nagarjuna Akkineni", "male", 6.5, comedy=True, action=True),
    te("te_hi_nanna_2023b", "Hi Nanna", 2023, "2020s", "romance",
       "Shouryuv", "Nani", "male", 7.6, romance=True, family=True),
    te("te_extra_ordinary_man_2023", "Extra Ordinary Man", 2023, "2020s", "comedy",
       "Vakkantham Vamsi", "Nithiin", "male", 6.7, comedy=True, romance=True),
    te("te_chaave_ranga_2023", "Chaave Ranga Chaave", 2023, "2020s", "comedy",
       "Srikant Addala", "Allari Naresh", "male", 7.0, comedy=True),
    te("te_gangs_of_godavari_2024", "Gangs of Godavari", 2024, "2020s", "action",
       "Krishna Chaitanya", "Vishwak Sen", "male", 6.9, action=True, thriller=True, anti_hero=True),
    te("te_tillu_square_2024b", "Tillu Square", 2024, "2020s", "comedy",
       "Mallik Ram", "Siddu Jonnalagadda", "male", 7.2, comedy=True, action=True),
    te("te_premalu_2024b", "Premalu", 2024, "2020s", "romance",
       "Girish A.D.", "Naslen", "male", 8.3, romance=True, comedy=True),
    te("te_saripodhaa_sanivaaram_2024b", "Saripodhaa Sanivaaram", 2024, "2020s", "action",
       "Vivek Athreya", "Nani", "male", 7.8, action=True, thriller=True, anti_hero=True),
    te("te_devara_2024b", "Devara: Part 1", 2024, "2020s", "action",
       "Koratala Siva", "Jr. NTR", "male", 6.5, action=True, thriller=True, villain=True),
    te("te_gam_gam_2023", "Gam Gam Ganesha", 2023, "2020s", "comedy",
       "Srinivas Avasarala", "Srinivas Avasarala", "male", 7.2, comedy=True, family=True),
    te("te_lucky_baskhar_2024b", "Lucky Baskhar", 2024, "2020s", "thriller",
       "Venky Atluri", "Dulquer Salmaan", "male", 8.1, thriller=True),
    te("te_oke_oka_jeevitham_2022b", "Oke Oka Jeevitham", 2022, "2020s", "drama",
       "Shree Karthick", "Sharwanand", "male", 6.8, romance=True, sci_fi=True),
    te("te_pakka_commercial_2022b", "Pakka Commercial", 2022, "2020s", "action",
       "Maruthi Dasari", "Gopichand", "male", 6.1, action=True, comedy=True),
    te("te_missing_2023", "Missing", 2023, "2020s", "thriller",
       "Mahesh Surapaneni", "Anand Deverakonda", "male", 7.4, thriller=True),
    te("te_pushpa_2_2024b", "Pushpa 2: The Rule", 2024, "2020s", "action",
       "Sukumar", "Allu Arjun", "male", 7.6, action=True, anti_hero=True, pan_india=True),
    te("te_salaar_2023b", "Salaar: Part 1", 2023, "2020s", "action",
       "Prashanth Neel", "Prabhas", "male", 6.9, action=True, villain=True, pan_india=True),
    te("te_rrr_2022b", "RRR", 2022, "2020s", "action",
       "S.S. Rajamouli", "Jr. NTR", "male", 7.9, action=True, historical=True, pan_india=True),
    te("te_major_2022b", "Major", 2022, "2020s", "action",
       "Sashi Kiran Tikka", "Adivi Sesh", "male", 8.3, action=True, true_story=True, bio=True, pan_india=True),

    # ── Fill extras ────────────────────────────────────────────────────────
    te("te_aagadu_2014b", "Aagadu", 2014, "2010s", "action",
       "Srinu Vaitla", "Mahesh Babu", "male", 6.8, action=True, comedy=True),
    te("te_nannaku_prematho_2016b", "Nannaku Prematho", 2016, "2010s", "action",
       "Sukumar", "Jr. NTR", "male", 7.6, action=True, romance=True),
    te("te_agnyaathavaasi_2018b", "Agnyaathavaasi", 2018, "2010s", "action",
       "Trivikram Srinivas", "Pawan Kalyan", "male", 5.3, action=True, romance=True),
    te("te_bheeshma_2020b", "Bheeshma", 2020, "2020s", "comedy",
       "Venky Atluri", "Nithiin", "male", 6.6, comedy=True, romance=True),
    te("te_f2_fun_frustration_2019b", "F2: Fun and Frustration", 2019, "2010s", "comedy",
       "Anil Ravipudi", "Venkatesh", "male", 7.4, comedy=True),
    te("te_gaddalakonda_ganesh_2019b", "Gaddalakonda Ganesh", 2019, "2010s", "action",
       "Harish Shankar", "Varun Tej", "male", 7.1, action=True, romance=True),
    te("te_ishq_2012b", "Ishq", 2012, "2010s", "romance",
       "Vikram Kumar", "Nitin", "male", 7.4, romance=True, comedy=True, thriller=True),
    te("te_seetharama_kalyanam_1988", "Seetharama Kalyanam", 1988, "classic", "romance",
       "Jandhyala", "Balakrishna", "male", 7.5, romance=True, family=True),
    te("te_brahma_naidu_2017", "Brahma Naidu", 2017, "2010s", "comedy",
       "Srikanth Addala", "Nagarjuna Akkineni", "male", 6.5, comedy=True, action=True),
    te("te_geetha_2018", "Geetha", 2018, "2010s", "action",
       "K.V. Guhan", "Ganesh", "male", 6.5, action=True, romance=True),
    te("te_antariksham_9000_kmph_2018", "Antariksham 9000 KMPH", 2018, "2010s", "sci_fi",
       "Sankalp Reddy", "Varun Tej", "male", 7.3, sci_fi=True, thriller=True, action=True),
    te("te_color_photo_2020b", "Colour Photo", 2020, "2020s", "romance",
       "Mohan Krishna Indraganti", "Suhas", "male", 8.4, romance=True, social=True),
    te("te_uppena_2021b", "Uppena", 2021, "2020s", "romance",
       "Buchi Babu Sana", "Panja Vaisshnav Tej", "male", 7.6, romance=True, forbidden=True),
    te("te_love_story_2021c", "Love Story", 2021, "2020s", "romance",
       "Sekhar Kammula", "Naga Chaitanya", "male", 7.5, romance=True, social=True),
    te("te_rang_de_2021b", "Rang De", 2021, "2020s", "romance",
       "Venky Atluri", "Nithiin", "male", 7.3, romance=True, comedy=True),
    te("te_drushyam_2_2021b", "Drushyam 2", 2021, "2020s", "thriller",
       "Jeethu Joseph", "Venkatesh", "male", 8.1, thriller=True, family=True),
    te("te_bangarraju_2022b", "Bangarraju", 2022, "2020s", "comedy",
       "Kalyan Krishna", "Nagarjuna Akkineni", "male", 7.0, comedy=True, family=True),
    te("te_ante_sundaraniki_2022b", "Ante Sundaraniki", 2022, "2020s", "romance",
       "Vivek Athreya", "Nani", "male", 7.5, romance=True, comedy=True),
    te("te_shyam_singha_roy_2021b", "Shyam Singha Roy", 2021, "2020s", "romance",
       "Rahul Sankrityan", "Nani", "male", 7.7, romance=True, historical=True),
    te("te_pushpa_rise_2021b", "Pushpa: The Rise", 2021, "2020s", "action",
       "Sukumar", "Allu Arjun", "male", 7.6, action=True, anti_hero=True, pan_india=True),
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
