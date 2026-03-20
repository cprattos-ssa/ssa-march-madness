"""
Deep data analysis for March Madness write-up.
Finds anomalies, surprising patterns, and generates publication-quality figures.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Paths
ROOT = Path("C:/dev/ssa-march-madness")
RAW = ROOT / "data" / "raw" / "kaggle"
PROC = ROOT / "data" / "processed"
FIG = ROOT / "results" / "figures"
FIG.mkdir(parents=True, exist_ok=True)

# Style setup - clean dark theme
plt.rcParams.update({
    'figure.facecolor': '#0e1117',
    'axes.facecolor': '#0e1117',
    'axes.edgecolor': '#333333',
    'axes.labelcolor': '#e0e0e0',
    'text.color': '#e0e0e0',
    'xtick.color': '#aaaaaa',
    'ytick.color': '#aaaaaa',
    'grid.color': '#222222',
    'grid.alpha': 0.5,
    'font.family': 'sans-serif',
    'font.size': 11,
    'axes.titlesize': 14,
    'axes.titleweight': 'bold',
    'figure.titlesize': 16,
    'figure.titleweight': 'bold',
})

ACCENT = '#ff6b35'  # Orange
ACCENT2 = '#00d4aa'  # Teal
ACCENT3 = '#7b68ee'  # Purple
ACCENT4 = '#ff4757'  # Red
ACCENT5 = '#ffd93d'  # Yellow
PALETTE = [ACCENT, ACCENT2, ACCENT3, ACCENT4, ACCENT5, '#4ecdc4', '#45b7d1', '#96ceb4']

print("=" * 80)
print("DEEP DATA ANALYSIS - MARCH MADNESS")
print("=" * 80)

# ============================================================================
# LOAD DATA
# ============================================================================
print("\n[Loading data...]")

tourney = pd.read_csv(RAW / "MNCAATourneyCompactResults.csv")
tourney_det = pd.read_csv(RAW / "MNCAATourneyDetailedResults.csv")
seeds = pd.read_csv(RAW / "MNCAATourneySeeds.csv")
reg_det = pd.read_csv(RAW / "MRegularSeasonDetailedResults.csv")
reg_compact = pd.read_csv(RAW / "MRegularSeasonCompactResults.csv")
teams = pd.read_csv(RAW / "MTeams.csv")
coaches = pd.read_csv(RAW / "MTeamCoaches.csv")
conferences = pd.read_csv(RAW / "MTeamConferences.csv")
conf_names = pd.read_csv(RAW / "Conferences.csv")
training = pd.read_parquet(PROC / "training_matchups.parquet")
team_features = pd.read_parquet(PROC / "team_features.parquet")

# Parse seed numbers
seeds['SeedNum'] = seeds['Seed'].str.extract(r'(\d+)').astype(int)
seeds['Region'] = seeds['Seed'].str[0]

# Team name lookup
team_names = dict(zip(teams['TeamID'], teams['TeamName']))

print(f"  Tourney games: {len(tourney)} ({tourney.Season.min()}-{tourney.Season.max()})")
print(f"  Detailed tourney: {len(tourney_det)} ({tourney_det.Season.min()}-{tourney_det.Season.max()})")
print(f"  Regular season detailed: {len(reg_det)}")
print(f"  Seeds: {len(seeds)}")

# ============================================================================
# 1. UPSET PATTERN ANALYSIS
# ============================================================================
print("\n" + "=" * 80)
print("1. UPSET PATTERN ANALYSIS")
print("=" * 80)

# Merge seeds into tourney results
t = tourney.copy()
t = t.merge(seeds[['Season', 'TeamID', 'SeedNum']].rename(
    columns={'TeamID': 'WTeamID', 'SeedNum': 'WSeed'}), on=['Season', 'WTeamID'], how='left')
t = t.merge(seeds[['Season', 'TeamID', 'SeedNum']].rename(
    columns={'TeamID': 'LTeamID', 'SeedNum': 'LSeed'}), on=['Season', 'LTeamID'], how='left')
t = t.dropna(subset=['WSeed', 'LSeed'])
t['Upset'] = t['WSeed'] > t['LSeed']
t['SeedDiff'] = t['LSeed'] - t['WSeed']  # positive = bigger upset
t['Margin'] = t['WScore'] - t['LScore']
t['MatchupKey'] = t.apply(lambda r: f"{int(min(r.WSeed, r.LSeed))}v{int(max(r.WSeed, r.LSeed))}", axis=1)

# Upset rate by matchup
matchup_stats = t.groupby('MatchupKey').agg(
    games=('Upset', 'count'),
    upsets=('Upset', 'sum'),
).reset_index()
matchup_stats['upset_rate'] = matchup_stats['upsets'] / matchup_stats['games']
matchup_stats = matchup_stats[matchup_stats.games >= 10].sort_values('upset_rate', ascending=False)

print("\nMost upset-prone matchups (min 10 games):")
for _, r in matchup_stats.head(10).iterrows():
    print(f"  {r.MatchupKey}: {r.upset_rate:.1%} upset rate ({int(r.upsets)}/{int(r.games)} games)")

# The 11-seed deep dive
seed_11_games = t[(t.WSeed == 11) | (t.LSeed == 11)]
seed_11_wins = t[t.WSeed == 11]
print(f"\n11-SEED ANALYSIS:")
print(f"  Total games involving 11-seeds: {len(seed_11_games)}")
print(f"  11-seed wins: {len(seed_11_wins)} ({len(seed_11_wins)/len(seed_11_games):.1%})")
# vs specific opponents
for opp in sorted(seed_11_games.apply(lambda r: int(r.LSeed) if r.WSeed == 11 else int(r.WSeed), axis=1).unique()):
    games_vs = seed_11_games[(seed_11_games.WSeed == opp) | (seed_11_games.LSeed == opp)]
    wins_vs = seed_11_wins[seed_11_wins.LSeed == opp]
    if len(games_vs) >= 3:
        print(f"  11 vs {opp}: {len(wins_vs)}/{len(games_vs)} ({len(wins_vs)/len(games_vs):.1%})")

# Chaos years - upset count per tournament
yearly_upsets = t.groupby('Season').agg(
    games=('Upset', 'count'),
    upsets=('Upset', 'sum'),
).reset_index()
yearly_upsets['upset_rate'] = yearly_upsets['upsets'] / yearly_upsets['games']

print(f"\nCHAOS YEARS (highest upset rates):")
for _, r in yearly_upsets.nlargest(5, 'upset_rate').iterrows():
    print(f"  {int(r.Season)}: {r.upset_rate:.1%} ({int(r.upsets)} upsets in {int(r.games)} games)")

print(f"\nCHALK YEARS (lowest upset rates):")
for _, r in yearly_upsets.nsmallest(5, 'upset_rate').iterrows():
    print(f"  {int(r.Season)}: {r.upset_rate:.1%} ({int(r.upsets)} upsets in {int(r.games)} games)")

# Does early-round chaos cascade?
# Split into first weekend (R64 + R32) vs second weekend (S16+)
# Use DayNum to approximate rounds
t['Round'] = pd.cut(t.DayNum, bins=[0, 137, 139, 144, 146, 153, 155, 200],
                     labels=['R64a', 'R64b', 'R32', 'S16', 'E8', 'F4', 'NCG'])

first_weekend = t[t.DayNum <= 139]
second_weekend = t[(t.DayNum > 139) & (t.DayNum <= 155)]

fw_upsets = first_weekend.groupby('Season')['Upset'].mean()
sw_upsets = second_weekend.groupby('Season')['Upset'].mean()
both = pd.DataFrame({'first_weekend': fw_upsets, 'second_weekend': sw_upsets}).dropna()
corr = both.corr().iloc[0, 1]
print(f"\nCASCADE EFFECT: Correlation between first-weekend and second-weekend upset rates: {corr:.3f}")
if abs(corr) < 0.3:
    print("  -> Weak correlation: chaos does NOT cascade. Early upsets don't predict late upsets.")
elif corr > 0.3:
    print("  -> Positive correlation: chaos DOES cascade. Wild first weekends lead to wild second weekends.")
else:
    print("  -> Negative correlation: chaos is self-correcting. Wild first weekends lead to chalk second weekends.")

# Upset rate over decades
t['Decade'] = (t.Season // 10) * 10
decade_upsets = t.groupby('Decade').agg(
    games=('Upset', 'count'),
    upsets=('Upset', 'sum'),
).reset_index()
decade_upsets['upset_rate'] = decade_upsets['upsets'] / decade_upsets['games']
print("\nUPSET RATE BY DECADE:")
for _, r in decade_upsets.iterrows():
    print(f"  {int(r.Decade)}s: {r.upset_rate:.1%} ({int(r.upsets)}/{int(r.games)})")

# --- FIGURE 1: Upset rate by seed matchup ---
fig, ax = plt.subplots(figsize=(14, 7))
# Focus on first-round matchups (1v16, 2v15, ..., 8v9)
fr_matchups = ['1v16', '2v15', '3v14', '4v13', '5v12', '6v11', '7v10', '8v9']
fr_data = matchup_stats[matchup_stats.MatchupKey.isin(fr_matchups)].copy()
fr_data['sort'] = fr_data.MatchupKey.map({m: i for i, m in enumerate(fr_matchups)})
fr_data = fr_data.sort_values('sort')

bars = ax.bar(fr_data.MatchupKey, fr_data.upset_rate * 100, color=ACCENT, alpha=0.85, width=0.6,
              edgecolor='white', linewidth=0.5)

# Highlight the anomalies
for bar, (_, row) in zip(bars, fr_data.iterrows()):
    if row.MatchupKey in ['5v12', '6v11']:
        bar.set_color(ACCENT4)
        bar.set_alpha(0.95)
    if row.MatchupKey == '8v9':
        bar.set_color(ACCENT2)
        bar.set_alpha(0.95)

# Add value labels
for bar, (_, row) in zip(bars, fr_data.iterrows()):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
            f'{row.upset_rate:.0%}\n({int(row.upsets)}/{int(row.games)})',
            ha='center', va='bottom', fontsize=9, color='#cccccc')

ax.set_ylabel('Upset Rate (%)', fontsize=12)
ax.set_xlabel('Seed Matchup (lower seed vs higher seed)', fontsize=12)
ax.set_title('First-Round Upset Rates: The 12-5 and 11-6 Anomalies', fontsize=15, pad=15)
ax.set_ylim(0, 60)
ax.grid(axis='y', alpha=0.3)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.tight_layout()
plt.savefig(FIG / '01_upset_rates_by_matchup.png', dpi=200, bbox_inches='tight')
plt.close()
print("\nSaved: 01_upset_rates_by_matchup.png")

# --- FIGURE 2: Upset rate over time with trend ---
fig, ax = plt.subplots(figsize=(14, 6))
ax.bar(yearly_upsets.Season, yearly_upsets.upset_rate * 100, color=ACCENT, alpha=0.6, width=0.8)

# Rolling average
window = 5
rolling = yearly_upsets.set_index('Season')['upset_rate'].rolling(window, center=True).mean() * 100
ax.plot(rolling.index, rolling.values, color=ACCENT2, linewidth=2.5, label=f'{window}-year rolling avg')

# Mark notable years
for _, r in yearly_upsets.nlargest(3, 'upset_rate').iterrows():
    ax.annotate(f"{int(r.Season)}", (r.Season, r.upset_rate * 100 + 1.5),
                ha='center', fontsize=8, color=ACCENT4, fontweight='bold')

ax.set_xlabel('Season', fontsize=12)
ax.set_ylabel('Upset Rate (%)', fontsize=12)
ax.set_title('Are Upsets Dying? Tournament Upset Rates 1985-2025', fontsize=15, pad=15)
ax.legend(framealpha=0.3, facecolor='#1a1a2e')
ax.grid(axis='y', alpha=0.3)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.tight_layout()
plt.savefig(FIG / '02_upset_rate_over_time.png', dpi=200, bbox_inches='tight')
plt.close()
print("Saved: 02_upset_rate_over_time.png")


# ============================================================================
# 2. EFFICIENCY ANOMALIES - "FOOL'S GOLD" AND "HIDDEN GEMS"
# ============================================================================
print("\n" + "=" * 80)
print("2. EFFICIENCY ANOMALIES")
print("=" * 80)

# Compute per-possession efficiency for all team-seasons
def compute_efficiency(df, season_min=2003):
    df = df[df.Season >= season_min].copy()

    # Winner stats
    w = df.groupby(['Season', 'WTeamID']).agg(
        W_FGM=('WFGM', 'sum'), W_FGA=('WFGA', 'sum'),
        W_FGM3=('WFGM3', 'sum'), W_FGA3=('WFGA3', 'sum'),
        W_FTM=('WFTM', 'sum'), W_FTA=('WFTA', 'sum'),
        W_OR=('WOR', 'sum'), W_DR=('WDR', 'sum'),
        W_TO=('WTO', 'sum'), W_Score=('WScore', 'sum'),
        W_Games=('WScore', 'count'),
        L_OR_opp=('LOR', 'sum'), L_FGA_opp=('LFGA', 'sum'),
        L_FTA_opp=('LFTA', 'sum'), L_TO_opp=('LTO', 'sum'),
        L_Score_opp=('LScore', 'sum'),
    ).reset_index().rename(columns={'WTeamID': 'TeamID'})

    # Loser stats
    l = df.groupby(['Season', 'LTeamID']).agg(
        L_FGM=('LFGM', 'sum'), L_FGA=('LFGA', 'sum'),
        L_FGM3=('LFGM3', 'sum'), L_FGA3=('LFGA3', 'sum'),
        L_FTM=('LFTM', 'sum'), L_FTA=('LFTA', 'sum'),
        L_OR=('LOR', 'sum'), L_DR=('LDR', 'sum'),
        L_TO=('LTO', 'sum'), L_Score=('LScore', 'sum'),
        L_Games=('LScore', 'count'),
        W_OR_opp=('WOR', 'sum'), W_FGA_opp=('WFGA', 'sum'),
        W_FTA_opp=('WFTA', 'sum'), W_TO_opp=('WTO', 'sum'),
        W_Score_opp=('WScore', 'sum'),
    ).reset_index().rename(columns={'LTeamID': 'TeamID'})

    # Combine
    merged = w.merge(l, on=['Season', 'TeamID'], how='outer').fillna(0)

    merged['Games'] = merged['W_Games'] + merged['L_Games']
    merged['Wins'] = merged['W_Games']
    merged['WinPct'] = merged['Wins'] / merged['Games']

    # Total stats
    merged['FGA'] = merged['W_FGA'] + merged['L_FGA']
    merged['FGM'] = merged['W_FGM'] + merged['L_FGM']
    merged['FGM3'] = merged['W_FGM3'] + merged['L_FGM3']
    merged['FGA3'] = merged['W_FGA3'] + merged['L_FGA3']
    merged['FTM'] = merged['W_FTM'] + merged['L_FTM']
    merged['FTA'] = merged['W_FTA'] + merged['L_FTA']
    merged['ORB'] = merged['W_OR'] + merged['L_OR']
    merged['TO'] = merged['W_TO'] + merged['L_TO']
    merged['Pts'] = merged['W_Score'] + merged['L_Score']
    merged['PtsAllowed'] = merged['L_Score_opp'] + merged['W_Score_opp']

    # Opponent stats for defensive efficiency
    merged['Opp_FGA'] = merged['L_FGA_opp'] + merged['W_FGA_opp']
    merged['Opp_FTA'] = merged['L_FTA_opp'] + merged['W_FTA_opp']
    merged['Opp_ORB'] = merged['L_OR_opp'] + merged['W_OR_opp']
    merged['Opp_TO'] = merged['L_TO_opp'] + merged['W_TO_opp']

    # Possessions
    merged['Poss'] = merged['FGA'] - merged['ORB'] + merged['TO'] + 0.475 * merged['FTA']
    merged['OppPoss'] = merged['Opp_FGA'] - merged['Opp_ORB'] + merged['Opp_TO'] + 0.475 * merged['Opp_FTA']

    # Efficiency per 100 possessions
    merged['OffEff'] = merged['Pts'] / merged['Poss'] * 100
    merged['DefEff'] = merged['PtsAllowed'] / merged['OppPoss'] * 100
    merged['NetEff'] = merged['OffEff'] - merged['DefEff']

    # eFG%
    merged['eFGPct'] = (merged['FGM'] + 0.5 * merged['FGM3']) / merged['FGA']

    # Turnover rate
    merged['TORate'] = merged['TO'] / merged['Poss']

    # 3-point rate
    merged['FG3Rate'] = merged['FGA3'] / merged['FGA']
    merged['FG3Pct'] = merged['FGM3'] / merged['FGA3']

    # PPG
    merged['PPG'] = merged['Pts'] / merged['Games']
    merged['OppPPG'] = merged['PtsAllowed'] / merged['Games']

    return merged[['Season', 'TeamID', 'Games', 'Wins', 'WinPct', 'Pts', 'PtsAllowed',
                    'Poss', 'OffEff', 'DefEff', 'NetEff', 'eFGPct', 'TORate',
                    'FG3Rate', 'FG3Pct', 'PPG', 'OppPPG', 'FGA3', 'FGM3', 'FGA', 'FGM']]

eff = compute_efficiency(reg_det)
print(f"Computed efficiency for {len(eff)} team-seasons")

# Merge with seeds
eff_seeded = eff.merge(seeds[['Season', 'TeamID', 'SeedNum']], on=['Season', 'TeamID'], how='inner')
print(f"Seeded teams with efficiency: {len(eff_seeded)}")

# Merge with tourney results to see how far they went
# Count tourney wins per team-season
tourney_wins = tourney.groupby(['Season', 'WTeamID']).size().reset_index(name='TourneyWins')
tourney_wins.rename(columns={'WTeamID': 'TeamID'}, inplace=True)
eff_seeded = eff_seeded.merge(tourney_wins, on=['Season', 'TeamID'], how='left')
eff_seeded['TourneyWins'] = eff_seeded['TourneyWins'].fillna(0).astype(int)

# Expected tourney wins by seed (baseline)
seed_avg_wins = eff_seeded.groupby('SeedNum')['TourneyWins'].mean()
eff_seeded['ExpectedWins'] = eff_seeded['SeedNum'].map(seed_avg_wins)
eff_seeded['WinsOverExpected'] = eff_seeded['TourneyWins'] - eff_seeded['ExpectedWins']

# Efficiency rank within season
eff_seeded['NetEffRank'] = eff_seeded.groupby('Season')['NetEff'].rank(ascending=False)

# Fool's gold: high seed (low number) but bad efficiency
fools_gold = eff_seeded[(eff_seeded.SeedNum <= 4) & (eff_seeded.NetEffRank > 30)]
fools_gold = fools_gold.sort_values('NetEffRank', ascending=False)
print(f"\nFOOL'S GOLD: Top-4 seeds with efficiency ranked outside top 30:")
for _, r in fools_gold.head(10).iterrows():
    name = team_names.get(r.TeamID, '???')
    print(f"  {int(r.Season)} {name} (#{int(r.SeedNum)} seed, eff rank #{int(r.NetEffRank)}, "
          f"NetEff={r.NetEff:.1f}) -> {int(r.TourneyWins)} tourney wins")

# Hidden gems: low seed (high number) but great efficiency
hidden_gems = eff_seeded[(eff_seeded.SeedNum >= 10) & (eff_seeded.NetEffRank <= 30)]
hidden_gems = hidden_gems.sort_values('TourneyWins', ascending=False)
print(f"\nHIDDEN GEMS: 10+ seeds with efficiency in top 30:")
for _, r in hidden_gems.head(10).iterrows():
    name = team_names.get(r.TeamID, '???')
    print(f"  {int(r.Season)} {name} (#{int(r.SeedNum)} seed, eff rank #{int(r.NetEffRank)}, "
          f"NetEff={r.NetEff:.1f}) -> {int(r.TourneyWins)} tourney wins")

# --- FIGURE 3: Seed vs Efficiency Scatter ---
fig, ax = plt.subplots(figsize=(14, 9))
scatter = ax.scatter(eff_seeded['SeedNum'], eff_seeded['NetEff'],
                     c=eff_seeded['TourneyWins'], cmap='plasma',
                     alpha=0.5, s=30, edgecolors='none')
cbar = plt.colorbar(scatter, ax=ax, label='Tournament Wins', shrink=0.8)
cbar.ax.yaxis.label.set_color('#e0e0e0')
cbar.ax.tick_params(colors='#aaaaaa')

# Highlight fool's gold and hidden gems
fg = fools_gold.head(5)
hg = hidden_gems.head(5)
ax.scatter(fg.SeedNum, fg.NetEff, s=120, facecolors='none', edgecolors=ACCENT4, linewidths=2, label="Fool's Gold")
ax.scatter(hg.SeedNum, hg.NetEff, s=120, facecolors='none', edgecolors=ACCENT2, linewidths=2, label="Hidden Gems")

for _, r in fg.iterrows():
    name = team_names.get(r.TeamID, '???')
    ax.annotate(f"{name} '{int(r.Season) % 100:02d}", (r.SeedNum, r.NetEff),
                xytext=(10, 5), textcoords='offset points', fontsize=7, color=ACCENT4)
for _, r in hg.iterrows():
    name = team_names.get(r.TeamID, '???')
    ax.annotate(f"{name} '{int(r.Season) % 100:02d}", (r.SeedNum, r.NetEff),
                xytext=(10, -10), textcoords='offset points', fontsize=7, color=ACCENT2)

ax.set_xlabel('Tournament Seed', fontsize=12)
ax.set_ylabel('Net Efficiency (Off - Def per 100 poss)', fontsize=12)
ax.set_title("Fool's Gold & Hidden Gems: When Seeds Lie About Team Quality", fontsize=15, pad=15)
ax.legend(framealpha=0.3, facecolor='#1a1a2e', loc='lower left')
ax.invert_xaxis()
ax.grid(alpha=0.2)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.tight_layout()
plt.savefig(FIG / '03_seed_vs_efficiency.png', dpi=200, bbox_inches='tight')
plt.close()
print("\nSaved: 03_seed_vs_efficiency.png")


# ============================================================================
# 3. THREE-POINT DEEP DIVE
# ============================================================================
print("\n" + "=" * 80)
print("3. THREE-POINT DEEP DIVE")
print("=" * 80)

# Season-level 3-point trends
season_3pt = eff.groupby('Season').agg(
    FGA3=('FGA3', 'sum'), FGM3=('FGM3', 'sum'),
    FGA=('FGA', 'sum'), FGM=('FGM', 'sum'),
    teams=('TeamID', 'nunique'),
).reset_index()
season_3pt['FG3Rate'] = season_3pt['FGA3'] / season_3pt['FGA']
season_3pt['FG3Pct'] = season_3pt['FGM3'] / season_3pt['FGA3']
season_3pt['FGA3_per_team'] = season_3pt['FGA3'] / season_3pt['teams']

print("THREE-POINT EVOLUTION:")
for _, r in season_3pt.iterrows():
    print(f"  {int(r.Season)}: {r.FG3Rate:.1%} of shots from 3 | {r.FG3Pct:.1%} accuracy | "
          f"{r.FGA3_per_team:.0f} 3PA/team")

# 3-point DEFENSE vs OFFENSE as tournament predictor
# For seeded teams, correlate 3-point offense vs defense with tourney wins
# Need opponent 3-point stats
det_w = reg_det.groupby(['Season', 'WTeamID']).agg(
    opp_FGM3=('LFGM3', 'sum'), opp_FGA3=('LFGA3', 'sum')
).reset_index().rename(columns={'WTeamID': 'TeamID'})

det_l = reg_det.groupby(['Season', 'LTeamID']).agg(
    opp_FGM3=('WFGM3', 'sum'), opp_FGA3=('WFGA3', 'sum')
).reset_index().rename(columns={'LTeamID': 'TeamID'})

opp3 = pd.concat([det_w, det_l]).groupby(['Season', 'TeamID']).sum().reset_index()
opp3['OppFG3Pct'] = opp3['opp_FGM3'] / opp3['opp_FGA3']

eff_seeded2 = eff_seeded.merge(opp3[['Season', 'TeamID', 'OppFG3Pct']], on=['Season', 'TeamID'], how='left')

corr_off = eff_seeded2[['FG3Pct', 'TourneyWins']].corr().iloc[0, 1]
corr_def = eff_seeded2[['OppFG3Pct', 'TourneyWins']].corr().iloc[0, 1]
corr_rate = eff_seeded2[['FG3Rate', 'TourneyWins']].corr().iloc[0, 1]
print(f"\n3-POINT CORRELATIONS WITH TOURNEY WINS:")
print(f"  3PT Offense (own FG3%):     r = {corr_off:+.4f}")
print(f"  3PT Defense (opp FG3%):     r = {corr_def:+.4f}")
print(f"  3PT Volume (FG3 rate):      r = {corr_rate:+.4f}")
if abs(corr_def) > abs(corr_off):
    print("  -> 3-POINT DEFENSE IS A STRONGER PREDICTOR THAN 3-POINT OFFENSE")

# 3-point variance analysis
# Do high-volume 3-point teams have more variable tournament outcomes?
eff_seeded2['FG3_Quartile'] = pd.qcut(eff_seeded2['FG3Rate'], 4, labels=['Q1 (low)', 'Q2', 'Q3', 'Q4 (high)'])
variance_by_q = eff_seeded2.groupby('FG3_Quartile')['WinsOverExpected'].agg(['mean', 'std', 'count'])
print(f"\n3-POINT VOLUME vs TOURNAMENT VARIANCE:")
print(f"  {'Quartile':<15} {'Avg WoE':>10} {'Std Dev':>10} {'N':>6}")
for q, r in variance_by_q.iterrows():
    print(f"  {q:<15} {r['mean']:>+10.3f} {r['std']:>10.3f} {int(r['count']):>6}")

# Champions' 3-point profile
champs = tourney.groupby('Season').apply(
    lambda x: x.loc[x.DayNum.idxmax(), 'WTeamID']
).reset_index(name='TeamID')
champ_eff = champs.merge(eff, on=['Season', 'TeamID'])

# Compare to field
field_avg = eff_seeded.groupby('Season')[['FG3Rate', 'FG3Pct']].mean()
champ_3pt = champ_eff[['Season', 'FG3Rate', 'FG3Pct']].set_index('Season')
comparison = champ_3pt.join(field_avg, rsuffix='_field')

print(f"\nCHAMPIONS vs FIELD (3-point profile):")
print(f"  Champions avg 3PT rate: {champ_3pt.FG3Rate.mean():.1%} vs Field: {field_avg.FG3Rate.mean():.1%}")
print(f"  Champions avg 3PT pct:  {champ_3pt.FG3Pct.mean():.1%} vs Field: {field_avg.FG3Pct.mean():.1%}")

# --- FIGURE 4: 3-Point Evolution (dual axis) ---
fig, ax1 = plt.subplots(figsize=(14, 7))
ax2 = ax1.twinx()

ax1.fill_between(season_3pt.Season, season_3pt.FG3Rate * 100, alpha=0.3, color=ACCENT)
ax1.plot(season_3pt.Season, season_3pt.FG3Rate * 100, color=ACCENT, linewidth=2.5,
         label='3PT share of all shots (%)', marker='o', markersize=4)

ax2.plot(season_3pt.Season, season_3pt.FG3Pct * 100, color=ACCENT2, linewidth=2.5,
         label='3PT accuracy (%)', marker='s', markersize=4)

# Mark the line move
ax1.axvline(x=2020, color=ACCENT4, linestyle='--', alpha=0.7, linewidth=1.5)
ax1.annotate('3PT line\nmoved back', (2020, season_3pt.FG3Rate.max() * 100),
             xytext=(-60, 10), textcoords='offset points', fontsize=9, color=ACCENT4,
             arrowprops=dict(arrowstyle='->', color=ACCENT4))

ax1.set_xlabel('Season', fontsize=12)
ax1.set_ylabel('3PT Share of All Shots (%)', fontsize=12, color=ACCENT)
ax2.set_ylabel('3PT Accuracy (%)', fontsize=12, color=ACCENT2)
ax1.set_title('The Three-Point Paradox: Volume Explodes, Accuracy Flatlines', fontsize=15, pad=15)

lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', framealpha=0.3, facecolor='#1a1a2e')

ax1.grid(axis='y', alpha=0.2)
ax1.spines['top'].set_visible(False)
ax2.spines['top'].set_visible(False)
ax1.tick_params(axis='y', labelcolor=ACCENT)
ax2.tick_params(axis='y', labelcolor=ACCENT2)
plt.tight_layout()
plt.savefig(FIG / '04_three_point_paradox.png', dpi=200, bbox_inches='tight')
plt.close()
print("\nSaved: 04_three_point_paradox.png")


# ============================================================================
# 4. MOMENTUM / "PEAKING AT THE RIGHT TIME"
# ============================================================================
print("\n" + "=" * 80)
print("4. MOMENTUM ANALYSIS")
print("=" * 80)

# Last 10 games of regular season - does finishing strong predict tourney success?
reg_all = reg_compact.copy()
reg_all['GameNum'] = reg_all.groupby(['Season', 'WTeamID']).cumcount()

# Build per-game records
games = []
for _, row in reg_compact.iterrows():
    games.append({'Season': row.Season, 'TeamID': row.WTeamID, 'DayNum': row.DayNum,
                  'Win': 1, 'Score': row.WScore, 'OppScore': row.LScore})
    games.append({'Season': row.Season, 'TeamID': row.LTeamID, 'DayNum': row.DayNum,
                  'Win': 0, 'Score': row.LScore, 'OppScore': row.WScore})
games_df = pd.DataFrame(games)
games_df = games_df.sort_values(['Season', 'TeamID', 'DayNum'])

# Last 10 games
games_df['GameRank'] = games_df.groupby(['Season', 'TeamID']).cumcount(ascending=False)
last10 = games_df[games_df.GameRank < 10]
momentum = last10.groupby(['Season', 'TeamID']).agg(
    Last10_WinPct=('Win', 'mean'),
    Last10_Margin=('Score', lambda x: (x - last10.loc[x.index, 'OppScore']).mean()),
).reset_index()

# Overall win pct
overall = games_df.groupby(['Season', 'TeamID']).agg(
    Overall_WinPct=('Win', 'mean'),
).reset_index()

momentum = momentum.merge(overall, on=['Season', 'TeamID'])
momentum['Momentum'] = momentum['Last10_WinPct'] - momentum['Overall_WinPct']

# Merge with tourney performance
momentum_seeded = momentum.merge(
    eff_seeded[['Season', 'TeamID', 'SeedNum', 'TourneyWins', 'ExpectedWins', 'WinsOverExpected']],
    on=['Season', 'TeamID'], how='inner'
)

# Correlation
corr_momentum = momentum_seeded[['Momentum', 'WinsOverExpected']].corr().iloc[0, 1]
corr_last10 = momentum_seeded[['Last10_WinPct', 'WinsOverExpected']].corr().iloc[0, 1]
print(f"MOMENTUM CORRELATIONS:")
print(f"  Late-season momentum (last10 wp - overall wp) vs WinsOverExpected: r = {corr_momentum:+.4f}")
print(f"  Last 10 win% vs WinsOverExpected: r = {corr_last10:+.4f}")

# Split into hot/cold teams
momentum_seeded['MomentumQ'] = pd.qcut(momentum_seeded['Momentum'], 4,
                                         labels=['Cold', 'Cooling', 'Warming', 'Hot'])
momentum_result = momentum_seeded.groupby('MomentumQ')['WinsOverExpected'].agg(['mean', 'std', 'count'])
print(f"\nMOMENTUM QUARTILES vs TOURNAMENT PERFORMANCE:")
for q, r in momentum_result.iterrows():
    print(f"  {q:<10}: Avg WoE = {r['mean']:+.3f}, Std = {r['std']:.3f}, N = {int(r['count'])}")

# Teams that went cold but were high seeds
cold_high_seeds = momentum_seeded[(momentum_seeded.Momentum < -0.15) & (momentum_seeded.SeedNum <= 4)]
cold_high_seeds = cold_high_seeds.sort_values('Momentum')
print(f"\nHIGH SEEDS THAT WENT COLD (>15% win rate drop in last 10):")
for _, r in cold_high_seeds.head(8).iterrows():
    name = team_names.get(r.TeamID, '???')
    print(f"  {int(r.Season)} {name} (#{int(r.SeedNum)} seed, overall {r.Overall_WinPct:.0%} -> "
          f"last 10: {r.Last10_WinPct:.0%}, momentum={r.Momentum:+.2f}) -> {int(r.TourneyWins)} tourney wins")

# Teams that surged
hot_low_seeds = momentum_seeded[(momentum_seeded.Momentum > 0.15) & (momentum_seeded.SeedNum >= 8)]
hot_low_seeds = hot_low_seeds.sort_values('TourneyWins', ascending=False)
print(f"\nLOW SEEDS THAT SURGED (>15% win rate gain in last 10):")
for _, r in hot_low_seeds.head(8).iterrows():
    name = team_names.get(r.TeamID, '???')
    print(f"  {int(r.Season)} {name} (#{int(r.SeedNum)} seed, overall {r.Overall_WinPct:.0%} -> "
          f"last 10: {r.Last10_WinPct:.0%}, momentum={r.Momentum:+.2f}) -> {int(r.TourneyWins)} tourney wins")

# --- FIGURE 5: Momentum vs Tournament Over/Under Performance ---
fig, ax = plt.subplots(figsize=(12, 8))
colors_by_seed = np.where(momentum_seeded.SeedNum <= 4, ACCENT,
                   np.where(momentum_seeded.SeedNum <= 8, ACCENT3,
                   np.where(momentum_seeded.SeedNum <= 12, ACCENT2, ACCENT5)))
ax.scatter(momentum_seeded.Momentum * 100, momentum_seeded.WinsOverExpected,
           c=colors_by_seed, alpha=0.35, s=25, edgecolors='none')

# Trend line
z = np.polyfit(momentum_seeded.Momentum, momentum_seeded.WinsOverExpected, 1)
p = np.poly1d(z)
x_line = np.linspace(momentum_seeded.Momentum.min(), momentum_seeded.Momentum.max(), 100)
ax.plot(x_line * 100, p(x_line), color=ACCENT4, linewidth=2, linestyle='--',
        label=f'Trend (r={corr_momentum:+.3f})')

ax.axhline(y=0, color='white', alpha=0.3, linewidth=0.5)
ax.axvline(x=0, color='white', alpha=0.3, linewidth=0.5)

# Legend for seed groups
from matplotlib.lines import Line2D
legend_elements = [
    Line2D([0], [0], marker='o', color='w', markerfacecolor=ACCENT, markersize=8, label='1-4 seeds'),
    Line2D([0], [0], marker='o', color='w', markerfacecolor=ACCENT3, markersize=8, label='5-8 seeds'),
    Line2D([0], [0], marker='o', color='w', markerfacecolor=ACCENT2, markersize=8, label='9-12 seeds'),
    Line2D([0], [0], marker='o', color='w', markerfacecolor=ACCENT5, markersize=8, label='13+ seeds'),
    Line2D([0], [0], color=ACCENT4, linewidth=2, linestyle='--', label=f'Trend (r={corr_momentum:+.3f})'),
]
ax.legend(handles=legend_elements, framealpha=0.3, facecolor='#1a1a2e')

ax.set_xlabel('Late-Season Momentum (Last 10 Win% - Season Win%)', fontsize=12)
ax.set_ylabel('Tournament Wins Over Expected', fontsize=12)
ax.set_title('Does "Peaking at the Right Time" Actually Work?', fontsize=15, pad=15)
ax.xaxis.set_major_formatter(mticker.PercentFormatter())
ax.grid(alpha=0.2)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.tight_layout()
plt.savefig(FIG / '05_momentum_vs_tourney.png', dpi=200, bbox_inches='tight')
plt.close()
print("\nSaved: 05_momentum_vs_tourney.png")


# ============================================================================
# 5. MOST SHOCKING RESULTS (by model predictions)
# ============================================================================
print("\n" + "=" * 80)
print("5. MOST SHOCKING TOURNAMENT RESULTS")
print("=" * 80)

# Use training matchups which have model features and actual results
tr = training.copy()
# Columns are TeamLow, TeamHigh, Target (1 = TeamLow wins)
# Use Elo_diff as proxy for expected outcome
# Games where the Elo favorite lost
# Surprise: when Target=1 (TeamLow won) but Elo_diff was very negative (TeamLow much worse by Elo)
# or when Target=0 (TeamHigh won) but Elo_diff was very positive (TeamLow much better by Elo)
tr['Surprise'] = np.where(tr.Target == 1, -tr.Elo_diff, tr.Elo_diff)
# Higher surprise = more unexpected

shockers = tr.nlargest(15, 'Surprise')
print("MOST SHOCKING RESULTS (by Elo):")
for _, r in shockers.iterrows():
    season = int(r.Season)
    low_id = int(r.TeamLow)
    high_id = int(r.TeamHigh)
    low_name = team_names.get(low_id, str(low_id))
    high_name = team_names.get(high_id, str(high_id))
    winner = low_name if r.Target == 1 else high_name
    loser = high_name if r.Target == 1 else low_name

    # Get seeds
    low_seed = seeds[(seeds.Season == season) & (seeds.TeamID == low_id)]
    high_seed = seeds[(seeds.Season == season) & (seeds.TeamID == high_id)]
    ls = int(low_seed.SeedNum.values[0]) if len(low_seed) > 0 else '?'
    hs = int(high_seed.SeedNum.values[0]) if len(high_seed) > 0 else '?'

    winner_seed = ls if r.Target == 1 else hs
    loser_seed = hs if r.Target == 1 else ls

    print(f"  {season}: ({winner_seed}) {winner} over ({loser_seed}) {loser} "
          f"[Elo diff: {r.Elo_diff:+.0f}, Surprise: {r.Surprise:.0f}]")

# --- FIGURE 6: Distribution of Elo surprises ---
fig, ax = plt.subplots(figsize=(14, 6))
ax.hist(tr.Surprise, bins=60, color=ACCENT, alpha=0.7, edgecolor='#0e1117', linewidth=0.5)

# Mark the extremes
p95 = tr.Surprise.quantile(0.95)
ax.axvline(x=p95, color=ACCENT4, linestyle='--', linewidth=1.5, label=f'95th percentile ({p95:.0f})')
ax.fill_betweenx([0, 50], p95, tr.Surprise.max(), alpha=0.15, color=ACCENT4)

# Annotate top shockers with staggered heights to avoid overlap
y_offsets = [45, 65, 35]
for i, (_, r) in enumerate(shockers.head(3).iterrows()):
    season = int(r.Season)
    low_id = int(r.TeamLow)
    high_id = int(r.TeamHigh)
    winner = team_names.get(low_id if r.Target == 1 else high_id, '???')
    ax.annotate(f"{winner} '{season % 100:02d}", (r.Surprise, 0),
                xytext=(0, y_offsets[i]), textcoords='offset points', fontsize=9,
                color='#ffffff', ha='center', fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='#0e1117',
                          edgecolor=ACCENT4, alpha=0.9),
                arrowprops=dict(arrowstyle='->', color=ACCENT4, lw=1.0),
                zorder=10)

ax.set_xlabel('Surprise Score (higher = more unexpected)', fontsize=12)
ax.set_ylabel('Count', fontsize=12)
ax.set_title('Distribution of Upsets by Shock Value', fontsize=15, pad=15)
ax.legend(framealpha=0.3, facecolor='#1a1a2e')
ax.grid(axis='y', alpha=0.2)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.tight_layout()
plt.savefig(FIG / '06_surprise_distribution.png', dpi=200, bbox_inches='tight')
plt.close()
print("\nSaved: 06_surprise_distribution.png")


# ============================================================================
# 6. SCORING DISTRIBUTION ANALYSIS
# ============================================================================
print("\n" + "=" * 80)
print("6. SCORING & MARGIN ANALYSIS")
print("=" * 80)

# Total scoring per game over time
t_det = tourney_det.copy()
t_det['TotalScore'] = t_det['WScore'] + t_det['LScore']
t_det['Margin'] = t_det['WScore'] - t_det['LScore']

# Merge with seeds
t_det = t_det.merge(seeds[['Season', 'TeamID', 'SeedNum']].rename(
    columns={'TeamID': 'WTeamID', 'SeedNum': 'WSeed'}), on=['Season', 'WTeamID'], how='left')
t_det = t_det.merge(seeds[['Season', 'TeamID', 'SeedNum']].rename(
    columns={'TeamID': 'LTeamID', 'SeedNum': 'LSeed'}), on=['Season', 'LTeamID'], how='left')

# Blowouts over time
t_det['Blowout'] = t_det.Margin >= 15

yearly_margins = t_det.groupby('Season').agg(
    avg_margin=('Margin', 'mean'),
    avg_total=('TotalScore', 'mean'),
    blowout_rate=('Blowout', 'mean'),
    games=('Margin', 'count'),
).reset_index()

print("TOURNAMENT SCORING TRENDS:")
for _, r in yearly_margins.tail(10).iterrows():
    print(f"  {int(r.Season)}: Avg total={r.avg_total:.1f}, Avg margin={r.avg_margin:.1f}, "
          f"Blowout rate={r.blowout_rate:.0%} ({int(r.games)} games)")

# Margin by round (approximated by DayNum)
round_labels = {134: 'R64', 135: 'R64', 136: 'R64', 137: 'R64',
                138: 'R32', 139: 'R32', 143: 'S16', 144: 'S16',
                145: 'E8', 146: 'E8', 152: 'F4', 153: 'F4', 154: 'NCG'}

# Use ranges instead
def get_round(day):
    if day <= 137: return 'R64'
    elif day <= 139: return 'R32'
    elif day <= 144: return 'S16'
    elif day <= 146: return 'E8'
    elif day <= 153: return 'F4'
    else: return 'NCG'

t_det['Round'] = t_det.DayNum.apply(get_round)
round_order = ['R64', 'R32', 'S16', 'E8', 'F4', 'NCG']

margin_by_round = t_det.groupby('Round')['Margin'].agg(['mean', 'median', 'std']).reindex(round_order)
print(f"\nMARGIN OF VICTORY BY ROUND:")
for rnd, r in margin_by_round.iterrows():
    print(f"  {rnd}: mean={r['mean']:.1f}, median={r['median']:.1f}, std={r['std']:.1f}")

# Spread of scoring - are teams more similar now?
scoring_spread = eff.groupby('Season')['PPG'].agg(['std', 'mean']).reset_index()
scoring_spread['cv'] = scoring_spread['std'] / scoring_spread['mean']
print(f"\nSCORING HOMOGENEITY (coefficient of variation in PPG):")
print(f"  2003: CV = {scoring_spread[scoring_spread.Season == 2003]['cv'].values[0]:.4f}")
print(f"  2026: CV = {scoring_spread[scoring_spread.Season == 2026]['cv'].values[0]:.4f}")
trend = "MORE homogeneous" if scoring_spread.iloc[-1]['cv'] < scoring_spread.iloc[0]['cv'] else "LESS homogeneous"
print(f"  Trend: Teams are becoming {trend} in scoring")

# --- FIGURE 7: Margin by round violin/box plot ---
fig, ax = plt.subplots(figsize=(12, 7))
round_data = [t_det[t_det.Round == r]['Margin'].values for r in round_order]
bp = ax.boxplot(round_data, labels=round_order, patch_artist=True, widths=0.6,
                medianprops=dict(color='white', linewidth=2),
                whiskerprops=dict(color='#555555'),
                capprops=dict(color='#555555'),
                flierprops=dict(marker='o', markerfacecolor=ACCENT4, markersize=3, alpha=0.5))
for patch, color in zip(bp['boxes'], [ACCENT, ACCENT2, ACCENT3, ACCENT4, ACCENT5, '#4ecdc4']):
    patch.set_facecolor(color)
    patch.set_alpha(0.7)

ax.set_xlabel('Tournament Round', fontsize=12)
ax.set_ylabel('Margin of Victory', fontsize=12)
ax.set_title('Games Get Tighter as the Tournament Goes On', fontsize=15, pad=15)
ax.grid(axis='y', alpha=0.2)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.tight_layout()
plt.savefig(FIG / '07_margin_by_round.png', dpi=200, bbox_inches='tight')
plt.close()
print("\nSaved: 07_margin_by_round.png")


# ============================================================================
# 7. TURNOVER RATE - THE CINDERELLA SIGNAL
# ============================================================================
print("\n" + "=" * 80)
print("7. TURNOVER RATE ANALYSIS")
print("=" * 80)

# Cinderellas = seeds 10+ that won 2+ tourney games
cinderellas = eff_seeded[(eff_seeded.SeedNum >= 10) & (eff_seeded.TourneyWins >= 2)]
non_cinderellas = eff_seeded[(eff_seeded.SeedNum >= 10) & (eff_seeded.TourneyWins < 2)]

print(f"Cinderellas (10+ seed, 2+ tourney wins): {len(cinderellas)}")
print(f"Non-Cinderellas (10+ seed, 0-1 wins): {len(non_cinderellas)}")
print(f"\n  Cinderella avg TO rate:     {cinderellas.TORate.mean():.4f}")
print(f"  Non-Cinderella avg TO rate: {non_cinderellas.TORate.mean():.4f}")
print(f"  All teams avg TO rate:      {eff_seeded.TORate.mean():.4f}")

# T-test
from scipy import stats
tstat, pval = stats.ttest_ind(cinderellas.TORate, non_cinderellas.TORate)
print(f"  T-test: t={tstat:.3f}, p={pval:.4f} {'***' if pval < 0.01 else '**' if pval < 0.05 else 'ns'}")

# Efficiency comparison
print(f"\n  Cinderella avg eFG%:        {cinderellas.eFGPct.mean():.4f}")
print(f"  Non-Cinderella avg eFG%:    {non_cinderellas.eFGPct.mean():.4f}")
print(f"  Cinderella avg DefEff:      {cinderellas.DefEff.mean():.1f}")
print(f"  Non-Cinderella avg DefEff:  {non_cinderellas.DefEff.mean():.1f}")

# Notable cinderellas
print(f"\nNOTABLE CINDERELLAS:")
for _, r in cinderellas.nlargest(10, 'TourneyWins').iterrows():
    name = team_names.get(r.TeamID, '???')
    to_rank = eff[eff.Season == r.Season]['TORate'].rank().loc[
        eff[(eff.Season == r.Season) & (eff.TeamID == r.TeamID)].index]
    print(f"  {int(r.Season)} {name} (#{int(r.SeedNum)} seed, {int(r.TourneyWins)} wins, "
          f"TORate={r.TORate:.4f}, eFG={r.eFGPct:.3f})")

# --- FIGURE 8: Cinderella DNA - TO rate comparison ---
fig, axes = plt.subplots(1, 2, figsize=(16, 7))

# Left: TO rate distribution
ax = axes[0]
ax.hist(non_cinderellas.TORate, bins=25, alpha=0.6, color=ACCENT, label='Early exits (0-1 wins)', density=True)
ax.hist(cinderellas.TORate, bins=15, alpha=0.7, color=ACCENT2, label='Cinderellas (2+ wins)', density=True)
ax.axvline(cinderellas.TORate.mean(), color=ACCENT2, linestyle='--', linewidth=2)
ax.axvline(non_cinderellas.TORate.mean(), color=ACCENT, linestyle='--', linewidth=2)
ax.set_xlabel('Turnover Rate', fontsize=12)
ax.set_ylabel('Density', fontsize=12)
ax.set_title('Cinderella DNA: Take Care of the Ball', fontsize=14, pad=10)
ax.legend(framealpha=0.3, facecolor='#1a1a2e')
ax.grid(alpha=0.2)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Right: eFG% vs TO rate scatter for 10+ seeds
ax = axes[1]
ax.scatter(non_cinderellas.TORate, non_cinderellas.eFGPct * 100,
           c=ACCENT, alpha=0.3, s=20, label='Early exits')
ax.scatter(cinderellas.TORate, cinderellas.eFGPct * 100,
           c=ACCENT2, alpha=0.8, s=50, edgecolors='white', linewidths=0.5, label='Cinderellas')

# Label notable cinderellas
for _, r in cinderellas.nlargest(5, 'TourneyWins').iterrows():
    name = team_names.get(r.TeamID, '???')
    ax.annotate(f"{name} '{int(r.Season) % 100:02d}", (r.TORate, r.eFGPct * 100),
                xytext=(5, 5), textcoords='offset points', fontsize=7, color=ACCENT2)

ax.set_xlabel('Turnover Rate (lower = better)', fontsize=12)
ax.set_ylabel('Effective FG% (%)', fontsize=12)
ax.set_title('The Cinderella Sweet Spot', fontsize=14, pad=10)
ax.legend(framealpha=0.3, facecolor='#1a1a2e')
ax.grid(alpha=0.2)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.tight_layout()
plt.savefig(FIG / '08_cinderella_dna.png', dpi=200, bbox_inches='tight')
plt.close()
print("\nSaved: 08_cinderella_dna.png")


# ============================================================================
# 8. CONFERENCE POWER SHIFTS
# ============================================================================
print("\n" + "=" * 80)
print("8. CONFERENCE POWER ANALYSIS")
print("=" * 80)

# Merge conference info
conf_data = conferences.merge(conf_names, on='ConfAbbrev', how='left')

# Tournament teams by conference over time
tourney_teams = seeds[['Season', 'TeamID', 'SeedNum']].merge(
    conf_data[['Season', 'TeamID', 'ConfAbbrev', 'Description']],
    on=['Season', 'TeamID'], how='left'
)

# Conference bids over time
major_confs = ['big_ten', 'sec', 'big_twelve', 'acc', 'big_east', 'pac_twelve', 'aac']
conf_bids = tourney_teams.groupby(['Season', 'ConfAbbrev']).size().reset_index(name='Bids')

print("CONFERENCE TOURNAMENT BIDS (recent 5 years):")
for conf in major_confs:
    recent = conf_bids[(conf_bids.ConfAbbrev == conf) & (conf_bids.Season >= 2021)]
    if len(recent) > 0:
        bids_str = ', '.join([f"{int(r.Season)}:{int(r.Bids)}" for _, r in recent.iterrows()])
        print(f"  {conf}: {bids_str}")

# Conference tourney win rate (how do conf teams perform?)
tourney_with_conf = t.merge(
    conf_data[['Season', 'TeamID', 'ConfAbbrev']].rename(columns={'TeamID': 'WTeamID', 'ConfAbbrev': 'WConf'}),
    on=['Season', 'WTeamID'], how='left')
tourney_with_conf = tourney_with_conf.merge(
    conf_data[['Season', 'TeamID', 'ConfAbbrev']].rename(columns={'TeamID': 'LTeamID', 'ConfAbbrev': 'LConf'}),
    on=['Season', 'LTeamID'], how='left')

# Win rate by conference (recent)
recent_years = tourney_with_conf[tourney_with_conf.Season >= 2015]
conf_wins = recent_years.groupby('WConf').size().reset_index(name='Wins')
conf_losses = recent_years.groupby('LConf').size().reset_index(name='Losses')
conf_perf = conf_wins.merge(conf_losses, left_on='WConf', right_on='LConf', how='outer').fillna(0)
conf_perf['WinRate'] = conf_perf['Wins'] / (conf_perf['Wins'] + conf_perf['Losses'])
conf_perf['TotalGames'] = conf_perf['Wins'] + conf_perf['Losses']
conf_perf = conf_perf[conf_perf.TotalGames >= 20].sort_values('WinRate', ascending=False)

print(f"\nCONFERENCE TOURNAMENT WIN RATE (2015-2025, min 20 games):")
for _, r in conf_perf.head(10).iterrows():
    conf = r.WConf if pd.notna(r.WConf) else r.LConf
    print(f"  {conf}: {r.WinRate:.1%} ({int(r.Wins)}W-{int(r.Losses)}L)")


# ============================================================================
# 9. THE COACHING EFFECT
# ============================================================================
print("\n" + "=" * 80)
print("9. COACHING ANALYSIS")
print("=" * 80)

# Coach tenure and tournament success
coach_seasons = coaches.copy()
coach_seasons['CoachName'] = coach_seasons['CoachName'].str.strip()

# Count consecutive seasons at same school
coach_tenure = coach_seasons.sort_values(['TeamID', 'Season'])
coach_tenure['NewStint'] = (
    (coach_tenure.TeamID != coach_tenure.TeamID.shift()) |
    (coach_tenure.CoachName != coach_tenure.CoachName.shift()) |
    (coach_tenure.Season != coach_tenure.Season.shift() + 1)
).cumsum()
coach_tenure['Tenure'] = coach_tenure.groupby('NewStint').cumcount() + 1

# Merge with tourney performance
coach_tourney = coach_tenure.merge(
    eff_seeded[['Season', 'TeamID', 'SeedNum', 'TourneyWins', 'WinsOverExpected']],
    on=['Season', 'TeamID'], how='inner'
)

tenure_bins = [0, 1, 3, 6, 10, 50]
tenure_labels = ['Year 1', 'Years 2-3', 'Years 4-6', 'Years 7-10', 'Years 11+']
coach_tourney['TenureBin'] = pd.cut(coach_tourney.Tenure, bins=tenure_bins, labels=tenure_labels)

tenure_performance = coach_tourney.groupby('TenureBin')['WinsOverExpected'].agg(['mean', 'std', 'count'])
print("COACH TENURE vs TOURNAMENT PERFORMANCE (Wins Over Expected):")
for tb, r in tenure_performance.iterrows():
    print(f"  {tb}: Avg WoE = {r['mean']:+.3f}, Std = {r['std']:.3f}, N = {int(r['count'])}")

# First-year coaches
first_year = coach_tourney[coach_tourney.Tenure == 1]
experienced = coach_tourney[coach_tourney.Tenure >= 5]
print(f"\nFIRST-YEAR COACHES IN TOURNEY:")
print(f"  Count: {len(first_year)}")
print(f"  Avg tourney wins: {first_year.TourneyWins.mean():.2f} vs experienced: {experienced.TourneyWins.mean():.2f}")
print(f"  Avg WoE: {first_year.WinsOverExpected.mean():+.3f} vs experienced: {experienced.WinsOverExpected.mean():+.3f}")


# ============================================================================
# 10. THE 2026 FIELD ANALYSIS
# ============================================================================
print("\n" + "=" * 80)
print("10. 2026 FIELD ANALYSIS")
print("=" * 80)

# 2026 seeds - merge with computed efficiency (avoid team_features overlap)
eff_2026 = eff[eff.Season == 2026][['Season', 'TeamID', 'OffEff', 'DefEff', 'NetEff',
                                      'eFGPct', 'TORate', 'FG3Rate', 'FG3Pct', 'WinPct']].copy()
seeds_2026 = seeds[seeds.Season == 2026][['Season', 'TeamID', 'SeedNum']].merge(
    eff_2026, on=['Season', 'TeamID'], how='left'
)

# Momentum for 2026
momentum_2026 = momentum[momentum.Season == 2026]
seeds_2026 = seeds_2026.merge(
    momentum_2026[['Season', 'TeamID', 'Momentum', 'Last10_WinPct']],
    on=['Season', 'TeamID'], how='left'
)

if len(seeds_2026) > 0:
    print(f"2026 Tournament field: {len(seeds_2026)} teams")

    # Best efficiency
    print(f"\nTOP 5 BY NET EFFICIENCY:")
    for _, r in seeds_2026.nlargest(5, 'NetEff').iterrows():
        name = team_names.get(r.TeamID, '???')
        print(f"  ({int(r.SeedNum)}) {name}: NetEff={r.NetEff:.1f}, OffEff={r.OffEff:.1f}, DefEff={r.DefEff:.1f}")

    # Biggest overseeds (seed better than efficiency suggests)
    seeds_2026['EffRank'] = seeds_2026['NetEff'].rank(ascending=False)
    seeds_2026['SeedRank'] = seeds_2026['SeedNum'].rank()
    seeds_2026['OverSeed'] = seeds_2026['EffRank'] - seeds_2026['SeedRank']

    print(f"\nMOST OVERSEEDED (seed better than efficiency):")
    for _, r in seeds_2026.nlargest(5, 'OverSeed').iterrows():
        name = team_names.get(r.TeamID, '???')
        print(f"  ({int(r.SeedNum)}) {name}: Eff rank #{int(r.EffRank)} (overseeded by {r.OverSeed:.0f} spots)")

    print(f"\nMOST UNDERSEEDED (efficiency better than seed):")
    for _, r in seeds_2026.nsmallest(5, 'OverSeed').iterrows():
        name = team_names.get(r.TeamID, '???')
        print(f"  ({int(r.SeedNum)}) {name}: Eff rank #{int(r.EffRank)} (underseeded by {-r.OverSeed:.0f} spots)")

    # Hottest and coldest teams
    if 'Momentum' in seeds_2026.columns:
        print(f"\nHOTTEST TEAMS ENTERING TOURNAMENT:")
        for _, r in seeds_2026.nlargest(5, 'Momentum').iterrows():
            name = team_names.get(r.TeamID, '???')
            if pd.notna(r.Momentum):
                print(f"  ({int(r.SeedNum)}) {name}: Last 10 WP={r.Last10_WinPct:.0%}, "
                      f"Momentum={r.Momentum:+.2f}")

        print(f"\nCOLDEST TEAMS ENTERING TOURNAMENT:")
        for _, r in seeds_2026.nsmallest(5, 'Momentum').iterrows():
            name = team_names.get(r.TeamID, '???')
            if pd.notna(r.Momentum):
                print(f"  ({int(r.SeedNum)}) {name}: Last 10 WP={r.Last10_WinPct:.0%}, "
                      f"Momentum={r.Momentum:+.2f}")

    # --- FIGURE 9: 2026 Field - Seed vs Efficiency with momentum ---
    fig, ax = plt.subplots(figsize=(14, 9))

    has_momentum = seeds_2026.dropna(subset=['Momentum', 'NetEff'])
    scatter = ax.scatter(has_momentum.SeedNum, has_momentum.NetEff,
                         c=has_momentum.Momentum, cmap='RdYlGn',
                         s=100, edgecolors='white', linewidths=0.5, vmin=-0.3, vmax=0.3)
    cbar = plt.colorbar(scatter, ax=ax, label='Late-Season Momentum', shrink=0.8)
    cbar.ax.yaxis.label.set_color('#e0e0e0')
    cbar.ax.tick_params(colors='#aaaaaa')

    # Label all teams
    for _, r in has_momentum.iterrows():
        name = team_names.get(r.TeamID, '???')
        # Shorten long names
        short = name[:12] if len(name) > 12 else name
        ax.annotate(short, (r.SeedNum, r.NetEff),
                    xytext=(5, 3), textcoords='offset points', fontsize=6.5, color='#cccccc')

    ax.set_xlabel('Tournament Seed', fontsize=12)
    ax.set_ylabel('Net Efficiency (per 100 poss)', fontsize=12)
    ax.set_title('2026 Tournament Field: Seed vs Reality vs Momentum', fontsize=15, pad=15)
    ax.invert_xaxis()
    ax.grid(alpha=0.2)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    plt.savefig(FIG / '09_2026_field_analysis.png', dpi=200, bbox_inches='tight')
    plt.close()
    print("\nSaved: 09_2026_field_analysis.png")

# --- FIGURE 10: Model performance comparison ---
fig, ax = plt.subplots(figsize=(10, 6))
models = ['Bradley-\nTerry', 'Logistic\nRegression', 'Neural\nNetwork', 'XGBoost', 'LightGBM']
brier_scores = [0.1996, 0.1171, 0.1152, 0.0536, 0.0503]
colors = [ACCENT, ACCENT, ACCENT, ACCENT2, ACCENT2]

bars = ax.barh(models, brier_scores, color=colors, alpha=0.85, height=0.5,
               edgecolor='white', linewidth=0.5)

# Add value labels
for bar, score in zip(bars, brier_scores):
    ax.text(bar.get_width() + 0.003, bar.get_y() + bar.get_height()/2,
            f'{score:.4f}', va='center', fontsize=11, color='#e0e0e0', fontweight='bold')

# Add "2.3x better" annotation
ax.annotate('', xy=(0.0503, 3.7), xytext=(0.1171, 3.7),
            arrowprops=dict(arrowstyle='<->', color=ACCENT5, lw=2))
ax.text(0.085, 3.85, '2.3x improvement', ha='center', fontsize=10, color=ACCENT5, fontweight='bold')

ax.set_xlabel('Brier Score (lower = better)', fontsize=12)
ax.set_title('The Model That Teaches Itself Wins', fontsize=15, pad=15)
ax.set_xlim(0, 0.25)
ax.grid(axis='x', alpha=0.2)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.tight_layout()
plt.savefig(FIG / '10_model_comparison.png', dpi=200, bbox_inches='tight')
plt.close()
print("\nSaved: 10_model_comparison.png")


print("\n" + "=" * 80)
print("ANALYSIS COMPLETE - 10 figures saved to results/figures/")
print("=" * 80)
