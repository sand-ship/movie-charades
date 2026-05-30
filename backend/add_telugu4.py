#!/usr/bin/env python3
"""Add more Telugu films (batch 4)."""
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
    te("te_appu_chesi_pappu_koodu_1959", "Appu Chesi Pappu Koodu", 1959, "classic", "comedy",
       "B. Vittalacharya", "N.T. Rama Rao", "male", 7.1, comedy=True),
    te("te_zindagi_1965", "Zindagi", 1965, "classic", "drama",
       "B. Vittalacharya", "N.T. Rama Rao", "male", 7.0, romance=True),
    te("te_prem_nagar_1971", "Prem Nagar", 1971, "classic", "romance",
       "K.S. Prakash Rao", "Akkineni Nageswara Rao", "male", 7.4, romance=True),
    te("te_sardar_papa_rayudu_1980", "Sardar Papa Rayudu", 1980, "classic", "action",
       "K.S.R. Das", "N.T. Rama Rao", "male", 7.2, action=True, family=True),
    te("te_aadavallaku_mogudu_1983", "Aadavallaku Mogudu", 1983, "classic", "comedy",
       "E.V.V. Satyanarayana", "Chiranjeevi", "male", 7.0, comedy=True, romance=True),
    te("te_jebu_donga_1987", "Jebu Donga", 1987, "classic", "action",
       "A. Kodandarami Reddy", "Chiranjeevi", "male", 7.1, action=True, comedy=True),
    te("te_chanakya_1989", "Chanakya", 1989, "classic", "action",
       "A. Kodandarami Reddy", "Chiranjeevi", "male", 7.5, action=True, villain=True, revenge=True),

    # ── 90s ──────────────────────────────────────────────────────────────
    te("te_donga_alludu_1993", "Donga Alludu", 1993, "90s", "action",
       "A. Kodandarami Reddy", "Chiranjeevi", "male", 6.7, action=True, comedy=True),
    te("te_muddula_priyudu_1994", "Muddula Priyudu", 1994, "90s", "romance",
       "K. Raghavendra Rao", "Venkatesh", "male", 7.1, romance=True, comedy=True),
    te("te_criminal_1995", "Criminal", 1995, "90s", "action",
       "B. Gopal", "Nagarjuna Akkineni", "male", 7.0, action=True, thriller=True, villain=True),
    te("te_subha_sankalpam_1995", "Subha Sankalpam", 1995, "90s", "romance",
       "K. Raghavendra Rao", "Venkatesh", "male", 7.2, romance=True, comedy=True),
    te("te_seetha_rama_kalyanam_1997", "Seetha Rama Kalyanam", 1997, "90s", "drama",
       "B. Gopal", "Venkatesh", "male", 7.3, romance=True, family=True),
    te("te_premalo_chikkadu_1996", "Premalo Chikkadu", 1996, "90s", "romance",
       "Jandhyala", "Venkatesh", "male", 7.0, romance=True, comedy=True),

    # ── 2000s ─────────────────────────────────────────────────────────────
    te("te_kaasi_2001", "Kaasi", 2001, "2000s", "action",
       "Gunasekhar", "Pawan Kalyan", "male", 7.4, action=True, revenge=True, villain=True),
    te("te_indra_2002", "Indra", 2002, "2000s", "action",
       "S.S. Rajamouli", "Chiranjeevi", "male", 7.5, action=True, villain=True, revenge=True),
    te("te_nuvvakosam_2002", "Nuvvakosam", 2002, "2000s", "romance",
       "S.V. Krishna Reddy", "Tarun", "male", 7.0, romance=True, songs=True),
    te("te_allari_2002", "Allari", 2002, "2000s", "comedy",
       "Vasu Varma", "Nithin", "male", 7.1, comedy=True, romance=True),
    te("te_nijam_2003", "Nijam", 2003, "2000s", "thriller",
       "Shyam Prasad Reddy", "Mahesh Babu", "male", 7.1, thriller=True, action=True, villain=True),
    te("te_desamuduru_2007", "Desamuduru", 2007, "2000s", "action",
       "Puri Jagannadh", "Allu Arjun", "male", 7.3, action=True, romance=True),
    te("te_athidi_2007", "Athidi", 2007, "2000s", "action",
       "Surender Reddy", "Mahesh Babu", "male", 7.1, action=True, comedy=True, romance=True),
    te("te_mass_2004", "Mass", 2004, "2000s", "action",
       "Raghava Lawrence", "Nagarjuna Akkineni", "male", 7.0, action=True, villain=True),
    te("te_seema_simham_2002", "Seema Simham", 2002, "2000s", "action",
       "S.V. Krishna Reddy", "Balakrishna", "male", 6.8, action=True, villain=True),
    te("te_nuvve_nuvve_2003", "Nuvve Nuvve", 2003, "2000s", "romance",
       "Trivikram Srinivas", "Tarun", "male", 7.3, romance=True, comedy=True),
    te("te_nuvvostanante_nenoddantana_2005", "Nuvvostanante Nenoddantana", 2005, "2000s", "romance",
       "Prabhu Deva", "Siddharth", "male", 7.7, romance=True, comedy=True),

    # ── 2010s ─────────────────────────────────────────────────────────────
    te("te_orange_2010", "Orange", 2010, "2010s", "romance",
       "Bhaskar", "Ram Charan", "male", 7.1, romance=True),
    te("te_simha_2010", "Simha", 2010, "2010s", "action",
       "S.S. Rajamouli", "Balakrishna", "male", 7.3, action=True, villain=True, historical=True),
    te("te_leader_2010", "Leader", 2010, "2010s", "drama",
       "Sekhar Kammula", "Rana Daggubati", "male", 7.7, social=True, romance=True),
    te("te_pilla_zamindar_2011", "Pilla Zamindar", 2011, "2010s", "comedy",
       "Bhaskar", "Nani", "male", 7.5, comedy=True, romance=True),
    te("te_adhinayakudu_2011", "Adhinayakudu", 2011, "2010s", "action",
       "Vasu Varma", "Balakrishna", "male", 6.5, action=True, villain=True),
    te("te_rebel_2012", "Rebel", 2012, "2010s", "action",
       "Raghava Lawrence", "Prabhas", "male", 5.5, action=True, romance=True),
    te("te_krishnam_vande_jagadgurum_2012", "Krishnam Vande Jagadgurum", 2012, "2010s", "action",
       "Krish Jagarlamudi", "Rana Daggubati", "male", 7.3, action=True, villain=True, revenge=True),
    te("te_shadow_2013", "Shadow", 2013, "2010s", "action",
       "Meher Ramesh", "Venkatesh", "male", 6.5, action=True, romance=True),
    te("te_masala_2013", "Masala", 2013, "2010s", "action",
       "V.V. Vinayak", "Venkatesh", "male", 6.3, action=True, comedy=True),
    te("te_drushyam_2014", "Drushyam", 2014, "2010s", "thriller",
       "Sripriya", "Venkatesh", "male", 8.1, thriller=True, family=True, remake=True),
    te("te_autonagar_surya_2014", "Autonagar Surya", 2014, "2010s", "action",
       "Deva Katta", "Naga Chaitanya", "male", 7.0, action=True, social=True),
    te("te_loukyam_2014", "Loukyam", 2014, "2010s", "comedy",
       "Vasu Varma", "Gopichand", "male", 6.9, comedy=True, action=True, romance=True),
    te("te_jil_2015", "Jil", 2015, "2010s", "action",
       "Radhakrishna Jagarlamudi", "Gopichand", "male", 6.8, action=True, romance=True, villain=True),
    te("te_bruce_lee_the_fighter_2015", "Bruce Lee: The Fighter", 2015, "2010s", "action",
       "Srinu Vaitla", "Ram Charan", "male", 6.4, action=True, comedy=True, romance=True),
    te("te_bengal_tiger_2015", "Bengal Tiger", 2015, "2010s", "action",
       "Sampath Nandi", "Ravi Teja", "male", 6.6, action=True, comedy=True, romance=True),
    te("te_pataas_2015", "Pataas", 2015, "2010s", "action",
       "Anil Ravipudi", "Kalyan Ram", "male", 7.4, action=True, social=True, villain=True),
    te("te_dictator_2016", "Dictator", 2016, "2010s", "action",
       "Sriwass", "Balakrishna", "male", 6.8, action=True, romance=True),
    te("te_raja_the_great_2017", "Raja The Great", 2017, "2010s", "action",
       "Anil Ravipudi", "Ravi Teja", "male", 7.1, action=True, comedy=True, romance=True),
    te("te_gautamiputra_satakarni_2017", "Gautamiputra Satakarni", 2017, "2010s", "historical",
       "Krish Jagarlamudi", "Balakrishna", "male", 7.2, historical=True, action=True, bio=True, true_story=True),
    te("te_nakshatram_2017", "Nakshatram", 2017, "2010s", "action",
       "Krishna Vamsi", "Sundeep Kishan", "male", 6.0, action=True, romance=True),
    te("te_nota_2018", "Nota", 2018, "2010s", "drama",
       "Anand Shankar", "Vijay Deverakonda", "male", 6.4, social=True, thriller=True, remake=True),
    te("te_goodachari_2018", "Goodachari", 2018, "2010s", "thriller",
       "Sashi Kiran Tikka", "Adivi Sesh", "male", 7.9, thriller=True, action=True, abroad=True),
    te("te_prati_roju_pandaage_2019", "Prati Roju Pandaage", 2019, "2010s", "romance",
       "Maruthi Dasari", "Sai Dharam Tej", "male", 6.8, romance=True, family=True),
    te("te_manmadhudu_2_2019", "Manmadhudu 2", 2019, "2010s", "comedy",
       "Rahul Ravindran", "Nagarjuna Akkineni", "male", 5.5, comedy=True, romance=True),
    te("te_world_famous_lover_2020", "World Famous Lover", 2020, "2020s", "romance",
       "Kranthi Madhav", "Vijay Deverakonda", "male", 5.5, romance=True),

    # ── 2020s ─────────────────────────────────────────────────────────────
    te("te_palasa_1978_2020", "Palasa 1978", 2020, "2020s", "drama",
       "Karuna Kumar", "Rakshith", "male", 8.0, social=True, historical=True, true_story=True),
    te("te_khiladi_2022", "Khiladi", 2022, "2020s", "action",
       "Ramesh Varma", "Ravi Teja", "male", 5.1, action=True, thriller=True),
    te("te_pakka_commercial_2022", "Pakka Commercial", 2022, "2020s", "action",
       "Maruthi Dasari", "Gopichand", "male", 6.1, action=True, comedy=True),
    te("te_oke_oka_jeevitham_2022", "Oke Oka Jeevitham", 2022, "2020s", "drama",
       "Shree Karthick", "Sharwanand", "male", 6.8, romance=True, sci_fi=True),
    te("te_veera_simha_reddy_2023", "Veera Simha Reddy", 2023, "2020s", "action",
       "Gopichand Malineni", "Balakrishna", "male", 6.4, action=True, villain=True, revenge=True),
    te("te_bhagavanth_kesari_2023", "Bhagavanth Kesari", 2023, "2020s", "action",
       "Anil Ravipudi", "Balakrishna", "male", 6.9, action=True, comedy=True, family=True),
    te("te_mangalavaaram_2023", "Mangalavaaram", 2023, "2020s", "thriller",
       "Ajay Bhupathi", "Nithiin", "male", 6.5, thriller=True, horror=True),
    te("te_bhimaa_2024", "Bhimaa", 2024, "2020s", "action",
       "Sanjay Gunasekhar", "Gopichand", "male", 5.8, action=True, social=True),
    te("te_guntur_kaaram_2024", "Guntur Kaaram", 2024, "2020s", "drama",
       "Trivikram Srinivas", "Mahesh Babu", "male", 6.0, family=True, romance=True),
    te("te_devara_part_1_2024", "Devara: Part 1", 2024, "2020s", "action",
       "Koratala Siva", "Jr. NTR", "male", 6.5, action=True, thriller=True, villain=True),
    te("te_hanu_man_2024", "HanuMan", 2024, "2020s", "action",
       "Prasanth Varma", "Teja Sajja", "male", 7.8, action=True, sci_fi=True, pan_india=True),
    te("te_lucky_baskhar_2024", "Lucky Baskhar", 2024, "2020s", "thriller",
       "Venky Atluri", "Dulquer Salmaan", "male", 8.1, thriller=True),

    # ── More 90s ──────────────────────────────────────────────────────────
    te("te_auto_ramudu_1994", "Auto Ramudu", 1994, "90s", "comedy",
       "B. Gopal", "Rajendra Prasad", "male", 7.0, comedy=True),
    te("te_seetharamaiah_gari_manavaralu_2_1998", "Seetharamaiah Gari Manavaralu", 1998, "90s", "drama",
       "Radha Krishna", "Mohan Babu", "male", 7.0, family=True, social=True),
    te("te_tholi_prema_1998", "Tholi Prema", 1998, "90s", "romance",
       "A. Karunakaran", "Pawan Kalyan", "male", 7.8, romance=True),
    te("te_thammudu_1997", "Thammudu", 1997, "90s", "comedy",
       "A. Kodandarami Reddy", "Pawan Kalyan", "male", 7.3, comedy=True, action=True),

    # ── More 2000s ────────────────────────────────────────────────────────
    te("te_okkade_2003", "Okkade", 2003, "2000s", "action",
       "Puri Jagannadh", "Nagarjuna Akkineni", "male", 6.5, action=True, romance=True),
    te("te_naa_autograph_2004", "Naa Autograph", 2004, "2000s", "drama",
       "Srikanth Addala", "Ravi Teja", "male", 8.1, romance=True, comedy=True, songs=True),
    te("te_super_2005", "Super", 2005, "2000s", "action",
       "Puri Jagannadh", "Nagarjuna Akkineni", "male", 6.9, action=True, romance=True, comedy=True),
    te("te_seema_tapakai_2006", "Seema Tapakai", 2006, "2000s", "comedy",
       "S.V. Krishna Reddy", "Allari Naresh", "male", 6.8, comedy=True),
    te("te_naa_oopiri_2009", "Naa Oopiri", 2009, "2000s", "drama",
       "G. Venu Gopal", "Nagarjuna Akkineni", "male", 6.2, remake=True),

    # ── More 2010s ────────────────────────────────────────────────────────
    te("te_seethamma_vakitlo_2013b", "Seethamma Vakitlo Sirimalle Chettu", 2013, "2010s", "drama",
       "Srikanth Addala", "Mahesh Babu", "male", 7.5, family=True, romance=True),
    te("te_tadakha_2013", "Tadakha", 2013, "2010s", "action",
       "Vasu Varma", "Manchu Manoj", "male", 6.5, action=True, romance=True),
    te("te_julayi_2012", "Julayi", 2012, "2010s", "action",
       "Trivikram Srinivas", "Allu Arjun", "male", 7.5, action=True, comedy=True, romance=True),
    te("te_kick_2_2015", "Kick 2", 2015, "2010s", "action",
       "Surender Reddy", "Ravi Teja", "male", 6.5, action=True, comedy=True),
    te("te_soggade_chinni_nayana_2016b", "Soggade Chinni Nayana", 2016, "2010s", "comedy",
       "Kalyan Krishna", "Nagarjuna Akkineni", "male", 7.4, comedy=True, romance=True, family=True),
    te("te_abhinetri_2016", "Abhinetri", 2016, "2010s", "horror",
       "A. Karunakaran", "Prabhu Deva", "male", 5.2, horror=True, comedy=True, romance=True),
    te("te_satamanam_bhavati_2017b", "Satamanam Bhavati", 2017, "2010s", "romance",
       "Satish Vegesna", "Sharwanand", "male", 7.6, romance=True, family=True),
    te("te_chalo_2018", "Chalo", 2018, "2010s", "romance",
       "Venky Atluri", "Naga Shaurya", "male", 7.4, romance=True, comedy=True),
    te("te_rx_100_2018", "RX 100", 2018, "2010s", "romance",
       "Ajay Bhupathi", "Karthikeya Gummakonda", "male", 7.7, romance=True, thriller=True, anti_hero=True),
    te("te_brochevarevarura_2019", "Brochevarevarura", 2019, "2010s", "comedy",
       "Vivek Athreya", "Sree Vishnu", "male", 7.8, comedy=True, thriller=True),
    te("te_ishq_2012", "Ishq", 2012, "2010s", "romance",
       "Vikram Kumar", "Nitin", "male", 7.4, romance=True, comedy=True, thriller=True),

    # ── More 2020s ────────────────────────────────────────────────────────
    te("te_sam_janam_2021", "Saahasam Swasaga Saagipo", 2021, "2020s", "action",
       "Trivikram Srinivas", "Nithiin", "male", 6.0, action=True, romance=True),
    te("te_wild_dog_2021", "Wild Dog", 2021, "2020s", "action",
       "Ashishor Solomon", "Nagarjuna Akkineni", "male", 6.5, action=True, thriller=True, true_story=True),
    te("te_maa_neella_tank_2021", "Republic", 2021, "2020s", "drama",
       "Deva Katta", "Sai Dharam Tej", "male", 6.8, social=True, action=True),
    te("te_rang_de_2021", "Rang De", 2021, "2020s", "romance",
       "Venky Atluri", "Nithiin", "male", 7.3, romance=True, comedy=True),
    te("te_love_story_2021b", "Love Story", 2021, "2020s", "romance",
       "Sekhar Kammula", "Naga Chaitanya", "male", 7.5, romance=True, social=True),
    te("te_vakeel_saab_2021b", "Vakeel Saab", 2021, "2020s", "drama",
       "Venu Sriram", "Pawan Kalyan", "male", 7.1, social=True, remake=True),
    te("te_a1_express_2021", "A1 Express", 2021, "2020s", "sports",
       "Dennis Jeevan Kanukolanu", "Sundeep Kishan", "male", 7.2, sports=True, romance=True),
    te("te_cinema_bandi_2021", "Cinema Bandi", 2021, "2020s", "comedy",
       "Praveen Kandregula", "Vikas Vasishta", "male", 8.0, comedy=True, family=True),
    te("te_bheeshma_parvam_2022", "Bheeshma Parvam", 2022, "2020s", "action",
       "Praveen Morchhale", "Mammootty", "male", 7.4, action=True, thriller=True, family=True),
    te("te_radhe_shyam_2022", "Radhe Shyam", 2022, "2020s", "romance",
       "Radha Krishna Kumar", "Prabhas", "male", 5.6, romance=True, abroad=True, pan_india=True),
    te("te_acharya_2022b", "Acharya", 2022, "2020s", "action",
       "Koratala Siva", "Chiranjeevi", "male", 4.3, action=True, social=True),
    te("te_sita_ramam_2022b", "Sita Ramam", 2022, "2020s", "romance",
       "Hanu Raghavapudi", "Dulquer Salmaan", "male", 8.4, romance=True, historical=True, songs=True),
    te("te_karthikeya_2022b", "Karthikeya 2", 2022, "2020s", "action",
       "Chandoo Mondeti", "Nikhil Siddharth", "male", 7.6, action=True, historical=True),
    te("te_ori_devuda_2022", "Ori Devuda", 2022, "2020s", "comedy",
       "Ashwath Marimuthu", "Vishwak Sen", "male", 6.3, comedy=True, romance=True),
    te("te_aa_ammayi_gurinchi_2022", "Aa Ammayi Gurinchi Meeku Cheppali", 2022, "2020s", "comedy",
       "Mohana Krishna Indraganti", "Sudheer Babu", "male", 7.2, romance=True, comedy=True),
    te("te_miss_shetty_mr_polishetty_2023", "Miss Shetty Mr Polishetty", 2023, "2020s", "comedy",
       "Mahesh Babu P.", "Naveen Polishetty", "male", 6.9, comedy=True, romance=True),
    te("te_mem_famous_2023", "Mem Famous", 2023, "2020s", "comedy",
       "Sumanth Prabhas", "Suhas", "male", 7.8, comedy=True),
    te("te_writer_padmabhushan_2023", "Writer Padmabhushan", 2023, "2020s", "comedy",
       "Shanmukha Prasanth", "Suhas", "male", 7.3, comedy=True, thriller=True),
    te("te_kishkindha_kaandam_2024", "Kishkindha Kaandam", 2024, "2020s", "thriller",
       "Dinjith Ayyathan", "Vineeth Sreenivasan", "male", 9.0, thriller=True, family=True),
    te("te_saindhav_2024b", "Saindhav", 2024, "2020s", "action",
       "Sailesh Kolanu", "Venkatesh", "male", 6.5, action=True, thriller=True),
    te("te_falaknuma_das_2019", "Falaknuma Das", 2019, "2010s", "action",
       "Trinadha Rao Nakkina", "Vishwak Sen", "male", 7.8, action=True, thriller=True, anti_hero=True),
    te("te_pellichoopulu_2016b", "Pelli Choopulu", 2016, "2010s", "romance",
       "Tharun Bhascker", "Vijay Deverakonda", "male", 8.3, romance=True, comedy=True),
    te("te_c_m_b_2019", "Chi La Sow", 2019, "2010s", "romance",
       "Rahul Ravindran", "Sushanth", "male", 7.7, romance=True, comedy=True),
    te("te_love_action_drama_2019", "Ninnu Kori 2", 2019, "2010s", "romance",
       "Caarthick Raju", "Nani", "male", 7.0, romance=True, comedy=True),
    te("te_hit_2020b", "HIT: The First Case", 2020, "2020s", "thriller",
       "Sailesh Kolanu", "Vishwak Sen", "male", 7.6, thriller=True, songs=False),
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
