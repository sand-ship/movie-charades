#!/usr/bin/env python3
"""Tag movies with the 8 new soft-trope fields."""
import json
from pathlib import Path

DATA = Path(__file__).parent / "data" / "movies.json"
movies = json.loads(DATA.read_text())

# ── trope tag sets (title_lower, year) ────────────────────────────────────────

ONE_SIDED_LOVE = {
    # Hindi
    ("devdas", 1955), ("devdas", 2002), ("devdas", 1935),
    ("kal ho na ho", 2003), ("ae dil hai mushkil", 2016), ("darr", 1993),
    ("dil to pagal hai", 1997), ("tere naam", 2003), ("raanjhanaa", 2013),
    ("rockstar", 2011), ("silsila", 1981), ("saathiya", 2002),
    ("kabhie kabhie", 1976), ("lamhe", 1991), ("mujhse dosti karoge!", 2002),
    ("hum tum", 2004), ("rehnaa hai terre dil mein", 2001),
    # Tamil
    ("96", 2018), ("alaipayuthey", 2000), ("kadhal", 2004),
    ("vinnaithaandi varuvaayaa", 2010), ("mouna ragam", 1986),
    ("ok kanmani", 2015), ("kaadhal kondein", 2003), ("ninaithale inikkum", 1979),
    ("7g rainbow colony", 2004), ("pithamagan", 2003), ("autograph", 2004),
    ("sillunu oru kadhal", 2006), ("kaakha kaakha", 2003),
    # Telugu
    ("ye maaya chesave", 2010), ("geetanjali", 1989), ("malli raava", 2017),
    ("ninnu kori", 2017), ("premalo chikkadu", 1996),
    ("tholi prema", 1998), ("nuvvostanante nenoddantana", 2005),
}

ITEM_NUMBER = {
    # Hindi — films famous for item numbers
    ("dabangg", 2010), ("dabangg 2", 2012), ("tees maar khan", 2010),
    ("agneepath", 2012), ("rowdy rathore", 2012), ("ra.one", 2011),
    ("don 2", 2011), ("housefull 2", 2012), ("student of the year", 2012),
    ("dhoom 3", 2013), ("kick", 2014), ("heropanti", 2014),
    ("bajrangi bhaijaan", 2015), ("dilwale", 2015), ("prem ratan dhan payo", 2015),
    ("sultan", 2016), ("ae dil hai mushkil", 2016), ("baaghi", 2016),
    ("tiger zinda hai", 2017), ("race 3", 2018), ("simmba", 2018),
    ("bharat", 2019), ("war", 2019), ("sooryavanshi", 2021),
    ("pushpa: the rise", 2021), ("pushpa 2: the rule", 2024),
    ("rrr", 2022), ("kgf: chapter 2", 2022),
    # Tamil
    ("enthiran", 2010), ("lingaa", 2014), ("petta", 2019),
    ("darbar", 2020), ("beast", 2022),
    # Telugu
    ("pokiri", 2006), ("magadheera", 2009), ("baahubali: the beginning", 2015),
    ("baahubali 2: the conclusion", 2017), ("sarrainodu", 2016),
    ("dj: duvvada jagannadham", 2017), ("ala vaikunthapurramuloo", 2020),
    ("sarkaru vaari paata", 2022),
}

DOUBLE_ROLE = {
    # Hindi
    ("ram aur shyam", 1967), ("seeta aur geeta", 1972), ("judwaa", 1997),
    ("judwaa 2", 2017), ("duplicate", 1998), ("kishen kanhaiya", 1990),
    ("do aankhen barah haath", 1957), ("don", 1978), ("don", 2006),
    ("don 2", 2011), ("agneepath", 2012), ("new york", 2009),
    # Tamil
    ("enthiran", 2010), ("2.0", 2018), ("dasavathaaram", 2008),
    ("eeram", 2009), ("vikram vedha", 2017), ("mersal", 2017),
    ("bigil", 2019), ("master", 2021), ("vikram", 2022),
    # Telugu
    ("jai lava kusa", 2017), ("aapattbandavudu", 1992), ("khaidi", 1983),
    ("daana veera soora karna", 1977), ("kondaveeti donga", 1990),
    ("simhadri", 2003), ("samba", 2004), ("sardaar gabbar singh", 2016),
}

COLLEGE_FILM = {
    # Hindi
    ("kuch kuch hota hai", 1998), ("mohabbatein", 2000),
    ("3 idiots", 2009), ("student of the year", 2012),
    ("student of the year 2", 2019), ("raanjhanaa", 2013),
    ("main hoon na", 2004), ("dil chahta hai", 2001),
    ("jaane tu... ya jaane na", 2008), ("wake up sid", 2009),
    ("rockstar", 2011), ("2 states", 2014), ("chhichhore", 2019),
    ("mujhse dosti karoge!", 2002), ("humpty sharma ki dulhania", 2014),
    ("badrinath ki dulhania", 2017), ("shuddh desi romance", 2013),
    # Tamil
    ("friends", 2001), ("7g rainbow colony", 2004), ("vallavan", 2006),
    ("aadhavan", 2009), ("vinnaithaandi varuvaayaa", 2010),
    ("3", 2012), ("ok kanmani", 2015), ("inaindha kaigal", 2020),
    # Telugu
    ("happy days", 2007), ("student no. 1", 2001), ("college kumar", 2010),
    ("swamy ra ra", 2013), ("gunde jaari gallanthayyinde", 2013),
    ("pelli choopulu", 2016), ("bhale bhale magadivoy", 2015),
    ("nuvvostanante nenoddantana", 2005), ("ee nagaraniki emaindi", 2018),
    ("nenu nanna abbayi", 2016), ("andala rakshasi", 2012),
}

PARENT_CHILD = {
    # Hindi
    ("mother india", 1957), ("deewar", 1975), ("trishul", 1978),
    ("kabhi khushi kabhie gham", 2001), ("baghban", 2003),
    ("taare zameen par", 2007), ("english vinglish", 2012),
    ("kapoor & sons", 2016), ("dil dhadakne do", 2015),
    ("udaan", 2010), ("piku", 2015), ("secret superstar", 2017),
    ("super 30", 2019), ("shershaah", 2021), ("brahmastra: part one - shiva", 2022),
    # Tamil
    ("pithamagan", 2003), ("ayan", 2009), ("mynaa", 2010),
    ("sathuranga vettai", 2014), ("kaaka muttai", 2014),
    ("kadhalil sodhappuvadhu yeppadi", 2012), ("theri", 2016),
    ("bigil", 2019), ("etharkkum thunindhavan", 2022),
    # Telugu
    ("suryavamsam", 1997), ("manam", 2014), ("shatamanam bhavati", 2017),
    ("prati roju pandaage", 2019), ("tuck jagadish", 2021),
    ("sreekaram", 2021), ("kondapolam", 2021),
    ("seetharamaiah gari manavaralu", 1991), ("babu bangaram", 2016),
}

POLICE_OR_LAW = {
    # Hindi
    ("sholay", 1975), ("zanjeer", 1973), ("ardh satya", 1983),
    ("singham", 2011), ("singham returns", 2014), ("simba", 2018),
    ("sooryavanshi", 2021), ("rowdy rathore", 2012), ("dabangg", 2010),
    ("dabangg 2", 2012), ("dabangg 3", 2019), ("gangaajal", 2003),
    ("apaharan", 2005), ("mardaani", 2014), ("mardaani 2", 2019),
    ("pink", 2016), ("jolly llb", 2013), ("jolly llb 2", 2017),
    ("article 15", 2019), ("badla", 2019), ("drishyam", 2015),
    ("drishyam 2", 2022), ("a wednesday!", 2008), ("talaash", 2012),
    ("kahaani", 2012), ("kahaani 2", 2016), ("special 26", 2013),
    ("baby", 2015), ("airlift", 2016), ("rustom", 2016),
    ("toilet: ek prem katha", 2017), ("shershaah", 2021),
    # Tamil
    ("vikram", 1986), ("ejamaan", 1993), ("kaaka kaakha", 2003),
    ("saamy", 2003), ("sivaji", 2007), ("mankatha", 2011),
    ("thuppakki", 2012), ("theri", 2016), ("singam", 2010),
    ("singam 2", 2013), ("singam 3", 2017), ("mersal", 2017),
    ("sarkar", 2018), ("bigil", 2019), ("master", 2021),
    ("beast", 2022), ("vikram", 2022), ("jailer", 2023),
    ("leo", 2023), ("vettaiyan", 2024), ("indian 2", 2024),
    ("saamy 2", 2018), ("saamy square", 2018),
    # Telugu
    ("vikramarkudu", 2006), ("temper", 2015), ("krack", 2021),
    ("khaidi no. 150", 2017), ("naayak", 2013), ("athadu", 2005),
    ("pokiri", 2006), ("dookudu", 2011), ("businessman", 2012),
    ("gabbar singh", 2012), ("sardaar gabbar singh", 2016),
    ("vakeel saab", 2021), ("goodachari", 2018), ("evaru", 2019),
    ("hit: the first case", 2020), ("hit: the second case", 2022),
    ("hit: the third case", 2023), ("naandhi", 2021),
    ("agent sai srinivasa athreya", 2019), ("brochevarevarura", 2019),
}

VILLAGE_SETTING = {
    # Hindi
    ("mother india", 1957), ("do bigha zamin", 1953),
    ("lagaan", 2001), ("swades", 2004), ("peepli live", 2010),
    ("toilet: ek prem katha", 2017), ("newton", 2017),
    ("son chiriya", 2019), ("bard of blood", 2019),
    ("sholay", 1975), ("nadiya ke paar", 1982), ("hum aapke hain koun..!", 1994),
    ("dilwale dulhania le jayenge", 1995), ("gadar: ek prem katha", 2003),
    # Tamil
    ("roja", 1992), ("muthu", 1995), ("aadukalam", 2011),
    ("kaaka muttai", 2014), ("pariyerum perumal", 2018),
    ("sarpatta parambarai", 2021), ("karnan", 2021),
    ("jai bhim", 2021), ("kaithi", 2019), ("virumaandi", 2004),
    ("pithamagan", 2003), ("mynaa", 2010), ("angadi theru", 2010),
    ("subramaniapuram", 2008), ("pasanga", 2009),
    # Telugu
    ("rangasthalam", 2018), ("baahubali: the beginning", 2015),
    ("baahubali 2: the conclusion", 2017), ("annavaram", 2006),
    ("sreekaram", 2021), ("kondapolam", 2021), ("virata parvam", 2022),
    ("kondaveeti donga", 1990), ("palasa 1978", 2020),
    ("sankarabharanam", 1980), ("swathi mutyam", 1986),
    ("alluri seetarama raju", 1974), ("seetharamaiah gari manavaralu", 1991),
    ("narappa", 2021), ("dasara", 2023),
}

MASS_ENTERTAINER = {
    # Hindi — masala blockbusters
    ("sholay", 1975), ("don", 1978), ("muqaddar ka sikandar", 1978),
    ("coolie", 1983), ("mard", 1985), ("tezaab", 1988),
    ("maine pyar kiya", 1989), ("ram lakhan", 1989),
    ("hum", 1991), ("jo jeeta wohi sikandar", 1992),
    ("baazigar", 1993), ("karan arjun", 1995),
    ("dilwale dulhania le jayenge", 1995), ("raja hindustani", 1996),
    ("dil to pagal hai", 1997), ("kuch kuch hota hai", 1998),
    ("hum saath-saath hain", 1999), ("refugee", 2000),
    ("lagaan", 2001), ("devdas", 2002), ("kal ho na ho", 2003),
    ("dhoom", 2004), ("veer-zaara", 2004), ("no entry", 2005),
    ("krrish", 2006), ("dhoom 2", 2006), ("don", 2006),
    ("jab we met", 2007), ("partner", 2007), ("race", 2008),
    ("singh is kinng", 2008), ("de de pyaar de", 2008),
    ("ghajini", 2008), ("wanted", 2009), ("3 idiots", 2009),
    ("dabangg", 2010), ("golmaal 3", 2010), ("housefull", 2010),
    ("bodyguard", 2011), ("don 2", 2011), ("ra.one", 2011),
    ("ek tha tiger", 2012), ("rowdy rathore", 2012),
    ("dabangg 2", 2012), ("agneepath", 2012), ("housefull 2", 2012),
    ("chennai express", 2013), ("dhoom 3", 2013), ("kick", 2014),
    ("entertainment", 2014), ("bang bang!", 2014), ("happy new year", 2014),
    ("bajrangi bhaijaan", 2015), ("sultan", 2016), ("tubelight", 2017),
    ("tiger zinda hai", 2017), ("race 3", 2018), ("simmba", 2018),
    ("war", 2019), ("sooryavanshi", 2021), ("pathaan", 2023),
    ("tiger 3", 2023), ("jawan", 2023),
    # Tamil — Rajinikanth, Vijay, Ajith mass films
    ("baashha", 1995), ("muthu", 1995), ("padayappa", 1999),
    ("baba", 2002), ("chandramukhi", 2005), ("sivaji", 2007),
    ("enthiran", 2010), ("kochadaiiyaan", 2014), ("lingaa", 2014),
    ("kabali", 2016), ("kaala", 2018), ("2.0", 2018), ("petta", 2019),
    ("darbar", 2020), ("annaatthe", 2021), ("jailer", 2023), ("vettaiyan", 2024),
    ("thuppakki", 2012), ("theri", 2016), ("mersal", 2017), ("sarkar", 2018),
    ("bigil", 2019), ("master", 2021), ("beast", 2022), ("leo", 2023),
    ("varisu", 2023), ("indian 2", 2024),
    ("kadhal", 2004), ("mankatha", 2011), ("veeram", 2014), ("vivegam", 2017),
    ("viswasam", 2019), ("nerkonda paarvai", 2019), ("valimai", 2022),
    ("thunivu", 2023),
    # Telugu — mass entertainers
    ("baahubali: the beginning", 2015), ("baahubali 2: the conclusion", 2017),
    ("rrr", 2022), ("pushpa: the rise", 2021), ("pushpa 2: the rule", 2024),
    ("pokiri", 2006), ("magadheera", 2009), ("dookudu", 2011),
    ("businessmanm", 2012), ("businessman", 2012), ("baadshah", 2013),
    ("attarintiki daredi", 2013), ("race gurram", 2014), ("srimanthudu", 2015),
    ("sarrainodu", 2016), ("khaidi no. 150", 2017), ("bharat ane nenu", 2018),
    ("maharshi", 2019), ("sarileru neekevvaru", 2020),
    ("ala vaikunthapurramuloo", 2020), ("sarkaru vaari paata", 2022),
    ("acharya", 2022), ("waltair veerayya", 2023), ("skanda", 2023),
    ("devara: part 1", 2024), ("kalki 2898 ad", 2024),
    ("temper", 2015), ("janatha garage", 2016), ("jai lava kusa", 2017),
    ("aravindha sametha veera raghava", 2018), ("krack", 2021),
    ("akhanda", 2021), ("vakeel saab", 2021), ("salaar: part 1", 2023),
}

# ── build lookup map ──────────────────────────────────────────────────────────

def key(m):
    return (m["title"].lower(), m["year"])

tagged = 0
for m in movies:
    k = key(m)
    changed = False
    for field, tag_set in [
        ("has_one_sided_love",    ONE_SIDED_LOVE),
        ("has_item_number",       ITEM_NUMBER),
        ("has_double_role",       DOUBLE_ROLE),
        ("is_college_film",       COLLEGE_FILM),
        ("has_parent_child_drama",PARENT_CHILD),
        ("has_police_or_law",     POLICE_OR_LAW),
        ("has_village_setting",   VILLAGE_SETTING),
        ("is_mass_entertainer",   MASS_ENTERTAINER),
    ]:
        val = k in tag_set
        if m.get(field) != val:
            m[field] = val
            changed = True
    if changed:
        tagged += 1

from collections import Counter
langs = Counter(m["language"] for m in movies)
print(f"Tagged {tagged} movies")
print(f"Counts by trope:")
for field in ["has_one_sided_love","has_item_number","has_double_role","is_college_film",
              "has_parent_child_drama","has_police_or_law","has_village_setting","is_mass_entertainer"]:
    n = sum(1 for m in movies if m.get(field))
    print(f"  {field}: {n}")

DATA.write_text(json.dumps(movies, indent=2, ensure_ascii=False))
print("Done.")
