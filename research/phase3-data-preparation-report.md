# Phase 3: Data Preparation - Report

## Class Balance
- Target mean: 0.5003 (724 class 0, 725 class 1)
- **Perfectly balanced by construction** (canonical TeamLow/TeamHigh ordering)
- **SMOTE not needed**

## Feature Selection

### Three importance methods applied to 39 full-coverage features:

**Top features by all 3 methods (correlation, mutual info, random forest):**

| Rank | Feature | Correlation | MI Score | RF Importance |
|------|---------|------------|----------|---------------|
| 1 | Elo_diff | 0.633 | 0.278 | 0.321 |
| 2 | SeedNum_diff | -0.482 | 0.120 | 0.032 |
| 3 | SOS_diff | 0.471 | 0.140 | 0.061 |
| 4 | SeedHistWinPct_diff | 0.495 | 0.150 | 0.048 |
| 5 | EloPreTourney_diff | 0.477 | 0.136 | 0.082 |
| 6 | PointDiff_diff | 0.406 | 0.087 | 0.018 |
| 7 | NetEff_diff | 0.404 | 0.089 | 0.018 |
| 8 | CoachTourneyWins_diff | 0.297 | 0.067 | 0.017 |

**Key finding**: Elo_diff is the single dominant predictor (r=0.63, RF importance=0.32). It alone captures more signal than any other feature.

### Curated Feature Sets

**CORE_FEATURES (21 features)** - for linear/logistic models:
- Elo_diff, SeedNum_diff, SOS_diff
- OffEff_diff, DefEff_diff
- Four factors: eFGPct, TOPct, ORBPct, FTRate (off + def)
- Shooting: FG3Pct, FG3Rate
- Tempo, AstRate, StlRate, BlkRate
- Coach: TourneyWins, SeasonsExp

**EXTENDED_FEATURES (41 features)** - for tree models:
- All CORE_FEATURES plus:
- EloPreTourney, WinPct, PointDiff, OWP, OOWP
- Seed transforms (Inv, HistWinPct)
- Sundberg features (ADJOE, ADJDE, BARTHAG, WAB, etc.)

## Collinearity in Training Data

- **53 pairs with |r| > 0.8**, 19 pairs with |r| > 0.9
- Worst offenders: WinPct <-> WP (r=1.0), PointDiff <-> NetEff (r=0.99), seed transforms (r=0.92-0.98), Elo <-> EloPreTourney (r=0.96)
- **Strategy**: CORE set avoids redundancy. EXTENDED set includes redundant features for tree models that handle it naturally.

## PCA Analysis

| Components | Variance Explained |
|-----------|-------------------|
| 5 | 70.2% |
| 10 | 85.2% |
| 13 | 90.0% |
| 16 | 95.0% |
| 20 | 98.3% |

- **16 components** capture 95% of variance (59% reduction from 39 features)
- Used for neural net preparation

## Data Preparation Pipeline (src/data/prepare.py)

Three model-specific preparation functions:

| Function | Features | NaN Handling | Scaling | Output Shape |
|----------|---------|-------------|---------|-------------|
| prepare_for_linear | 21 (CORE) | Fill with 0 | StandardScaler | (1449, 21) |
| prepare_for_trees | 41 (EXTENDED) | Keep NaN | None | (1449, 41) |
| prepare_for_nn | 16 (PCA) | Fill with 0 | StandardScaler + PCA | (1449, 16) |

## Data Augmentation
- Each matchup flipped: (A-B diff, P(A wins)) -> (-diff, 1-P(A wins))
- Doubles training set: 1,449 -> 2,898 rows
- Used for linear/NN models (tree models don't need it)

## Cross-Validation Strategy
- **Leave-one-tournament-out** on most recent 5 seasons
- Fold 1: val=2021 (66 games), train=1383
- Fold 2: val=2022 (67 games), train=1382
- Fold 3: val=2023 (67 games), train=1382
- Fold 4: val=2024 (67 games), train=1382
- Fold 5: val=2025 (67 games), train=1382
- 2020 excluded (COVID - no tournament)

## Near-Zero Variance / Outliers
- All features have adequate variance
- Only 2 outliers detected (Games_diff, >5 std) - not concerning
- No features dropped for low variance
