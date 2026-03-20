"""
Injury-adjusted predictions for 2026 NCAA Tournament first-round matchups.

Computes WAR-proportional adjustments for teams missing key players,
then compares Brier scores between original and adjusted predictions.
"""
import pandas as pd
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

ROOT = Path("C:/dev/ssa-march-madness")
RAW = ROOT / "data" / "raw" / "kaggle"
PLAYER = ROOT / "data" / "raw" / "external" / "player_data"
PROC = ROOT / "data" / "processed"
RESULTS = ROOT / "results"

# ============================================================================
# COLUMN MAPPING FOR BARTTORVIK CSV (no header row)
# ============================================================================
COLS = {
    0: 'Name', 1: 'School', 2: 'Conf', 3: 'Games', 4: 'MinPct',
    5: 'Pace', 6: 'eFGPct', 7: 'FGPct', 8: 'FGA', 9: 'FG2Pct',
    10: 'FG2A', 11: 'FG2APct', 12: 'FG3APct', 13: 'FG3M', 14: 'FG3A',
    15: 'FG3Pct', 16: 'FTM', 17: 'FTA', 18: 'FTPct', 19: 'ORB',
    20: 'DRB', 21: 'ORBPct', 22: 'AstPct', 23: 'TORate', 24: 'Usage',
    25: 'Class', 26: 'Height', 27: 'Rank', 28: 'Zscore', 29: 'Rating',
    30: 'WAR', 31: 'DraftYear', 32: 'PlayerID', 33: 'Hometown',
    34: 'ProjMin', 35: 'WeightedMin', 36: 'GamesSample', 37: 'MinSample',
    38: 'FGMSample', 39: 'FGASample', 40: 'FGPctSample', 41: 'FG3PctSample',
    42: 'FTASample', 43: 'FTMSample', 44: 'FTPctSample', 45: 'blank1',
    46: 'OffRtg', 47: 'DefRtg', 48: 'NetRtg', 49: 'AdjOffRtg',
    50: 'AdjDefRtg', 51: 'PTS', 52: 'OWS', 53: 'DWS',
    54: 'OffRtg40', 55: 'DefRtg40', 56: 'NetRtg40',
    57: 'ORBper40', 58: 'DRBper40', 59: 'TRBper40',
    60: 'ASTper40', 61: 'TOVper40', 62: 'STLper40', 63: 'PTSper40',
    64: 'Position', 65: 'ValueMetric'
}

print("=" * 80)
print("INJURY-ADJUSTED PREDICTIONS FOR 2026 TOURNAMENT")
print("=" * 80)

# ============================================================================
# STEP 1: LOAD DATA
# ============================================================================
print("\n[Step 1] Loading data...")

# Predictions
preds = pd.read_parquet(PROC / "preds_lgbm.parquet")
print(f"  Predictions: {preds.shape[0]} matchups, columns={preds.columns.tolist()}")

# Team names
teams = pd.read_csv(RAW / "MTeams.csv")
team_id_to_name = dict(zip(teams['TeamID'], teams['TeamName']))
print(f"  Teams: {len(teams)} teams")

# Spellings for name mapping
spellings = pd.read_csv(RAW / "MTeamSpellings.csv", encoding='latin1')
name_to_id = {}
for _, row in spellings.iterrows():
    name_to_id[str(row.iloc[0]).lower().strip()] = row.iloc[1]
for _, row in teams.iterrows():
    name_to_id[row['TeamName'].lower().strip()] = row['TeamID']

# Seeds (2026 only)
seeds = pd.read_csv(RAW / "MNCAATourneySeeds.csv")
seeds_2026 = seeds[seeds['Season'] == 2026].copy()
seeds_2026['SeedNum'] = seeds_2026['Seed'].str.extract(r'(\d+)').astype(int)
print(f"  2026 seeds: {len(seeds_2026)} teams")

# Player data (2026 only)
player_df = pd.read_csv(PLAYER / "barttorvik_players_2026.csv", header=None)
player_df = player_df.iloc[:, :min(len(COLS), player_df.shape[1])]
player_df = player_df.rename(columns={k: v for k, v in COLS.items() if k < player_df.shape[1]})

# Clean numeric columns
for col in ['Games', 'MinPct', 'WAR', 'Rating', 'Usage', 'PTSper40']:
    if col in player_df.columns:
        player_df[col] = pd.to_numeric(player_df[col], errors='coerce')

# Strip quotes from Name and School
player_df['Name'] = player_df['Name'].str.strip('"').str.strip()
player_df['School'] = player_df['School'].str.strip('"').str.strip()

print(f"  Players (2026): {len(player_df)} players")


# ============================================================================
# BARTTORVIK SCHOOL -> KAGGLE TEAM ID MAPPING
# ============================================================================
def normalize_school(name):
    """Match Barttorvik school name to Kaggle TeamID."""
    if pd.isna(name):
        return None
    name_lower = name.strip().lower()

    if name_lower in name_to_id:
        return name_to_id[name_lower]

    replacements = {
        'st.': 'state', 'st ': 'state ', 'unc ': 'north carolina ',
        'usc': 'southern california', 'lsu': 'louisiana state',
        'smu': 'southern methodist', 'tcu': 'texas christian',
        'byu': 'brigham young', 'vcu': 'virginia commonwealth',
        'ucf': 'central florida', 'uab': 'alabama birmingham',
        'unlv': 'nevada las vegas', 'umbc': 'maryland baltimore county',
        'liu brooklyn': 'long island university', 'liu': 'long island university',
        'fiu': 'florida international', 'utep': 'texas el paso',
        'etsu': 'east tennessee st', 'utsa': 'texas san antonio',
        'ole miss': 'mississippi', 'miami fl': 'miami fl',
        'miami oh': 'miami oh', 'penn': 'pennsylvania',
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


player_df['TeamID'] = player_df['School'].apply(normalize_school)
matched = player_df['TeamID'].notna().sum()
print(f"  Player->Team matched: {matched}/{len(player_df)} ({matched/len(player_df):.1%})")


# ============================================================================
# HELPER: FIND TEAM ID FROM NAME FRAGMENT
# ============================================================================
def find_team_id(fragment):
    """Find Kaggle TeamID from a team name fragment."""
    frag_lower = fragment.lower().strip()

    # Direct lookup
    if frag_lower in name_to_id:
        return name_to_id[frag_lower]

    # Search through teams
    for _, row in teams.iterrows():
        if frag_lower in row['TeamName'].lower():
            return row['TeamID']

    # Search through spellings
    for spell, tid in name_to_id.items():
        if frag_lower in spell or spell in frag_lower:
            return tid

    return None


def get_matchup_pred(team_a_id, team_b_id, preds_df):
    """Get prediction for matchup. Returns (TeamLow, TeamHigh, Pred)."""
    low = min(team_a_id, team_b_id)
    high = max(team_a_id, team_b_id)
    row = preds_df[(preds_df['TeamLow'] == low) & (preds_df['TeamHigh'] == high)]
    if len(row) == 0:
        return low, high, None
    return low, high, row.iloc[0]['Pred']


# ============================================================================
# STEP 2: DEFINE INJURED PLAYERS AND MATCHUPS
# ============================================================================
print("\n[Step 2] Defining injury matchups...")

injuries = [
    ('Duke', 'Siena', ['Caleb Foster', 'Patrick Ngongba']),
    ('North Carolina', 'VCU', ['Caleb Wilson']),
    ('Louisville', 'South Florida', ['Mikel Brown']),
    ('Alabama', 'Hofstra', ['Aden Holloway']),
    ('Texas Tech', 'Akron', ['JT Toppin']),
    ('BYU', 'Texas', ['Richie Saunders']),
    ('Gonzaga', 'Kennesaw', ['Braden Huff']),
]

# Map team names to IDs
for team_name, opp_name, injured_list in injuries:
    tid = find_team_id(team_name)
    oid = find_team_id(opp_name)
    print(f"  {team_name} (ID={tid}) vs {opp_name} (ID={oid}) - OUT: {injured_list}")


# ============================================================================
# STEP 3: COMPUTE INJURY ADJUSTMENTS
# ============================================================================
print("\n[Step 3] Computing injury adjustments...")
print("-" * 80)

ADJUSTMENT_STRENGTH = 1.0
results = []

for team_name, opp_name, injured_list in injuries:
    team_id = find_team_id(team_name)
    opp_id = find_team_id(opp_name)

    if team_id is None or opp_id is None:
        print(f"  WARNING: Could not find IDs for {team_name} vs {opp_name}")
        continue

    low, high, orig_pred = get_matchup_pred(team_id, opp_id, preds)

    if orig_pred is None:
        print(f"  WARNING: No prediction found for {team_name} vs {opp_name} (IDs {low} vs {high})")
        continue

    # Determine if team is TeamLow or TeamHigh
    team_is_low = (team_id == low)

    # Get team's players from Barttorvik (with meaningful playing time)
    team_players = player_df[
        (player_df['TeamID'] == team_id) &
        (player_df['MinPct'] >= 10) &
        (player_df['Games'] >= 5)
    ].copy()

    team_total_war = team_players['WAR'].sum()

    print(f"\n  {team_name} (ID={team_id}) vs {opp_name} (ID={opp_id})")
    print(f"    TeamLow={low} ({team_id_to_name.get(low, '?')}), "
          f"TeamHigh={high} ({team_id_to_name.get(high, '?')})")
    print(f"    Original P(TeamLow wins) = {orig_pred:.4f}")
    print(f"    {team_name} is {'TeamLow' if team_is_low else 'TeamHigh'}")
    print(f"    Team total WAR (rotation players): {team_total_war:.2f}")

    # Find injured players
    total_injured_war = 0.0
    for inj_name in injured_list:
        # Search by last name + school
        last_name = inj_name.split()[-1]
        matches = player_df[
            (player_df['TeamID'] == team_id) &
            (player_df['Name'].str.contains(last_name, case=False, na=False))
        ]

        if len(matches) == 0:
            # Try first name too
            first_name = inj_name.split()[0]
            matches = player_df[
                (player_df['TeamID'] == team_id) &
                (player_df['Name'].str.contains(first_name, case=False, na=False))
            ]

        if len(matches) > 0:
            player = matches.iloc[0]
            war = player['WAR']
            total_injured_war += war
            print(f"    Injured: {player['Name']} - WAR={war:.2f}, "
                  f"MinPct={player['MinPct']:.1f}%, Rating={player['Rating']:.1f}")
        else:
            print(f"    WARNING: Could not find {inj_name} for {team_name}")

    if team_total_war > 0:
        war_fraction = total_injured_war / team_total_war
    else:
        war_fraction = 0.0

    print(f"    Total injured WAR: {total_injured_war:.2f}")
    print(f"    WAR fraction lost: {war_fraction:.4f} ({war_fraction*100:.1f}%)")

    # Apply adjustment
    # The prediction is P(TeamLow wins).
    # If the injured team IS TeamLow, losing players pulls pred toward 0.5
    # If the injured team IS TeamHigh, losing players also pulls pred toward 0.5
    # The formula: adjusted_P = P + (0.5 - P) * war_fraction * adjustment_strength
    # This always moves toward 0.5, which is correct regardless of which team is injured.
    adjusted_pred = orig_pred + (0.5 - orig_pred) * war_fraction * ADJUSTMENT_STRENGTH

    print(f"    Adjusted P(TeamLow wins) = {adjusted_pred:.4f}")
    print(f"    Change: {adjusted_pred - orig_pred:+.4f}")

    results.append({
        'team_name': team_name,
        'opp_name': opp_name,
        'team_id': team_id,
        'opp_id': opp_id,
        'team_low': low,
        'team_high': high,
        'team_is_low': team_is_low,
        'orig_pred': orig_pred,
        'adjusted_pred': adjusted_pred,
        'injured_players': injured_list,
        'total_injured_war': total_injured_war,
        'team_total_war': team_total_war,
        'war_fraction': war_fraction,
    })


# ============================================================================
# STEP 4: BRIER SCORE COMPARISON
# ============================================================================
print("\n" + "=" * 80)
print("[Step 4] Brier score comparison on known results")
print("=" * 80)

# Known first-round results from March 19, 2026
# Format: (winner, loser, winner_score, loser_score)
known_results_raw = [
    ('TCU', 'Ohio St', 66, 64),
    ('Nebraska', 'Troy', 76, 47),
    ('Louisville', 'South Florida', 66, 44),
    ('Wisconsin', 'High Point', 52, 48),
]

print("\n  Known results:")
brier_data = []

for winner, loser, w_score, l_score in known_results_raw:
    winner_id = find_team_id(winner)
    loser_id = find_team_id(loser)

    if winner_id is None or loser_id is None:
        print(f"    WARNING: Could not find IDs for {winner} vs {loser}")
        continue

    low = min(winner_id, loser_id)
    high = max(winner_id, loser_id)

    # actual = 1.0 if TeamLow won, 0.0 if TeamHigh won
    actual = 1.0 if winner_id == low else 0.0

    # Get original prediction
    row = preds[(preds['TeamLow'] == low) & (preds['TeamHigh'] == high)]
    if len(row) == 0:
        print(f"    WARNING: No prediction for {winner} vs {loser}")
        continue

    orig_pred = row.iloc[0]['Pred']

    # Check if this matchup has an injury adjustment
    adjusted_pred = orig_pred
    injury_info = None
    for r in results:
        if r['team_low'] == low and r['team_high'] == high:
            adjusted_pred = r['adjusted_pred']
            injury_info = r
            break

    brier_orig = (orig_pred - actual) ** 2
    brier_adj = (adjusted_pred - actual) ** 2

    winner_name = team_id_to_name.get(winner_id, winner)
    loser_name = team_id_to_name.get(loser_id, loser)

    print(f"\n    {winner_name} {w_score}, {loser_name} {l_score}")
    print(f"      TeamLow={low} ({team_id_to_name.get(low, '?')}), "
          f"TeamHigh={high} ({team_id_to_name.get(high, '?')})")
    print(f"      Actual (TeamLow wins): {actual:.0f}")
    print(f"      Original pred: {orig_pred:.4f}  ->  Brier: {brier_orig:.6f}")
    if injury_info is not None:
        print(f"      Adjusted pred: {adjusted_pred:.4f}  ->  Brier: {brier_adj:.6f}")
        print(f"      Injury: {injury_info['team_name']} missing {injury_info['injured_players']}")
        print(f"      Brier improvement: {brier_orig - brier_adj:+.6f}")
    else:
        print(f"      (No injury adjustment for this matchup)")

    brier_data.append({
        'matchup': f"{winner_name} def. {loser_name}",
        'winner': winner_name,
        'loser': loser_name,
        'score': f"{w_score}-{l_score}",
        'actual': actual,
        'orig_pred': orig_pred,
        'adjusted_pred': adjusted_pred,
        'brier_orig': brier_orig,
        'brier_adj': brier_adj,
        'has_injury': injury_info is not None,
    })

# Compute totals
if brier_data:
    total_brier_orig = sum(d['brier_orig'] for d in brier_data)
    total_brier_adj = sum(d['brier_adj'] for d in brier_data)
    avg_brier_orig = total_brier_orig / len(brier_data)
    avg_brier_adj = total_brier_adj / len(brier_data)
    improvement = total_brier_orig - total_brier_adj

    print(f"\n  {'='*60}")
    print(f"  BRIER SCORE SUMMARY ({len(brier_data)} games)")
    print(f"  {'='*60}")
    print(f"  Total Brier (original):  {total_brier_orig:.6f}")
    print(f"  Total Brier (adjusted):  {total_brier_adj:.6f}")
    print(f"  Total improvement:       {improvement:+.6f}")
    print(f"  Avg Brier (original):    {avg_brier_orig:.6f}")
    print(f"  Avg Brier (adjusted):    {avg_brier_adj:.6f}")
    print(f"  Avg improvement:         {improvement/len(brier_data):+.6f}")

    # Only for injury-adjusted games
    inj_games = [d for d in brier_data if d['has_injury']]
    if inj_games:
        inj_brier_orig = sum(d['brier_orig'] for d in inj_games)
        inj_brier_adj = sum(d['brier_adj'] for d in inj_games)
        inj_improvement = inj_brier_orig - inj_brier_adj
        print(f"\n  Injury-affected games only ({len(inj_games)} games):")
        print(f"    Brier (original): {inj_brier_orig:.6f}")
        print(f"    Brier (adjusted): {inj_brier_adj:.6f}")
        print(f"    Improvement:      {inj_improvement:+.6f}")


# ============================================================================
# STEP 6: OHIO STATE VS TCU - STAR PLAYER ANALYSIS
# ============================================================================
print("\n" + "=" * 80)
print("[Step 6] Ohio State vs TCU - Star player context")
print("=" * 80)

osu_id = find_team_id('Ohio St')
tcu_id = find_team_id('TCU')

print(f"\n  Ohio State ID: {osu_id}")
print(f"  TCU ID: {tcu_id}")

# Get TCU players
tcu_players = player_df[
    (player_df['TeamID'] == tcu_id) &
    (player_df['MinPct'] >= 10) &
    (player_df['Games'] >= 5)
].sort_values('WAR', ascending=False)

osu_players = player_df[
    (player_df['TeamID'] == osu_id) &
    (player_df['MinPct'] >= 10) &
    (player_df['Games'] >= 5)
].sort_values('WAR', ascending=False)

print(f"\n  TCU top players by WAR:")
for _, p in tcu_players.head(5).iterrows():
    print(f"    {p['Name']:25s}  WAR={p['WAR']:.2f}  MinPct={p['MinPct']:.1f}  "
          f"Rating={p['Rating']:.1f}  PTSper40={p['PTSper40']:.1f}")

print(f"\n  Ohio State top players by WAR:")
for _, p in osu_players.head(5).iterrows():
    print(f"    {p['Name']:25s}  WAR={p['WAR']:.2f}  MinPct={p['MinPct']:.1f}  "
          f"Rating={p['Rating']:.1f}  PTSper40={p['PTSper40']:.1f}")

# Find specific players: Pierre, Punch for TCU
print(f"\n  TCU star players (Pierre + Punch):")
tcu_stars = tcu_players[
    tcu_players['Name'].str.contains('Pierre|Punch', case=False, na=False)
]
tcu_star_war = 0.0
for _, p in tcu_stars.iterrows():
    print(f"    {p['Name']:25s}  WAR={p['WAR']:.2f}")
    tcu_star_war += p['WAR']

tcu_total_war = tcu_players['WAR'].sum()
osu_total_war = osu_players['WAR'].sum()

print(f"\n  TCU total team WAR: {tcu_total_war:.2f}")
print(f"  TCU star WAR (Pierre+Punch): {tcu_star_war:.2f} ({tcu_star_war/tcu_total_war*100:.1f}% of team)")
print(f"  Ohio State total team WAR: {osu_total_war:.2f}")

# OSU top player
if len(osu_players) > 0:
    osu_star = osu_players.iloc[0]
    print(f"  Ohio State best player: {osu_star['Name']} WAR={osu_star['WAR']:.2f}")

# Get the matchup prediction
low, high, orig_pred_osu = get_matchup_pred(osu_id, tcu_id, preds)
print(f"\n  Original P(TeamLow wins) = {orig_pred_osu:.4f}")
print(f"  TeamLow={low} ({team_id_to_name.get(low, '?')}), "
      f"TeamHigh={high} ({team_id_to_name.get(high, '?')})")

# Show what a star-player-adjusted pred would look like
# If TCU's stars have higher WAR, the model's confidence in Ohio State should decrease
# The star power ratio: TCU_star_WAR / (TCU_star_WAR + OSU_star_WAR)
if len(osu_players) > 0:
    osu_star_war = osu_players.iloc[0]['WAR']
    star_ratio = tcu_star_war / (tcu_star_war + osu_star_war) if (tcu_star_war + osu_star_war) > 0 else 0.5

    # WAR advantage factor: how much more star power TCU has
    war_advantage = (tcu_total_war - osu_total_war) / max(tcu_total_war, osu_total_war)

    print(f"\n  Star WAR comparison:")
    print(f"    TCU stars (Pierre+Punch): {tcu_star_war:.2f}")
    print(f"    OSU top player: {osu_star_war:.2f}")
    print(f"    Star ratio (TCU share): {star_ratio:.3f}")
    print(f"    Overall WAR advantage (TCU): {war_advantage:+.3f}")

    # A simple star-adjusted model: pull prediction toward 0.5 proportional to
    # how much the underdog (TCU) has superior star power
    # Since TeamLow is likely OSU (lower ID), and our model favors OSU at ~0.82,
    # we pull toward 0.5
    if tcu_total_war > osu_total_war:
        war_diff_frac = (tcu_total_war - osu_total_war) / tcu_total_war
        star_adjusted = orig_pred_osu + (0.5 - orig_pred_osu) * war_diff_frac * 0.5
        print(f"\n  Star-player-adjusted prediction:")
        print(f"    WAR difference fraction: {war_diff_frac:.3f}")
        print(f"    Adjustment factor (0.5x conservative): {war_diff_frac * 0.5:.3f}")
        print(f"    Original P(TeamLow wins): {orig_pred_osu:.4f}")
        print(f"    Star-adjusted P(TeamLow wins): {star_adjusted:.4f}")
        print(f"    Change: {star_adjusted - orig_pred_osu:+.4f}")

        # Actual result: TCU won, so actual = 0 if OSU is TeamLow
        actual_osu = 0.0  # TCU won, OSU is TeamLow (lower ID)
        brier_orig_osu = (orig_pred_osu - actual_osu) ** 2
        brier_star = (star_adjusted - actual_osu) ** 2
        print(f"\n    Actual result: TCU won (actual=0 for TeamLow)")
        print(f"    Brier (original):      {brier_orig_osu:.6f}")
        print(f"    Brier (star-adjusted): {brier_star:.6f}")
        print(f"    Brier improvement:     {brier_orig_osu - brier_star:+.6f}")
    else:
        print(f"\n  OSU has equal or higher team WAR - no TCU star advantage to model.")


# ============================================================================
# STEP 5: SAVE RESULTS
# ============================================================================
print("\n" + "=" * 80)
print("[Step 5] Saving results...")
print("=" * 80)

output_lines = []
output_lines.append("INJURY-ADJUSTED PREDICTIONS - 2026 NCAA TOURNAMENT")
output_lines.append("=" * 70)
output_lines.append(f"Generated: 2026-03-19")
output_lines.append(f"Adjustment strength: {ADJUSTMENT_STRENGTH}")
output_lines.append("")

output_lines.append("INJURY ADJUSTMENTS")
output_lines.append("-" * 70)
output_lines.append(f"{'Matchup':<35} {'Orig':>8} {'Adj':>8} {'Change':>8} {'WAR Lost':>10}")
output_lines.append("-" * 70)

for r in results:
    matchup_str = f"{r['team_name']} vs {r['opp_name']}"
    change = r['adjusted_pred'] - r['orig_pred']
    output_lines.append(
        f"{matchup_str:<35} {r['orig_pred']:>8.4f} {r['adjusted_pred']:>8.4f} "
        f"{change:>+8.4f} {r['total_injured_war']:>10.2f}"
    )
    for inj in r['injured_players']:
        output_lines.append(f"    OUT: {inj}")

output_lines.append("")
output_lines.append("BRIER SCORE COMPARISON (known results)")
output_lines.append("-" * 70)
output_lines.append(f"{'Game':<35} {'Actual':>6} {'Orig':>8} {'Adj':>8} "
                     f"{'B_orig':>10} {'B_adj':>10} {'Improv':>10}")
output_lines.append("-" * 70)

for d in brier_data:
    improvement_str = f"{d['brier_orig'] - d['brier_adj']:+.6f}" if d['has_injury'] else "N/A"
    output_lines.append(
        f"{d['matchup']:<35} {d['actual']:>6.0f} {d['orig_pred']:>8.4f} "
        f"{d['adjusted_pred']:>8.4f} {d['brier_orig']:>10.6f} {d['brier_adj']:>10.6f} "
        f"{improvement_str:>10}"
    )

output_lines.append("")
if brier_data:
    total_brier_orig = sum(d['brier_orig'] for d in brier_data)
    total_brier_adj = sum(d['brier_adj'] for d in brier_data)
    improvement = total_brier_orig - total_brier_adj
    output_lines.append(f"Total Brier (original):  {total_brier_orig:.6f}")
    output_lines.append(f"Total Brier (adjusted):  {total_brier_adj:.6f}")
    output_lines.append(f"EXACT IMPROVEMENT:       {improvement:+.6f}")
    output_lines.append(f"Avg Brier (original):    {total_brier_orig/len(brier_data):.6f}")
    output_lines.append(f"Avg Brier (adjusted):    {total_brier_adj/len(brier_data):.6f}")

    inj_games = [d for d in brier_data if d['has_injury']]
    if inj_games:
        inj_orig = sum(d['brier_orig'] for d in inj_games)
        inj_adj = sum(d['brier_adj'] for d in inj_games)
        output_lines.append(f"\nInjury-affected games ({len(inj_games)}):")
        output_lines.append(f"  Brier original:  {inj_orig:.6f}")
        output_lines.append(f"  Brier adjusted:  {inj_adj:.6f}")
        output_lines.append(f"  Improvement:     {inj_orig - inj_adj:+.6f}")

output_lines.append("")
output_lines.append("OHIO STATE VS TCU - STAR PLAYER ANALYSIS")
output_lines.append("-" * 70)
if 'orig_pred_osu' in dir() and orig_pred_osu is not None:
    output_lines.append(f"Original P(Ohio St wins): {orig_pred_osu:.4f}")
    output_lines.append(f"TCU total WAR: {tcu_total_war:.2f}")
    output_lines.append(f"Ohio State total WAR: {osu_total_war:.2f}")
    if tcu_total_war > osu_total_war:
        war_diff_frac = (tcu_total_war - osu_total_war) / tcu_total_war
        star_adjusted = orig_pred_osu + (0.5 - orig_pred_osu) * war_diff_frac * 0.5
        actual_osu = 0.0
        brier_orig_osu = (orig_pred_osu - actual_osu) ** 2
        brier_star = (star_adjusted - actual_osu) ** 2
        output_lines.append(f"Star-adjusted P(Ohio St wins): {star_adjusted:.4f}")
        output_lines.append(f"Brier original: {brier_orig_osu:.6f}")
        output_lines.append(f"Brier star-adjusted: {brier_star:.6f}")
        output_lines.append(f"Improvement: {brier_orig_osu - brier_star:+.6f}")

output_path = RESULTS / "injury_adjusted_predictions.txt"
with open(output_path, 'w') as f:
    f.write('\n'.join(output_lines))

print(f"\n  Results saved to: {output_path}")
print("\n" + "=" * 80)
print("DONE")
print("=" * 80)
