# Phase 2: Feature Engineering - Report

## Pipeline Overview

Built a modular feature engineering pipeline in `src/features/` with the following modules:
- `elo.py` - Custom Elo rating system
- `efficiency.py` - Per-possession efficiency metrics from box scores
- `seeds.py` - Tournament seed features with nonlinear transforms
- `strength_of_schedule.py` - Multi-level SOS (WP, OWP, OOWP)
- `build_features.py` - Orchestrator that merges everything + external data

---

## Features Built (57 total per team-season)

### Elo Ratings (2 features)
| Feature | Description |
|---------|-------------|
| Elo | End-of-season Elo rating |
| EloPreTourney | Elo rating at end of regular season (before tournament games) |

**Parameters**: K=20, home advantage=100, initial=1500, season carryover=0.75, margin-of-victory weighting enabled.

### Efficiency Metrics (21 features, from detailed box scores)
| Feature | Description |
|---------|-------------|
| OffEff | Points per 100 possessions (offense) |
| DefEff | Points per 100 possessions (defense) |
| NetEff | Offensive - defensive efficiency |
| Tempo | Estimated possessions per game |
| eFGPct | Effective FG% = (FGM + 0.5 * FGM3) / FGA |
| TOPct | Turnover % = TO / possessions |
| ORBPct | Offensive rebound % = ORB / (ORB + Opp DRB) |
| FTRate | Free throw rate = FTA / FGA |
| OppeFGPct | Opponent effective FG% |
| OppTOPct | Opponent turnover % |
| DRBPct | Defensive rebound % |
| OppFTRate | Opponent free throw rate |
| FGPct, FG3Pct, FTPct | Raw shooting percentages |
| FG3Rate | 3PA / FGA (three-point attempt rate) |
| AstRate | Assists / FGM |
| StlRate, BlkRate | Steals and blocks per game |
| Games, Wins, WinPct | Basic record |
| PointsPerGame, OppPointsPerGame, PointDiff | Scoring |

### Strength of Schedule (4 features)
| Feature | Description |
|---------|-------------|
| WP | Team winning percentage |
| OWP | Average opponent winning percentage |
| OOWP | Average opponent's opponent WP |
| SOS | RPI-style composite: 0.25*WP + 0.50*OWP + 0.25*OOWP |

### Seed Features (8 features, tournament teams only)
| Feature | Description |
|---------|-------------|
| SeedNum | Raw seed number (1-16) |
| SeedLog | log(seed + 1) |
| SeedSq | seed^2 |
| SeedInv | 1/seed |
| SeedHistWinPct | Historical win rate for that seed |
| PlayIn | Boolean - is this a play-in team? |
| Seed | Raw seed string (e.g. "W01") |
| Region | Tournament region (W/X/Y/Z) |

### Coach Features (3 features)
| Feature | Description |
|---------|-------------|
| CoachSeasonsExp | Number of prior seasons as head coach |
| CoachTourneyApps | Prior tournament appearances |
| CoachTourneyWins | Prior tournament game wins |

### External / Sundberg Features (13 features, 2013-2026 only)
| Feature | Description |
|---------|-------------|
| ADJOE | Adjusted offensive efficiency (Barttorvik) |
| ADJDE | Adjusted defensive efficiency (Barttorvik) |
| BARTHAG | Win probability metric (Barttorvik) |
| TOR | Turnover rate |
| TORD | Opponent turnover rate |
| ORB | Offensive rebound % |
| DRB | Defensive rebound % |
| FTR | Free throw rate |
| FTRD | Opponent free throw rate |
| 3P_O | 3-point shooting % (offense) |
| 3P_D | 3-point shooting % (defense) |
| ADJ_T | Adjusted tempo |
| WAB | Wins above bubble |

---

## Output Files

### team_features.parquet
- **Shape**: 12,748 rows x 57 columns
- **Coverage**: 2003-2026, ~361 teams per season
- **Missing data**:
  - Core features (Elo, efficiency, SOS, coach): < 3% missing
  - Seed features: 81.6% missing (expected - only 68 tournament teams per year)
  - Sundberg features: 30.5% missing (data starts 2013, not all names matched)

### training_matchups.parquet
- **Shape**: 1,449 rows x 56 columns (52 differential features + Season, TeamLow, TeamHigh, Target)
- **Coverage**: 2003-2025 tournament games
- **Target**: Mean = 0.500 (perfectly balanced by construction)
- **Missing**: Sundberg-derived features missing for 45.2% of rows (pre-2013 games)

### prediction_matchups_2026.parquet
- **Shape**: 72,390 rows x 55 columns
- **Coverage**: All possible 2026 team pairings
- **Note**: Submission only requires ~66,430 men's matchups. This includes all teams, will filter at submission time.

---

## Matchup Feature Construction

All features are computed as **differentials** (TeamLow - TeamHigh):
- `Elo_diff` = Elo(TeamLow) - Elo(TeamHigh)
- `OffEff_diff` = OffEff(TeamLow) - OffEff(TeamHigh)
- etc.

This approach:
- Halves the feature count (one value per matchup, not two per team)
- Sign encodes direction (positive = TeamLow is stronger)
- Works directly with the target: P(TeamLow beats TeamHigh)

---

## Key Decisions Made

1. **Elo uses margin-of-victory weighting** - blowouts update less than close games (diminishing returns on large margins)
2. **Season carryover = 0.75** - 75% of rating carried over, 25% regressed to mean
3. **Selected non-redundant Sundberg features** based on collinearity analysis - excluded EFG_O/EFG_D/2P_O/2P_D (already captured by our own eFGPct and ADJOE/ADJDE)
4. **Coach features use historical data only** - tournament apps/wins counted from prior seasons, not current (prevents leakage)
5. **Possessions estimated** using standard formula: FGA - ORB + TO + 0.475*FTA

---

## Known Limitations

1. **Sundberg name matching**: 13 of 365 teams unmatched (3.6%). These teams get NaN for Sundberg features. Minor impact - none are likely tournament contenders.
2. **Training data size**: Only 1,449 tournament games (2003-2025). Small for neural nets, fine for tree models and logistic regression.
3. **No women's Massey Ordinals**: Women's model will lack ranking system features. Will rely more on Elo, efficiency, and seeds.
4. **No player-level features**: All features are team aggregates. Injuries and roster changes not captured in stats.
