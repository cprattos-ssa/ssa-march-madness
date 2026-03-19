# Phase 4: Model Training - Report

## Model Comparison

| Model | CV Brier Score | Notes |
|-------|---------------|-------|
| LightGBM | **0.0503** | Best overall. Shallow trees (depth 3, 8 leaves), lr=0.05, 300 trees |
| XGBoost | 0.0536 | Close second. depth=4, lr=0.05, 300 trees |
| Neural Network | 0.1152 | No PCA (21 features) beat PCA (0.1867). 128-64-32 architecture |
| Logistic Regression | 0.1171 | C=1.0, L1 penalty. Simple but solid baseline |
| Bradley-Terry (LR on Elo) | 0.1996 | K=28, home_adv=75, carryover=0.8. Elo + seed features |
| Bradley-Terry (raw) | 0.2031 | K=20, home_adv=75, carryover=0.8. Pure Elo probabilities |

**Key finding**: Tree-based models (LightGBM/XGBoost) dramatically outperform everything else. The gap between LightGBM (0.050) and logistic regression (0.117) is enormous.

## Model Details

### LightGBM (Best - Brier 0.0503)
- **Params**: max_depth=3, num_leaves=8, learning_rate=0.05, n_estimators=300, subsample=0.8, colsample_bytree=0.8
- **Feature set**: 41 EXTENDED features (includes Sundberg, handles NaN natively)
- **Top features by split count**: Elo_diff, EloPreTourney_diff, AstRate_diff, StlRate_diff, BlkRate_diff
- Prediction correlation with XGBoost: 0.989

### XGBoost (Brier 0.0536)
- **Params**: max_depth=4, learning_rate=0.05, n_estimators=300, subsample=0.8, colsample_bytree=0.8
- **Top features by importance**: Elo_diff, EloPreTourney_diff, SeedHistWinPct_diff, WinPct_diff, PointDiff_diff

### Neural Network (Brier 0.1152)
- **Architecture**: 21 -> 128 -> ReLU -> Drop(0.3) -> 64 -> ReLU -> Drop(0.3) -> 32 -> ReLU -> 1 -> Sigmoid
- **Training**: BCELoss, Adam lr=0.001, 200 epochs, early stopping patience=20, augmented data
- **PCA hurt performance**: 0.1867 with PCA vs 0.1152 without
- Per-fold: 2024 (0.0955) and 2025 (0.0900) much better than earlier seasons

### Logistic Regression (Brier 0.1171)
- **Params**: C=1.0, l1_ratio=1.0 (pure L1/Lasso), saga solver
- **Feature set**: 21 CORE features, augmented (2898 rows)
- **Top coefficients**: Elo_diff (5.86), SOS_diff (1.87), DefEff_diff (0.97), OffEff_diff (0.71)
- L1 performs slightly better than L2 or ElasticNet at C=1.0

### Bradley-Terry (Brier 0.1996)
- LR on Elo features (elo_diff, elo_diff^2, seed_diff) beats raw BT probabilities
- **LR coefficients**: elo_diff=0.00385, seed_diff=-0.0805
- Only uses 2278 predictions (tournament teams only, not all 72K matchups)
- Simplest model but weakest performance

## Observations

1. **Elo is the dominant feature** across all models - consistently #1 importance
2. **Tree models capture nonlinear interactions** that linear models miss (huge Brier gap)
3. **Shallow trees work best** - depth 3-4 prevents overfitting on 1449 training samples
4. **PCA hurts more than it helps** - the raw features contain signal that PCA destroys
5. **Recent seasons are easier to predict** - 2024 and 2025 folds have lower Brier across all models
6. **XGBoost and LightGBM highly agree** (r=0.989) but LightGBM edges ahead

## Prediction Files

| File | Rows | Model |
|------|------|-------|
| preds_lgbm.parquet | 72,390 | LightGBM (best) |
| preds_xgb.parquet | 72,390 | XGBoost |
| preds_nn.parquet | 72,390 | Neural Network |
| preds_logistic.parquet | 72,390 | Logistic Regression |
| preds_bt.parquet | 2,278 | Bradley-Terry (tournament teams only) |
