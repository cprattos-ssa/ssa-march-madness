"""Evaluation metrics for tournament prediction."""

import numpy as np
from sklearn.metrics import brier_score_loss, log_loss
from sklearn.calibration import calibration_curve


def brier_score(y_true: np.ndarray, y_prob: np.ndarray) -> float:
    """Compute Brier score (lower is better). This is the competition metric."""
    return brier_score_loss(y_true, y_prob)


def competition_log_loss(y_true: np.ndarray, y_prob: np.ndarray) -> float:
    """Compute log loss (for comparison)."""
    return log_loss(y_true, y_prob)


def calibration_stats(
    y_true: np.ndarray, y_prob: np.ndarray, n_bins: int = 10
) -> dict:
    """Compute calibration curve statistics."""
    fraction_of_positives, mean_predicted_value = calibration_curve(
        y_true, y_prob, n_bins=n_bins
    )
    calibration_error = np.mean(np.abs(fraction_of_positives - mean_predicted_value))
    return {
        "fraction_of_positives": fraction_of_positives,
        "mean_predicted_value": mean_predicted_value,
        "mean_calibration_error": calibration_error,
    }
