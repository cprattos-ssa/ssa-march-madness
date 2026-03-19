"""Phase 3: Data preparation - feature selection, scaling, CV splits."""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import os


# Curated feature sets based on importance analysis and collinearity
CORE_FEATURES = [
    # Top predictors (all 3 methods agree)
    "Elo_diff",
    "SeedNum_diff",
    "SOS_diff",
    # Efficiency (low collinearity with above)
    "OffEff_diff",
    "DefEff_diff",
    # Four factors
    "eFGPct_diff",
    "TOPct_diff",
    "ORBPct_diff",
    "FTRate_diff",
    # Defensive four factors
    "OppeFGPct_diff",
    "OppTOPct_diff",
    "DRBPct_diff",
    "OppFTRate_diff",
    # Shooting
    "FG3Pct_diff",
    "FG3Rate_diff",
    # Other
    "Tempo_diff",
    "AstRate_diff",
    "StlRate_diff",
    "BlkRate_diff",
    # Coach
    "CoachTourneyWins_diff",
    "CoachSeasonsExp_diff",
]

# Extended set for tree models (can handle collinearity + NaN)
EXTENDED_FEATURES = CORE_FEATURES + [
    "EloPreTourney_diff",
    "WinPct_diff",
    "PointDiff_diff",
    "OWP_diff",
    "OOWP_diff",
    "Games_diff",
    "SeedInv_diff",
    "SeedHistWinPct_diff",
    "CoachTourneyApps_diff",
    "PointsPerGame_diff",
    "OppPointsPerGame_diff",
    # Sundberg features (partial coverage)
    "ADJOE_diff",
    "ADJDE_diff",
    "BARTHAG_diff",
    "WAB_diff",
    "ADJ_T_diff",
    "3P_O_diff",
    "3P_D_diff",
    "TOR_diff",
    "TORD_diff",
]


def build_cv_splits(
    train_df: pd.DataFrame,
    n_recent: int = 5,
) -> list[tuple[np.ndarray, np.ndarray]]:
    """Leave-one-tournament-out cross-validation splits.

    Uses the most recent n_recent seasons as individual validation folds.
    Earlier seasons are always in training.

    Returns:
        List of (train_idx, val_idx) tuples
    """
    seasons = sorted(train_df["Season"].unique())
    val_seasons = seasons[-n_recent:]
    early_seasons = seasons[:-n_recent]

    splits = []
    for val_season in val_seasons:
        train_mask = train_df["Season"] != val_season
        val_mask = train_df["Season"] == val_season
        splits.append((
            np.where(train_mask)[0],
            np.where(val_mask)[0],
        ))

    return splits


def prepare_for_linear(
    train_df: pd.DataFrame,
    pred_df: pd.DataFrame,
    features: list[str] = None,
) -> tuple:
    """Prepare data for linear/logistic models: fill NaN, scale.

    Returns:
        (X_train, y_train, X_pred, scaler, feature_names)
    """
    if features is None:
        features = CORE_FEATURES

    # Only use features that exist in both datasets
    features = [f for f in features if f in train_df.columns and f in pred_df.columns]

    X_train = train_df[features].copy()
    y_train = train_df["Target"].values
    X_pred = pred_df[features].copy()

    # Fill NaN with 0 (no advantage for either team)
    X_train = X_train.fillna(0)
    X_pred = X_pred.fillna(0)

    # Standardize
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_pred_scaled = scaler.transform(X_pred)

    return X_train_scaled, y_train, X_pred_scaled, scaler, features


def prepare_for_trees(
    train_df: pd.DataFrame,
    pred_df: pd.DataFrame,
    features: list[str] = None,
) -> tuple:
    """Prepare data for tree models: keep NaN (XGBoost/LightGBM handle them).

    Returns:
        (X_train, y_train, X_pred, feature_names)
    """
    if features is None:
        features = EXTENDED_FEATURES

    features = [f for f in features if f in train_df.columns and f in pred_df.columns]

    X_train = train_df[features].values
    y_train = train_df["Target"].values
    X_pred = pred_df[features].values

    return X_train, y_train, X_pred, features


def prepare_for_nn(
    train_df: pd.DataFrame,
    pred_df: pd.DataFrame,
    features: list[str] = None,
    n_components: int = 16,
    use_pca: bool = False,
) -> tuple:
    """Prepare data for neural nets: fill NaN, scale, optional PCA.

    Returns:
        (X_train, y_train, X_pred, transformer, feature_names)
    """
    if features is None:
        features = CORE_FEATURES

    features = [f for f in features if f in train_df.columns and f in pred_df.columns]

    X_train = train_df[features].fillna(0).values
    y_train = train_df["Target"].values
    X_pred = pred_df[features].fillna(0).values

    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_pred = scaler.transform(X_pred)

    if use_pca:
        pca = PCA(n_components=n_components)
        X_train = pca.fit_transform(X_train)
        X_pred = pca.transform(X_pred)
        feature_names = [f"PC{i+1}" for i in range(n_components)]
        return X_train, y_train, X_pred, (scaler, pca), feature_names

    return X_train, y_train, X_pred, scaler, features


def augment_training_data(
    X: np.ndarray,
    y: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Double training data by flipping perspective.

    For each matchup (A-B diff, P(A wins)), add (-diff, 1-P(A wins)).
    """
    X_flip = -X
    y_flip = 1.0 - y
    return np.vstack([X, X_flip]), np.concatenate([y, y_flip])


if __name__ == "__main__":
    train = pd.read_parquet("data/processed/training_matchups.parquet")
    pred = pd.read_parquet("data/processed/prediction_matchups_2026.parquet")

    print("=== Data Preparation Summary ===")
    print(f"Training: {train.shape}")
    print(f"Prediction: {pred.shape}")

    # Linear prep
    X_lin, y_lin, X_pred_lin, scaler, feats_lin = prepare_for_linear(train, pred)
    print(f"\nLinear features: {len(feats_lin)}")
    print(f"  X_train: {X_lin.shape}, X_pred: {X_pred_lin.shape}")

    # Tree prep
    X_tree, y_tree, X_pred_tree, feats_tree = prepare_for_trees(train, pred)
    print(f"\nTree features: {len(feats_tree)}")
    print(f"  X_train: {X_tree.shape}, X_pred: {X_pred_tree.shape}")

    # NN prep
    X_nn, y_nn, X_pred_nn, _, feats_nn = prepare_for_nn(train, pred, use_pca=True, n_components=16)
    print(f"\nNN features (PCA): {len(feats_nn)}")
    print(f"  X_train: {X_nn.shape}, X_pred: {X_pred_nn.shape}")

    # Augmented
    X_aug, y_aug = augment_training_data(X_lin, y_lin)
    print(f"\nAugmented linear: {X_aug.shape} (doubled)")

    # CV splits
    splits = build_cv_splits(train)
    print(f"\nCV splits: {len(splits)}")
    for i, (tr, val) in enumerate(splits):
        val_season = train.iloc[val]["Season"].unique()
        print(f"  Fold {i+1}: train={len(tr)}, val={len(val)}, season={val_season}")
