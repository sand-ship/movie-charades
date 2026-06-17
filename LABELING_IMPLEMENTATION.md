# Labeling Standardization Implementation Plan

**Status:** Ready to execute  
**Timeline:** 4 weeks  
**Team:** 1-3 people  
**Deliverable:** Consistently labeled 2,649 films across Hindi/Tamil/Telugu

---

## Week 1: Sample Validation & Standard Refinement

### Goal
Validate that standards are **unambiguous** and **achievable** (90%+ tagger agreement)

### Deliverables
1. **Sample set:** 50 films per language × 3 attributes = 450 films total
2. **Tagger agreement results:** 90%+ on all 5 attributes
3. **Refined standards:** Any clarifications needed based on disagreements

### Process

**Day 1-2: Create Sample Sets**
```bash
# Identify 50 films per language (stratified by rating/year)
- 10 films rated 5.0-6.5
- 15 films rated 6.5-7.5
- 15 films rated 7.5-8.5
- 10 films rated 8.5+

For each language: Hindi (50), Tamil (50), Telugu (50)
Total: 150 films to validate
```

**Day 3-4: Independent Tagging**
- **Person A:** Tags all 150 films on 5 attributes
- **Person B:** Tags same 150 films independently
- **Person C:** Tags same 150 films independently

Use this template:
```json
{
  "title": "Film Name",
  "language": "hindi",
  "tagger": "Person A",
  "has_comedy": true/false,
  "has_thriller_elements": true/false,
  "is_family_film": true/false,
  "has_class_conflict": true/false,
  "has_romance": true/false,
  "reasoning": "Why I tagged it this way (1-2 sentences)"
}
```

**Day 5: Agreement Analysis**
- Calculate agreement % per attribute per language
- If <90%: Identify disagreements, refine standard
- If 90%+: Standard is ready for full tagging

### Success Criteria
✅ 90%+ agreement on `has_comedy`  
✅ 90%+ agreement on `has_thriller_elements`  
✅ 90%+ agreement on `is_family_film`  
✅ 90%+ agreement on `has_class_conflict`  
✅ 90%+ agreement on `has_romance`

---

## Week 2: Hindi Re-tagging (987 films)

### Division of Labor
- **Person A:** 330 films
- **Person B:** 330 films
- **Person C:** 327 films

### Process
1. **Divide films by rating quartile** (ensure balanced)
2. **Use standardized tagging form** (from Week 1)
3. **Track progress daily** (aim: 50-80 films/day per person)
4. **Weekly spot-check:** Random 10 films, independent re-verify

### Output
- CSV with 987 Hindi films + 5 attributes each
- Tagging reasoning (sample: 10%)

### Deadline
End of Week 2: All 987 Hindi films tagged

---

## Week 3: Tamil Re-tagging (840 films)

### Same process as Week 2
- **Person A:** 280 films
- **Person B:** 280 films
- **Person C:** 280 films

### Parallel Validation
- Week 2 Hindi films undergoing initial QA
- Week 3 Tamil tagging proceeds

### Deadline
End of Week 3: All 840 Tamil films tagged

---

## Week 4: Telugu Re-tagging (769 films)

### Same process, final language
- **Person A:** 256 films
- **Person B:** 256 films
- **Person C:** 257 films

### Parallel QA
- Week 3 Tamil films undergoing final QA
- Week 4 Telugu tagging proceeds

### Deadline
End of Week 4: All 769 Telugu films tagged

---

## Week 5: Verification & Deployment

### Phase 5A: QA Pass (Days 1-3)

**Spot-check verification:**
```
- 100 random films across all languages (33/33/34)
- 2 independent people re-verify
- Must match original tagging 95%+
```

**Coverage gap check:**
```
Check target ranges:
- has_comedy: 50-55% per language
- has_thriller_elements: 38-42% per language
- is_family_film: 32-35% per language
- has_class_conflict: 40-45% per language
- has_romance: 85-90% per language
```

**Consistency check:**
```
For each attribute, calculate:
  gap = max(H%, T%, Te%) - min(H%, T%, Te%)
  
Success if gap < 5% for all attributes
```

### Phase 5B: Migrate to Database (Day 4)

```bash
# Backup current data
cp backend/data/movies.json backend/data/movies.json.pre-standardization.20260701

# Load new tags
python3 scripts/migrate_standardized_labels.py

# Verify
python3 -c "
import json
movies = json.load(open('backend/data/movies.json'))
hindi = [m for m in movies if m['language']=='hindi']
tamil = [m for m in movies if m['language']=='tamil']
telugu = [m for m in movies if m['language']=='telugu']

print('Hindi has_comedy:', sum(1 for m in hindi if m.get('has_comedy'))/len(hindi))
print('Tamil has_comedy:', sum(1 for m in tamil if m.get('has_comedy'))/len(tamil))
print('Telugu has_comedy:', sum(1 for m in telugu if m.get('has_comedy'))/len(telugu))
"

# Should show <5% variance
```

### Phase 5C: Deploy (Day 5)

```bash
# Commit standardized labels
git add backend/data/movies.json
git commit -m "Apply standardized labeling across all 2,649 films"

# Deploy Phase 1-2 enhancements
git cherry-pick c0d7a88 25e06a6  # Phase 1 & 2 commits

# Deploy to production
git push origin main
```

### Deployment Success Criteria
✅ Backend starts without errors  
✅ All 70 questions load correctly  
✅ Games 31-41 show improvement  
✅ Win rate improves to 45%+ within 50 games  
✅ No language bias in results  

---

## Tools & Templates

### Tagging Template (JSON)
```json
{
  "film_id": "hindi_dilwale_1989",
  "title": "Dilwale Dulhania Le Jayenge",
  "language": "hindi",
  "year": 1995,
  "tagger": "Person A",
  "date": "2026-07-01",
  "tags": {
    "has_comedy": false,
    "has_thriller_elements": false,
    "is_family_film": true,
    "has_class_conflict": true,
    "has_romance": true
  },
  "reasoning": {
    "has_comedy": "No - serious romance and class drama, occasional comedic moments but not primary",
    "has_thriller_elements": "No - romance/drama focus, no suspense or mystery elements",
    "is_family_film": "Yes - all-ages appropriate, family values and wedding themes",
    "has_class_conflict": "Yes - central conflict is NRI family vs Indian girl from middle class",
    "has_romance": "Yes - primary plot is romance across class lines"
  }
}
```

### Daily Progress Tracker
```csv
Date,Person,Language,Films_Tagged,Total_Progress,Comments
2026-07-01,Person A,Hindi,60,60,Sampled 5 random films - 100% agreement
2026-07-02,Person B,Hindi,55,115,Some ambiguity on 'family_film' - discussed clarification
2026-07-02,Person C,Hindi,58,173,Standard is clear and consistent
```

### QA Checklist
```
□ Sample validation: 90%+ agreement on all 5 attributes
□ Hindi re-tagging: 987 films complete
□ Tamil re-tagging: 840 films complete
□ Telugu re-tagging: 769 films complete
□ Spot-check QA: 100 random films, 95%+ match
□ Coverage verification: All attributes in target range
□ Consistency check: <5% variance across languages
□ Database migration: Successful backup + load
□ Deployment: Phase 1-2 merged and deployed
□ Post-deployment: Win rate 45%+ on first 50 games
□ No language bias: Equal performance across languages
```

---

## Risk Mitigation

### Risk: Tagger Fatigue
**Mitigation:**
- Limit to 50-80 films/day per person
- Rotate between languages daily
- Weekly breaks every Friday

### Risk: Disagreements on Standards
**Mitigation:**
- Week 1 validation catches this early
- Weekly sync-ups to discuss edge cases
- Documented decision log

### Risk: Data Corruption During Migration
**Mitigation:**
- Full backup before migration
- Verify 1% of data post-migration
- Keep backup for 2 weeks post-deploy

### Risk: Regression in Game Performance
**Mitigation:**
- Deploy Phase 1-2 first (known-good)
- Monitor first 50 games carefully
- Rollback available (git reset --hard pre-standardization)

---

## Success Metrics

**After Standardization:**

| Metric | Target | Current | Improvement |
|--------|--------|---------|-------------|
| `has_comedy` variance | <5% | 35.8% | ✅ |
| `has_thriller_elements` variance | <5% | 22.0% | ✅ |
| `is_family_film` variance | <5% | 19.6% | ✅ |
| `has_class_conflict` variance | <5% | 17.3% | ✅ |
| `has_romance` variance | <5% | 16.0% | ✅ |
| **Win rate (Phase 1-2)** | 45-50% | 17.1% | ✅ +28-33% |
| **Language bias** | None | High | ✅ |
| **Tagger agreement** | 90%+ | N/A | ✅ |

---

## Timeline Summary

```
Week 1 (Jun 24-28): Sample validation + refinement
  ├─ Day 1-2: Prepare 150 sample films
  ├─ Day 3-4: Independent tagging (3 people)
  └─ Day 5: Agreement analysis, refine standards

Week 2 (Jul 1-5): Hindi re-tagging (987 films)
  ├─ Days 1-4: Tagging sprint (50-80 films/day per person)
  └─ Day 5: Spot-check + QA start

Week 3 (Jul 8-12): Tamil re-tagging (840 films)
  ├─ Days 1-4: Tagging sprint
  ├─ Day 5: Spot-check + Hindi QA continues
  └─ Parallel: Hindi QA in progress

Week 4 (Jul 15-19): Telugu re-tagging (769 films)
  ├─ Days 1-4: Tagging sprint
  ├─ Day 5: Spot-check + Tamil QA continues
  └─ Parallel: Tamil QA in progress

Week 5 (Jul 22-26): Verification + Deployment
  ├─ Days 1-3: Final QA (100 films, coverage check)
  ├─ Day 4: Database migration + verification
  ├─ Day 5: Deploy Phase 1-2
  └─ Post-deploy: Monitor first 50 games
```

---

## Handoff Document

**For the team executing this:**

1. **Read:** LABELING_STANDARDS.md (definitions & examples)
2. **Validate:** Week 1 sample validation (test standards)
3. **Execute:** Weeks 2-4 tagging sprints (987+840+769 films)
4. **Verify:** Week 5 QA & deployment
5. **Monitor:** First 50 games post-deploy

**Critical Files:**
- `LABELING_STANDARDS.md` — Reference definitions
- `LABELING_IMPLEMENTATION.md` — This document
- Template JSON — Use for each film
- Daily tracker — Maintain progress
- QA checklist — Sign off on each phase

---

**Prepared by:** Claude  
**Date:** 2026-06-17  
**Status:** Ready to execute  
**Estimated effort:** 200 person-hours (with 3 people: ~4 weeks)
