# Labeling Standards & Consistency Framework

**Status:** Audit complete. Critical inconsistencies identified. Framework ready for standardization.

---

## Problem Statement

**5 critical labeling inconsistencies across 2,649 films:**

| Attribute | Hindi | Tamil | Telugu | Gap | Root Cause |
|-----------|-------|-------|--------|-----|-----------|
| `has_comedy` | 42.7% | 61.9% | 78.4% | **35.8%** | Definition inconsistency: What counts as "comedy"? |
| `has_thriller_elements` | 41.0% | 41.0% | 19.0% | **22.0%** | Telugu under-tagged for thriller elements |
| `is_family_film` | 30.6% | 32.5% | 50.2% | **19.6%** | Telugu over-tagged for "family-friendly" |
| `has_class_conflict` | 31.6% | 47.3% | 48.9% | **17.3%** | Hindi under-tagged for social themes |
| `has_romance` | 78.8% | 89.0% | 94.8% | **16.0%** | Hindi under-tagged for romance elements |

**Impact:**
- Game learns **language-dependent biases** instead of film characteristics
- Questions have **variable accuracy** across languages
- **Can't reliably compare** films across Hindi/Tamil/Telugu

---

## Solution: Labeling Standardization

### Phase 1: Define Standards (This Document)

#### Attribute: `has_comedy`

**Definition (across all languages):**
> A film is tagged `has_comedy` if:
> - Comedy is a **primary genre** (not secondary)
> - OR **>20% of runtime** features comedic scenes/dialogue
> - OR comedy is a **core plot element** (e.g., protagonist is a comedian)
>
> **Exclude:** Drama with comedic moments, dark comedy, sarcasm

**Examples:**
- ✅ Andaz Apna Apna (Hindi) - Comedy is primary genre
- ✅ Pizza (Tamil) - Sustained comedic narrative
- ✅ Pelli Choopulu (Telugu) - Comedy-driven romance
- ❌ Dilwale Dulhania (Hindi) - Drama with comedic scenes, not primary
- ❌ Drishyam (Tamil) - Thriller with one-liners, not comedy
- ❌ Arjun Reddy (Telugu) - Dark situations with dark humor, not comedy

**Target Coverage:** 50-55% across all languages (currently 42-78% spread)

---

#### Attribute: `has_thriller_elements`

**Definition:**
> A film is tagged if:
> - **Suspense/mystery** is a core narrative driver
> - OR **plot hinges** on uncertainty of outcome
> - OR **protagonist faces time-pressure** (heist, bomb, etc.)
>
> **Include:** Crime, mystery, psychological suspense, heists
> **Exclude:** Action films without suspense, revenge without mystery

**Examples:**
- ✅ Rang De Basanti (Hindi) - Heist-like plan, suspense
- ✅ Drishyam (Tamil) - Mystery/suspense-driven
- ✅ Arjun Reddy (Telugu) - Emotional suspense, uncertain outcome
- ❌ Pushpa (Telugu) - Smuggling + action, but not suspense-focused
- ❌ Kabali (Tamil) - Action-driven, not suspense

**Target Coverage:** 38-42% across all languages (currently 19-41% spread)

---

#### Attribute: `is_family_film`

**Definition:**
> A film is tagged if:
> - **Suitable for all ages** (no explicit violence/sex/language)
> - AND **family themes** (relationships, values, bonding)
> - OR **explicitly aimed** at multi-generational audiences
>
> **Exclude:** Films with violence even if "rated" family
> **Include:** Family dramas, parent-child stories, wedding films

**Examples:**
- ✅ DDLJ (Hindi) - Romance + family values, no explicit content
- ✅ Jai Bheem (Tamil) - Social drama, family values
- ✅ Chandramukhi (Telugu) - Entertainment + family suitable
- ❌ Arjun Reddy (Telugu) - Violence and sexual content
- ❌ Eega (Tamil) - Revenge violence

**Target Coverage:** 32-35% across all languages (currently 31-50% spread)

---

#### Attribute: `has_class_conflict`

**Definition:**
> A film is tagged if:
> - **Central theme** involves class/caste/economic inequality
> - OR **plot driven** by class differences (e.g., family opposes romance due to class)
> - OR **social message** explicitly addresses class systems
>
> **Exclude:** Plots where class is backdrop but not central
> **Include:** Class romance, caste politics, wealth vs poverty conflicts

**Examples:**
- ✅ Lagaan (Hindi) - Class conflict central to narrative
- ✅ Jai Bheem (Tamil) - Caste oppression central
- ✅ Arjun Reddy (Telugu) - Class-based family opposition to romance
- ❌ DDLJ (Hindi) - Class backdrop but romance is central
- ❌ Kabali (Tamil) - Underworld conflict, not class-based

**Target Coverage:** 40-45% across all languages (currently 32-49% spread)

---

#### Attribute: `has_romance`

**Definition:**
> A film is tagged if:
> - **Romance subplot** exists (not just one-sided attraction)
> - OR **romantic elements** are meaningful to character/plot
> - OR **love story** is a primary or secondary arc
>
> **Exclude:** Pure action, no relationship development
> **Include:** Romance-driven or romance-supported narratives

**Examples:**
- ✅ Most Hindi films tagged (reasonable - Bollywood tradition)
- ✅ Most Tamil films tagged (reasonable - Tamil cinema tradition)
- ✅ Telugu films should align (currently under-tagged at 95%)

**Target Coverage:** 85-90% across all languages (currently 79-95% spread)

---

### Phase 2: Implement Standards

**Scope:** Re-tag 2,649 films

**Process:**
1. **Sample validation** (50 films per language per attribute)
   - 3 people tag independently
   - Compare results (target: 90%+ agreement)
   - Refine standard if <90%

2. **Full re-tagging** (batch by language)
   - Week 1: Hindi re-tag (987 films)
   - Week 2: Tamil re-tag (840 films)
   - Week 3: Telugu re-tag (769 films)

3. **Verification** (QA pass)
   - Spot-check 100 random films
   - Verify consistency across languages
   - Check before/after gap reduction

---

### Phase 3: Deploy

After standardization:
- Deploy Phase 1-2 enhancements (confirmed safe)
- Deploy Phase 3 Rule 1 (already verified)
- Expand with confidence

**Expected outcome:** 
- Win rate: 50%+ (consistent across languages)
- Questions work equally for all languages
- Can reliably compare films across languages

---

## Implementation Roadmap

### Option A: Conservative (Current Plan)
- Skip standardization for now
- Deploy Phase 1-2 only
- Accept labeling inconsistencies as technical debt
- **Timeline:** 1 day
- **Win rate:** 45-50%
- **Risk:** Inconsistencies affect future development

### Option B: Full Standardization (Recommended)
- Standardize all 5 problematic attributes
- Re-tag 2,649 films
- Deploy Phase 1-2 + verified Phase 3
- **Timeline:** 3-4 weeks
- **Win rate:** 50%+ consistent
- **Risk:** None (fixes root cause)

### Option C: Partial Standardization (Middle Ground)
- Standardize top 2 critical attributes (`has_comedy`, `has_thriller_elements`)
- Spot-check Hindi/Tamil consistency
- Deploy Phase 1-2 with limited Phase 3
- **Timeline:** 1 week
- **Win rate:** 45-50% with less technical debt
- **Risk:** Other inconsistencies remain

---

## Recommendation

**Go with Option B (Full Standardization)** because:

1. **Systemic Problem:** 5 attributes with 15%+ gaps won't go away
2. **Foundation Quality:** Building features on inconsistent data leads to problems later
3. **Long-term:** Any future enhancements (more languages, new questions) will compound issues
4. **Effort:** 3-4 weeks now vs. 10+ weeks of fixing later (e.g., "why does the game favor Telugu films?")

**Timeline:**
- **Week 1:** Sample validation of 5 attributes (3 people, 50 films each)
- **Week 2-4:** Full re-tagging (divide 2,600 films by 3 people)
- **Week 5:** Verification + deploy Phase 1-2

**Total effort:** ~200 hours (assuming 3 people, 4 hours/day)

---

## Success Criteria

✅ **Labeling standardization complete if:**
- 90%+ agreement on sample validation across all 3 attributes
- Re-tagged films show <5% variance across languages
- `has_comedy`: 50-55% coverage across all languages
- `has_thriller_elements`: 38-42% coverage across all languages
- `is_family_film`: 32-35% coverage across all languages
- `has_class_conflict`: 40-45% coverage across all languages
- `has_romance`: 85-90% coverage across all languages

---

**Prepared:** 2026-06-17  
**Status:** Framework ready. Awaiting decision on Option A/B/C.
