"""Shared model training utilities."""

import numpy as np
import pandas as pd
from sklearn.metrics import brier_score_loss, log_loss
from src.data.prepare import build_cv_splits


def cross_validate(
    model_fn,
    train_df: pd.DataFrame,
    prepare_fn,
    prepare_kwargs: dict = None,
    n_folds: int = 5,
    augment: bool = False,
) -> dict:
    """Run leave-one-tournament-out CV and return Brier scores.

    Args:
        model_fn: Callable that takes (X_train, y_train) and returns a fitted model with .predict_proba
        train_df: Training matchup DataFrame
        prepare_fn: Function to prepare features (prepare_for_linear, prepare_for_trees, etc.)
        prepare_kwargs: Extra kwargs for prepare_fn
        n_folds: Number of CV folds
        augment: Whether to augment training data

    Returns:
        Dict with per-fold and mean Brier scores
    """
    if prepare_kwargs is None:
        prepare_kwargs = {}

    splits = build_cv_splits(train_df, n_recent=n_folds)
    fold_scores = []
    all_preds = []
    all_true = []

    for fold_idx, (train_idx, val_idx) in enumerate(splits):
        train_fold = train_df.iloc[train_idx]
        val_fold = train_df.iloc[val_idx]

        # Prepare features
        # We need a dummy pred_df for the prepare function - use val_fold
        X_train, y_train, X_val, *rest = prepare_fn(train_fold, val_fold, **prepare_kwargs)

        # Augment if requested
        if augment:
            from src.data.prepare import augment_training_data
            X_train, y_train = augment_training_data(X_train, y_train)

        # Train and predict
        model = model_fn(X_train, y_train)

        if hasattr(model, "predict_proba"):
            y_pred = model.predict_proba(X_val)[:, 1]
        else:
            y_pred = model.predict(X_val)

        # Clip to avoid log(0)
        y_pred = np.clip(y_pred, 0.001, 0.999)

        brier = brier_score_loss(val_fold["Target"].values, y_pred)
        fold_scores.append(brier)
        all_preds.extend(y_pred)
        all_true.extend(val_fold["Target"].values)

        season = val_fold["Season"].iloc[0]
        print(f"  Fold {fold_idx+1} (season {season}): Brier = {brier:.4f}")

    mean_brier = np.mean(fold_scores)
    overall_brier = brier_score_loss(all_true, all_preds)

    print(f"  Mean Brier: {mean_brier:.4f}")
    print(f"  Overall Brier: {overall_brier:.4f}")

    return {
        "fold_scores": fold_scores,
        "mean_brier": mean_brier,
        "overall_brier": overall_brier,
        "predictions": all_preds,
        "true_values": all_true,
    }
