# March Machine Learning Mania 2026 — Competition Research

## Competition Overview

- **Name**: March Machine Learning Mania 2026 (Kaggle, 12th annual)
- **Goal**: Predict probability of every possible NCAA tournament matchup (Men's + Women's)
- **Prize Pool**: $50,000
- **Final Submission Deadline**: March 19, 2026
- **Tournament Play**: March 21 – April 8, 2026
- **Results Finalized**: ~April 10, 2026
- **Evaluation Metric**: Brier Score (MSE between predicted probabilities and actual 0/1 outcomes)
- **Submissions Scored**: Must select 2 submissions for final scoring

## Submission Format

- CSV with two columns: `ID` and `Pred`
- `ID` format: `2026_TeamIdLow_TeamIdHigh`
- `Pred` = P(lower TeamID beats higher TeamID)
- Men's TeamIDs: 1000–1999
- Women's TeamIDs: 3000–3999
- Must predict every possible pairing (not bracket-style — you can't "bust")

## Two Stages

- **Stage 1**: Sample submission contains 2022–2025 matchups for validation/testing
- **Stage 2**: Contains all 2026 tournament matchups for actual scoring

## Competition Variants

- Main competition (Brier score)
- Semi Spherical Scoring variant
- Logistic Brier variant

---

## Available Data (~35 CSV Files)

Files prefixed with `M` (men's) and `W` (women's).

### Core Reference Files

| File | Description |
|---|---|
| `MTeams.csv` / `WTeams.csv` | Team lookup — TeamID, TeamName, FirstD1Season, LastD1Season |
| `MSeasons.csv` / `WSeasons.csv` | Season info — DayZero reference date, region names (W/X/Y/Z) |
| `Conferences.csv` | Conference abbreviations and full names |
| `MTeamConferences.csv` / `WTeamConferences.csv` | Team-to-conference mapping by season |

### Game Results

| File | Key Columns |
|---|---|
| `MRegularSeasonCompactResults.csv` | Season, DayNum, WTeamID, LTeamID, WScore, LScore, WLoc, NumOT |
| `MRegularSeasonDetailedResults.csv` | All compact columns + box score stats |
| `MNCAATourneyCompactResults.csv` | Same structure as regular season compact |
| `MNCAATourneyDetailedResults.csv` | Same structure as regular season detailed |

### Detailed Box Score Columns (for DetailedResults files)

For both winning (W) and losing (L) teams:
- `FGM/FGA` — Field goals made/attempted
- `FGM3/FGA3` — Three-pointers made/attempted
- `FTM/FTA` — Free throws made/attempted
- `OR/DR` — Offensive/defensive rebounds
- `Ast` — Assists
- `TO` — Turnovers
- `Stl` — Steals
- `Blk` — Blocks
- `PF` — Personal fouls

### Tournament Structure

| File | Description |
|---|---|
| `MNCAATourneySeeds.csv` | Season, Seed (e.g. "W01" = West #1), TeamID |
| `MNCAATourneySlots.csv` | Bracket structure and advancement paths |

### Geography

| File | Description |
|---|---|
| `Cities.csv` | CityID, City, State, Latitude, Longitude |
| `MGameCities.csv` / `WGameCities.csv` | Links games to locations |

### Rankings & Coaching

| File | Description |
|---|---|
| `MMasseyOrdinals.csv` | Public ranking systems (Pomeroy, Sagarin, RPI, ESPN, etc.) — SystemName, RankingDayNum, TeamID, OrdinalRank. Men's only, 2003+ |
| `MTeamCoaches.csv` / `WTeamCoaches.csv` | CoachName, tenure period per season |

---

## How Basketball Has Changed (Modeling Implications)

### The Three-Point Revolution

- 3-pointers now ~40% of all shot attempts (up from 22% in 2001-02). 24-season high of 39.5% this year.
- Accuracy stable at 33-35% (34.1% this year). Volume exploded, not accuracy.
- 3s = 29.8% of all made shots, up from ~25% in 2002-03.
- Alabama: most 3s and 3-point attempts of any team in last 4 seasons (3,436 attempts).

**Modeling implication**: Models trained on older data may be biased. Weight recent seasons more heavily or use time-windowed features.

### Championship Paradox

- Only 18.4% of Final Four teams had 3s at this year's proportion of made shots
- Only 13.8% of Final Four teams took as many 3s as current average
- Only 10% of champions exceeded 45% three-point attempt rate
- Efficiency > volume for deep tournament runs

**Modeling implication**: Raw 3-point volume isn't predictive of deep runs. Efficiency metrics (eFG%, defensive efficiency) matter more.

### Transfer Portal Era

- ~2,000 players enter the portal annually
- 2026 portal window: April 7–21 (new 15-day window)
- Creates more parity, less year-over-year predictability
- Team identity less stable than ever

**Modeling implication**: Historical team performance less reliable. Current-season metrics and player-level data increasingly important.

### Defense-First Anomalies

Florida 2026: KenPom #4 defense, leads nation in rebounding (45.5/game), but 316th in 3-point shooting (31.25%). Old-school style is now an anomaly.

---

## Key Analytical Findings

### Feature Importance (What Predicts Wins)

Top 6 predictive features from past solutions:
1. **Winning percentage** (+ opponent WP, opponent-of-opponent WP = strength of schedule)
2. **Offensive efficiency** (points per possession)
3. **Defensive efficiency** (points allowed per possession)
4. **Effective field goal percentage (eFG%)** — adjusts for 3-point value
5. **Seed** — strongest single predictor, but non-linear
6. **Elo ratings** — correlate 0.841 with seed (captures distinct information)

### The 11-Seed Anomaly

- 11 seeds consistently outperform expectations, winning more games than 9 or 10 seeds
- Cinderella 11-seeds that make deep runs typically have Elo ranking inside top 20
- Well-documented pattern models should account for

### Seed Performance Cliffs

- Massive dropoff from 1→2 seeds (over a full round difference)
- Significant cliffs at 3→4 and 4→5 (~half a round each)
- 16 seeds almost never win (1 upset in history: UMBC over Virginia 2018)
- 1 seeds: 26 national championships (~2x all other seeds combined)
- Performance decline is NON-LINEAR

### Derived Efficiency Metrics

- **Possessions** = standardize team activity levels
- **Offensive/defensive efficiency** = points per possession
- **eFG%** = adjusts FG% for 3-point value
- **Turnover %** = ball security per possession
- **Offensive rebound %** and **free throw rate**

---

## Winning Strategies from Past Competitors

| Approach | Details |
|---|---|
| Bradley-Terry models | Popular baseline — pairwise team strength |
| Logistic regression on strength diff | Build team strength from win% + point differential, predict P(low beats high) |
| Neural networks | 4-layer networks w/ KenPom + HeatCheck stats, ~204 input features |
| Ensembles | Top competitors ensemble multiple model types |
| Data augmentation | Each game as (A,B,Win) AND (B,A,Loss) to double data, reduce bias |
| External data | KenPom, Sagarin, ESPN BPI supplement Kaggle data significantly |

### The Role of Luck

2014 winners Matthews & Lopez published a paper showing luck plays a significant role. Practical takeaway: "Take a model, tweak it a bit to generate some distance from the field, and you are competitive to win."

### Brier Score Strategy

- Predicting 0.5 everywhere = safe but uncompetitive
- Being confidently wrong = heavily penalized (quadratic loss)
- Optimal strategy = well-calibrated probabilities, not extreme predictions
- Slight deviations toward upsets can differentiate from the field

---

## External Data Sources Used by Top Competitors

- **KenPom** (kenpom.com) — adjusted efficiency, tempo, luck, SOS
- **Sagarin ratings**
- **ESPN BPI**
- **HeatCheck** — advanced analytics
- **Massey ordinals** (provided in competition data)
- **WAB (Wins Above Bubble)**
- **RPI**

---

## Key Modeling Decisions

1. **Recency weighting** — weight recent seasons more due to game evolution + portal parity
2. **Efficiency over volume** — eFG%, off/def efficiency per possession > raw scoring
3. **Seed + Elo combined** — each captures distinct info (0.841 correlation)
4. **Account for 11-seed anomaly**
5. **External data** — KenPom/Massey used by virtually all competitive entries
6. **Calibrate probabilities** — Brier score rewards calibration, not accuracy
7. **Feature differences** — compute stat differences between paired teams, not raw stats
