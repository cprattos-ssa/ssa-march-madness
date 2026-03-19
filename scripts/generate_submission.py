"""Phase 6: Generate Kaggle submission CSV files."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
import pandas as pd


def load_sample_submission(stage=2):
    """Load the sample submission to get required IDs."""
    path = f"data/raw/kaggle/SampleSubmissionStage{stage}.csv"
    return pd.read_csv(path)


def parse_submission_id(id_str):
    """Parse '2026_1104_1112' into (season, team_low, team_high)."""
    parts = id_str.split("_")
    return int(parts[0]), int(parts[1]), int(parts[2])


def build_submission(ensemble_path, sample_sub, output_path, default_pred=0.5):
    """Build submission CSV by matching ensemble predictions to required IDs.

    Args:
        ensemble_path: Path to ensemble parquet with predictions
        sample_sub: Sample submission DataFrame
        output_path: Where to save the submission CSV
        default_pred: Default prediction for matchups without model predictions
    """
    ensemble = pd.read_parquet(ensemble_path)

    # Identify team columns in ensemble
    team_cols = [c for c in ensemble.columns if "Team" in c]
    if len(team_cols) >= 2:
        low_col = [c for c in team_cols if "Low" in c or "A" in c or "ID_A" in c]
        high_col = [c for c in team_cols if "High" in c or "B" in c or "ID_B" in c]
        if low_col and high_col:
            low_col = low_col[0]
            high_col = high_col[0]
        else:
            low_col = team_cols[0]
            high_col = team_cols[1]
    else:
        raise ValueError(f"Cannot identify team columns in {team_cols}")

    # Build lookup: (season, team_low, team_high) -> prediction
    season_col = [c for c in ensemble.columns if "Season" in c or "season" in c]
    if season_col:
        season_col = season_col[0]
    else:
        ensemble["Season"] = 2026
        season_col = "Season"

    lookup = {}
    for _, row in ensemble.iterrows():
        season = int(row[season_col])
        t_low = int(row[low_col])
        t_high = int(row[high_col])
        key = (season, min(t_low, t_high), max(t_low, t_high))
        lookup[key] = row["Pred"]

    # Build submission
    predictions = []
    missing_count = 0

    for _, row in sample_sub.iterrows():
        id_str = row["ID"]
        season, t_low, t_high = parse_submission_id(id_str)
        key = (season, t_low, t_high)

        if key in lookup:
            pred = lookup[key]
        else:
            pred = default_pred
            missing_count += 1

        predictions.append({"ID": id_str, "Pred": np.clip(pred, 0.001, 0.999)})

    sub_df = pd.DataFrame(predictions)

    print(f"  Total matchups: {len(sub_df)}")
    print(f"  Matched: {len(sub_df) - missing_count}")
    print(f"  Missing (default={default_pred}): {missing_count}")
    print(f"  Pred range: [{sub_df['Pred'].min():.4f}, {sub_df['Pred'].max():.4f}]")
    print(f"  Pred mean: {sub_df['Pred'].mean():.4f}")

    sub_df.to_csv(output_path, index=False)
    print(f"  Saved to {output_path}")

    return sub_df


def validate_submission(sub_df, sample_sub):
    """Validate submission format."""
    issues = []

    if list(sub_df.columns) != ["ID", "Pred"]:
        issues.append(f"Expected columns ['ID', 'Pred'], got {list(sub_df.columns)}")

    if len(sub_df) != len(sample_sub):
        issues.append(f"Expected {len(sample_sub)} rows, got {len(sub_df)}")

    missing = set(sample_sub["ID"]) - set(sub_df["ID"])
    if missing:
        issues.append(f"{len(missing)} missing IDs")

    if sub_df["Pred"].min() < 0 or sub_df["Pred"].max() > 1:
        issues.append(f"Pred out of [0,1]: [{sub_df['Pred'].min()}, {sub_df['Pred'].max()}]")

    if sub_df["Pred"].isna().any():
        issues.append(f"{sub_df['Pred'].isna().sum()} NaN values")

    return issues


def main():
    print("=" * 70)
    print("PHASE 6: GENERATING KAGGLE SUBMISSIONS")
    print("=" * 70)

    sample_sub = load_sample_submission(stage=2)
    print(f"\nSample submission: {len(sample_sub)} matchups")

    # Parse to understand the split
    sample_sub_parsed = sample_sub["ID"].apply(
        lambda x: parse_submission_id(x)
    ).apply(pd.Series)
    sample_sub_parsed.columns = ["Season", "TeamLow", "TeamHigh"]

    mens = sample_sub_parsed[sample_sub_parsed["TeamLow"].between(1000, 1999)]
    womens = sample_sub_parsed[sample_sub_parsed["TeamLow"].between(3000, 3999)]
    print(f"  Men's matchups: {len(mens)}")
    print(f"  Women's matchups: {len(womens)}")

    # Submission 1: LightGBM only
    print(f"\n{'='*70}")
    print("SUBMISSION 1: LightGBM Only")
    print("=" * 70)
    sub1 = build_submission(
        "data/processed/ensemble_lgbm_only.parquet",
        sample_sub,
        "data/submissions/submission_lgbm.csv",
        default_pred=0.5,
    )

    issues1 = validate_submission(sub1, sample_sub)
    if issues1:
        print(f"  VALIDATION ISSUES: {issues1}")
    else:
        print("  VALIDATION: PASSED")

    # Submission 2: Weighted ensemble
    print(f"\n{'='*70}")
    print("SUBMISSION 2: Weighted Ensemble")
    print("=" * 70)
    sub2 = build_submission(
        "data/processed/ensemble_weighted.parquet",
        sample_sub,
        "data/submissions/submission_ensemble.csv",
        default_pred=0.5,
    )

    issues2 = validate_submission(sub2, sample_sub)
    if issues2:
        print(f"  VALIDATION ISSUES: {issues2}")
    else:
        print("  VALIDATION: PASSED")

    # Compare the two submissions
    print(f"\n{'='*70}")
    print("SUBMISSION COMPARISON")
    print("=" * 70)
    merged = sub1.merge(sub2, on="ID", suffixes=("_lgbm", "_ensemble"))
    diff = (merged["Pred_lgbm"] - merged["Pred_ensemble"]).abs()
    print(f"  Mean absolute difference: {diff.mean():.4f}")
    print(f"  Max absolute difference: {diff.max():.4f}")
    print(f"  Correlation: {merged['Pred_lgbm'].corr(merged['Pred_ensemble']):.4f}")
    agree_direction = ((merged["Pred_lgbm"] > 0.5) == (merged["Pred_ensemble"] > 0.5)).mean()
    print(f"  Agreement on winner: {agree_direction*100:.1f}%")


if __name__ == "__main__":
    main()
