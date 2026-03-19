"""Validate submission CSV before uploading to Kaggle."""

import pandas as pd


def validate_submission(submission_path: str, sample_submission_path: str) -> list[str]:
    """Check submission CSV for common errors. Returns list of issues (empty = valid)."""
    issues = []
    sub = pd.read_csv(submission_path)
    sample = pd.read_csv(sample_submission_path)

    # Check columns
    if list(sub.columns) != ["ID", "Pred"]:
        issues.append(f"Expected columns ['ID', 'Pred'], got {list(sub.columns)}")

    # Check row count
    if len(sub) != len(sample):
        issues.append(f"Expected {len(sample)} rows, got {len(sub)}")

    # Check all IDs present
    missing = set(sample["ID"]) - set(sub["ID"])
    if missing:
        issues.append(f"{len(missing)} missing IDs (e.g. {list(missing)[:3]})")

    extra = set(sub["ID"]) - set(sample["ID"])
    if extra:
        issues.append(f"{len(extra)} extra IDs (e.g. {list(extra)[:3]})")

    # Check probability range
    if sub["Pred"].min() < 0 or sub["Pred"].max() > 1:
        issues.append(f"Pred out of [0,1] range: [{sub['Pred'].min()}, {sub['Pred'].max()}]")

    # Check for NaN
    if sub["Pred"].isna().any():
        issues.append(f"{sub['Pred'].isna().sum()} NaN values in Pred column")

    # Check ID format (YYYY_TeamLow_TeamHigh)
    bad_format = sub[~sub["ID"].str.match(r"^\d{4}_\d{4}_\d{4}$")]
    if len(bad_format) > 0:
        issues.append(f"{len(bad_format)} IDs with bad format (e.g. {bad_format['ID'].iloc[0]})")

    return issues
