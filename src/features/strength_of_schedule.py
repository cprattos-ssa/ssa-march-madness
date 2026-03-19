"""Strength of schedule features."""

import pandas as pd
import numpy as np


def compute_sos(compact_results: pd.DataFrame) -> pd.DataFrame:
    """Compute multi-level strength of schedule.

    Levels:
        WP: Team's winning percentage
        OWP: Average winning percentage of opponents
        OOWP: Average winning percentage of opponents' opponents

    Args:
        compact_results: MRegularSeasonCompactResults.csv

    Returns:
        DataFrame with Season, TeamID, WP, OWP, OOWP, SOS (RPI-style)
    """
    records = []

    for season in compact_results["Season"].unique():
        sg = compact_results[compact_results["Season"] == season]

        # Build win/loss record for each team
        team_records = {}
        team_opponents = {}

        for _, game in sg.iterrows():
            w, l = game["WTeamID"], game["LTeamID"]

            for team in [w, l]:
                if team not in team_records:
                    team_records[team] = {"wins": 0, "losses": 0}
                    team_opponents[team] = []

            team_records[w]["wins"] += 1
            team_records[l]["losses"] += 1
            team_opponents[w].append(l)
            team_opponents[l].append(w)

        # WP
        wp = {}
        for team, rec in team_records.items():
            total = rec["wins"] + rec["losses"]
            wp[team] = rec["wins"] / total if total > 0 else 0.5

        # OWP: average opponent WP
        owp = {}
        for team, opps in team_opponents.items():
            if opps:
                owp[team] = np.mean([wp.get(opp, 0.5) for opp in opps])
            else:
                owp[team] = 0.5

        # OOWP: average opponent's OWP
        oowp = {}
        for team, opps in team_opponents.items():
            if opps:
                oowp[team] = np.mean([owp.get(opp, 0.5) for opp in opps])
            else:
                oowp[team] = 0.5

        for team in team_records:
            # RPI-style SOS = 0.25 * WP + 0.50 * OWP + 0.25 * OOWP
            sos = 0.25 * wp[team] + 0.50 * owp[team] + 0.25 * oowp[team]
            records.append({
                "Season": season,
                "TeamID": team,
                "WP": round(wp[team], 4),
                "OWP": round(owp[team], 4),
                "OOWP": round(oowp[team], 4),
                "SOS": round(sos, 4),
            })

    return pd.DataFrame(records)
