"""Train XGBoost and LightGBM with hyperparameter sweeps."""

import sys
import os
import time

# Allow imports from project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
import pandas as pd
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier

from src.data.prepare import (
    prepare_for_trees, EXTENDED_FEATURES, EXTENDED_PLAYER_FEATURES,
    augment_training_data,
)
from src.models.train import cross_validate


# Smart subset of the full grid - key combos covering the search space
XGB_PARAM_COMBOS = [
    # Shallow + low LR + many trees (conservative)
    {"max_depth": 3, "learning_rate": 0.01, "n_estimators": 500},
    {"max_depth": 3, "learning_rate": 0.05, "n_estimators": 300},
    {"max_depth": 3, "learning_rate": 0.1, "n_estimators": 100},
    # Medium depth
    {"max_depth": 4, "learning_rate": 0.01, "n_estimators": 500},
    {"max_depth": 4, "learning_rate": 0.05, "n_estimators": 300},
    {"max_depth": 4, "learning_rate": 0.1, "n_estimators": 100},
    {"max_depth": 4, "learning_rate": 0.1, "n_estimators": 300},
    # Deeper
    {"max_depth": 5, "learning_rate": 0.05, "n_estimators": 300},
    {"max_depth": 5, "learning_rate": 0.1, "n_estimators": 100},
    {"max_depth": 5, "learning_rate": 0.1, "n_estimators": 300},
    # Deepest
    {"max_depth": 6, "learning_rate": 0.05, "n_estimators": 300},
    {"max_depth": 6, "learning_rate": 0.1, "n_estimators": 100},
]

LGBM_PARAM_COMBOS = [
    {"max_depth": 3, "learning_rate": 0.01, "n_estimators": 500, "num_leaves": 8},
    {"max_depth": 3, "learning_rate": 0.05, "n_estimators": 300, "num_leaves": 8},
    {"max_depth": 3, "learning_rate": 0.1, "n_estimators": 100, "num_leaves": 8},
    {"max_depth": 4, "learning_rate": 0.01, "n_estimators": 500, "num_leaves": 16},
    {"max_depth": 4, "learning_rate": 0.05, "n_estimators": 300, "num_leaves": 16},
    {"max_depth": 4, "learning_rate": 0.1, "n_estimators": 100, "num_leaves": 16},
    {"max_depth": 4, "learning_rate": 0.1, "n_estimators": 300, "num_leaves": 16},
    {"max_depth": 5, "learning_rate": 0.05, "n_estimators": 300, "num_leaves": 31},
    {"max_depth": 5, "learning_rate": 0.1, "n_estimators": 100, "num_leaves": 31},
    {"max_depth": 5, "learning_rate": 0.1, "n_estimators": 300, "num_leaves": 31},
    {"max_depth": 6, "learning_rate": 0.05, "n_estimators": 300, "num_leaves": 50},
    {"max_depth": 6, "learning_rate": 0.1, "n_estimators": 100, "num_leaves": 50},
]

# Shared params for regularization
SHARED_XGB = {"subsample": 0.8, "colsample_bytree": 0.8}
SHARED_LGBM = {"subsample": 0.8, "colsample_bytree": 0.8}


def run_xgb_sweep(train_df):
    """Run XGBoost hyperparameter sweep and return results."""
    print("=" * 60)
    print("XGBOOST HYPERPARAMETER SWEEP")
    print("=" * 60)

    results = []
    best_brier = float("inf")
    best_params = None

    for i, combo in enumerate(XGB_PARAM_COMBOS):
        params = {**combo, **SHARED_XGB}
        label = f"depth={params['max_depth']}, lr={params['learning_rate']}, trees={params['n_estimators']}"
        print(f"\n--- XGB [{i+1}/{len(XGB_PARAM_COMBOS)}] {label} ---")

        def make_xgb(X, y, _params=dict(params)):
            model = XGBClassifier(
                **_params,
                objective="binary:logistic",
                eval_metric="logloss",
                use_label_encoder=False,
                verbosity=0,
                random_state=42,
            )
            model.fit(X, y)
            return model

        t0 = time.time()
        cv_result = cross_validate(
            model_fn=make_xgb,
            train_df=train_df,
            prepare_fn=prepare_for_trees,
            prepare_kwargs={"features": EXTENDED_FEATURES},
            augment=True,
        )
        elapsed = time.time() - t0

        results.append({
            "model": "XGBoost",
            "max_depth": params["max_depth"],
            "learning_rate": params["learning_rate"],
            "n_estimators": params["n_estimators"],
            "mean_brier": cv_result["mean_brier"],
            "overall_brier": cv_result["overall_brier"],
            "time_s": round(elapsed, 1),
        })

        if cv_result["mean_brier"] < best_brier:
            best_brier = cv_result["mean_brier"]
            best_params = dict(params)

    return results, best_params, best_brier


def run_lgbm_sweep(train_df):
    """Run LightGBM hyperparameter sweep and return results."""
    print("\n" + "=" * 60)
    print("LIGHTGBM HYPERPARAMETER SWEEP")
    print("=" * 60)

    results = []
    best_brier = float("inf")
    best_params = None

    for i, combo in enumerate(LGBM_PARAM_COMBOS):
        params = {**combo, **SHARED_LGBM}
        label = (
            f"depth={params['max_depth']}, lr={params['learning_rate']}, "
            f"trees={params['n_estimators']}, leaves={params['num_leaves']}"
        )
        print(f"\n--- LGBM [{i+1}/{len(LGBM_PARAM_COMBOS)}] {label} ---")

        def make_lgbm(X, y, _params=dict(params)):
            model = LGBMClassifier(
                **_params,
                objective="binary",
                metric="binary_logloss",
                verbose=-1,
                random_state=42,
            )
            model.fit(X, y)
            return model

        t0 = time.time()
        cv_result = cross_validate(
            model_fn=make_lgbm,
            train_df=train_df,
            prepare_fn=prepare_for_trees,
            prepare_kwargs={"features": EXTENDED_FEATURES},
            augment=True,
        )
        elapsed = time.time() - t0

        results.append({
            "model": "LightGBM",
            "max_depth": params["max_depth"],
            "learning_rate": params["learning_rate"],
            "n_estimators": params["n_estimators"],
            "num_leaves": params["num_leaves"],
            "mean_brier": cv_result["mean_brier"],
            "overall_brier": cv_result["overall_brier"],
            "time_s": round(elapsed, 1),
        })

        if cv_result["mean_brier"] < best_brier:
            best_brier = cv_result["mean_brier"]
            best_params = dict(params)

    return results, best_params, best_brier


def train_final_and_predict(model_type, best_params, train_df, pred_df):
    """Train final model on all data and generate predictions."""
    print(f"\nTraining final {model_type} on all data with best params...")

    feat_list = EXTENDED_PLAYER_FEATURES if "Player" in model_type else EXTENDED_FEATURES
    X_train, y_train, X_pred, feature_names = prepare_for_trees(
        train_df, pred_df, features=feat_list
    )

    # Augment training data
    X_train_aug, y_train_aug = augment_training_data(X_train, y_train)

    if model_type == "XGBoost":
        model = XGBClassifier(
            **best_params,
            objective="binary:logistic",
            eval_metric="logloss",
            use_label_encoder=False,
            verbosity=0,
            random_state=42,
        )
    else:
        model = LGBMClassifier(
            **best_params,
            objective="binary",
            metric="binary_logloss",
            verbose=-1,
            random_state=42,
        )

    model.fit(X_train_aug, y_train_aug)

    # Predictions
    preds = model.predict_proba(X_pred)[:, 1]
    preds = np.clip(preds, 0.001, 0.999)

    # Feature importance
    importances = model.feature_importances_
    feat_imp = pd.DataFrame({
        "feature": feature_names,
        "importance": importances,
    }).sort_values("importance", ascending=False)

    print(f"\n{model_type} Top 15 Feature Importances:")
    print(feat_imp.head(15).to_string(index=False))

    return model, preds, feature_names


def main():
    # Load data
    train_df = pd.read_parquet("data/processed/training_matchups.parquet")
    pred_df = pd.read_parquet("data/processed/prediction_matchups_2026.parquet")

    print(f"Training data: {train_df.shape}")
    print(f"Prediction data: {pred_df.shape}")
    avail = [f for f in EXTENDED_FEATURES if f in train_df.columns and f in pred_df.columns]
    print(f"Extended features available: {len(avail)} / {len(EXTENDED_FEATURES)}")

    # -- BASELINE: XGBoost + LightGBM sweep (team features only) --
    xgb_results, xgb_best_params, xgb_best_brier = run_xgb_sweep(train_df)
    lgbm_results, lgbm_best_params, lgbm_best_brier = run_lgbm_sweep(train_df)

    # -- PLAYER FEATURES: LightGBM sweep with player data --
    print("\n" + "=" * 60)
    print("LIGHTGBM + PLAYER FEATURES SWEEP")
    print("=" * 60)

    player_avail = [f for f in EXTENDED_PLAYER_FEATURES if f in train_df.columns and f in pred_df.columns]
    player_new = [f for f in player_avail if f not in EXTENDED_FEATURES]
    print(f"Player features available: {player_new}")

    lgbm_player_results = []
    lgbm_player_best_brier = float("inf")
    lgbm_player_best_params = None

    # Tighter regularization combos for player features (prevent overfitting on 334 games)
    LGBM_PLAYER_COMBOS = [
        {"max_depth": 3, "learning_rate": 0.05, "n_estimators": 300, "num_leaves": 8, "colsample_bytree": 0.7, "min_child_samples": 10},
        {"max_depth": 3, "learning_rate": 0.1, "n_estimators": 100, "num_leaves": 8, "colsample_bytree": 0.7, "min_child_samples": 10},
        {"max_depth": 3, "learning_rate": 0.05, "n_estimators": 300, "num_leaves": 8, "colsample_bytree": 0.8, "min_child_samples": 5},
        {"max_depth": 4, "learning_rate": 0.05, "n_estimators": 300, "num_leaves": 16, "colsample_bytree": 0.7, "min_child_samples": 10},
        {"max_depth": 4, "learning_rate": 0.1, "n_estimators": 100, "num_leaves": 16, "colsample_bytree": 0.7, "min_child_samples": 10},
        {"max_depth": 4, "learning_rate": 0.05, "n_estimators": 300, "num_leaves": 16, "colsample_bytree": 0.8, "min_child_samples": 5},
    ]

    for i, combo in enumerate(LGBM_PLAYER_COMBOS):
        params = {**combo, "subsample": 0.8}
        label = (
            f"depth={params['max_depth']}, lr={params['learning_rate']}, "
            f"trees={params['n_estimators']}, leaves={params['num_leaves']}, "
            f"colsample={params['colsample_bytree']}"
        )
        print(f"\n--- LGBM+Player [{i+1}/{len(LGBM_PLAYER_COMBOS)}] {label} ---")

        def make_lgbm_player(X, y, _params=dict(params)):
            model = LGBMClassifier(
                **_params,
                objective="binary",
                metric="binary_logloss",
                verbose=-1,
                random_state=42,
            )
            model.fit(X, y)
            return model

        cv_result = cross_validate(
            model_fn=make_lgbm_player,
            train_df=train_df,
            prepare_fn=prepare_for_trees,
            prepare_kwargs={"features": EXTENDED_PLAYER_FEATURES},
            augment=True,
        )

        lgbm_player_results.append({
            "model": "LGBM+Player",
            "max_depth": params["max_depth"],
            "learning_rate": params["learning_rate"],
            "n_estimators": params["n_estimators"],
            "num_leaves": params["num_leaves"],
            "colsample_bytree": params["colsample_bytree"],
            "mean_brier": cv_result["mean_brier"],
            "overall_brier": cv_result["overall_brier"],
        })

        if cv_result["mean_brier"] < lgbm_player_best_brier:
            lgbm_player_best_brier = cv_result["mean_brier"]
            lgbm_player_best_params = dict(params)

    print("\n" + "=" * 60)
    print("PLAYER FEATURES COMPARISON")
    print("=" * 60)
    print(f"Best LGBM (team only):    {lgbm_best_brier:.6f}")
    print(f"Best LGBM (+ player):     {lgbm_player_best_brier:.6f}")
    diff = lgbm_best_brier - lgbm_player_best_brier
    print(f"Improvement:              {diff:+.6f} ({'BETTER' if diff > 0 else 'WORSE'})")
    lgbm_player_df = pd.DataFrame(lgbm_player_results).sort_values("mean_brier")
    print(lgbm_player_df.to_string(index=False))

    # -- Summary --
    print("\n" + "=" * 60)
    print("RESULTS SUMMARY - XGBOOST")
    print("=" * 60)
    xgb_df = pd.DataFrame(xgb_results).sort_values("mean_brier")
    print(xgb_df.to_string(index=False))
    print(f"\nBest XGB params: {xgb_best_params}")
    print(f"Best XGB CV Brier: {xgb_best_brier:.6f}")

    print("\n" + "=" * 60)
    print("RESULTS SUMMARY - LIGHTGBM")
    print("=" * 60)
    lgbm_df = pd.DataFrame(lgbm_results).sort_values("mean_brier")
    print(lgbm_df.to_string(index=False))
    print(f"\nBest LGBM params: {lgbm_best_params}")
    print(f"Best LGBM CV Brier: {lgbm_best_brier:.6f}")

    # -- Train final models and save predictions --
    xgb_model, xgb_preds, feat_names = train_final_and_predict(
        "XGBoost", xgb_best_params, train_df, pred_df
    )
    lgbm_model, lgbm_preds, _ = train_final_and_predict(
        "LightGBM", lgbm_best_params, train_df, pred_df
    )

    # Train LGBM+Player model if it improved
    if lgbm_player_best_brier < lgbm_best_brier:
        print("\n*** Player features IMPROVED Brier - training final model with player features ***")
        lgbm_p_model, lgbm_p_preds, lgbm_p_feats = train_final_and_predict(
            "LGBM+Player", lgbm_player_best_params, train_df, pred_df
        )
        out_lgbm_p = pred_df[["Season", "TeamLow", "TeamHigh"]].copy()
        out_lgbm_p["Pred"] = lgbm_p_preds
        out_lgbm_p.to_parquet("data/processed/preds_lgbm_player.parquet", index=False)
        print(f"Saved LGBM+Player predictions to data/processed/preds_lgbm_player.parquet")
    else:
        print("\n*** Player features did NOT improve Brier - sticking with team-only model ***")

    # Save XGBoost predictions
    out_xgb = pred_df[["Season", "TeamLow", "TeamHigh"]].copy()
    out_xgb["Pred"] = xgb_preds
    out_xgb.to_parquet("data/processed/preds_xgb.parquet", index=False)
    print(f"\nSaved XGB predictions to data/processed/preds_xgb.parquet ({len(out_xgb)} matchups)")

    # Save LightGBM predictions
    out_lgbm = pred_df[["Season", "TeamLow", "TeamHigh"]].copy()
    out_lgbm["Pred"] = lgbm_preds
    out_lgbm.to_parquet("data/processed/preds_lgbm.parquet", index=False)
    print(f"Saved LGBM predictions to data/processed/preds_lgbm.parquet ({len(out_lgbm)} matchups)")

    # -- Final comparison --
    print("\n" + "=" * 60)
    print("FINAL COMPARISON")
    print("=" * 60)
    print(f"XGBoost  best CV Brier: {xgb_best_brier:.6f}")
    print(f"LightGBM best CV Brier: {lgbm_best_brier:.6f}")
    winner = "XGBoost" if xgb_best_brier < lgbm_best_brier else "LightGBM"
    print(f"Winner: {winner}")

    # Prediction correlation
    corr = np.corrcoef(xgb_preds, lgbm_preds)[0, 1]
    print(f"Prediction correlation (XGB vs LGBM): {corr:.4f}")
    print(f"Mean pred XGB: {np.mean(xgb_preds):.4f}, LGBM: {np.mean(lgbm_preds):.4f}")


if __name__ == "__main__":
    main()
