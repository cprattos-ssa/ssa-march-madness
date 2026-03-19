# Phase 5: Calibration and Ensemble - Report

## Prediction Distribution Analysis

| Model | Mean | Std | Near 0.5 | Confident (<0.2 or >0.8) |
|-------|------|-----|----------|--------------------------|
| LightGBM | 0.474 | 0.411 | 4.2% | 81.7% |
| XGBoost | 0.474 | 0.416 | 3.7% | 84.4% |
| Neural Net | 0.468 | 0.449 | 4.2% | 86.4% |
| Logistic | 0.473 | 0.405 | 7.5% | 74.9% |
| Bradley-Terry | 0.545 | 0.260 | 21.5% | 34.5% |

- Tree models are highly confident (80-84% of predictions are below 0.2 or above 0.8)
- NN is the most extreme (86.4% confident) - may be slightly overconfident
- Logistic is the most conservative (74.9% confident)
- Bradley-Terry is very conservative (only 34.5% confident) - reflects simpler model

## Model Correlation Matrix

|  | lgbm | xgb | nn | logistic |
|--|------|-----|----|----------|
| lgbm | 1.00 | 0.99 | 0.91 | 0.93 |
| xgb | 0.99 | 1.00 | 0.91 | 0.92 |
| nn | 0.91 | 0.91 | 1.00 | 0.96 |
| logistic | 0.93 | 0.92 | 0.96 | 1.00 |

- LightGBM and XGBoost are nearly identical (r=0.99) - expected, same feature set
- NN and Logistic are more similar to each other (r=0.96) than to trees - same CORE feature set
- Moderate diversity exists between tree and non-tree models (r=0.91-0.93) - ensemble can benefit

## Ensemble Weight Experiments

| Config | Weights | Std | Confident% |
|--------|---------|-----|-----------|
| LightGBM only | LGBM=1.0 | 0.411 | 81.7% |
| Trees avg | LGBM=0.5, XGB=0.5 | 0.412 | 82.9% |
| Trees + NN | LGBM=0.4, XGB=0.4, NN=0.2 | 0.413 | 82.3% |
| LGBM heavy | LGBM=0.6, XGB=0.3, NN=0.05, LR=0.05 | 0.410 | 81.8% |
| Inv Brier weighted | LGBM=0.36, XGB=0.33, NN=0.16, LR=0.15 | 0.409 | 80.7% |
| All equal | All=0.25 | 0.410 | 79.7% |

**Observations:**
- All configurations produce very similar distributions - dominated by tree models
- Including NN/LR slightly reduces confidence (more conservative)
- Equal weighting slightly hurts vs tree-heavy weighting

## Final Submissions

### Submission 1: LightGBM Only
- Pure best single model
- CV Brier: 0.0503
- Most confident predictions

### Submission 2: Weighted Ensemble
- 50% LightGBM + 35% XGBoost + 10% Neural Net + 5% Logistic
- Adds model diversity while keeping tree models dominant
- Slightly more conservative than LightGBM alone

## Rationale for Two Submissions
- Kaggle allows selecting 2 submissions for final scoring
- Sub 1 (LGBM only): Best CV score, high confidence - bet on single best model
- Sub 2 (ensemble): Hedged bet - diversity may help if LightGBM overfits to validation years
- The two submissions represent different risk profiles
