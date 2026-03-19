"""Train Logistic Regression with ElasticNet regularization."""

import sys
import os
import warnings

# Allow imports from project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Suppress sklearn deprecation warnings
warnings.filterwarnings("ignore", category=FutureWarning)

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression

from src.data.prepare import prepare_for_linear, augment_training_data, CORE_FEATURES
from src.models.train import cross_validate


def main():
    # Load data
    train_df = pd.read_parquet("data/processed/training_matchups.parquet")
    pred_df = pd.read_parquet("data/processed/prediction_matchups_2026.parquet")

    print(f"Training data: {train_df.shape}")
    print(f"Prediction data: {pred_df.shape}")
    print(f"Features: {len(CORE_FEATURES)}")
    print()

    # Hyperparameter grid
    l1_ratios = [0.0, 0.25, 0.5, 0.75, 1.0]
    C_values = [0.01, 0.1, 1.0, 10.0]

    best_brier = float("inf")
    best_params = {}
    results = []

    for C in C_values:
        for l1_ratio in l1_ratios:
            # Build model kwargs using the new sklearn API style.
            # saga solver supports all penalty types via l1_ratio parameter.
            model_kwargs = {
                "C": C,
                "solver": "saga",
                "l1_ratio": l1_ratio,
                "penalty": "elasticnet",
                "max_iter": 5000,
            }

            # Capture current kwargs in closure
            _kwargs = dict(model_kwargs)

            def make_model(X, y, _kw=_kwargs):
                model = LogisticRegression(**_kw)
                model.fit(X, y)
                return model

            print(f"=== C={C}, l1_ratio={l1_ratio} ===")
            cv_result = cross_validate(
                model_fn=make_model,
                train_df=train_df,
                prepare_fn=prepare_for_linear,
                prepare_kwargs={"features": CORE_FEATURES},
                augment=True,
            )

            mean_brier = cv_result["mean_brier"]
            results.append({
                "C": C,
                "l1_ratio": l1_ratio,
                "mean_brier": mean_brier,
                "overall_brier": cv_result["overall_brier"],
            })

            if mean_brier < best_brier:
                best_brier = mean_brier
                best_params = {"C": C, "l1_ratio": l1_ratio}

            print()

    # Summary table
    print("=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    results_df = pd.DataFrame(results)
    print(results_df.to_string(index=False))
    print()

    print(f"Best params: C={best_params['C']}, l1_ratio={best_params['l1_ratio']}")
    print(f"Best CV Brier score: {best_brier:.6f}")
    print()

    # Train final model on all training data with best hyperparameters
    print("Training final model on all data...")
    final_kwargs = {
        "C": best_params["C"],
        "penalty": "elasticnet",
        "solver": "saga",
        "l1_ratio": best_params["l1_ratio"],
        "max_iter": 5000,
    }

    X_train, y_train, X_pred, scaler, feature_names = prepare_for_linear(
        train_df, pred_df, features=CORE_FEATURES
    )

    # Augment full training data
    X_train_aug, y_train_aug = augment_training_data(X_train, y_train)

    final_model = LogisticRegression(**final_kwargs)
    final_model.fit(X_train_aug, y_train_aug)

    # Generate predictions for 2026 matchups
    preds = final_model.predict_proba(X_pred)[:, 1]
    preds = np.clip(preds, 0.001, 0.999)

    out = pred_df[["Season", "TeamLow", "TeamHigh"]].copy()
    out["Pred"] = preds
    out.to_parquet("data/processed/preds_logistic.parquet", index=False)
    print(f"Saved predictions to data/processed/preds_logistic.parquet ({len(out)} matchups)")

    # Feature importance via coefficients
    print("\nFeature coefficients (absolute value):")
    coef_df = pd.DataFrame({
        "feature": feature_names,
        "coefficient": final_model.coef_[0],
        "abs_coef": np.abs(final_model.coef_[0]),
    }).sort_values("abs_coef", ascending=False)
    print(coef_df.to_string(index=False))

    print(f"\nBest CV Brier score: {best_brier:.6f}")


if __name__ == "__main__":
    main()
