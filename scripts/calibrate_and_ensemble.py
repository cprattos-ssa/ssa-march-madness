"""Phase 5: Calibration analysis and ensemble construction."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
import pandas as pd
from sklearn.calibration import calibration_curve
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss


def load_predictions():
    """Load all model predictions for 2026."""
    preds = {}
    pred_dir = "data/processed"

    for name, fname in [
        ("lgbm", "preds_lgbm.parquet"),
        ("xgb", "preds_xgb.parquet"),
        ("nn", "preds_nn.parquet"),
        ("logistic", "preds_logistic.parquet"),
        ("bt", "preds_bt.parquet"),
    ]:
        path = os.path.join(pred_dir, fname)
        if os.path.exists(path):
            preds[name] = pd.read_parquet(path)
            print(f"  Loaded {name}: {len(preds[name])} predictions")

    return preds


def analyze_prediction_distributions(preds):
    """Analyze and compare prediction distributions."""
    print("\n" + "=" * 70)
    print("PREDICTION DISTRIBUTION ANALYSIS")
    print("=" * 70)

    for name, df in preds.items():
        pred_col = "Pred" if "Pred" in df.columns else "Pred_lgbm" if "Pred_lgbm" in df.columns else df.columns[-1]
        vals = df[pred_col]
        print(f"\n  {name}:")
        print(f"    Mean: {vals.mean():.4f}")
        print(f"    Std:  {vals.std():.4f}")
        print(f"    Min:  {vals.min():.4f}")
        print(f"    Max:  {vals.max():.4f}")
        print(f"    Median: {vals.median():.4f}")
        # Confidence check - how many predictions are near 0.5?
        near_50 = ((vals > 0.4) & (vals < 0.6)).mean()
        confident = ((vals < 0.2) | (vals > 0.8)).mean()
        print(f"    Near 0.5 (0.4-0.6): {near_50*100:.1f}%")
        print(f"    Confident (<0.2 or >0.8): {confident*100:.1f}%")


def compute_correlation_matrix(preds):
    """Compute pairwise correlation between model predictions."""
    print("\n" + "=" * 70)
    print("MODEL PREDICTION CORRELATIONS")
    print("=" * 70)

    # Align all predictions on the same matchups
    # Use lgbm as base (has all 72390 matchups)
    base = preds["lgbm"].copy()

    # Identify the prediction column and team columns for each model
    model_preds = {}
    for name, df in preds.items():
        if name == "bt":
            continue  # Different format / fewer matchups
        pred_col = [c for c in df.columns if "Pred" in c or "pred" in c]
        if not pred_col:
            pred_col = [df.columns[-1]]
        model_preds[name] = df[pred_col[0]].values

    # Correlation matrix
    names = list(model_preds.keys())
    n = len(names)
    print(f"\n{'':>12}", end="")
    for name in names:
        print(f"{name:>12}", end="")
    print()

    for i, name_i in enumerate(names):
        print(f"{name_i:>12}", end="")
        for j, name_j in enumerate(names):
            r = np.corrcoef(model_preds[name_i], model_preds[name_j])[0, 1]
            print(f"{r:>12.4f}", end="")
        print()


def build_ensemble(preds, weights=None):
    """Build weighted ensemble of model predictions.

    Args:
        preds: Dict of model predictions DataFrames
        weights: Dict of model weights. If None, uses CV Brier scores to compute.

    Returns:
        DataFrame with ensemble predictions
    """
    if weights is None:
        # Weight inversely proportional to CV Brier score
        cv_brier = {
            "lgbm": 0.0503,
            "xgb": 0.0536,
            "nn": 0.1152,
            "logistic": 0.1171,
        }
        # Inverse Brier weighting
        inv_brier = {k: 1.0 / v for k, v in cv_brier.items()}
        total = sum(inv_brier.values())
        weights = {k: v / total for k, v in inv_brier.items()}

    print("\n" + "=" * 70)
    print("ENSEMBLE WEIGHTS")
    print("=" * 70)
    for name, w in sorted(weights.items(), key=lambda x: x[1], reverse=True):
        print(f"  {name:>12}: {w:.4f}")

    # Use lgbm as base for matchup IDs
    base = preds["lgbm"].copy()
    team_cols = [c for c in base.columns if "Team" in c or "Season" in c]

    # Get prediction column for each model
    ensemble_pred = np.zeros(len(base))
    for name, w in weights.items():
        if name not in preds:
            continue
        df = preds[name]
        pred_col = [c for c in df.columns if "Pred" in c or "pred" in c]
        if not pred_col:
            pred_col = [df.columns[-1]]
        ensemble_pred += w * df[pred_col[0]].values

    # Clip
    ensemble_pred = np.clip(ensemble_pred, 0.001, 0.999)

    result = base[team_cols].copy()
    result["Pred"] = ensemble_pred

    print(f"\n  Ensemble predictions: {len(result)}")
    print(f"  Mean: {ensemble_pred.mean():.4f}")
    print(f"  Std: {ensemble_pred.std():.4f}")

    return result


def try_ensemble_weights(preds):
    """Try different ensemble weight combinations."""
    print("\n" + "=" * 70)
    print("ENSEMBLE WEIGHT EXPERIMENTS")
    print("=" * 70)

    configs = [
        ("LightGBM only", {"lgbm": 1.0, "xgb": 0.0, "nn": 0.0, "logistic": 0.0}),
        ("XGBoost only", {"lgbm": 0.0, "xgb": 1.0, "nn": 0.0, "logistic": 0.0}),
        ("Trees avg (LGBM+XGB)", {"lgbm": 0.5, "xgb": 0.5, "nn": 0.0, "logistic": 0.0}),
        ("Trees + NN", {"lgbm": 0.4, "xgb": 0.4, "nn": 0.2, "logistic": 0.0}),
        ("Trees + Logistic", {"lgbm": 0.4, "xgb": 0.4, "nn": 0.0, "logistic": 0.2}),
        ("All equal", {"lgbm": 0.25, "xgb": 0.25, "nn": 0.25, "logistic": 0.25}),
        ("Inv Brier weighted", None),  # Will auto-compute
        ("LGBM heavy", {"lgbm": 0.6, "xgb": 0.3, "nn": 0.05, "logistic": 0.05}),
    ]

    for config_name, weights in configs:
        if weights is None:
            cv_brier = {"lgbm": 0.0503, "xgb": 0.0536, "nn": 0.1152, "logistic": 0.1171}
            inv_brier = {k: 1.0 / v for k, v in cv_brier.items()}
            total = sum(inv_brier.values())
            weights = {k: v / total for k, v in inv_brier.items()}

        # Compute blended predictions
        base = preds["lgbm"]
        blend = np.zeros(len(base))
        for name, w in weights.items():
            if name not in preds or w == 0:
                continue
            df = preds[name]
            pred_col = [c for c in df.columns if "Pred" in c or "pred" in c]
            if not pred_col:
                pred_col = [df.columns[-1]]
            blend += w * df[pred_col[0]].values

        blend = np.clip(blend, 0.001, 0.999)

        # Stats
        mean_pred = blend.mean()
        std_pred = blend.std()
        confident = ((blend < 0.2) | (blend > 0.8)).mean()

        print(f"\n  {config_name}:")
        active = {k: f"{v:.2f}" for k, v in weights.items() if v > 0}
        print(f"    Weights: {active}")
        print(f"    Mean={mean_pred:.4f}, Std={std_pred:.4f}, Confident={confident*100:.1f}%")


def main():
    print("Loading predictions...")
    preds = load_predictions()

    analyze_prediction_distributions(preds)
    compute_correlation_matrix(preds)
    try_ensemble_weights(preds)

    # Build final ensembles
    print("\n" + "=" * 70)
    print("BUILDING FINAL ENSEMBLES")
    print("=" * 70)

    # Submission 1: LightGBM only (best single model)
    sub1 = preds["lgbm"].copy()
    pred_col = [c for c in sub1.columns if "Pred" in c][0]
    sub1 = sub1.rename(columns={pred_col: "Pred"})
    sub1["Pred"] = np.clip(sub1["Pred"].values, 0.001, 0.999)
    sub1.to_parquet("data/processed/ensemble_lgbm_only.parquet", index=False)
    print(f"\n  Submission 1 (LightGBM only): saved")

    # Submission 2: Weighted ensemble (trees heavy)
    ensemble_weights = {"lgbm": 0.5, "xgb": 0.35, "nn": 0.10, "logistic": 0.05}
    sub2 = build_ensemble(preds, weights=ensemble_weights)
    sub2.to_parquet("data/processed/ensemble_weighted.parquet", index=False)
    print(f"  Submission 2 (weighted ensemble): saved")

    print("\n" + "=" * 70)
    print("DONE - Two ensemble strategies saved")
    print("=" * 70)
    print("  1. data/processed/ensemble_lgbm_only.parquet (pure LightGBM)")
    print("  2. data/processed/ensemble_weighted.parquet (50% LGBM + 35% XGB + 10% NN + 5% LR)")


if __name__ == "__main__":
    main()
