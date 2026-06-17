# Indian Movie Charades - Analytics & Game Data Index

## Quick Reference

**Live Site:** https://movie-charades.onrender.com/  
**Status:** ✓ Operational  
**Movie Catalog:** 2,553 films (Hindi, Tamil, Telugu + others)  
**Local Stumpers:** 3 records  
**Game History:** Stored in Supabase (requires admin authentication)

---

## Files in This Repository

### Analysis Reports
- **`GAME_ANALYSIS_REPORT.md`** - Comprehensive analysis report with findings, metrics, and recommendations

### Analysis Tools
- **`comprehensive_analysis.py`** - Analyze local stumpers, movies, and catalog
  ```bash
  python3 comprehensive_analysis.py
  ```

- **`fetch_live_metrics.py`** - Fetch and analyze live game metrics from Supabase (requires admin key)
  ```bash
  python3 fetch_live_metrics.py --key YOUR_ADMIN_KEY --output metrics.json
  ```

- **`test_api.py`** - Test API by playing sample games
  ```bash
  python3 test_api.py
  ```

- **`analyze_games.py`** - Basic stumper analysis
  ```bash
  python3 analyze_games.py
  ```

### Data Files
- **`backend/data/movies.json`** - 2,553 film catalog with full metadata
- **`backend/data/stumpers.jsonl`** - 3 stumper records (films AI couldn't guess)
- **`backend/data/movies.csv`** - Spreadsheet export of movies

---

## Data Structure Overview

### Stumper Record (JSONL)
```json
{
  "ts": "2026-05-30T08:06:09.214814Z",
  "title": "Film Title",
  "yes_answers": ["q_hindi", "q_action", ...],
  "remaining_candidates": 521
}
```
**Meaning:** A player reported that the AI couldn't guess their film after answering questions

### Game Record (in Supabase)
```json
{
  "ts": "2026-06-17T...",
  "outcome": "correct|wrong_guess|stumped",
  "guessed_movie_id": "film_id",
  "guessed_movie_title": "Film Name",
  "correct_movie_id": "actual_film_id",
  "yes_answers": ["q_id_1", "q_id_2", ...],
  "all_answers": {"q_id": "yes|no|maybe|dunno", ...},
  "questions_asked": ["q_id_1", ...],
  "remaining_candidates": 42,
  "question_count": 12
}
```

### Movie Record
```json
{
  "id": "unique_id",
  "title": "Film Name",
  "year": 2020,
  "language": "Hindi",
  "era": "2020s",
  "genres": ["action", "thriller"],
  "lead_gender": "male",
  "has_villain": true,
  "has_songs": false,
  "has_romance": true,
  "has_comedy": false,
  "has_action": true,
  "has_thriller_elements": true,
  "has_social_message": false,
  ... (100+ attributes)
}
```

---

## Key Metrics

### Current Data (2026-06-17)

**Stumpers (Local):**
- Total: 3 records
- Average remaining candidates: 176 (range: 3-521)
- Average yes-answers: 6 questions
- Catalog coverage: 2 missing films, 1 mislabeled

**Catalog:**
- Total films: 2,553
- Hindi: 958 (37.5%)
- Tamil: 820 (32.1%)
- Telugu: 724 (28.3%)
- Year range: 1949-2026

**API Tests:**
- Health: ✓ Operational
- Response time: 100-200ms
- Session creation: ✓ Working
- Question flow: ✓ Working

### Available When Authenticated

(Requires ADMIN_KEY to fetch via `/admin/games`)

- **Success Rate** - % of games where AI guessed correctly
- **Stump Rate** - % of games where player stumped the AI
- **Average Questions** - Questions needed per game
- **Language Breakdown** - Performance by Hindi/Tamil/Telugu
- **Most Common Errors** - Films most frequently guessed wrong
- **Difficulty Profile** - Distribution of easy/medium/hard films

---

## How to Analyze Data

### Option 1: Analyze Local Data (No Auth Required)
```bash
python3 comprehensive_analysis.py
```
Output: Movie catalog, stumper analysis, data availability

### Option 2: Fetch Live Metrics (Requires ADMIN_KEY)
```bash
python3 fetch_live_metrics.py --key ${ADMIN_KEY} --output metrics.json
```
Output: Complete game statistics in JSON format

### Option 3: Test API Directly
```bash
python3 test_api.py
```
Output: Play sample games, test game flow

---

## API Endpoints Reference

### Public Endpoints
```
GET  /health
     Response: {"status": "ok", "movie_count": 2553}

GET  /movies?language=Hindi
     Response: {"count": 958, "movies": [...]}

GET  /movies/export.csv
     Response: CSV file download

POST /game/start
     Response: {"session_id": "...", "question": {...}, ...}

POST /game/answer
     Body: {"session_id": "...", "question_id": "...", "answer": "yes|no|maybe|dunno"}
     Response: {"phase": "question|guess", "question": {...} or "guesses": [...]}

POST /game/feedback
     Body: {"session_id": "...", "was_correct": true, "correct_movie_id": "..."}
     Response: {"status": "ok"}

POST /game/stumped
     Body: {"session_id": "...", "title": "Film Title"}
     Response: {"status": "ok"}
```

### Admin Endpoints (Require ADMIN_KEY)
```
GET  /admin/games?key=${ADMIN_KEY}
     Response: {"count": N, "entries": [game_records...]}

GET  /admin/stumpers?key=${ADMIN_KEY}
     Response: {"count": N, "entries": [stumper_records...]}

GET  /admin/analyze-stumpers?key=${ADMIN_KEY}&verbose=true
     Response: Detailed stumper analysis with mismatches
```

---

## Next Steps for Complete Analysis

### 1. Obtain Admin Access
Request the `ADMIN_KEY` from the application maintainers to unlock:
- Complete game history
- Live stumper statistics
- Performance trending

### 2. Run Live Metrics
```bash
python3 fetch_live_metrics.py --key <YOUR_KEY> --output report_$(date +%Y%m%d).json
```

### 3. Analyze Results
Review the generated JSON or use tools to visualize:
- Success/stump rates by language
- Question distribution
- Common error patterns

### 4. Schedule Regular Reports
Set up cron job to capture metrics weekly:
```bash
0 9 * * 1 cd ~/indian-movie-genie && python3 fetch_live_metrics.py --key ${ADMIN_KEY} --output reports/metrics_$(date +\%Y\%m\%d).json
```

---

## Troubleshooting

### Can't reach the site?
- Check: https://movie-charades.onrender.com/
- If down, it may be a Render free tier sleep or deployment issue
- Check git logs for recent deployments

### Admin endpoints return 403?
- `ADMIN_KEY` environment variable not set or incorrect
- Request key from project maintainers

### Missing movie in catalog?
- Check `stumpers.jsonl` for "not in catalog" stumpers
- These represent coverage gaps
- Review the `/admin/analyze-stumpers` endpoint for detailed analysis

### High stump rate?
- Check `remaining_candidates` metric
- If high when stumped (e.g., 176 average), questions may not be discriminative enough
- Review mislabeled films via `/admin/analyze-stumpers`

---

## Architecture Overview

```
User Playing Game
       ↓
FastAPI Backend (main.py)
       ↓
GameEngine (engine.py)
       ↓
QUESTIONS (questions.py)
       ↓
Movies Database (2,553 films)
       ↓
Supabase
  ├─ games table (all game outcomes)
  ├─ stumpers table (films AI couldn't guess)
  └─ PostgreSQL storage
```

**Question Flow:**
1. Start session → Load all films
2. Next question → Narrow candidates based on attributes
3. Apply answer → Filter candidates by yes/no/maybe/dunno
4. Repeat until:
   - Remaining candidates ≤ 1 (guess phase)
   - Questions exhausted
   - Player satisfied

---

## Key Performance Indicators (KPIs)

### Primary Metrics
| Metric | Current | Goal | Source |
|--------|---------|------|--------|
| Success Rate | ? | >70% | /admin/games |
| Stump Rate | ? | <5% | /admin/games |
| Avg Questions | 15 (test) | <10 | /admin/games |
| Language Parity | ? | Equal across languages | /admin/games |

### Secondary Metrics
| Metric | Tracks | Collection |
|--------|--------|-----------|
| Remaining Candidates | Filter quality | Game records |
| Wrong Guesses | Confusion pairs | Game records |
| Missing Stumpers | Catalog coverage | /admin/stumpers |
| Mislabeled Films | Data quality | /admin/analyze-stumpers |

---

## Contact & Support

- **Live Site Issues:** Check Render deployment logs
- **Data Questions:** Refer to GAME_ANALYSIS_REPORT.md
- **API Integration:** Review backend/main.py for implementation details
- **Admin Access:** Request ADMIN_KEY from project owner

---

*Last updated: 2026-06-17*  
*Data freshness: Local stumpers (3), Movie catalog (2,553), Live games (in Supabase)*
