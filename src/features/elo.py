"""Custom Elo rating system for NCAA basketball."""

import pandas as pd
import numpy as np


def compute_elo_ratings(
    games: pd.DataFrame,
    k: float = 20.0,
    home_advantage: float = 100.0,
    initial_rating: float = 1500.0,
    season_carryover: float = 0.75,
    margin_multiplier: bool = True,
) -> pd.DataFrame:
    """Compute Elo ratings from game-by-game results.

    Args:
        games: DataFrame with columns Season, DayNum, WTeamID, LTeamID, WScore, LScore, WLoc
        k: K-factor controlling update magnitude
        home_advantage: Elo bonus for home team
        initial_rating: Starting Elo for new teams
        season_carryover: Fraction of rating carried between seasons (rest regresses to mean)
        margin_multiplier: Scale K by margin of victory (reduces impact of blowouts)

    Returns:
        DataFrame with Season, TeamID, Elo (end-of-season rating), and EloPreTourney
    """
    ratings = {}
    history = []

    for season in sorted(games["Season"].unique()):
        # Season reset: regress toward mean
        if ratings:
            mean_elo = np.mean(list(ratings.values()))
            ratings = {
                team: mean_elo + season_carryover * (elo - mean_elo)
                for team, elo in ratings.items()
            }

        season_games = games[games["Season"] == season].sort_values("DayNum")

        # Track pre-tournament ratings (before DayNum 132ish)
        pre_tourney_ratings = {}

        for _, game in season_games.iterrows():
            w_team = game["WTeamID"]
            l_team = game["LTeamID"]

            # Initialize new teams
            if w_team not in ratings:
                ratings[w_team] = initial_rating
            if l_team not in ratings:
                ratings[l_team] = initial_rating

            w_elo = ratings[w_team]
            l_elo = ratings[l_team]

            # Home advantage adjustment
            w_ha = 0
            if game["WLoc"] == "H":
                w_ha = home_advantage
            elif game["WLoc"] == "A":
                w_ha = -home_advantage

            # Expected scores
            w_expected = 1.0 / (1.0 + 10.0 ** ((l_elo - w_elo - w_ha) / 400.0))
            l_expected = 1.0 - w_expected

            # Margin of victory multiplier
            mov = game["WScore"] - game["LScore"]
            if margin_multiplier:
                elo_diff = w_elo - l_elo + w_ha
                mult = np.log(max(mov, 1) + 1) * (2.2 / ((elo_diff * 0.001) + 2.2))
            else:
                mult = 1.0

            # Update ratings
            update = k * mult
            ratings[w_team] = w_elo + update * (1.0 - w_expected)
            ratings[l_team] = l_elo + update * (0.0 - l_expected)

            # Snapshot pre-tournament ratings (regular season ends ~day 132)
            if game["DayNum"] <= 132:
                pre_tourney_ratings[w_team] = ratings[w_team]
                pre_tourney_ratings[l_team] = ratings[l_team]

        # Record end-of-season ratings
        for team, elo in ratings.items():
            pre_elo = pre_tourney_ratings.get(team, elo)
            history.append({
                "Season": season,
                "TeamID": team,
                "Elo": round(elo, 1),
                "EloPreTourney": round(pre_elo, 1),
            })

    return pd.DataFrame(history)


def compute_current_season_elo(
    games: pd.DataFrame,
    prior_ratings: dict = None,
    k: float = 20.0,
    home_advantage: float = 100.0,
    initial_rating: float = 1500.0,
    margin_multiplier: bool = True,
) -> dict:
    """Compute Elo ratings for a single season (e.g., 2026 for prediction).

    Args:
        games: Single season of games
        prior_ratings: Ratings carried over from previous season
        k, home_advantage, initial_rating, margin_multiplier: Elo params

    Returns:
        Dict of {TeamID: current_elo}
    """
    ratings = dict(prior_ratings) if prior_ratings else {}

    for _, game in games.sort_values("DayNum").iterrows():
        w_team = game["WTeamID"]
        l_team = game["LTeamID"]

        if w_team not in ratings:
            ratings[w_team] = initial_rating
        if l_team not in ratings:
            ratings[l_team] = initial_rating

        w_elo = ratings[w_team]
        l_elo = ratings[l_team]

        w_ha = 0
        if game["WLoc"] == "H":
            w_ha = home_advantage
        elif game["WLoc"] == "A":
            w_ha = -home_advantage

        w_expected = 1.0 / (1.0 + 10.0 ** ((l_elo - w_elo - w_ha) / 400.0))
        l_expected = 1.0 - w_expected

        mov = game["WScore"] - game["LScore"]
        if margin_multiplier:
            elo_diff = w_elo - l_elo + w_ha
            mult = np.log(max(mov, 1) + 1) * (2.2 / ((elo_diff * 0.001) + 2.2))
        else:
            mult = 1.0

        update = k * mult
        ratings[w_team] = w_elo + update * (1.0 - w_expected)
        ratings[l_team] = l_elo + update * (0.0 - l_expected)

    return ratings
