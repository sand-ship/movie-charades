# Manual Review Queue - Romance Tagging

**Date Created:** 2026-06-21  
**Status:** FLAGGED FOR MANUAL REVIEW  
**Priority:** MEDIUM

---

## What Needs Review?

**1,171 secondary romance films** - Films where 'romance' appears in the genres list but it's NOT the primary genre.

Examples:
- **Sholay** (primary: action, genres: action, adventure, drama, comedy, romance, thriller)
- **3 Idiots** (primary: comedy, genres: comedy, drama, romance)
- **Rang De Basanti** (primary: drama, genres: drama, historical, action, thriller, romance)

---

## What's the Issue?

These films have `has_romance=true` and now have `has_love_triangle=true` (added automatically).

**But:** We don't know if the romance is significant enough to justify these tags.

### Possible scenarios:

**KEEP tags (romance is significant):**
- Love interest is a major subplot
- Romance affects character development
- Emotional weight to the relationship
- Example: Sholay has Hema Malini as love interest throughout

**REMOVE tags (romance is minor):**
- Love interest appears briefly
- Romance is just a plot device
- No emotional development
- Example: Film where hero has a 30-second crush scene

---

## Files

**Review spreadsheet:** `REVIEW_secondary_romance_707.csv`

Contains:
- Title, Year, Language
- Primary Genre
- All Genres
- Director, Lead Actor
- Current tags (has_love_triangle=true)
- Notes column for your decisions

---

## How to Review

For each film, watch or research to answer:

**Does this film have a SIGNIFICANT romantic subplot?**

1. **YES** → Keep:
   - `has_romance: true`
   - `has_love_triangle: true` (or appropriate love element)

2. **NO** → Remove:
   - `has_romance: false`
   - `has_love_triangle: false`

3. **MAYBE** → Mark for follow-up
   - Add notes on what you're unsure about

---

## Priority Films to Review First

**High confidence needed for:**
- Primary action films with romance (499 films)
- Drama films (308 films)
- Comedy films (241 films)

**Easier to verify:**
- Biopics (7 films) - usually clear if romance is central
- Horror films (6 films) - romance is typically secondary
- Historical films (24 films) - often have known romantic subplots

---

## Impact on Game

**Why this matters:**
- Romance questions use `has_love_triangle`, `has_one_sided_love`, `has_forbidden_love`
- Incorrect tagging → questions don't discriminate properly
- Wrong narrowing → stumpers fail

**Example:**
- If Sholay is tagged as romance but it shouldn't be
- Player answers "Does it have a love triangle?" YES
- Game narrows to romance films only
- But Sholay is primarily an action film
- Game can't identify it correctly

---

## Timeline

- Created: 2026-06-21
- Expected review: Not urgent
- Can be done incrementally

---

## Contact

Questions? Check the database cleanup commits for context.

