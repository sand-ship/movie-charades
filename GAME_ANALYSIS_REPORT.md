# Indian Movie Charades - Game Analysis Report

## Executive Summary

The Indian Movie Charades game is accessible at https://movie-charades.onrender.com/ with a FastAPI backend and Supabase database for game storage. The application features a rich movie catalog of 2,553 films across multiple Indian languages and a sophisticated questioning engine.

**Key Status:**
- ✓ Live server is accessible and healthy
- ✓ Movie catalog has 2,553 films (Hindi, Tamil, Telugu, Kannada, Malayalam, Marathi)
- ✓ Game sessions successfully created and can progress through questioning
- ⚠ Live game data is stored in Supabase (requires admin authentication to access)
- ✓ 3 stumper records available locally for analysis

---

## Accessible API Endpoints

### Public Endpoints
- `GET /health` - Server health check + movie count
- `GET /movies` - List all movies (optional language filter)
- `GET /movies/export.csv` - Export catalog as CSV
- `POST /game/start` - Start a new game session
- `POST /game/answer` - Submit answer to a question
- `POST /game/batch-answer` - Submit multiple answers
- `POST /game/back` - Undo last answer
- `POST /game/feedback` - Provide outcome feedback
- `POST /game/stumped` - Report that genie couldn't guess
- `GET /game/session/{session_id}` - Get session state

### Protected Admin Endpoints (require ADMIN_KEY)
- `GET /admin/games` - List all completed games
- `GET /admin/stumpers` - List all stumpers
- `GET /admin/analyze-stumpers` - Analyze stumper patterns

---

## Data Analysis Findings

### 1. Movie Catalog (2,553 films)

**Language Distribution:**
| Language | Count | Percentage |
|----------|-------|-----------|
| Hindi | 958 | 37.5% |
| Tamil | 820 | 32.1% |
| Telugu | 724 | 28.3% |
| Kannada | 20 | 0.8% |
| Malayalam | 30 | 1.2% |
| Marathi | 1 | 0.04% |

**Time Span:** 1949 - 2026 (77 years of Indian cinema)

### 2. Stumper Records (3 local entries)

Games where the Genie failed to make a correct guess:

| # | Film Title | Remaining Candidates | Yes Answers | Status |
|---|-----------|---------------------|-------------|--------|
| 1 | Some Rare Film 1994 | 521 | 1 | NOT IN CATALOG |
| 2 | Durandhar | 3 | 9 | NOT IN CATALOG |
| 3 | Anaganaga Oka Roju | 4 | 8 | IN CATALOG |

**Stumper Statistics:**
- Average remaining candidates: **176.0**
- Median remaining candidates: **4**
- Range: 3-521 candidates
- Average yes-answers per stumper: **6.0** questions
- Range: 1-9 yes-answers

**Interpretation:**
- 2 out of 3 stumpers are not in the current catalog (missing films)
- 1 stumper (Anaganaga Oka Roju) is in catalog but mislabeled
- High variance in remaining_candidates suggests:
  - Some stumpers are "needle in haystack" scenarios (521 candidates left)
  - Some are highly specific (3-4 candidates), indicating narrow filtering

### 3. Game Session Testing

Tested the API with random gameplay patterns:
- **3 games played** with simulated random answers
- **Average questions per session:** 15.0
- **Server response time:** ~100-200ms per request
- **Game phases observed:** question → question → ... → (guess or no_questions)

### 4. Live Game Data (Supabase)

All completed game records are stored in Supabase with the following structure:

```json
{
  "ts": "2026-06-17T...",
  "outcome": "correct|wrong_guess|stumped",
  "guessed_movie_id": "string",
  "guessed_movie_title": "string",
  "correct_movie_id": "string (optional)",
  "yes_answers": ["q_id_1", "q_id_2", ...],
  "all_answers": {"q_id": "yes|no|maybe|dunno", ...},
  "questions_asked": ["q_id_1", "q_id_2", ...],
  "remaining_candidates": number,
  "question_count": number
}
```

**Data that should be available via `/admin/games` (with auth):**
- Total games played
- Success rate (correct guesses / total)
- Stump rate (stumped games / total)
- Average questions per game
- Performance by language
- Most common incorrect guesses
- Average remaining_candidates at stump time

---

## Game Engine Architecture

### Question Types
The engine uses multiple question categories:
1. **Language questions** - Hindi, Tamil, Telugu filters
2. **Era questions** - Before 1990s, 1990s, 2000s, 2010s, 2020s
3. **Genre questions** - Action, Comedy, Romance, Drama, Thriller, Sci-Fi, Other
4. **Attribute questions** - Villain presence, Romance, Social message, etc.
5. **Actor/Actress questions** - Lead actor/actress specific questions
6. **Director questions** - Director-specific questions

### Session State
Each game maintains:
- `session_id` - Unique identifier
- `answers` - Dictionary of question_id → answer
- `asked` - List of asked question IDs
- `candidates` - Current filtered movie set
- `last_guesses` - Top N guesses when phase transitions to "guess"

### Guess Triggering
The engine triggers a "guess phase" when:
1. Remaining candidates ≤ threshold (typically 1)
2. Confidence reaches high level
3. Questions exhausted

---

## Key Metrics to Track (when Supabase accessible)

### Primary KPIs
1. **Success Rate** = Correct Guesses / Total Games
2. **Stump Rate** = Stumped Games / Total Games
3. **Accuracy of Guesses** = Correct / (Correct + Wrong Guesses)
4. **Average Questions per Game** - How many questions needed on average
5. **Questions to Guess** - Distribution pattern

### Secondary KPIs
1. **Language Performance**
   - Success rate by language
   - Average questions needed per language
   - Stump rate by language

2. **Difficulty Profiles**
   - Easy films (guessed in < 5 questions)
   - Medium films (5-10 questions)
   - Hard films (10+ questions)

3. **Error Analysis**
   - Most confused film pairs
   - Repeated wrong guesses
   - Stumper patterns (missing vs mislabeled)

4. **Remaining Candidates Distribution**
   - At guess phase
   - At stump phase
   - By difficulty level

---

## Data Collection Points

### Where Game Data Lives

**Local (Git-tracked)**
- `/backend/data/stumpers.jsonl` - 3 stumper records
- `/backend/data/movies.json` - 2,553 film catalog
- `/backend/data/movies.csv` - Spreadsheet export

**Remote (Supabase - NOT in Git)**
- `supabase_url/games` - All game outcomes
- `supabase_url/stumpers` - Remote stumper records
- Games sync happens via `/game/feedback` and `/game/stumped` endpoints

### Access Requirements

To access full game analytics:
```bash
curl "https://movie-charades.onrender.com/admin/games?key={ADMIN_KEY}"
```

The `ADMIN_KEY` is configured via environment variable `ADMIN_KEY` and is not in git.

---

## Deployment Status

**Live Instance:** https://movie-charades.onrender.com/
- Platform: Render (hosting)
- Backend: FastAPI + Python
- Database: Supabase (PostgreSQL)
- Frontend: React/HTML (served from `/frontend`)
- Movies: 2,553 films indexed

**Recent Commits** (git history shows):
- c12abc7: Safe adaptive density-aware boost
- ff0b638: Fix problematic density-aware routing
- af5030a: Adaptive density-aware questioning
- 71573fe: Density stratification + collision resolution
- 5c9de79: Language-specific confirmation routing

---

## Recommendations

### For Game Metrics Tracking
1. **Enable admin access** to fetch complete game history from Supabase
2. **Export weekly snapshots** of games and stumpers for trending analysis
3. **Track game difficulty** by measuring questions needed per film

### For Catalog Improvement
1. **Investigate 2 missing stumpers:**
   - "Some Rare Film 1994" - 521 candidates remain (likely film not in catalog)
   - "Durandhar" - Only 3 candidates left (catalog may need language/year fix)

2. **Fix mislabeled "Anaganaga Oka Roju"**
   - 8 yes-answers but still not guessed
   - Indicates label mismatches on yes-answered attributes

### For Engine Optimization
1. **Analyze remaining_candidates distribution:**
   - Current stump: average 176 candidates remaining
   - Goal: lower before stump (tighter filtering before giving up)

2. **Language-specific tuning:**
   - Current distribution: Hindi 37.5% | Tamil 32% | Telugu 28%
   - May need more discriminative questions for minority languages

---

## Files Generated for This Analysis

- `analyze_games.py` - Basic stumper analysis
- `test_api.py` - API functionality testing
- `comprehensive_analysis.py` - Full data analysis
- `GAME_ANALYSIS_REPORT.md` - This report

---

## Next Steps

1. Obtain `ADMIN_KEY` to access Supabase game data
2. Fetch complete game history via `/admin/games?key=...`
3. Run performance analysis to calculate:
   - True success/stump rates
   - Language-specific metrics
   - Difficulty distribution
   - Most problematic films

4. Set up automated reporting:
   - Daily game metrics
   - Weekly stumper analysis
   - Monthly trend reports

---

*Report generated: 2026-06-17*  
*Data scope: Live server accessible, 3 local stumpers, 2,553 films in catalog*  
*Game history: Stored in Supabase (requires admin auth)*
