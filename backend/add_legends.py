import json

movies = json.load(open('data/movies.json'))
existing_ids = {m['id'] for m in movies}
existing_keys = {f"{m['title'].lower()}_{m.get('year', 0)}" for m in movies}

def film(id, title, year, era, genre, director, actor, imdb, lang="hindi",
         actress=None,
         action=False, comedy=False, romance=False, villain=False, songs=True,
         thriller=False, social=False, family=False, true_story=False,
         historical=False, bio=False, sports=False, sci_fi=False, horror=False,
         remake=False, franchise=False, pan_india=False, anti_hero=False,
         abroad=False, triangle=False, revenge=False, forbidden=False,
         double_role=False, police=False, village=False, mass=False,
         item=False, college=False, parent_child=False, one_sided=False):
    m = {
        "id": id, "title": title, "year": year, "language": lang, "era": era,
        "primary_genre": genre, "director": director,
        "lead_actor": actor, "lead_gender": "male", "imdb_rating": imdb,
        "has_action": action, "has_comedy": comedy, "has_romance": romance,
        "has_villain": villain, "has_songs": songs,
        "has_thriller_elements": thriller, "has_social_message": social,
        "is_family_film": family, "is_based_on_true_story": true_story,
        "is_historical": historical, "is_biographical": bio,
        "is_sports_film": sports, "is_sci_fi": sci_fi, "is_horror": horror,
        "is_remake": remake, "is_franchise": franchise,
        "is_pan_india_blockbuster": pan_india, "is_anti_hero": anti_hero,
        "is_set_abroad": abroad, "has_love_triangle": triangle,
        "has_revenge_plot": revenge, "has_forbidden_love": forbidden,
        "has_double_role": double_role, "has_police_or_law": police,
        "has_village_setting": village, "is_mass_entertainer": mass,
        "has_item_number": item, "is_college_film": college,
        "has_parent_child_drama": parent_child, "has_one_sided_love": one_sided,
    }
    if actress:
        m["lead_actress"] = actress
    return m

def hi(*a, **kw): return film(*a, **kw, lang="hindi")
def ta(*a, **kw): return film(*a, **kw, lang="tamil")

new_films = [

    # ─── AAMIR KHAN ─────────────────────────────────────────────────────────

    hi("aamir_dil_hai_ke", "Dil Hai Ke Manta Nahin", 1991,
       "90s", "romance", "Mahesh Bhatt", "Aamir Khan", 7.0,
       actress="Pooja Bhatt",
       romance=True, comedy=True, songs=True, remake=True),

    hi("aamir_akele_hum", "Akele Hum Akele Tum", 1995,
       "90s", "drama", "Mansoor Khan", "Aamir Khan", 7.2,
       actress="Manisha Koirala",
       romance=True, songs=True, family=True, parent_child=True, remake=True),

    hi("aamir_raja_hindustani", "Raja Hindustani", 1996,
       "90s", "romance", "Dharmesh Darshan", "Aamir Khan", 6.1,
       actress="Karisma Kapoor",
       romance=True, songs=True, family=True, forbidden=True),

    hi("aamir_ghulam", "Ghulam", 1998,
       "90s", "action", "Vikram Bhatt", "Aamir Khan", 7.2,
       actress="Rani Mukerji",
       action=True, romance=True, songs=True, villain=True,
       remake=True, anti_hero=True),

    hi("aamir_mangal_pandey", "Mangal Pandey: The Rising", 2005,
       "2000s", "historical", "Ketan Mehta", "Aamir Khan", 6.5,
       historical=True, bio=True, true_story=True, social=True,
       action=True, songs=True),

    # Taare Zameen Par is already in DB under Darsheel Safary — updating lead

    # ─── SALMAN KHAN ────────────────────────────────────────────────────────

    hi("salman_saajan", "Saajan", 1991,
       "90s", "romance", "Lawrence D'Souza", "Salman Khan", 7.2,
       actress="Madhuri Dixit",
       romance=True, songs=True, triangle=True),

    hi("salman_judwaa", "Judwaa", 1997,
       "90s", "comedy", "David Dhawan", "Salman Khan", 6.2,
       actress="Karisma Kapoor",
       comedy=True, action=True, songs=True, double_role=True, mass=True),

    hi("salman_pyaar_kiya", "Pyaar Kiya To Darna Kya", 1998,
       "90s", "romance", "Sohail Khan", "Salman Khan", 6.6,
       actress="Kajol",
       romance=True, comedy=True, songs=True),

    # ─── AMITABH BACHCHAN ───────────────────────────────────────────────────

    hi("ab_zanjeer", "Zanjeer", 1973,
       "classic", "action", "Prakash Mehra", "Amitabh Bachchan", 7.5,
       actress="Jaya Bachchan",
       action=True, villain=True, songs=True, social=True,
       police=True, revenge=True),

    hi("ab_namak_haraam", "Namak Haraam", 1973,
       "classic", "drama", "Hrishikesh Mukherjee", "Amitabh Bachchan", 7.2,
       social=True, songs=True),

    hi("ab_muqaddar_ka_sikandar", "Muqaddar Ka Sikandar", 1978,
       "classic", "drama", "Prakash Mehra", "Amitabh Bachchan", 7.4,
       actress="Raakhee",
       romance=True, songs=True, villain=True, one_sided=True, action=True),

    hi("ab_kaala_patthar", "Kaala Patthar", 1979,
       "classic", "drama", "Yash Chopra", "Amitabh Bachchan", 7.6,
       social=True, true_story=True, action=True, songs=True, anti_hero=True),

    hi("ab_lawaaris", "Lawaaris", 1981,
       "classic", "drama", "Prakash Mehra", "Amitabh Bachchan", 7.0,
       action=True, songs=True, family=True, social=True),

    hi("ab_naseeb", "Naseeb", 1981,
       "classic", "action", "Manmohan Desai", "Amitabh Bachchan", 7.1,
       action=True, romance=True, songs=True, villain=True, comedy=True),

    hi("ab_kaalia", "Kaalia", 1981,
       "classic", "action", "Tinnu Anand", "Amitabh Bachchan", 6.7,
       action=True, songs=True, villain=True, anti_hero=True, social=True),

    hi("ab_khuda_gawah", "Khuda Gawah", 1992,
       "90s", "action", "Mukul S. Anand", "Amitabh Bachchan", 7.0,
       action=True, romance=True, songs=True, historical=True,
       double_role=True, pan_india=True),

    hi("ab_paa", "Paa", 2009,
       "2000s", "drama", "R. Balki", "Amitabh Bachchan", 7.1,
       actress="Vidya Balan",
       comedy=True, family=True, social=True, parent_child=True),

    # ─── SHAH RUKH KHAN ─────────────────────────────────────────────────────

    hi("srk_raju_ban_gaya", "Raju Ban Gaya Gentleman", 1992,
       "90s", "comedy", "Aziz Mirza", "Shah Rukh Khan", 6.7,
       actress="Juhi Chawla",
       comedy=True, romance=True, songs=True, social=True),

    hi("srk_koyla", "Koyla", 1997,
       "90s", "action", "Rakesh Roshan", "Shah Rukh Khan", 6.2,
       actress="Madhuri Dixit",
       action=True, romance=True, songs=True, villain=True, revenge=True),

    # ─── KAMAL HAASAN (Hindi films) ─────────────────────────────────────────

    hi("kamal_ek_duuje", "Ek Duuje Ke Liye", 1981,
       "classic", "romance", "K. Balachander", "Kamal Haasan", 7.5,
       actress="Rati Agnihotri",
       romance=True, songs=True, social=True, forbidden=True),

    hi("kamal_sadma", "Sadma", 1983,
       "classic", "drama", "Balu Mahendra", "Kamal Haasan", 8.3,
       actress="Sridevi",
       romance=True, songs=True, social=True, remake=True),

    # ─── KAMAL HAASAN (Tamil films) ─────────────────────────────────────────

    ta("kamal_gunaa", "Gunaa", 1991,
       "90s", "action", "Santhana Bharathi", "Kamal Haasan", 7.9,
       actress="Roshini",
       action=True, romance=True, songs=True, anti_hero=True, thriller=True),

    ta("kamal_vettaiyaadu", "Vettaiyaadu Vilaiyaadu", 2006,
       "2000s", "thriller", "Gautham Menon", "Kamal Haasan", 7.9,
       thriller=True, action=True, police=True, songs=True),

    ta("kamal_papanasam", "Papanasam", 2015,
       "2010s", "thriller", "Jeethu Joseph", "Kamal Haasan", 8.4,
       actress="Gautami",
       thriller=True, family=True, remake=True, social=True,
       parent_child=True),

    # ─── RAJINIKANTH ────────────────────────────────────────────────────────

    ta("rajini_murattu_kaalai", "Murattu Kaalai", 1980,
       "classic", "action", "S. P. Muthuraman", "Rajinikanth", 7.3,
       action=True, romance=True, songs=True, village=True, anti_hero=True),

]

# Fix Taare Zameen Par — update lead to Aamir Khan (director/star; child Darsheel was protagonist)
for m in movies:
    if m['title'].lower() == 'taare zameen par':
        m['lead_actor'] = 'Aamir Khan'
        print(f"Updated lead_actor of 'Taare Zameen Par' to Aamir Khan")
        break

# Add new films, skip duplicates
added = []
for m in new_films:
    key = f"{m['title'].lower()}_{m['year']}"
    if m['id'] in existing_ids or key in existing_keys:
        print(f"SKIP (already exists): {m['title']} ({m['year']})")
    else:
        movies.append(m)
        added.append(m)

with open('data/movies.json', 'w') as f:
    json.dump(movies, f, indent=2, ensure_ascii=False)

print(f"\nAdded {len(added)} films. Total: {len(movies)}")
for m in added:
    print(f"  + [{m['language'].upper()}] {m['title']} ({m['year']}) — {m['lead_actor']}")
