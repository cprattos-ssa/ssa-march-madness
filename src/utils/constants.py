"""Constants for the March Madness prediction pipeline."""

# Team ID ranges
MENS_TEAM_ID_RANGE = (1000, 1999)
WOMENS_TEAM_ID_RANGE = (3000, 3999)

# CSV file prefixes by gender
FILE_PREFIX = {
    "mens": "M",
    "womens": "W",
}

# Data files available for both genders
GENDERED_FILES = [
    "Teams",
    "Seasons",
    "RegularSeasonCompactResults",
    "RegularSeasonDetailedResults",
    "NCAATourneyCompactResults",
    "NCAATourneyDetailedResults",
    "NCAATourneySeeds",
    "NCAATourneySlots",
    "TeamCoaches",
    "TeamConferences",
    "GameCities",
]

# Men's-only files
MENS_ONLY_FILES = [
    "MasseyOrdinals",
    "ConferenceTourneyGames",
    "SecondaryTourneyCompactResults",
    "SecondaryTourneyTeams",
]

# Gender-neutral files
SHARED_FILES = [
    "Cities",
    "Conferences",
]

# Box score stat columns (for DetailedResults files)
# Prefix with W or L for winning/losing team
BOX_SCORE_STATS = [
    "FGM", "FGA",       # Field goals made/attempted
    "FGM3", "FGA3",     # Three-pointers made/attempted
    "FTM", "FTA",       # Free throws made/attempted
    "OR", "DR",         # Offensive/defensive rebounds
    "Ast",              # Assists
    "TO",               # Turnovers
    "Stl",              # Steals
    "Blk",              # Blocks
    "PF",               # Personal fouls
]

# Seed string format: e.g. "W01", "X16a"
# Region codes: W, X, Y, Z
SEED_REGIONS = ["W", "X", "Y", "Z"]

# Season boundaries
FIRST_SEASON_WITH_DETAILED = 2003  # Detailed box scores start here
FIRST_SEASON_WITH_MASSEY = 2003    # Massey ordinals start here

# Submission format
SUBMISSION_SEASON = 2026
SUBMISSION_ID_FORMAT = "{season}_{team_low}_{team_high}"
