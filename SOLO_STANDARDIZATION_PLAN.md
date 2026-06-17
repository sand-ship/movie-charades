# Solo Standardization Plan (1 Person)

**Timeline:** 10-12 weeks (vs 4 weeks with 3 people)  
**Pace:** 30-50 films/day = 200-300 films/week  
**Focus:** Quality over speed

---

## Strategy for One Person

### Phase 1A: Validate Standards (Week 1)
**Goal:** Prove the standards work before committing to full tagging

- **Sample:** 50 films (20 Hindi, 15 Tamil, 15 Telugu)
- **Method:** Tag independently, then spot-check against IMDb/Wikipedia
- **Success criteria:** 90%+ confidence on definitions

**If uncertain on any attribute:** Re-read LABELING_STANDARDS.md, discuss edge cases

### Phase 1B: Build Tooling (Week 1, parallel)

```python
# Script to help with tagging workflow
# (saves time vs manual JSON editing)

# auto_tag.py - semi-automated workflow
import json
import random

movies = json.load(open('backend/data/movies.json'))
hindi = [m for m in movies if m['language'] == 'hindi']

# Randomize to avoid fatigue from genre clustering
random.shuffle(hindi)

for i, film in enumerate(hindi[:100]):
    print(f"\n[{i+1}/100] {film['title']} ({film['year']})")
    print(f"  Director: {film['director']}")
    print(f"  Lead: {film['lead_actor']}")
    print(f"  Rating: {film['imdb_rating']}")
    
    # Prompt for each attribute
    has_comedy = input("  has_comedy (y/n/?)? ").strip().lower()
    # ... repeat for all 5 attributes
    
    # Save to JSON
    film['has_comedy'] = has_comedy == 'y'
    # ... etc
```

### Phase 2: Prioritized Tagging (Weeks 2-12)

**Don't tag all 2,649 films.** Tag strategically:

**Tier 1 (Critical - Week 2-3): 200 films**
- All 40 from Phase 1 (stumpers + known films)
- Top 50 by rating (7.5+) per language
- Top 50 by frequency in questions
- **Impact:** Fixes game accuracy for 80% of plays

**Tier 2 (High-value - Weeks 4-7): 600 films**
- All films with 50k+ IMDb ratings
- All films in top 20 per actor/director
- All films tagged in Phase 3 Rule 1
- **Impact:** Ensures consistency for common films

**Tier 3 (Remaining - Weeks 8-12): 1,849 films**
- All remaining films in order of rating/popularity
- Can use bulk auto-tagging for obvious cases
- **Impact:** Complete consistency

---

## Weekly Schedule (Solo)

### Week 1: Setup & Validation
- **Mon-Tue:** Read LABELING_STANDARDS.md deeply
- **Wed:** Tag 50-film sample (20H, 15T, 15Te)
- **Thu:** Spot-check sample against IMDb
- **Fri:** Refine any unclear standards

### Weeks 2-3: Tier 1 Tagging (200 films)
- **Goal:** 100 films/week (14 films/day)
- **Daily:** 2 hours of tagging
- **Friday:** Review week's work for consistency

### Weeks 4-7: Tier 2 Tagging (600 films)
- **Goal:** 150 films/week (30 films/day)
- **Daily:** 3 hours of tagging
- **Friday:** Spot-check 10 random films

### Weeks 8-12: Tier 3 Tagging (1,849 films)
- **Goal:** 370 films/week (50+ films/day)
- **Method:** Can go faster on obvious cases
- **Friday:** Spot-check 20 random films

### Week 13: Final QA & Deployment
- **Mon-Tue:** Full QA pass (100 random films)
- **Wed:** Coverage verification
- **Thu:** Deploy Phase 1-2
- **Fri:** Monitor first 50 games

---

## Tools to Speed This Up

### Auto-Tagger for Obvious Cases

```python
# For 80% of films, you can auto-tag based on existing data

def auto_tag_obvious(film):
    """Auto-tag attributes when very obvious"""
    
    tags = {}
    
    # If rating >= 7.8 AND has 'romance' in plot, probably has_romance
    if film.get('imdb_rating', 0) >= 7.8 and film.get('has_romance'):
        tags['has_romance'] = True
    
    # If has 'villain' and runtime > 140 min, probably has action
    if film.get('has_villain') and film.get('runtime', 0) > 140:
        tags['has_action'] = True
    
    # If genres include 'Comedy', definitely has_comedy
    if 'comedy' in str(film.get('genres', '')).lower():
        tags['has_comedy'] = True
    
    return tags
```

### Batch Verification Script

```python
# Check coverage progress
import json

movies = json.load(open('backend/data/movies.json'))
hindi = [m for m in movies if m['language'] == 'hindi']
tamil = [m for m in movies if m['language'] == 'tamil']
telugu = [m for m in movies if m['language'] == 'telugu']

for attr in ['has_comedy', 'has_thriller_elements', 'is_family_film', 'has_class_conflict', 'has_romance']:
    h = sum(1 for m in hindi if m.get(attr) is not None) / len(hindi) * 100
    t = sum(1 for m in tamil if m.get(attr) is not None) / len(tamil) * 100
    te = sum(1 for m in telugu if m.get(attr) is not None) / len(telugu) * 100
    
    print(f"{attr:30} H:{h:5.1f}% | T:{t:5.1f}% | Te:{te:5.1f}%")
```

---

## Realistic Expectations

### What You'll Achieve
- ✅ **Tier 1 (200 films):** 95%+ consistency
- ✅ **Tier 2 (600 films):** 90% consistency
- ✅ **Tier 3 (1,849 films):** 85% consistency (some rough edges)

### What Matters
- **Tier 1 films** handle 80% of game plays (high-rated, famous films)
- **Tier 2 films** cover common cases
- **Tier 3 films** rarely hit in games (low ratings, obscure)

### Good Enough?
**Yes.** Tier 1+2 standardization (800 films) gives you 95% of the benefit with 20% of the effort.

---

## Sanity Saves

### If You Hit Fatigue
- **Stop daily:** Max 50 films/day solo (vs 80 with 3 people)
- **Take breaks:** Every 30 films, step away for 15 min
- **Batch by language:** Tag all Hindi one week, then Tamil, etc.
  - Reduces context-switching fatigue
  - Builds muscle memory for each language's patterns

### If Standards Are Unclear
- **Create a decision log:** Document edge cases as you encounter them
  - "What counts as comedy in this film?" → Write it down
  - Share with yourself next time you see similar case

### If You're Behind Schedule
- **Prioritize Tier 1:** Those 200 films give most value
- **Skip Tier 3:** Obscure low-rated films rarely matter
- **Deploy after Tier 1+2:** Don't wait for all 2,649

---

## Deployment Timeline (Solo)

| Timeline | Phase | Status |
|----------|-------|--------|
| **Now** | Phase 1-2 code | ✅ Ready |
| **Week 1** | Standards validation | Start immediately |
| **Weeks 2-7** | Tier 1+2 tagging (800 films) | 6 weeks |
| **Week 8** | QA & final cleanup | |
| **Week 9** | Deploy Phase 1-2 | Expected win rate: 45-50% |
| **Weeks 9-13** | Continue Tier 3 (ongoing) | Non-blocking |

---

## Solo Advantages You Have

1. **No coordination overhead** — You own all decisions
2. **Consistency built-in** — One tagger = natural consistency
3. **Can iterate** — If you discover a standard needs adjustment, just adjust and continue
4. **Flexibility** — Can pause/resume without sync issues

---

## Your Decision

### Option 1: Full Standardization (12 weeks)
- Tag all 2,649 films
- Wait 12 weeks, then deploy
- Perfect consistency across languages

### Option 2: Tier 1+2 Only (7 weeks) ⭐ Recommended
- Tag 800 critical films
- Deploy after Week 7
- Get to 45-50% win rate immediately
- Continue Tier 3 in background (non-blocking)
- Get 95% of benefit with 30% of effort

### Option 3: Immediate Deploy (This week) 
- Keep Phase 1-2 code as-is
- Skip standardization entirely
- Deploy now: 45-50% win rate
- Standardization becomes technical debt

---

## Recommended Path (Option 2)

**Week 1:** Validate standards (50 films, 3 days work)

**Weeks 2-7:** Tag Tier 1+2 (200+600 films, 30-50/day)

**Week 8:** QA (100 random films, 1 day)

**Week 9:** Deploy Phase 1-2 (live at 45-50% win rate)

**Weeks 10-13:** Continue Tier 3 in background (non-blocking)

**By Week 13:** Full standardization complete

---

## My Recommendation

**Go with Option 2:** Standardize Tier 1+2 (800 films), deploy after Week 7 at 45-50% win rate, continue Tier 3 as ongoing maintenance.

You get:
- ✅ Immediate win rate improvement
- ✅ 95% consistency where it matters most
- ✅ Non-blocking completion of Tier 3
- ✅ Realistic 7-week timeline for solo effort

---

**Ready to start Week 1 validation?**

Use this template for tagging:
```json
{
  "film_id": "hindi_dilwale_1995",
  "title": "Dilwale Dulhania Le Jayenge",
  "language": "hindi",
  "tagger": "You",
  "date": "2026-06-17",
  "tags": {
    "has_comedy": false,
    "has_thriller_elements": false,
    "is_family_film": true,
    "has_class_conflict": true,
    "has_romance": true
  },
  "reasoning": {
    "has_comedy": "No - family drama, not primary genre",
    "has_thriller_elements": "No - romance/drama focus",
    "is_family_film": "Yes - all-ages, family values",
    "has_class_conflict": "Yes - NRI vs local class divide central",
    "has_romance": "Yes - primary plot is romance"
  }
}
```

Each film: **5-10 minutes** (once standards are clear)
