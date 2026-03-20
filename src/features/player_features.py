"""Player-level feature aggregation from Barttorvik data."""

import pandas as pd
import numpy as np
import os

# Column mapping for headerless Barttorvik CSV
BARTTORVIK_COLS = {
    0: 'Name', 1: 'School', 2: 'Conf', 3: 'Games', 4: 'MinPct',
    5: 'Pace', 6: 'eFGPct', 7: 'FGPct', 8: 'FGA', 24: 'Usage',
    25: 'Class', 26: 'Height', 27: 'Rank', 29: 'Rating', 30: 'WAR',
    46: 'OffRtg', 47: 'DefRtg', 63: 'PTSper40', 64: 'Position',
}

# Features that will be added to team_features (as _diff in matchups)
PLAYER_FEATURE_NAMES = [
    "Team_WAR",
    "Star_WAR",
    "WAR_Gini",
    "Avg_ClassNum",
    "Star_Usage",
    "Top3_WAR",
    "Avg_Height",
    "Sr_Pct",
]


def load_player_data(data_dir: str, seasons: list[int]) -> pd.DataFrame:
    """Load and parse Barttorvik player CSVs for given seasons."""
    all_dfs = []
    for year in seasons:
        path = os.path.join(data_dir, f"barttorvik_players_{year}.csv")
        if not os.path.exists(path):
            continue
        df = pd.read_csv(path, header=None)
        cols_to_use = {k: v for k, v in BARTTORVIK_COLS.items() if k < df.shape[1]}
        df = df.rename(columns=cols_to_use)
        df = df[list(cols_to_use.values())]
        df['Season'] = year

        # Clean numeric columns
        for col in ['Games', 'MinPct', 'Usage', 'Rating', 'WAR', 'OffRtg', 'DefRtg', 'PTSper40', 'Rank']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # Parse height to inches
        def parse_height(h):
            try:
                parts = str(h).split('-')
                return int(parts[0]) * 12 + int(parts[1])
            except Exception:
                return np.nan
        df['HeightIn'] = df['Height'].apply(parse_height)

        # Class encoding
        class_map = {'Fr': 1, 'So': 2, 'Jr': 3, 'Sr': 4}
        df['ClassNum'] = df['Class'].map(class_map).fillna(2.5)

        all_dfs.append(df)

    if not all_dfs:
        return pd.DataFrame()

    return pd.concat(all_dfs, ignore_index=True)


def map_schools_to_team_ids(players: pd.DataFrame, name_to_id: dict) -> pd.DataFrame:
    """Map Barttorvik school names to Kaggle TeamIDs."""

    def normalize_school(name):
        if pd.isna(name):
            return None
        name_lower = name.strip().lower()

        if name_lower in name_to_id:
            return name_to_id[name_lower]

        replacements = {
            'st.': 'state', 'unc ': 'north carolina ',
            'usc': 'southern california', 'lsu': 'louisiana state',
            'smu': 'southern methodist', 'tcu': 'texas christian',
            'byu': 'brigham young', 'vcu': 'virginia commonwealth',
            'ucf': 'central florida', 'uab': 'alabama birmingham',
            'unlv': 'nevada las vegas', 'umbc': 'maryland baltimore county',
            'fiu': 'florida international', 'utep': 'texas el paso',
            'ole miss': 'mississippi',
        }

        test = name_lower
        for old, new in replacements.items():
            test = test.replace(old, new)
        if test in name_to_id:
            return name_to_id[test]

        if name_lower + ' state' in name_to_id:
            return name_to_id[name_lower + ' state']

        for spell, tid in name_to_id.items():
            if name_lower in spell or spell in name_lower:
                return tid

        return None

    players = players.copy()
    players['TeamID'] = players['School'].apply(normalize_school)
    return players


def aggregate_player_features(
    players: pd.DataFrame,
    min_minutes_pct: float = 10,
    min_games: int = 5,
) -> pd.DataFrame:
    """Aggregate player data into team-season features.

    Returns DataFrame with Season, TeamID, and PLAYER_FEATURE_NAMES columns.
    """
    p = players[
        players.TeamID.notna()
        & (players.MinPct >= min_minutes_pct)
        & (players.Games >= min_games)
    ].copy()

    records = []
    for (season, team_id), group in p.groupby(['Season', 'TeamID']):
        g = group.sort_values('MinPct', ascending=False)
        top1 = g.iloc[0] if len(g) > 0 else None
        top3 = g.head(3)

        features = {
            'Season': int(season),
            'TeamID': int(team_id),
            'Team_WAR': g['WAR'].sum(),
            'Star_WAR': top1['WAR'] if top1 is not None else np.nan,
            'Star_Usage': top1['Usage'] if top1 is not None else np.nan,
            'Top3_WAR': top3['WAR'].sum() if len(top3) > 0 else np.nan,
            'Avg_ClassNum': g['ClassNum'].mean(),
            'Sr_Pct': (g['Class'] == 'Sr').mean(),
            'Avg_Height': g['HeightIn'].mean(),
        }

        # WAR Gini coefficient
        war_vals = g['WAR'].dropna().values
        if len(war_vals) > 1 and war_vals.sum() > 0:
            war_sorted = np.sort(war_vals)
            n = len(war_sorted)
            index = np.arange(1, n + 1)
            features['WAR_Gini'] = (
                (2 * np.sum(index * war_sorted) - (n + 1) * np.sum(war_sorted))
                / (n * np.sum(war_sorted))
            )
        else:
            features['WAR_Gini'] = np.nan

        records.append(features)

    return pd.DataFrame(records)
