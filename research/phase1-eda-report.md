# Phase 1: Exploratory Data Analysis - Report

## Data Inventory

### Kaggle Competition Data (35 CSVs, ~35MB)
- **Zero missing values** across all files
- Men's compact results: 198,577 games (1985-2026)
- Men's detailed results: 124,529 games (2003-2026) - 34 columns with full box scores
- Women's compact: 142,507 games (1998-2026)
- Women's detailed: 87,187 games (2010-2026)
- Tournament seeds: 2,694 entries (1985-2026), 68 men's teams seeded for 2026
- Massey Ordinals: 5.87M rows - 50+ ranking systems, men's only, 2003+
- Team spellings file: 1,178 alternate names for joining external data

### External Data (66 CSVs)
- **Sundberg** (15 files): ADJOE, ADJDE, BARTHAG, WAB, four factors. Per-season 2013-2026, all 365 D1 teams
- **Amin** (38 files): KenPom + Barttorvik (103 cols), EvanMiya, Heat Check, resumes (ELO, NET, quad wins), tournament matchups/simulations. Tournament teams only.
- **Pilafas** (13 files): KenPom efficiency/defense/offense/height/coaching, 179 cols in master file. 2002-2026.

### Data Quality
- All 101 files parse correctly, no corrupted data
- Security scan: clean (no formula injection, SQL injection, binary payloads, XSS)
- Licensing: CC0 Public Domain (Sundberg, Amin), MIT (Pilafas), competition rules (Kaggle)
- External data explicitly encouraged by competition rules

### Team Name Mapping
- 96% of external names match Kaggle spellings automatically
- 13 names need manual mapping (abbreviation differences like "St." vs "State")
- Kaggle uses numeric TeamIDs (1000-1999 men's, 3000-3999 women's)
- External data uses team name strings - joined via MTeamSpellings.csv

---

## Scoring Trends

| Season | Avg Total Score | Avg Margin | Avg Winner | OT% |
|--------|----------------|------------|------------|-----|
| 2016 | 144.6 | 12.0 | 78.3 | 6.2% |
| 2020 | 140.4 | 11.9 | 76.2 | 5.6% |
| 2024 | 145.2 | 12.1 | 78.6 | 6.0% |
| 2025 | 145.6 | 12.2 | 78.9 | 5.6% |
| **2026** | **149.4** | **12.4** | **80.9** | **5.6%** |

2026 has the **highest average total score in the dataset**. Steady upward trend since 2015.

---

## Three-Point Shooting Evolution

| Season | 3PA/game | 3PA as % of all shots | 3PT accuracy |
|--------|----------|----------------------|-------------|
| 2003 | 36.1 | 32.3% | 34.6% |
| 2010 | 36.1 | 32.7% | 33.9% |
| 2016 | 40.8 | 35.4% | 34.5% |
| 2020 | 43.1 | 37.6% | 33.2% |
| 2025 | 45.3 | 39.1% | 33.7% |
| **2026** | **46.0** | **39.5%** | **33.8%** |

**Key insight**: Volume has exploded (32% -> 40% of all shots), but accuracy is flat at ~34%. This means models trained on older data will underweight 3-point volume.

**Modeling implication**: Weight recent seasons more heavily. Consider time-windowed features.

---

## Pace / Tempo

Estimated possessions per game (both teams combined):
- 2003: 138.2
- 2012: 133.4 (low point)
- 2016: 139.5 (jumped after rule changes)
- 2026: 139.9

Pace is relatively stable at ~139-140 since 2016. Not a major trend to account for.

---

## Tournament Seed Performance (1985-2025)

| Seed | Win% | Avg Wins/Tourney | Championships |
|------|------|-----------------|---------------|
| 1 | 79.9% | 13.35 | 26 |
| 2 | 70.6% | 9.32 | 5 |
| 3 | 65.3% | 7.35 | 4 |
| 4 | 61.3% | 6.25 | 2 |
| 5 | 53.4% | 4.58 | 0 |
| 6 | 51.4% | 4.20 | 0 |
| 7 | 47.0% | 3.52 | 1 |
| 8 | 41.5% | 2.82 | 1 |
| 9 | 38.0% | 2.45 | 0 |
| 10 | 38.1% | 2.48 | 0 |
| **11** | **41.0%** | **3.12** | **0** |
| 12 | 34.1% | 2.12 | 0 |
| 13 | 19.9% | 1.00 | 0 |
| 14 | 13.9% | 0.65 | 0 |
| 15 | 9.1% | 0.40 | 0 |
| 16 | 16.8% | 1.00 | 0 |

### Key Patterns
- **1-seed dominance**: 26 of 40 championships (~65%)
- **Massive 1->2 cliff**: 80% -> 71% win rate
- **Significant cliffs at 3->4 and 4->5**: ~half a round each
- **8v9 is a coin flip**: 52.5% upset rate
- **11-seed anomaly CONFIRMED**: 41.0% win rate, higher than seeds 9 (38.0%) and 10 (38.1%)

### First Round Upset Rates

| Matchup | Upset Rate |
|---------|-----------|
| 1v16 | 1.3% |
| 2v15 | 7.0% |
| 3v14 | 13.9% |
| 4v13 | 20.3% |
| 5v12 | 36.1% |
| 6v11 | 38.6% |
| 7v10 | 38.6% |
| 8v9 | 52.5% |

---

## 2026 Tournament Bracket (68 teams)

### 1-seeds: Duke, Florida, Michigan, Arizona
### 2-seeds: Connecticut, Houston, Iowa St, Purdue
### 3-seeds: Michigan St, Illinois, Virginia, Gonzaga
### 4-seeds: Kansas, Nebraska, Alabama, Arkansas

### Notable injuries (for final prediction adjustments):
- Duke: Caleb Foster (broken foot) - likely out
- BYU: Richie Saunders (knee) - season-ending
- Louisville: Mikel Brown Jr. (back) - out first weekend
- Gonzaga: Braden Huff (knee) - out since January
- UNC: Caleb Wilson (hand) - season-ending

---

## Collinearity Analysis

### Redundant Feature Groups (r > 0.9)

| Group | Redundant Features | Recommended Pick |
|-------|-------------------|-----------------|
| Overall strength | KADJ EM, BADJ EM, BARTHAG, WAB | KADJ EM |
| Offense | KADJ O, BADJ O, K OFF, PPPO, AdjOE | KADJ O |
| Defense | KADJ D, BADJ D, K DEF, PPPD, AdjDE | KADJ D |
| Tempo | K TEMPO, KADJ T, RAW T, BADJ T | KADJ T |
| Shooting | EFG%, eFGPct, 2PT% | EFG% |
| Free throws | FTM <-> FTA (r=0.93) | FTRate |

### VIF Analysis (Sundberg data)
- CRITICAL (VIF > 10): EFG_O (324), EFG_D (324), 2P_O (92), 2P_D (164), 3P_O (39), 3P_D (66), BARTHAG (33), ADJOE (31), ADJDE (23), WAB (16)
- SAFE (VIF < 5): TOR (2.8), ORB (2.7), TORD (2.8), DRB (2.3), FTRD (1.6), FTR (1.3), ADJ_T (1.2)

### Strategy by Model Type
- **XGBoost/LightGBM**: Can include all features - trees handle collinearity naturally
- **Logistic regression**: One feature per group, VIF < 5
- **Neural net**: PCA or curated feature set to decorrelate

---

## Submission Requirements
- 132,133 total matchups (66,430 men's + 65,703 women's)
- Format: CSV with `ID` (2026_TeamLow_TeamHigh) and `Pred` (probability)
- All 365 men's teams and 363 women's teams must have predictions
- Evaluated on **Brier score** (lower = better)
- Must select 2 submissions for final scoring
