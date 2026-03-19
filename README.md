# SSA March Madness - NCAA Tournament Prediction

Entry for Kaggle's [March Machine Learning Mania 2026](https://www.kaggle.com/competitions/march-machine-learning-mania-2026) competition. Predicts the probability of every possible matchup in the 2026 NCAA Men's and Women's basketball tournaments. Evaluated on Brier score (lower is better).

**Prize Pool**: $50,000 | **Teams**: 2,944 | **Metric**: Brier Score

---

## Results Summary

### Model Performance (5-Fold Leave-One-Tournament-Out CV)

| Model | Men's CV Brier | Women's CV Brier |
|-------|---------------|-----------------|
| **LightGBM** | **0.0503** | **0.0439** |
| XGBoost | 0.0536 | - |
| Neural Network | 0.1152 | - |
| Logistic Regression | 0.1171 | - |
| Bradley-Terry (LR on Elo) | 0.1996 | - |

### Tournament Predictions (Monte Carlo, 10,000 simulations)

| Team | Championship % | Final Four % |
|------|---------------|-------------|
| (1) Duke | 60.7% | 78.3% |
| (1) Arizona | 23.9% | 64.9% |
| (1) Michigan | 10.7% | 27.6% |
| (1) Florida | 2.3% | 13.4% |
| (2) Houston | 0.8% | 3.8% |

**Chalk bracket champion**: (1) Duke over (1) Arizona (78.4%)

### Two Kaggle Submissions
1. `submission_lgbm.csv` - Pure LightGBM (best single model)
2. `submission_ensemble.csv` - Weighted ensemble (50% LGBM + 35% XGB + 10% NN + 5% LR)

---

## Project Structure

```
ssa-march-madness/
|-- config/                        # YAML configuration files
|   |-- config.yaml                # Master config (gender, seasons, feature flags)
|   |-- features.yaml              # Feature engineering parameters (Elo K-factor, etc.)
|   |-- models/                    # Per-model hyperparameters
|       |-- logistic.yaml
|       |-- xgboost.yaml
|       |-- neural_net.yaml
|       |-- ensemble.yaml
|
|-- data/
|   |-- raw/kaggle/                # 35 competition CSVs (immutable)
|   |-- raw/external/              # 66 external dataset CSVs
|   |   |-- sundberg/              # Barttorvik advanced stats (2013-2026)
|   |   |-- amin/                  # KenPom, Barttorvik, EvanMiya, Heat Check, resumes
|   |   |-- pilafas/               # KenPom historical efficiency/defense/offense
|   |-- processed/                 # Feature matrices and model predictions
|   |-- submissions/               # Final Kaggle submission CSVs
|
|-- src/                           # Production pipeline code
|   |-- data/
|   |   |-- download.py            # Kaggle API data download
|   |   |-- prepare.py             # Feature selection, scaling, CV splits, augmentation
|   |-- features/
|   |   |-- elo.py                 # Custom Elo rating system
|   |   |-- efficiency.py          # Per-possession efficiency metrics
|   |   |-- seeds.py               # Tournament seed features
|   |   |-- strength_of_schedule.py # Multi-level SOS (WP, OWP, OOWP)
|   |   |-- build_features.py     # Orchestrator - builds all features + matchup matrix
|   |-- models/
|   |   |-- train.py               # Shared CV and training utilities
|   |-- evaluation/
|   |   |-- metrics.py             # Brier score, calibration stats
|   |-- submission/
|   |   |-- validate.py            # Submission format checker
|   |-- utils/
|       |-- constants.py           # Team ID ranges, file mappings, column names
|
|-- scripts/                       # Entry point scripts
|   |-- train_logistic.py          # Logistic regression with ElasticNet
|   |-- train_trees.py             # XGBoost and LightGBM with hyperparameter sweep
|   |-- train_nn.py                # PyTorch neural network
|   |-- train_bradley_terry.py     # Bradley-Terry / Elo probabilistic model
|   |-- calibrate_and_ensemble.py  # Model comparison and ensemble construction
|   |-- generate_submission.py     # Format predictions into Kaggle submission CSV
|   |-- simulate_brackets.py       # Chalk and Monte Carlo bracket simulations
|
|-- research/                      # Detailed reports for each phase
|   |-- competition-research.md    # Competition overview, rules, strategy
|   |-- data-sources.md            # All data sources, licensing, collection plan
|   |-- phase1-eda-report.md       # Data profiling, trends, seed analysis, collinearity
|   |-- phase2-feature-engineering-report.md
|   |-- phase3-data-preparation-report.md
|   |-- phase4-model-training-report.md
|   |-- phase5-calibration-ensemble-report.md
|   |-- phase6-submission-report.md
|
|-- results/                       # Outputs
|   |-- bracket_chalk.txt          # Full chalk bracket with win probabilities
|   |-- bracket_monte_carlo.txt    # Monte Carlo bracket + simulation statistics
|   |-- figures/                   # Saved plots
|
|-- requirements.txt
|-- pyproject.toml
|-- Makefile
|-- CLAUDE.md
```

---

## Methodology

### Phase 1: Exploratory Data Analysis

**Data inventory**: 101 CSV files across 4 sources (35 Kaggle competition + 66 external).

**Key findings**:
- 2026 has the highest average total score (149.4 pts/game) in the dataset, driven by the three-point revolution
- Three-point attempts now account for 39.5% of all shots (up from 32.3% in 2003), but accuracy is flat at ~34%
- The 11-seed anomaly is real: 41.0% tournament win rate vs 38.0% for 9-seeds and 38.1% for 10-seeds
- 1-seeds have won 26 of 40 championships (65%)
- The 5-vs-12 matchup has a 36.1% upset rate; 8-vs-9 is a coin flip (52.5%)

**Collinearity analysis** identified 6 groups of redundant features (r > 0.9). VIF analysis on Sundberg data showed EFG_O (324), EFG_D (324), and other shooting metrics are critically inflated. Safe features (VIF < 5): TOR, ORB, DRB, FTR, ADJ_T.

**Security audit**: All 101 files scanned for formula injection, SQL injection, shell injection, XSS, binary payloads. All clean.

### Phase 2: Feature Engineering

Built a modular pipeline (`src/features/`) producing **57 features per team-season**:

**Elo Ratings** (2 features):
- Custom Elo system with margin-of-victory weighting, K=20, home advantage=100, season carryover=0.75
- Both end-of-season and pre-tournament snapshots

**Efficiency Metrics** (21 features):
- Points per 100 possessions (offense/defense)
- Four factors: eFG%, turnover%, offensive rebound%, free throw rate (offense and defense)
- Shooting splits: FG%, 3PT%, FT%, 3-point attempt rate
- Possessions estimated via: FGA - ORB + TO + 0.475*FTA

**Strength of Schedule** (4 features):
- RPI-style: 0.25*WP + 0.50*OWP + 0.25*OOWP

**Seed Features** (8 features):
- Raw seed + nonlinear transforms (log, squared, inverse)
- Historical win rate by seed number
- Play-in flag

**Coach Features** (3 features):
- Seasons as head coach, prior tournament appearances, prior tournament wins

**External Data** (13 features from Sundberg/Barttorvik):
- ADJOE, ADJDE, BARTHAG, WAB, tempo, four factors
- Selected non-redundant features based on collinearity analysis

**Matchup construction**: All features computed as differentials (TeamLow - TeamHigh). Each game also augmented by flipping perspective, doubling the training set.

**Output**: 12,748 team-seasons, 1,449 training matchups, 72,390 prediction matchups.

### Phase 3: Data Preparation

**Class balance**: Target is exactly 50/50 by construction. SMOTE not needed.

**Feature importance** (3 methods - correlation, mutual information, random forest):
- Elo_diff is the dominant predictor (r=0.63, RF importance=0.32)
- Top 5: Elo_diff, SeedNum_diff, SOS_diff, SeedHistWinPct_diff, EloPreTourney_diff

**Three model-specific feature sets**:

| Prep Function | Features | For Models |
|--------------|----------|-----------|
| `prepare_for_linear` | 21 core (collinearity-safe, scaled) | Logistic, NN |
| `prepare_for_trees` | 41 extended (includes NaN, no scaling) | XGBoost, LightGBM |
| `prepare_for_nn` | 16 PCA components (95% variance) | Neural Network (alt) |

**PCA analysis**: 16 components capture 95% of variance (59% dimensionality reduction from 39 features). However, PCA hurt neural network performance in practice.

**Cross-validation**: Leave-one-tournament-out on the 5 most recent seasons (2021-2025). ~67 games per fold, ~1382 training games per fold.

### Phase 4: Model Training

Five models trained in parallel using Claude Code subagents:

**LightGBM** (Best - Brier 0.0503):
- max_depth=3, num_leaves=8, learning_rate=0.05, n_estimators=300
- 41 extended features, handles NaN natively
- Top features: Elo_diff, EloPreTourney_diff, AstRate_diff

**XGBoost** (Brier 0.0536):
- max_depth=4, learning_rate=0.05, n_estimators=300
- Same feature set as LightGBM
- 0.989 correlation with LightGBM predictions

**Neural Network** (Brier 0.1152):
- Architecture: 21 -> 128 -> ReLU -> Drop(0.3) -> 64 -> ReLU -> Drop(0.3) -> 32 -> ReLU -> 1 -> Sigmoid
- BCELoss, Adam lr=0.001, early stopping patience=20
- No PCA performed better than PCA (0.1152 vs 0.1867)

**Logistic Regression** (Brier 0.1171):
- C=1.0, L1 penalty (Lasso), saga solver
- 21 core features, augmented training data (2898 rows)
- Top coefficients: Elo_diff (5.86), SOS_diff (1.87)

**Bradley-Terry** (Brier 0.1996):
- LR on Elo features (elo_diff, elo_diff^2, seed_diff) beats raw Elo probabilities
- Best Elo params: K=28, home_advantage=75, carryover=0.8
- Simplest model, weakest performance, but useful as a baseline

**Key insight**: Tree-based models dramatically outperform everything else. The gap between LightGBM (0.050) and logistic regression (0.117) reflects nonlinear interactions that trees capture.

### Phase 5: Calibration and Ensemble

**Prediction distributions**: Tree models are highly confident (81-84% of predictions below 0.2 or above 0.8). Neural net is most extreme (86.4%), logistic is most conservative (74.9%).

**Model correlation matrix**:
- LightGBM/XGBoost: r=0.99 (nearly identical)
- Trees/NN: r=0.91 (moderate diversity)
- NN/Logistic: r=0.96 (similar feature sets)

**Ensemble strategy**: LightGBM-heavy weighting. Including NN/LR adds diversity without significantly changing predictions (99.4% agreement on winner direction).

**Two submissions** built:
1. Pure LightGBM (highest CV score, most confident)
2. Weighted ensemble (hedged bet with model diversity)

### Phase 6: Submission

**Women's model**: Applied the same pipeline (Elo + efficiency + SOS + seeds) with LightGBM. Fewer features (36 vs 41 - no external data or Massey ordinals for women). CV Brier: 0.0439.

**Final submissions**: 132,133 matchups each (66,430 men's + 65,703 women's). Zero missing predictions. Both pass format validation.

**Bracket simulations**: Chalk bracket and 10,000-run Monte Carlo both saved to `results/`.

---

## Data Sources

### Kaggle Competition Data (35 CSVs)
- Game results (compact + detailed box scores) back to 1985/2003
- Tournament seeds, bracket structure, geography
- Massey ordinals (50+ ranking systems, men's only)
- Coach tenure, conference affiliations
- License: Competition rules

### External Data (66 CSVs, all free)

| Source | Files | License | Key Features |
|--------|-------|---------|-------------|
| [Sundberg](https://www.kaggle.com/datasets/andrewsundberg/college-basketball-dataset) | 15 | CC0 | ADJOE, ADJDE, BARTHAG, WAB, four factors (2013-2026) |
| [Amin](https://www.kaggle.com/datasets/nishaanamin/march-madness-data) | 38 | CC0 | KenPom, Barttorvik, EvanMiya, resumes, Elo, ratings (2008-2026) |
| [Pilafas](https://www.kaggle.com/datasets/jonathanpilafas/2024-march-madness-statistical-analysis) | 13 | MIT | KenPom efficiency/defense/offense/height (2002-2026) |

External data explicitly encouraged by competition rules.

---

## How Basketball Has Changed (and Why It Matters)

Key trends that informed our modeling decisions:

- **Three-point revolution**: 3PA as % of all shots went from 32% to 40% since 2003. Volume exploded, accuracy flat at ~34%. Models trained on older data are biased.
- **Transfer portal era**: ~2,000 players transfer annually. Team identity is less stable year-over-year. Current-season metrics matter more than historical team performance.
- **Championship paradox**: Only 18.4% of Final Four teams shot 3s at this year's rate. Efficiency > volume for deep runs.
- **Recency weighting**: We weight recent seasons more heavily due to these structural changes.

---

## Setup and Reproduction

### Prerequisites
- Python 3.12+
- Kaggle API token (set `KAGGLE_API_TOKEN` env var)

### Installation
```bash
git clone <repo-url>
cd ssa-march-madness
python -m venv .venv
source .venv/Scripts/activate  # Windows
pip install -r requirements.txt
```

### Run Pipeline
```bash
# Download data
make data
# Or manually:
python src/data/download.py

# Build features (Elo, efficiency, SOS, seeds, coach, external)
python -m src.features.build_features

# Train models
python scripts/train_trees.py         # XGBoost + LightGBM
python scripts/train_logistic.py      # Logistic Regression
python scripts/train_nn.py            # Neural Network
python scripts/train_bradley_terry.py # Bradley-Terry / Elo

# Calibrate and ensemble
python scripts/calibrate_and_ensemble.py

# Generate submission
python scripts/generate_submission.py

# Simulate brackets
python scripts/simulate_brackets.py
```

### Key Configuration
Edit `config/config.yaml` to switch between men's and women's data:
```yaml
gender: "mens"   # or "womens"
season_predict: 2026
```

---

## Tech Stack

- **Python 3.12** with pandas, NumPy, scikit-learn
- **XGBoost 3.2** and **LightGBM 4.6** for gradient boosted trees
- **PyTorch** for neural network
- **pyarrow** for efficient parquet I/O
- **Kaggle API** for data download and submission

---

## Predicted Upsets (Chalk Bracket)

Our model predicts these first-round upsets even in the chalk (always-pick-favorite) bracket:

| Upset | Over | Win Probability |
|-------|------|----------------|
| (11) South Florida | (6) Louisville | 65.8% |
| (11) VCU | (6) North Carolina | 60.8% |
| (12) Akron | (5) Texas Tech | 72.7% |
| (10) Santa Clara | (7) Kentucky | 70.4% |
| (9) St Louis | (8) Georgia | 63.7% |
| (9) Utah St | (8) Villanova | 94.3% |

Later round upsets:
- (5) St John's over (4) Kansas in Round of 32 (95.2%)
- (3) Gonzaga over (2) Purdue in Sweet 16 (72.1%)

---

## Known Limitations

1. **No player-level features** - all features are team aggregates. Injuries and roster changes not captured in stats
2. **External data name matching** - 13 of 365 team names unmatched (3.6%), none are tournament contenders
3. **Small training set** - only 1,449 tournament games (2003-2025). Sufficient for tree models, tight for neural nets
4. **No women's Massey ordinals** - women's model has fewer features than men's
5. **No injury adjustments** - Duke (Foster), BYU (Saunders), Louisville (Brown Jr.), Gonzaga (Huff), UNC (Wilson) all have key players out
