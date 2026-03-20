"""Orchestrate feature building: compute all features and create matchup-level training data."""

import pandas as pd
import numpy as np
import os

from src.features.elo import compute_elo_ratings
from src.features.efficiency import compute_team_season_stats
from src.features.seeds import build_seed_features
from src.features.strength_of_schedule import compute_sos
from src.features.player_features import (
    load_player_data, map_schools_to_team_ids, aggregate_player_features,
)


def load_kaggle_data(data_dir: str = "data/raw/kaggle", gender: str = "mens") -> dict:
    """Load all relevant Kaggle CSVs for the given gender."""
    prefix = "M" if gender == "mens" else "W"
    data = {}
    data["compact"] = pd.read_csv(os.path.join(data_dir, f"{prefix}RegularSeasonCompactResults.csv"))
    data["detailed"] = pd.read_csv(os.path.join(data_dir, f"{prefix}RegularSeasonDetailedResults.csv"))
    data["tourney_compact"] = pd.read_csv(os.path.join(data_dir, f"{prefix}NCAATourneyCompactResults.csv"))
    data["seeds"] = pd.read_csv(os.path.join(data_dir, f"{prefix}NCAATourneySeeds.csv"))
    data["teams"] = pd.read_csv(os.path.join(data_dir, f"{prefix}Teams.csv"))
    data["coaches"] = pd.read_csv(os.path.join(data_dir, f"{prefix}TeamCoaches.csv"))
    if gender == "mens":
        data["tourney_detailed"] = pd.read_csv(os.path.join(data_dir, f"{prefix}NCAATourneyDetailedResults.csv"))
    return data


def load_external_data(data_dir: str = "data/raw/external") -> dict:
    """Load external datasets."""
    ext = {}
    # Sundberg - advanced stats per season
    sundberg_files = [f for f in os.listdir(os.path.join(data_dir, "sundberg")) if f.endswith(".csv")]
    sundberg_dfs = []
    for f in sundberg_files:
        df = pd.read_csv(os.path.join(data_dir, "sundberg", f))
        if "YEAR" not in df.columns and f != "cbb.csv":
            # Individual year files (cbb13.csv, etc.) - extract year from filename
            year_str = f.replace("cbb", "").replace(".csv", "")
            if year_str.isdigit():
                df["YEAR"] = 2000 + int(year_str)
        sundberg_dfs.append(df)
    ext["sundberg"] = pd.concat(sundberg_dfs, ignore_index=True)

    # Amin - KenPom/Barttorvik
    kenpom_path = os.path.join(data_dir, "amin", "KenPom Barttorvik.csv")
    if os.path.exists(kenpom_path):
        ext["amin_kenpom"] = pd.read_csv(kenpom_path)

    # Amin - Resumes (has Elo, NET, WAB)
    resumes_path = os.path.join(data_dir, "amin", "Resumes.csv")
    if os.path.exists(resumes_path):
        ext["amin_resumes"] = pd.read_csv(resumes_path)

    return ext


def build_team_name_mapping(teams: pd.DataFrame, spellings_path: str) -> dict:
    """Build mapping from external team names to Kaggle TeamIDs."""
    spellings = pd.read_csv(spellings_path, encoding="latin-1")
    name_to_id = {}
    for _, row in spellings.iterrows():
        name_to_id[row["TeamNameSpelling"].lower().strip()] = row["TeamID"]
    # Also add official names
    for _, row in teams.iterrows():
        name_to_id[row["TeamName"].lower().strip()] = row["TeamID"]
    return name_to_id


def merge_external_features(
    team_features: pd.DataFrame,
    external: dict,
    name_to_id: dict,
) -> pd.DataFrame:
    """Merge external data (Sundberg, Amin) into team features by name matching."""
    # Sundberg: ADJOE, ADJDE, BARTHAG, WAB, EFG_O, EFG_D, etc.
    if "sundberg" in external:
        sund = external["sundberg"].copy()
        if "YEAR" in sund.columns:
            sund["TeamID"] = sund["TEAM"].str.lower().str.strip().map(name_to_id)
            sund = sund.dropna(subset=["TeamID"])
            sund["TeamID"] = sund["TeamID"].astype(int)

            # Select non-redundant columns based on collinearity analysis
            sund_cols = ["TeamID", "YEAR", "ADJOE", "ADJDE", "BARTHAG",
                         "TOR", "TORD", "ORB", "DRB", "FTR", "FTRD",
                         "3P_O", "3P_D", "ADJ_T", "WAB"]
            sund_cols = [c for c in sund_cols if c in sund.columns]
            sund_merge = sund[sund_cols].rename(columns={"YEAR": "Season"})

            team_features = team_features.merge(
                sund_merge, on=["Season", "TeamID"], how="left", suffixes=("", "_sund")
            )

    return team_features


def compute_coach_features(coaches: pd.DataFrame, tourney_results: pd.DataFrame) -> pd.DataFrame:
    """Compute coach experience and tournament history features."""
    records = []
    coach_tourney_history = {}

    for season in sorted(coaches["Season"].unique()):
        season_coaches = coaches[coaches["Season"] == season]

        # Get end-of-season coach for each team
        end_coaches = season_coaches.loc[season_coaches.groupby("TeamID")["LastDayNum"].idxmax()]

        for _, row in end_coaches.iterrows():
            coach = row["CoachName"]
            team = row["TeamID"]

            # Count prior seasons as head coach
            prior = coaches[(coaches["CoachName"] == coach) & (coaches["Season"] < season)]
            seasons_as_hc = prior["Season"].nunique()

            # Tournament history
            if coach not in coach_tourney_history:
                coach_tourney_history[coach] = {"appearances": 0, "wins": 0}

            hist = coach_tourney_history[coach]

            records.append({
                "Season": season,
                "TeamID": team,
                "CoachName": coach,
                "CoachSeasonsExp": seasons_as_hc,
                "CoachTourneyApps": hist["appearances"],
                "CoachTourneyWins": hist["wins"],
            })

        # Update tourney history after recording (so it's historical, not including current)
        season_tourney = tourney_results[tourney_results["Season"] == season]
        tourney_coaches = set()
        for _, game in season_tourney.iterrows():
            w_coach_row = end_coaches[end_coaches["TeamID"] == game["WTeamID"]]
            l_coach_row = end_coaches[end_coaches["TeamID"] == game["LTeamID"]]
            if len(w_coach_row) > 0:
                wc = w_coach_row.iloc[0]["CoachName"]
                if wc not in coach_tourney_history:
                    coach_tourney_history[wc] = {"appearances": 0, "wins": 0}
                coach_tourney_history[wc]["wins"] += 1
                tourney_coaches.add(wc)
            if len(l_coach_row) > 0:
                lc = l_coach_row.iloc[0]["CoachName"]
                tourney_coaches.add(lc)

        for c in tourney_coaches:
            if c not in coach_tourney_history:
                coach_tourney_history[c] = {"appearances": 0, "wins": 0}
            coach_tourney_history[c]["appearances"] += 1

    return pd.DataFrame(records)


def build_all_team_features(
    data: dict,
    external: dict,
    name_to_id: dict,
    min_season: int = 2003,
) -> pd.DataFrame:
    """Build complete team-season feature matrix."""
    # 1. Elo ratings
    all_games = pd.concat([data["compact"], data.get("tourney_compact", pd.DataFrame())])
    elo = compute_elo_ratings(all_games)
    print(f"  Elo: {len(elo)} team-seasons")

    # 2. Efficiency from detailed box scores
    eff = compute_team_season_stats(data["detailed"])
    print(f"  Efficiency: {len(eff)} team-seasons")

    # 3. Strength of schedule
    sos = compute_sos(data["compact"])
    print(f"  SOS: {len(sos)} team-seasons")

    # 4. Seed features
    seed_feats = build_seed_features(data["seeds"])
    print(f"  Seeds: {len(seed_feats)} team-seasons")

    # 5. Coach features
    coach_feats = compute_coach_features(data["coaches"], data.get("tourney_compact", pd.DataFrame()))
    print(f"  Coach: {len(coach_feats)} team-seasons")

    # Merge everything
    team_features = elo.merge(eff, on=["Season", "TeamID"], how="outer")
    team_features = team_features.merge(sos, on=["Season", "TeamID"], how="left")
    team_features = team_features.merge(seed_feats, on=["Season", "TeamID"], how="left")
    team_features = team_features.merge(
        coach_feats.drop(columns=["CoachName"], errors="ignore"),
        on=["Season", "TeamID"], how="left"
    )

    # 6. External data
    team_features = merge_external_features(team_features, external, name_to_id)

    # 7. Player-level features (Barttorvik, 2021-2026 only)
    player_data_dir = os.path.join("data", "raw", "external", "player_data")
    if os.path.exists(player_data_dir):
        player_seasons = list(range(2021, 2027))
        players = load_player_data(player_data_dir, player_seasons)
        if len(players) > 0:
            players = map_schools_to_team_ids(players, name_to_id)
            player_feats = aggregate_player_features(players)
            team_features = team_features.merge(
                player_feats, on=["Season", "TeamID"], how="left"
            )
            matched = player_feats.TeamID.nunique()
            print(f"  Player features: {len(player_feats)} team-seasons ({matched} teams matched)")

    # Filter to seasons with detailed data
    team_features = team_features[team_features["Season"] >= min_season]

    print(f"  Final team features: {team_features.shape}")
    return team_features


def build_matchup_features(
    team_features: pd.DataFrame,
    tourney_results: pd.DataFrame,
    season_predict: int = 2026,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Build matchup-level features for training and prediction.

    For training: use historical tournament matchups with known outcomes.
    For prediction: use 2026 team features for all possible matchups.

    Returns:
        (training_df, prediction_df)
    """
    # --- TRAINING DATA ---
    train_rows = []
    hist_tourney = tourney_results[tourney_results["Season"] < season_predict]

    for _, game in hist_tourney.iterrows():
        season = game["Season"]
        w_id = game["WTeamID"]
        l_id = game["LTeamID"]

        # Canonical ordering: lower TeamID = TeamA
        team_low = min(w_id, l_id)
        team_high = max(w_id, l_id)
        target = 1.0 if w_id == team_low else 0.0  # P(low beats high)

        feat_low = team_features[(team_features["Season"] == season) & (team_features["TeamID"] == team_low)]
        feat_high = team_features[(team_features["Season"] == season) & (team_features["TeamID"] == team_high)]

        if len(feat_low) == 0 or len(feat_high) == 0:
            continue

        row = {"Season": season, "TeamLow": team_low, "TeamHigh": team_high, "Target": target}

        # Compute differentials (low - high) for all numeric features
        numeric_cols = feat_low.select_dtypes(include=[np.number]).columns
        skip_cols = {"Season", "TeamID"}

        for col in numeric_cols:
            if col in skip_cols:
                continue
            val_low = feat_low[col].values[0]
            val_high = feat_high[col].values[0]
            if pd.notna(val_low) and pd.notna(val_high):
                row[f"{col}_diff"] = val_low - val_high

        train_rows.append(row)

    training_df = pd.DataFrame(train_rows)

    # --- PREDICTION DATA ---
    pred_rows = []
    pred_teams = team_features[team_features["Season"] == season_predict]
    team_ids = sorted(pred_teams["TeamID"].unique())

    for i, t_low in enumerate(team_ids):
        for t_high in team_ids[i+1:]:
            feat_low = pred_teams[pred_teams["TeamID"] == t_low]
            feat_high = pred_teams[pred_teams["TeamID"] == t_high]

            if len(feat_low) == 0 or len(feat_high) == 0:
                continue

            row = {"Season": season_predict, "TeamLow": t_low, "TeamHigh": t_high}

            numeric_cols = feat_low.select_dtypes(include=[np.number]).columns
            skip_cols = {"Season", "TeamID"}

            for col in numeric_cols:
                if col in skip_cols:
                    continue
                val_low = feat_low[col].values[0]
                val_high = feat_high[col].values[0]
                if pd.notna(val_low) and pd.notna(val_high):
                    row[f"{col}_diff"] = val_low - val_high

            pred_rows.append(row)

    prediction_df = pd.DataFrame(pred_rows)

    print(f"  Training matchups: {training_df.shape}")
    print(f"  Prediction matchups: {prediction_df.shape}")

    return training_df, prediction_df


if __name__ == "__main__":
    print("Loading Kaggle data...")
    data = load_kaggle_data()

    print("Loading external data...")
    external = load_external_data()

    print("Building team name mapping...")
    name_to_id = build_team_name_mapping(
        data["teams"], "data/raw/kaggle/MTeamSpellings.csv"
    )

    print("Building team features...")
    team_features = build_all_team_features(data, external, name_to_id)

    print("Building matchup features...")
    train_df, pred_df = build_matchup_features(
        team_features, data["tourney_compact"]
    )

    # Save
    os.makedirs("data/processed", exist_ok=True)
    team_features.to_parquet("data/processed/team_features.parquet", index=False)
    train_df.to_parquet("data/processed/training_matchups.parquet", index=False)
    pred_df.to_parquet("data/processed/prediction_matchups_2026.parquet", index=False)

    print("\nSaved to data/processed/")
    print(f"  team_features: {team_features.shape}")
    print(f"  training_matchups: {train_df.shape}")
    print(f"  prediction_matchups_2026: {pred_df.shape}")
