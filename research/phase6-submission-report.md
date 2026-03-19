# Phase 6: Submission Generation - Report

## Final Submissions

### Submission 1: `submission_lgbm.csv`
- **Men's model**: LightGBM (CV Brier 0.0503)
- **Women's model**: LightGBM (CV Brier 0.0439)
- **Total matchups**: 132,133 (66,430 men's + 65,703 women's)
- **Missing**: 0
- **Prediction range**: [0.0010, 0.9990]

### Submission 2: `submission_ensemble.csv`
- **Men's model**: Weighted ensemble (50% LGBM + 35% XGB + 10% NN + 5% LR)
- **Women's model**: LightGBM (same as Sub 1 - only had time for one women's model)
- **Total matchups**: 132,133 (66,430 men's + 65,703 women's)
- **Missing**: 0
- **Prediction range**: [0.0010, 0.9990]

## Women's Model
- Applied same pipeline as men's: Elo + efficiency + SOS + seeds
- Fewer features (36 vs 41) - no Sundberg/external data for women, no Massey ordinals
- CV Brier: 0.0439 (better than men's 0.0503 - possibly less parity in women's game)
- Used same LightGBM hyperparameters as men's best config

## Key Injuries NOT Applied
Time constraint prevented manual injury adjustments. These would have been:
- Duke: Caleb Foster (broken foot) - slight downgrade
- BYU: Richie Saunders (knee) - significant downgrade
- Louisville: Mikel Brown Jr. (back) - downgrade for first weekend
- Gonzaga: Braden Huff (knee) - moderate downgrade
- UNC: Caleb Wilson (hand) - moderate downgrade

## Validation
- Both submissions pass format validation
- All 132,133 required IDs present
- All predictions in [0.001, 0.999] range
- No NaN values
- Submissions agree on winner 99.4% of the time (men's portion)
