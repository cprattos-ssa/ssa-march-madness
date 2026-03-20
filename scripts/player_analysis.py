"""
Player-level data analysis for March Madness write-up.
Uses Barttorvik player data to derive team-level player features
and test whether they could predict 2026 upsets.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

ROOT = Path("C:/dev/ssa-march-madness")
RAW = ROOT / "data" / "raw" / "kaggle"
PLAYER = ROOT / "data" / "raw" / "external" / "player_data"
PROC = ROOT / "data" / "processed"
FIG = ROOT / "results" / "figures"

plt.rcParams.update({
    'figure.facecolor': '#0e1117', 'axes.facecolor': '#0e1117',
    'axes.edgecolor': '#333333', 'axes.labelcolor': '#e0e0e0',
    'text.color': '#e0e0e0', 'xtick.color': '#aaaaaa', 'ytick.color': '#aaaaaa',
    'grid.color': '#222222', 'grid.alpha': 0.5, 'font.family': 'sans-serif',
    'font.size': 11, 'axes.titlesize': 14, 'axes.titleweight': 'bold',
})
ACCENT = '#ff6b35'; ACCENT2 = '#00d4aa'; ACCENT3 = '#7b68ee'
ACCENT4 = '#ff4757'; ACCENT5 = '#ffd93d'

# Column mapping for Barttorvik CSV (no header row)
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
print("PLAYER-LEVEL ANALYSIS")
print("=" * 80)

# ============================================================================
# LOAD AND PARSE PLAYER DATA
# ============================================================================
print("\n[Loading player data...]")

all_players = []
for year in range(2021, 2027):
    path = PLAYER / f"barttorvik_players_{year}.csv"
    df = pd.read_csv(path, header=None)
    # Only use columns we mapped
    df = df.iloc[:, :min(len(COLS), df.shape[1])]
    df = df.rename(columns={k: v for k, v in COLS.items() if k < df.shape[1]})
    df['Season'] = year
    all_players.append(df)
    print(f"  {year}: {len(df)} players")

players = pd.concat(all_players, ignore_index=True)

# Clean numeric columns
for col in ['Games', 'MinPct', 'eFGPct', 'Usage', 'Rating', 'WAR',
            'OffRtg', 'DefRtg', 'NetRtg', 'OWS', 'DWS', 'PTSper40',
            'ASTper40', 'TRBper40', 'STLper40', 'TOVper40', 'Rank',
            'AdjOffRtg', 'AdjDefRtg']:
    if col in players.columns:
        players[col] = pd.to_numeric(players[col], errors='coerce')

# Parse height to inches
def parse_height(h):
    try:
        parts = str(h).split('-')
        return int(parts[0]) * 12 + int(parts[1])
    except:
        return np.nan

players['HeightIn'] = players['Height'].apply(parse_height)

# Class encoding
class_map = {'Fr': 1, 'So': 2, 'Jr': 3, 'Sr': 4}
players['ClassNum'] = players['Class'].map(class_map).fillna(2.5)

print(f"\nTotal players loaded: {len(players)}")
print(f"Columns: {list(players.columns[:30])}")

# ============================================================================
# BUILD TEAM NAME MAPPING (Barttorvik -> Kaggle TeamID)
# ============================================================================
print("\n[Building team name mapping...]")

teams = pd.read_csv(RAW / "MTeams.csv")
spellings = pd.read_csv(RAW / "MTeamSpellings.csv", encoding='latin1')

# Build mapping from various name forms to TeamID
name_to_id = {}
for _, row in spellings.iterrows():
    name_to_id[str(row.iloc[0]).lower().strip()] = row.iloc[1]
for _, row in teams.iterrows():
    name_to_id[row['TeamName'].lower().strip()] = row['TeamID']

# Barttorvik school names need some normalization
def normalize_school(name):
    """Try to match Barttorvik school name to Kaggle TeamID."""
    if pd.isna(name):
        return None
    name_lower = name.strip().lower()

    # Direct match
    if name_lower in name_to_id:
        return name_to_id[name_lower]

    # Common replacements
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

    # Try with 'state' suffix
    if name_lower + ' state' in name_to_id:
        return name_to_id[name_lower + ' state']

    # Fuzzy: try each spelling and find closest
    for spell, tid in name_to_id.items():
        if name_lower in spell or spell in name_lower:
            return tid

    return None

players['TeamID'] = players['School'].apply(normalize_school)

matched = players.TeamID.notna().sum()
total = len(players)
print(f"Matched: {matched}/{total} ({matched/total:.1%})")

# Show unmatched schools
unmatched = players[players.TeamID.isna()]['School'].unique()
if len(unmatched) > 0:
    print(f"Unmatched schools ({len(unmatched)}): {list(unmatched[:20])}")

# ============================================================================
# AGGREGATE PLAYER DATA TO TEAM FEATURES
# ============================================================================
print("\n[Aggregating player features per team...]")

# Filter to matched players with meaningful playing time
p = players[players.TeamID.notna() & (players.MinPct >= 10) & (players.Games >= 5)].copy()
print(f"Players with >=10% minutes and >=5 games: {len(p)}")

# Team-level aggregations
team_player_features = []

for (season, team_id), group in p.groupby(['Season', 'TeamID']):
    # Sort by minutes percentage (proxy for importance)
    g = group.sort_values('MinPct', ascending=False)

    # Star power
    top_player = g.iloc[0] if len(g) > 0 else None
    top3 = g.head(3)
    top5 = g.head(5)

    features = {
        'Season': int(season),
        'TeamID': int(team_id),
        'RosterSize': len(g),

        # Star player features
        'Star_WAR': top_player['WAR'] if top_player is not None else np.nan,
        'Star_Rating': top_player['Rating'] if top_player is not None else np.nan,
        'Star_MinPct': top_player['MinPct'] if top_player is not None else np.nan,
        'Star_Usage': top_player['Usage'] if top_player is not None else np.nan,
        'Star_PTSper40': top_player['PTSper40'] if top_player is not None else np.nan,

        # Top 3 concentration
        'Top3_WAR': top3['WAR'].sum() if len(top3) > 0 else np.nan,
        'Top3_MinPct': top3['MinPct'].sum() if len(top3) > 0 else np.nan,
        'Top3_Usage': top3['Usage'].mean() if len(top3) > 0 else np.nan,

        # Team depth (how much do top 5 dominate?)
        'Top5_MinShare': top5['MinPct'].sum() / g['MinPct'].sum() if g['MinPct'].sum() > 0 else np.nan,

        # Total team WAR
        'Team_WAR': g['WAR'].sum(),
        'Team_WAR_Std': g['WAR'].std(),

        # Experience
        'Avg_ClassNum': g['ClassNum'].mean(),
        'Sr_Count': (g['Class'] == 'Sr').sum(),
        'Fr_Count': (g['Class'] == 'Fr').sum(),
        'Sr_Pct': (g['Class'] == 'Sr').mean(),

        # Height
        'Avg_Height': g['HeightIn'].mean(),
        'Max_Height': g['HeightIn'].max(),

        # Shooting
        'Team_eFGPct': (g['eFGPct'] * g['MinPct']).sum() / g['MinPct'].sum() if g['MinPct'].sum() > 0 else np.nan,

        # Ratings
        'Avg_Rating': g['Rating'].mean(),
        'Avg_OffRtg': g['OffRtg'].mean() if 'OffRtg' in g.columns else np.nan,
        'Avg_DefRtg': g['DefRtg'].mean() if 'DefRtg' in g.columns else np.nan,

        # WAR distribution (inequality = fragile)
        'WAR_Gini': np.nan,  # will compute below
        'WAR_Top1_Share': top_player['WAR'] / g['WAR'].sum() if g['WAR'].sum() > 0 and top_player is not None else np.nan,
    }

    # Gini coefficient of WAR (higher = more unequal = star-dependent)
    war_vals = g['WAR'].dropna().values
    if len(war_vals) > 1 and war_vals.sum() > 0:
        war_sorted = np.sort(war_vals)
        n = len(war_sorted)
        index = np.arange(1, n + 1)
        features['WAR_Gini'] = (2 * np.sum(index * war_sorted) - (n + 1) * np.sum(war_sorted)) / (n * np.sum(war_sorted))

    team_player_features.append(features)

tpf = pd.DataFrame(team_player_features)
print(f"Team-player features computed: {len(tpf)} team-seasons")
print(f"Feature columns: {list(tpf.columns)}")

# ============================================================================
# MERGE WITH TOURNAMENT DATA AND ANALYZE
# ============================================================================
print("\n" + "=" * 80)
print("PLAYER FEATURES vs TOURNAMENT PERFORMANCE")
print("=" * 80)

seeds = pd.read_csv(RAW / "MNCAATourneySeeds.csv")
seeds['SeedNum'] = seeds['Seed'].str.extract(r'(\d+)').astype(int)

tourney = pd.read_csv(RAW / "MNCAATourneyCompactResults.csv")
tourney_wins = tourney.groupby(['Season', 'WTeamID']).size().reset_index(name='TourneyWins')
tourney_wins.rename(columns={'WTeamID': 'TeamID'}, inplace=True)

# Merge
analysis = tpf.merge(seeds[['Season', 'TeamID', 'SeedNum']], on=['Season', 'TeamID'], how='inner')
analysis = analysis.merge(tourney_wins, on=['Season', 'TeamID'], how='left')
analysis['TourneyWins'] = analysis['TourneyWins'].fillna(0).astype(int)

# Expected wins by seed
seed_avg = analysis.groupby('SeedNum')['TourneyWins'].mean()
analysis['ExpectedWins'] = analysis['SeedNum'].map(seed_avg)
analysis['WinsOverExpected'] = analysis['TourneyWins'] - analysis['ExpectedWins']

print(f"Tournament teams with player features: {len(analysis)}")
print(f"Seasons covered: {sorted(analysis.Season.unique())}")

# Correlation analysis - which player features predict tournament overperformance?
player_cols = ['Star_WAR', 'Star_Rating', 'Star_MinPct', 'Star_Usage',
               'Top3_WAR', 'Top3_MinPct', 'Team_WAR', 'Team_WAR_Std',
               'Avg_ClassNum', 'Sr_Count', 'Sr_Pct', 'Avg_Height',
               'Team_eFGPct', 'Avg_Rating', 'WAR_Gini', 'WAR_Top1_Share',
               'RosterSize', 'Top5_MinShare']

print(f"\nPLAYER FEATURE CORRELATIONS WITH TOURNAMENT WINS OVER EXPECTED:")
corrs = []
for col in player_cols:
    valid = analysis[[col, 'WinsOverExpected']].dropna()
    if len(valid) > 20:
        r = valid.corr().iloc[0, 1]
        corrs.append((col, r, len(valid)))

corrs.sort(key=lambda x: abs(x[1]), reverse=True)
for col, r, n in corrs:
    sig = '***' if abs(r) > 0.15 else '**' if abs(r) > 0.10 else '*' if abs(r) > 0.05 else ''
    print(f"  {col:<20}: r = {r:+.4f} (n={n}) {sig}")

# ============================================================================
# STAR DEPENDENCY ANALYSIS
# ============================================================================
print("\n" + "=" * 80)
print("STAR DEPENDENCY: DOES RELYING ON ONE PLAYER HURT IN MARCH?")
print("=" * 80)

analysis['StarDependent'] = analysis['WAR_Top1_Share'] > analysis['WAR_Top1_Share'].median()

star_dep = analysis.groupby('StarDependent').agg(
    avg_woe=('WinsOverExpected', 'mean'),
    avg_wins=('TourneyWins', 'mean'),
    n=('TourneyWins', 'count'),
).reset_index()

print("Star-dependent (top player has >median share of team WAR):")
for _, r in star_dep.iterrows():
    label = "Star-dependent" if r.StarDependent else "Balanced roster"
    print(f"  {label}: Avg WoE = {r.avg_woe:+.3f}, Avg wins = {r.avg_wins:.2f} (n={int(r.n)})")

# ============================================================================
# EXPERIENCE ANALYSIS
# ============================================================================
print("\n" + "=" * 80)
print("EXPERIENCE: DO SENIOR-HEAVY TEAMS OUTPERFORM?")
print("=" * 80)

analysis['ExpQ'] = pd.qcut(analysis['Avg_ClassNum'], 4,
                             labels=['Young', 'Youngish', 'Older', 'Very Exp'])
exp_result = analysis.groupby('ExpQ')['WinsOverExpected'].agg(['mean', 'std', 'count'])
for q, r in exp_result.iterrows():
    print(f"  {q:<12}: Avg WoE = {r['mean']:+.3f}, Std = {r['std']:.3f}, N = {int(r['count'])}")

# ============================================================================
# 2026 TOURNAMENT FIELD - PLAYER FEATURES
# ============================================================================
print("\n" + "=" * 80)
print("2026 FIELD: PLAYER-LEVEL INSIGHTS")
print("=" * 80)

team_names_map = dict(zip(teams['TeamID'], teams['TeamName']))

field_2026 = tpf[tpf.Season == 2026].merge(
    seeds[seeds.Season == 2026][['Season', 'TeamID', 'SeedNum']],
    on=['Season', 'TeamID'], how='inner'
)
field_2026['TeamName'] = field_2026['TeamID'].map(team_names_map)

if len(field_2026) > 0:
    print(f"2026 teams with player data: {len(field_2026)}")

    print(f"\nHIGHEST TEAM WAR (total roster talent):")
    for _, r in field_2026.nlargest(10, 'Team_WAR').iterrows():
        print(f"  ({int(r.SeedNum)}) {r.TeamName}: Team WAR={r.Team_WAR:.1f}, "
              f"Star WAR={r.Star_WAR:.1f}, Roster={int(r.RosterSize)}")

    print(f"\nMOST STAR-DEPENDENT (highest % of WAR in one player):")
    for _, r in field_2026.nlargest(10, 'WAR_Top1_Share').iterrows():
        print(f"  ({int(r.SeedNum)}) {r.TeamName}: Top1 WAR share={r.WAR_Top1_Share:.1%}, "
              f"Star WAR={r.Star_WAR:.1f}, Team WAR={r.Team_WAR:.1f}")

    print(f"\nMOST EXPERIENCED ROSTERS:")
    for _, r in field_2026.nlargest(5, 'Avg_ClassNum').iterrows():
        print(f"  ({int(r.SeedNum)}) {r.TeamName}: Avg class={r.Avg_ClassNum:.2f}, "
              f"Seniors={int(r.Sr_Count)}, Freshmen={int(r.Fr_Count)}")

    print(f"\nYOUNGEST ROSTERS:")
    for _, r in field_2026.nsmallest(5, 'Avg_ClassNum').iterrows():
        print(f"  ({int(r.SeedNum)}) {r.TeamName}: Avg class={r.Avg_ClassNum:.2f}, "
              f"Seniors={int(r.Sr_Count)}, Freshmen={int(r.Fr_Count)}")

    print(f"\nDEEPEST ROSTERS (most balanced WAR distribution):")
    for _, r in field_2026.nsmallest(5, 'WAR_Gini').iterrows():
        print(f"  ({int(r.SeedNum)}) {r.TeamName}: WAR Gini={r.WAR_Gini:.3f}, "
              f"Team WAR={r.Team_WAR:.1f}, Roster={int(r.RosterSize)}")

    # --- Look at specific matchups that are potential upsets ---
    print(f"\n{'=' * 80}")
    print("UPSET PREDICTION: PLAYER DATA ANGLE ON KEY 2026 MATCHUPS")
    print("=" * 80)

    # Get star players for 2026 tournament teams
    p2026 = players[(players.Season == 2026) & players.TeamID.notna()].copy()
    p2026_tourney = p2026[p2026.TeamID.isin(field_2026.TeamID.values)]
    p2026_tourney = p2026_tourney.sort_values(['TeamID', 'MinPct'], ascending=[True, False])

    # Define key matchups (seed matchups from 2026 bracket)
    # We know: 8 Ohio State vs 9 TCU, plus the popular upset picks
    key_matchups = [
        # (team_a_seed, team_a_name_fragment, team_b_seed, team_b_name_fragment)
        (8, 'Ohio St', 9, 'TCU'),
        (5, 'Texas Tech', 12, 'Akron'),
        (6, 'Louisville', 11, 'South Florida'),
        (6, 'North Carolina', 11, 'VCU'),
        (4, 'Alabama', 13, 'Hofstra'),
        (4, 'Kansas', 13, 'Cal Baptist'),
        (5, 'Wisconsin', 12, 'High Point'),
        (3, 'Gonzaga', 14, 'Penn'),
    ]

    for seed_a, name_a, seed_b, name_b in key_matchups:
        team_a = field_2026[field_2026.TeamName.str.contains(name_a, case=False, na=False)]
        team_b = field_2026[field_2026.TeamName.str.contains(name_b, case=False, na=False)]

        if len(team_a) > 0 and len(team_b) > 0:
            a = team_a.iloc[0]
            b = team_b.iloc[0]

            # Get star players
            a_stars = p2026_tourney[p2026_tourney.TeamID == a.TeamID].head(3)
            b_stars = p2026_tourney[p2026_tourney.TeamID == b.TeamID].head(3)

            war_adv = a.Team_WAR - b.Team_WAR
            depth_adv = a.WAR_Gini - b.WAR_Gini  # lower gini = deeper

            print(f"\n  ({seed_a}) {a.TeamName} vs ({seed_b}) {b.TeamName}")
            print(f"    Team WAR: {a.Team_WAR:.1f} vs {b.Team_WAR:.1f} (diff: {war_adv:+.1f})")
            print(f"    Star WAR: {a.Star_WAR:.1f} vs {b.Star_WAR:.1f}")
            print(f"    Depth (Gini): {a.WAR_Gini:.3f} vs {b.WAR_Gini:.3f} ({'deeper' if depth_adv > 0 else 'shallower'})")
            print(f"    Experience: {a.Avg_ClassNum:.2f} vs {b.Avg_ClassNum:.2f}")

            if len(a_stars) > 0:
                print(f"    {a.TeamName} stars:", end='')
                for _, s in a_stars.iterrows():
                    print(f" {s.Name}({s.WAR:.1f}WAR)", end='')
                print()
            if len(b_stars) > 0:
                print(f"    {b.TeamName} stars:", end='')
                for _, s in b_stars.iterrows():
                    print(f" {s.Name}({s.WAR:.1f}WAR)", end='')
                print()

            # Flag potential upset
            if b.Team_WAR > a.Team_WAR * 0.85:
                print(f"    ** UPSET SIGNAL: {b.TeamName} WAR within 15% of {a.TeamName}")
            if b.Star_WAR > a.Star_WAR:
                print(f"    ** UPSET SIGNAL: {b.TeamName} has better star player")

# ============================================================================
# FIGURES
# ============================================================================

# --- FIGURE 11: Team WAR vs Tournament Performance ---
fig, ax = plt.subplots(figsize=(12, 8))
modern = analysis[analysis.Season >= 2021]
scatter = ax.scatter(modern.Team_WAR, modern.TourneyWins,
                     c=modern.SeedNum, cmap='RdYlGn_r', s=60,
                     alpha=0.7, edgecolors='white', linewidths=0.3)
cbar = plt.colorbar(scatter, ax=ax, label='Seed', shrink=0.8)
cbar.ax.yaxis.label.set_color('#e0e0e0')
cbar.ax.tick_params(colors='#aaaaaa')

z = np.polyfit(modern.Team_WAR.dropna(), modern.loc[modern.Team_WAR.notna(), 'TourneyWins'], 1)
x_line = np.linspace(modern.Team_WAR.min(), modern.Team_WAR.max(), 100)
ax.plot(x_line, np.poly1d(z)(x_line), color=ACCENT4, linewidth=2, linestyle='--')

corr = modern[['Team_WAR', 'TourneyWins']].corr().iloc[0, 1]
ax.set_xlabel('Total Team WAR (Barttorvik)', fontsize=12)
ax.set_ylabel('Tournament Wins', fontsize=12)
ax.set_title(f'Does Roster Talent (WAR) Predict March Success? (r={corr:.3f}, 2021-2025)', fontsize=14, pad=15)
ax.grid(alpha=0.2)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.tight_layout()
plt.savefig(FIG / '11_team_war_vs_tourney.png', dpi=200, bbox_inches='tight')
plt.close()
print(f"\nSaved: 11_team_war_vs_tourney.png")

# --- FIGURE 12: Star Dependency vs Upset Vulnerability ---
fig, ax = plt.subplots(figsize=(12, 8))
favs = modern[modern.SeedNum <= 4]  # Top-4 seeds
ax.scatter(favs.WAR_Top1_Share * 100, favs.WinsOverExpected,
           c=favs.SeedNum, cmap='RdYlGn_r', s=80, alpha=0.7,
           edgecolors='white', linewidths=0.3)

z = np.polyfit(favs.WAR_Top1_Share.dropna() * 100,
               favs.loc[favs.WAR_Top1_Share.notna(), 'WinsOverExpected'], 1)
x_line = np.linspace(favs.WAR_Top1_Share.min() * 100, favs.WAR_Top1_Share.max() * 100, 100)
ax.plot(x_line, np.poly1d(z)(x_line), color=ACCENT4, linewidth=2, linestyle='--')

corr = favs[['WAR_Top1_Share', 'WinsOverExpected']].corr().iloc[0, 1]
ax.axhline(y=0, color='white', alpha=0.3, linewidth=0.5)
ax.set_xlabel('Star Player WAR Share (% of Team Total)', fontsize=12)
ax.set_ylabel('Tournament Wins Over Expected', fontsize=12)
ax.set_title(f'Star Dependency & March Vulnerability (Top-4 Seeds, r={corr:.3f})', fontsize=14, pad=15)
ax.grid(alpha=0.2)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.tight_layout()
plt.savefig(FIG / '12_star_dependency.png', dpi=200, bbox_inches='tight')
plt.close()
print(f"Saved: 12_star_dependency.png")

# --- FIGURE 13: 2026 Field - Team WAR vs Seed ---
if len(field_2026) > 0:
    fig, ax = plt.subplots(figsize=(16, 10))
    scatter = ax.scatter(field_2026.SeedNum, field_2026.Team_WAR,
                         c=field_2026.WAR_Gini, cmap='RdYlGn_r',
                         s=120, edgecolors='white', linewidths=0.5, zorder=5)
    cbar = plt.colorbar(scatter, ax=ax, label='WAR Gini (lower = deeper roster)', shrink=0.8)
    cbar.ax.yaxis.label.set_color('#e0e0e0')
    cbar.ax.tick_params(colors='#aaaaaa')

    for _, r in field_2026.iterrows():
        ax.annotate(r.TeamName[:14] if len(str(r.TeamName)) > 14 else r.TeamName,
                    (r.SeedNum, r.Team_WAR),
                    xytext=(6, 3), textcoords='offset points', fontsize=6.5, color='#cccccc')

    ax.set_xlabel('Tournament Seed', fontsize=12)
    ax.set_ylabel('Total Team WAR', fontsize=12)
    ax.set_title('2026 Tournament: Roster Talent vs Seed (color = depth)', fontsize=15, pad=15)
    ax.invert_xaxis()
    ax.grid(alpha=0.2)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    plt.savefig(FIG / '13_2026_team_war.png', dpi=200, bbox_inches='tight')
    plt.close()
    print(f"Saved: 13_2026_team_war.png")

# --- FIGURE 14: Experience vs Tournament (modern era only) ---
fig, axes = plt.subplots(1, 2, figsize=(16, 7))

ax = axes[0]
modern_valid = modern.dropna(subset=['Avg_ClassNum', 'WinsOverExpected'])
ax.scatter(modern_valid.Avg_ClassNum, modern_valid.WinsOverExpected,
           c=modern_valid.SeedNum, cmap='RdYlGn_r', alpha=0.6, s=50,
           edgecolors='white', linewidths=0.3)
z = np.polyfit(modern_valid.Avg_ClassNum, modern_valid.WinsOverExpected, 1)
x_line = np.linspace(modern_valid.Avg_ClassNum.min(), modern_valid.Avg_ClassNum.max(), 100)
ax.plot(x_line, np.poly1d(z)(x_line), color=ACCENT4, linewidth=2, linestyle='--')
corr = modern_valid[['Avg_ClassNum', 'WinsOverExpected']].corr().iloc[0, 1]
ax.set_xlabel('Average Roster Experience (1=Fr, 4=Sr)', fontsize=11)
ax.set_ylabel('Wins Over Expected', fontsize=11)
ax.set_title(f'Experience in the Portal Era (r={corr:.3f})', fontsize=13, pad=10)
ax.axhline(y=0, color='white', alpha=0.3)
ax.grid(alpha=0.2)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

ax = axes[1]
# Senior percentage
modern_valid2 = modern.dropna(subset=['Sr_Pct', 'WinsOverExpected'])
ax.scatter(modern_valid2.Sr_Pct * 100, modern_valid2.WinsOverExpected,
           c=modern_valid2.SeedNum, cmap='RdYlGn_r', alpha=0.6, s=50,
           edgecolors='white', linewidths=0.3)
z = np.polyfit(modern_valid2.Sr_Pct * 100, modern_valid2.WinsOverExpected, 1)
x_line = np.linspace(0, 100, 100)
ax.plot(x_line, np.poly1d(z)(x_line), color=ACCENT4, linewidth=2, linestyle='--')
corr = modern_valid2[['Sr_Pct', 'WinsOverExpected']].corr().iloc[0, 1]
ax.set_xlabel('Senior Percentage (%)', fontsize=11)
ax.set_ylabel('Wins Over Expected', fontsize=11)
ax.set_title(f'Seniors in March (r={corr:.3f})', fontsize=13, pad=10)
ax.axhline(y=0, color='white', alpha=0.3)
ax.grid(alpha=0.2)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.tight_layout()
plt.savefig(FIG / '14_experience_portal_era.png', dpi=200, bbox_inches='tight')
plt.close()
print(f"Saved: 14_experience_portal_era.png")

print("\n" + "=" * 80)
print("PLAYER ANALYSIS COMPLETE")
print("=" * 80)
