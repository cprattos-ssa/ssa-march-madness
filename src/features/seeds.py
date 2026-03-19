"""Seed-based features for tournament prediction."""

import pandas as pd
import numpy as np


def parse_seed(seed_str: str) -> dict:
    """Parse seed string like 'W01' or 'Z11a' into components."""
    region = seed_str[0]
    num_str = seed_str[1:3]
    seed_num = int(num_str)
    play_in = len(seed_str) > 3  # e.g. 'Y11a', 'Y11b'
    return {"Region": region, "SeedNum": seed_num, "PlayIn": play_in}


def build_seed_features(seeds: pd.DataFrame) -> pd.DataFrame:
    """Build seed-based features from MNCAATourneySeeds.csv.

    Returns DataFrame with Season, TeamID, SeedNum, and derived features.
    """
    parsed = seeds["Seed"].apply(parse_seed).apply(pd.Series)
    result = pd.concat([seeds, parsed], axis=1)

    # Nonlinear transforms (seed performance is nonlinear)
    result["SeedLog"] = np.log(result["SeedNum"] + 1)
    result["SeedSq"] = result["SeedNum"] ** 2
    result["SeedInv"] = 1.0 / result["SeedNum"]

    # Historical win expectation by seed (from our EDA)
    seed_win_pct = {
        1: 0.799, 2: 0.706, 3: 0.653, 4: 0.613,
        5: 0.534, 6: 0.514, 7: 0.470, 8: 0.415,
        9: 0.380, 10: 0.381, 11: 0.410, 12: 0.341,
        13: 0.199, 14: 0.139, 15: 0.091, 16: 0.168,
    }
    result["SeedHistWinPct"] = result["SeedNum"].map(seed_win_pct)

    return result[["Season", "TeamID", "Seed", "Region", "SeedNum", "PlayIn",
                    "SeedLog", "SeedSq", "SeedInv", "SeedHistWinPct"]]


def build_matchup_seed_features(team_a_seed: int, team_b_seed: int) -> dict:
    """Compute seed-based matchup features."""
    return {
        "SeedDiff": team_a_seed - team_b_seed,
        "SeedDiffAbs": abs(team_a_seed - team_b_seed),
        "SeedProduct": team_a_seed * team_b_seed,
        "SeedSum": team_a_seed + team_b_seed,
        "HigherSeed": min(team_a_seed, team_b_seed),
        "LowerSeed": max(team_a_seed, team_b_seed),
    }
