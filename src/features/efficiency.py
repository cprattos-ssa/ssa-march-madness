"""Compute per-possession efficiency metrics from box score data."""

import pandas as pd
import numpy as np


def estimate_possessions(fga, fga3, fta, orb, to, opp_drb):
    """Estimate possessions using the standard formula."""
    return fga - orb + to + 0.475 * fta


def compute_team_season_stats(detailed_results: pd.DataFrame) -> pd.DataFrame:
    """Compute per-team, per-season aggregated efficiency metrics.

    Args:
        detailed_results: MRegularSeasonDetailedResults.csv

    Returns:
        DataFrame with one row per (Season, TeamID) with efficiency metrics
    """
    records = []

    for season in detailed_results["Season"].unique():
        season_df = detailed_results[detailed_results["Season"] == season]

        # Collect stats for each team (as winner and as loser)
        team_stats = {}

        for _, g in season_df.iterrows():
            for role in ["W", "L"]:
                opp = "L" if role == "W" else "W"
                team_id = g[f"{role}TeamID"]

                if team_id not in team_stats:
                    team_stats[team_id] = {
                        "games": 0, "wins": 0, "pts": 0, "opp_pts": 0,
                        "fgm": 0, "fga": 0, "fgm3": 0, "fga3": 0,
                        "ftm": 0, "fta": 0, "orb": 0, "drb": 0,
                        "ast": 0, "to": 0, "stl": 0, "blk": 0, "pf": 0,
                        "opp_fgm": 0, "opp_fga": 0, "opp_fgm3": 0, "opp_fga3": 0,
                        "opp_ftm": 0, "opp_fta": 0, "opp_orb": 0, "opp_drb": 0,
                        "opp_to": 0,
                    }

                s = team_stats[team_id]
                s["games"] += 1
                s["wins"] += 1 if role == "W" else 0
                s["pts"] += g[f"{role}Score"]
                s["opp_pts"] += g[f"{opp}Score"]
                s["fgm"] += g[f"{role}FGM"]
                s["fga"] += g[f"{role}FGA"]
                s["fgm3"] += g[f"{role}FGM3"]
                s["fga3"] += g[f"{role}FGA3"]
                s["ftm"] += g[f"{role}FTM"]
                s["fta"] += g[f"{role}FTA"]
                s["orb"] += g[f"{role}OR"]
                s["drb"] += g[f"{role}DR"]
                s["ast"] += g[f"{role}Ast"]
                s["to"] += g[f"{role}TO"]
                s["stl"] += g[f"{role}Stl"]
                s["blk"] += g[f"{role}Blk"]
                s["pf"] += g[f"{role}PF"]
                s["opp_fgm"] += g[f"{opp}FGM"]
                s["opp_fga"] += g[f"{opp}FGA"]
                s["opp_fgm3"] += g[f"{opp}FGM3"]
                s["opp_fga3"] += g[f"{opp}FGA3"]
                s["opp_ftm"] += g[f"{opp}FTM"]
                s["opp_fta"] += g[f"{opp}FTA"]
                s["opp_orb"] += g[f"{opp}OR"]
                s["opp_drb"] += g[f"{opp}DR"]
                s["opp_to"] += g[f"{opp}TO"]

        for team_id, s in team_stats.items():
            g = s["games"]
            if g == 0:
                continue

            # Possessions
            poss = estimate_possessions(
                s["fga"], s["fga3"], s["fta"], s["orb"], s["to"], s["opp_drb"]
            )
            opp_poss = estimate_possessions(
                s["opp_fga"], s["opp_fga3"], s["opp_fta"], s["opp_orb"], s["opp_to"], s["drb"]
            )
            avg_poss = (poss + opp_poss) / 2

            if avg_poss == 0:
                continue

            records.append({
                "Season": season,
                "TeamID": team_id,
                "Games": g,
                "Wins": s["wins"],
                "WinPct": s["wins"] / g,
                "PointsPerGame": s["pts"] / g,
                "OppPointsPerGame": s["opp_pts"] / g,
                "PointDiff": (s["pts"] - s["opp_pts"]) / g,
                # Per-possession metrics
                "OffEff": s["pts"] / avg_poss * 100,  # Points per 100 possessions
                "DefEff": s["opp_pts"] / avg_poss * 100,
                "NetEff": (s["pts"] - s["opp_pts"]) / avg_poss * 100,
                "Tempo": avg_poss / g,  # Possessions per game
                # Four factors (offense)
                "eFGPct": (s["fgm"] + 0.5 * s["fgm3"]) / max(s["fga"], 1),
                "TOPct": s["to"] / max(avg_poss, 1),
                "ORBPct": s["orb"] / max(s["orb"] + s["opp_drb"], 1),
                "FTRate": s["fta"] / max(s["fga"], 1),
                # Four factors (defense)
                "OppeFGPct": (s["opp_fgm"] + 0.5 * s["opp_fgm3"]) / max(s["opp_fga"], 1),
                "OppTOPct": s["opp_to"] / max(opp_poss, 1),
                "DRBPct": s["drb"] / max(s["drb"] + s["opp_orb"], 1),
                "OppFTRate": s["opp_fta"] / max(s["opp_fga"], 1),
                # Shooting splits
                "FGPct": s["fgm"] / max(s["fga"], 1),
                "FG3Pct": s["fgm3"] / max(s["fga3"], 1),
                "FTPct": s["ftm"] / max(s["fta"], 1),
                "FG3Rate": s["fga3"] / max(s["fga"], 1),
                # Other
                "AstRate": s["ast"] / max(s["fgm"], 1),
                "StlRate": s["stl"] / g,
                "BlkRate": s["blk"] / g,
            })

    return pd.DataFrame(records)
