"""Train a Bradley-Terry / Elo-based probabilistic model.

This script:
1. Computes Elo ratings from regular season data with grid-searched hyperparameters
2. Evaluates via leave-one-tournament-out CV (2021-2025)
3. Optionally fits a logistic regression on top of Elo + seed features
4. Generates 2026 predictions for all possible matchups
"""

import sys
import os
import time
from itertools import product

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss

from src.features.elo import compute_elo_ratings


DATA_DIR = "data/raw/kaggle"
OUT_PATH = "data/processed/preds_bt.parquet"

# Focused hyperparameter grid (reduced from 80 to 12 combos)
K_FACTORS = [20, 28]
HOME_ADVANTAGES = [75, 100]
SEASON_CARRYOVERS = [0.7, 0.75, 0.8]

# Validation seasons
VAL_SEASONS = [2021, 2022, 2023, 2024, 2025]


def parse_seed_number(seed_str: str) -> int:
    """Extract numeric seed from seed string like 'W01' or 'X16a'."""
    return int(seed_str[1:3])


def load_data():
    """Load regular season, tournament, and seed data."""
    reg = pd.read_csv(os.path.join(DATA_DIR, "MRegularSeasonCompactResults.csv"))
    tourney = pd.read_csv(os.path.join(DATA_DIR, "MNCAATourneyCompactResults.csv"))
    seeds = pd.read_csv(os.path.join(DATA_DIR, "MNCAATourneySeeds.csv"))
    seeds["SeedNum"] = seeds["Seed"].apply(parse_seed_number)
    return reg, tourney, seeds


def predict_bt(elo_a, elo_b):
    """Bradley-Terry probability: P(A beats B) = 1 / (1 + 10^((EloB - EloA)/400))."""
    return 1.0 / (1.0 + 10.0 ** ((elo_b - elo_a) / 400.0))


def compute_all_season_elos(reg, k, home_advantage, season_carryover):
    """Compute Elo ratings for all seasons in one pass.

    Returns a dict: {season: {team_id: pre_tourney_elo}}.
    """
    elo_df = compute_elo_ratings(
        reg,
        k=k,
        home_advantage=home_advantage,
        season_carryover=season_carryover,
        margin_multiplier=True,
    )
    # Build lookup: season -> {team_id: pre_tourney_elo}
    result = {}
    for season in elo_df["Season"].unique():
        season_data = elo_df[elo_df["Season"] == season]
        result[int(season)] = dict(zip(season_data["TeamID"], season_data["EloPreTourney"]))
    return result


def build_tourney_matchups(tourney_season, elo_dict, seed_map=None):
    """Build feature matrix from tournament games for a given season.

    Returns DataFrame with elo_diff, elo_diff_sq, seed_diff, target, bt_pred.
    TeamA is always the lower TeamID (Kaggle convention).
    """
    w_teams = tourney_season["WTeamID"].values
    l_teams = tourney_season["LTeamID"].values

    team_a = np.minimum(w_teams, l_teams)
    team_b = np.maximum(w_teams, l_teams)

    elo_a = np.array([elo_dict.get(t, 1500.0) for t in team_a])
    elo_b = np.array([elo_dict.get(t, 1500.0) for t in team_b])
    elo_diff = elo_a - elo_b

    if seed_map is not None:
        seed_a = np.array([seed_map.get(t, 8) for t in team_a])
        seed_b = np.array([seed_map.get(t, 8) for t in team_b])
        seed_diff = seed_a - seed_b
    else:
        seed_diff = np.zeros(len(team_a))

    target = (w_teams == team_a).astype(float)
    bt_pred = 1.0 / (1.0 + 10.0 ** ((elo_b - elo_a) / 400.0))

    return pd.DataFrame({
        "TeamA": team_a,
        "TeamB": team_b,
        "elo_a": elo_a,
        "elo_b": elo_b,
        "elo_diff": elo_diff,
        "elo_diff_sq": elo_diff ** 2,
        "seed_diff": seed_diff,
        "target": target,
        "bt_pred": bt_pred,
    })


def evaluate_raw_bt_fast(tourney, seeds, all_elos):
    """Evaluate raw Bradley-Terry predictions using precomputed Elo ratings.

    Returns (mean_brier, fold_scores_dict).
    """
    fold_scores = []
    fold_details = {}

    for season in VAL_SEASONS:
        if season not in all_elos:
            continue
        elo_dict = all_elos[season]

        tourney_season = tourney[tourney["Season"] == season]
        if len(tourney_season) == 0:
            continue

        seeds_season_df = seeds[seeds["Season"] == season]
        seed_map = dict(zip(seeds_season_df["TeamID"], seeds_season_df["SeedNum"]))

        matchups = build_tourney_matchups(tourney_season, elo_dict, seed_map)

        brier = brier_score_loss(matchups["target"].values, matchups["bt_pred"].values)
        fold_scores.append(brier)
        fold_details[season] = brier

    if not fold_scores:
        return float("inf"), {}
    return np.mean(fold_scores), fold_details


def evaluate_logistic_on_elo_fast(tourney, seeds, all_elos):
    """Evaluate logistic regression on Elo features using precomputed ratings.

    For each val season, train on all prior tournament data, predict on val season.
    """
    # Precompute matchups for all tournament seasons
    season_matchups = {}
    for season in sorted(tourney["Season"].unique()):
        s = int(season)
        if s not in all_elos:
            continue
        ts = tourney[tourney["Season"] == s]
        if len(ts) == 0:
            continue
        seeds_s = seeds[seeds["Season"] == s]
        sm = dict(zip(seeds_s["TeamID"], seeds_s["SeedNum"]))
        season_matchups[s] = build_tourney_matchups(ts, all_elos[s], sm)

    fold_scores = []
    fold_details = {}
    all_preds = []
    all_true = []

    features = ["elo_diff", "elo_diff_sq", "seed_diff"]

    for season in VAL_SEASONS:
        if season not in season_matchups:
            continue
        val_matchups = season_matchups[season]

        # Collect training data from all prior seasons
        train_parts = []
        for s in sorted(season_matchups.keys()):
            if s >= season:
                break
            train_parts.append(season_matchups[s])

        if not train_parts:
            continue

        train_data = pd.concat(train_parts, ignore_index=True)

        X_train = train_data[features].values
        y_train = train_data["target"].values
        X_val = val_matchups[features].values
        y_val = val_matchups["target"].values

        lr = LogisticRegression(max_iter=5000, C=1.0)
        lr.fit(X_train, y_train)
        y_pred = lr.predict_proba(X_val)[:, 1]
        y_pred = np.clip(y_pred, 0.001, 0.999)

        brier = brier_score_loss(y_val, y_pred)
        fold_scores.append(brier)
        fold_details[season] = brier
        all_preds.extend(y_pred)
        all_true.extend(y_val)

    if not fold_scores:
        return float("inf"), {}, float("inf")

    mean_brier = np.mean(fold_scores)
    overall_brier = brier_score_loss(all_true, all_preds)
    return mean_brier, fold_details, overall_brier


def main():
    t0 = time.time()
    print("Loading data...")
    reg, tourney, seeds = load_data()
    print(f"  Regular season games: {len(reg)}")
    print(f"  Tournament games: {len(tourney)}")
    print(f"  Seeds entries: {len(seeds)}")
    print(f"  Validation seasons: {VAL_SEASONS}")
    print()

    # ---------------------------------------------------------------
    # Phase 1: Grid search for raw Bradley-Terry (Elo only)
    # ---------------------------------------------------------------
    print("=" * 70)
    print("PHASE 1: Raw Bradley-Terry (Elo-based) - Grid Search")
    print("=" * 70)

    all_results = []
    best_bt_brier = float("inf")
    best_bt_params = {}
    best_bt_folds = {}
    elo_cache = {}  # Cache Elo computations keyed by (k, ha, co)

    total_combos = len(K_FACTORS) * len(HOME_ADVANTAGES) * len(SEASON_CARRYOVERS)
    combo_idx = 0

    for k, ha, co in product(K_FACTORS, HOME_ADVANTAGES, SEASON_CARRYOVERS):
        combo_idx += 1

        # Compute Elo for all seasons in one pass
        key = (k, ha, co)
        all_elos = compute_all_season_elos(reg, k, ha, co)
        elo_cache[key] = all_elos

        mean_brier, fold_details = evaluate_raw_bt_fast(tourney, seeds, all_elos)

        all_results.append({
            "K": k,
            "HomeAdv": ha,
            "Carryover": co,
            "MeanBrier": mean_brier,
        })

        if mean_brier < best_bt_brier:
            best_bt_brier = mean_brier
            best_bt_params = {"K": k, "HomeAdv": ha, "Carryover": co}
            best_bt_folds = fold_details

        if combo_idx % 10 == 0:
            elapsed = time.time() - t0
            print(f"  [{combo_idx}/{total_combos}] {elapsed:.0f}s - best so far: Brier={best_bt_brier:.6f} "
                  f"(K={best_bt_params['K']}, HA={best_bt_params['HomeAdv']}, "
                  f"CO={best_bt_params['Carryover']})")

    print()
    print(f"Best raw BT params: K={best_bt_params['K']}, "
          f"HomeAdv={best_bt_params['HomeAdv']}, "
          f"Carryover={best_bt_params['Carryover']}")
    print(f"Best raw BT mean Brier: {best_bt_brier:.6f}")
    print(f"  Per-fold Brier scores: {best_bt_folds}")
    print()

    # Top 10 results
    results_df = pd.DataFrame(all_results).sort_values("MeanBrier")
    print("Top 10 raw BT configurations:")
    print(results_df.head(10).to_string(index=False))
    print()

    # ---------------------------------------------------------------
    # Phase 2: Logistic regression on top of Elo features
    # ---------------------------------------------------------------
    print("=" * 70)
    print("PHASE 2: Logistic Regression on Elo + Seed Features")
    print("=" * 70)

    # Use top-5 BT configs for logistic regression search
    top_configs = results_df.head(5)
    best_lr_brier = float("inf")
    best_lr_params = {}
    best_lr_folds = {}
    lr_results = []

    for _, row in top_configs.iterrows():
        k = int(row["K"])
        ha = int(row["HomeAdv"])
        co = float(row["Carryover"])

        key = (k, ha, co)
        all_elos = elo_cache[key]

        mean_brier, fold_details, overall_brier = evaluate_logistic_on_elo_fast(
            tourney, seeds, all_elos
        )

        lr_results.append({
            "K": k,
            "HomeAdv": ha,
            "Carryover": co,
            "MeanBrier": mean_brier,
            "OverallBrier": overall_brier,
        })

        print(f"  K={k}, HA={ha}, CO={co}: Mean Brier={mean_brier:.6f}, "
              f"Overall={overall_brier:.6f}")
        print(f"    Per-fold: {fold_details}")

        if mean_brier < best_lr_brier:
            best_lr_brier = mean_brier
            best_lr_params = {"K": k, "HomeAdv": ha, "Carryover": co}
            best_lr_folds = fold_details

    print()
    print(f"Best LR-on-Elo params: K={best_lr_params['K']}, "
          f"HomeAdv={best_lr_params['HomeAdv']}, "
          f"Carryover={best_lr_params['Carryover']}")
    print(f"Best LR-on-Elo mean Brier: {best_lr_brier:.6f}")
    print()

    # ---------------------------------------------------------------
    # Phase 3: Choose best approach and generate 2026 predictions
    # ---------------------------------------------------------------
    print("=" * 70)
    print("PHASE 3: Final Model and 2026 Predictions")
    print("=" * 70)

    use_lr = best_lr_brier < best_bt_brier
    if use_lr:
        print(f"Using logistic regression model (Brier={best_lr_brier:.6f} vs raw BT={best_bt_brier:.6f})")
        final_params = best_lr_params
        final_folds = best_lr_folds
    else:
        print(f"Using raw Bradley-Terry model (Brier={best_bt_brier:.6f} vs LR={best_lr_brier:.6f})")
        final_params = best_bt_params
        final_folds = best_bt_folds

    final_k = final_params["K"]
    final_ha = final_params["HomeAdv"]
    final_co = final_params["Carryover"]

    print(f"Final params: K={final_k}, HomeAdv={final_ha}, Carryover={final_co}")
    print(f"Final per-fold scores: {final_folds}")
    print()

    # Get the precomputed Elo for the final params (includes 2026)
    key = (final_k, final_ha, final_co)
    all_elos = elo_cache[key]

    if 2026 not in all_elos:
        print("WARNING: 2026 not in precomputed Elos, recomputing...")
        all_elos = compute_all_season_elos(reg, final_k, final_ha, final_co)

    elo_dict_2026 = all_elos[2026]
    print(f"  Teams with 2026 Elo ratings: {len(elo_dict_2026)}")

    # Get 2026 tournament seeds
    seeds_2026 = seeds[seeds["Season"] == 2026]
    seed_map_2026 = dict(zip(seeds_2026["TeamID"], seeds_2026["SeedNum"]))
    tourney_teams_2026 = sorted(seeds_2026["TeamID"].unique())
    print(f"  2026 tournament teams: {len(tourney_teams_2026)}")
    print()

    final_lr = None
    if use_lr:
        # Train logistic regression on all historical tournament data
        print("Training final logistic regression on all historical tournament data...")
        train_parts = []
        for season in sorted(tourney["Season"].unique()):
            s = int(season)
            if s not in all_elos:
                continue
            ts = tourney[tourney["Season"] == s]
            if len(ts) == 0:
                continue
            seeds_s = seeds[seeds["Season"] == s]
            sm = dict(zip(seeds_s["TeamID"], seeds_s["SeedNum"]))
            train_parts.append(build_tourney_matchups(ts, all_elos[s], sm))

        all_train = pd.concat(train_parts, ignore_index=True)
        features = ["elo_diff", "elo_diff_sq", "seed_diff"]
        X_all = all_train[features].values
        y_all = all_train["target"].values

        final_lr = LogisticRegression(max_iter=5000, C=1.0)
        final_lr.fit(X_all, y_all)
        print(f"  Trained on {len(all_train)} tournament games")
        print(f"  Coefficients: {dict(zip(features, final_lr.coef_[0].round(6)))}")
        print(f"  Intercept: {final_lr.intercept_[0]:.6f}")
        print()

    # Generate predictions for all 2026 team pairs (P(low ID beats high ID))
    print("Generating 2026 predictions...")
    n_teams = len(tourney_teams_2026)
    n_pairs = n_teams * (n_teams - 1) // 2

    seasons = np.full(n_pairs, 2026, dtype=int)
    team_a_arr = np.empty(n_pairs, dtype=int)
    team_b_arr = np.empty(n_pairs, dtype=int)
    elo_diff_arr = np.empty(n_pairs)
    seed_diff_arr = np.empty(n_pairs)

    idx = 0
    for i, ta in enumerate(tourney_teams_2026):
        for tb in tourney_teams_2026[i + 1:]:
            team_a_arr[idx] = ta
            team_b_arr[idx] = tb
            elo_a = elo_dict_2026.get(ta, 1500.0)
            elo_b = elo_dict_2026.get(tb, 1500.0)
            elo_diff_arr[idx] = elo_a - elo_b
            seed_diff_arr[idx] = seed_map_2026.get(ta, 8) - seed_map_2026.get(tb, 8)
            idx += 1

    if use_lr and final_lr is not None:
        X_pred = np.column_stack([elo_diff_arr, elo_diff_arr ** 2, seed_diff_arr])
        preds = final_lr.predict_proba(X_pred)[:, 1]
    else:
        elo_b_arr_vals = np.array([elo_dict_2026.get(t, 1500.0) for t in team_b_arr])
        elo_a_arr_vals = np.array([elo_dict_2026.get(t, 1500.0) for t in team_a_arr])
        preds = 1.0 / (1.0 + 10.0 ** ((elo_b_arr_vals - elo_a_arr_vals) / 400.0))

    preds = np.clip(preds, 0.001, 0.999)

    pred_df = pd.DataFrame({
        "Season": seasons,
        "TeamID_A": team_a_arr,
        "TeamID_B": team_b_arr,
        "Pred": np.round(preds, 6),
    })
    pred_df.to_parquet(OUT_PATH, index=False)
    print(f"  Saved {len(pred_df)} predictions to {OUT_PATH}")
    print()

    # Summary stats
    elapsed = time.time() - t0
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Raw BT best CV Brier:        {best_bt_brier:.6f}")
    print(f"  Params: K={best_bt_params['K']}, HA={best_bt_params['HomeAdv']}, CO={best_bt_params['Carryover']}")
    print(f"  Per-fold: {best_bt_folds}")
    print(f"LR-on-Elo best CV Brier:     {best_lr_brier:.6f}")
    print(f"  Params: K={best_lr_params['K']}, HA={best_lr_params['HomeAdv']}, CO={best_lr_params['Carryover']}")
    print(f"  Per-fold: {best_lr_folds}")
    print(f"Final model: {'Logistic Regression on Elo' if use_lr else 'Raw Bradley-Terry'}")
    print(f"Prediction stats: mean={pred_df['Pred'].mean():.4f}, "
          f"std={pred_df['Pred'].std():.4f}, "
          f"min={pred_df['Pred'].min():.4f}, "
          f"max={pred_df['Pred'].max():.4f}")
    print(f"Total runtime: {elapsed:.1f}s")


if __name__ == "__main__":
    main()
