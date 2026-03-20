"""Finish the last 2 figures (9 and 10) that errored in deep_analysis.py"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

ROOT = Path("C:/dev/ssa-march-madness")
RAW = ROOT / "data" / "raw" / "kaggle"
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

# Load data
seeds = pd.read_csv(RAW / "MNCAATourneySeeds.csv")
seeds['SeedNum'] = seeds['Seed'].str.extract(r'(\d+)').astype(int)
reg_det = pd.read_csv(RAW / "MRegularSeasonDetailedResults.csv")
reg_compact = pd.read_csv(RAW / "MRegularSeasonCompactResults.csv")
teams = pd.read_csv(RAW / "MTeams.csv")
team_names = dict(zip(teams['TeamID'], teams['TeamName']))

# Compute efficiency (same as deep_analysis.py)
def compute_efficiency(df, season_min=2003):
    df = df[df.Season >= season_min].copy()
    w = df.groupby(['Season', 'WTeamID']).agg(
        W_FGA=('WFGA', 'sum'), W_FGM=('WFGM', 'sum'), W_FGM3=('WFGM3', 'sum'),
        W_FGA3=('WFGA3', 'sum'), W_FTA=('WFTA', 'sum'), W_OR=('WOR', 'sum'),
        W_TO=('WTO', 'sum'), W_Score=('WScore', 'sum'), W_Games=('WScore', 'count'),
        L_OR_opp=('LOR', 'sum'), L_FGA_opp=('LFGA', 'sum'), L_FTA_opp=('LFTA', 'sum'),
        L_TO_opp=('LTO', 'sum'), L_Score_opp=('LScore', 'sum'),
    ).reset_index().rename(columns={'WTeamID': 'TeamID'})
    l = df.groupby(['Season', 'LTeamID']).agg(
        L_FGA=('LFGA', 'sum'), L_FGM=('LFGM', 'sum'), L_FGM3=('LFGM3', 'sum'),
        L_FGA3=('LFGA3', 'sum'), L_FTA=('LFTA', 'sum'), L_OR=('LOR', 'sum'),
        L_TO=('LTO', 'sum'), L_Score=('LScore', 'sum'), L_Games=('LScore', 'count'),
        W_OR_opp=('WOR', 'sum'), W_FGA_opp=('WFGA', 'sum'), W_FTA_opp=('WFTA', 'sum'),
        W_TO_opp=('WTO', 'sum'), W_Score_opp=('WScore', 'sum'),
    ).reset_index().rename(columns={'LTeamID': 'TeamID'})
    m = w.merge(l, on=['Season', 'TeamID'], how='outer').fillna(0)
    m['Games'] = m['W_Games'] + m['L_Games']
    m['Pts'] = m['W_Score'] + m['L_Score']
    m['PtsA'] = m['L_Score_opp'] + m['W_Score_opp']
    m['FGA'] = m['W_FGA'] + m['L_FGA']
    m['ORB'] = m['W_OR'] + m['L_OR']
    m['TO'] = m['W_TO'] + m['L_TO']
    m['FTA'] = m['W_FTA'] + m['L_FTA']
    m['OppFGA'] = m['L_FGA_opp'] + m['W_FGA_opp']
    m['OppORB'] = m['L_OR_opp'] + m['W_OR_opp']
    m['OppTO'] = m['L_TO_opp'] + m['W_TO_opp']
    m['OppFTA'] = m['L_FTA_opp'] + m['W_FTA_opp']
    m['Poss'] = m['FGA'] - m['ORB'] + m['TO'] + 0.475 * m['FTA']
    m['OppPoss'] = m['OppFGA'] - m['OppORB'] + m['OppTO'] + 0.475 * m['OppFTA']
    m['OffEff'] = m['Pts'] / m['Poss'] * 100
    m['DefEff'] = m['PtsA'] / m['OppPoss'] * 100
    m['NetEff'] = m['OffEff'] - m['DefEff']
    return m[['Season', 'TeamID', 'Games', 'OffEff', 'DefEff', 'NetEff']]

eff = compute_efficiency(reg_det)

# Momentum
games = []
for _, row in reg_compact.iterrows():
    games.append({'Season': row.Season, 'TeamID': row.WTeamID, 'DayNum': row.DayNum,
                  'Win': 1, 'Score': row.WScore, 'OppScore': row.LScore})
    games.append({'Season': row.Season, 'TeamID': row.LTeamID, 'DayNum': row.DayNum,
                  'Win': 0, 'Score': row.LScore, 'OppScore': row.WScore})
games_df = pd.DataFrame(games).sort_values(['Season', 'TeamID', 'DayNum'])
games_df['GameRank'] = games_df.groupby(['Season', 'TeamID']).cumcount(ascending=False)
last10 = games_df[games_df.GameRank < 10]
momentum = last10.groupby(['Season', 'TeamID'])['Win'].mean().reset_index(name='Last10_WP')
overall = games_df.groupby(['Season', 'TeamID'])['Win'].mean().reset_index(name='Overall_WP')
momentum = momentum.merge(overall, on=['Season', 'TeamID'])
momentum['Momentum'] = momentum['Last10_WP'] - momentum['Overall_WP']

# 2026 field
eff_2026 = eff[eff.Season == 2026].copy()
seeds_2026 = seeds[seeds.Season == 2026][['Season', 'TeamID', 'SeedNum']].merge(
    eff_2026, on=['Season', 'TeamID'], how='left')
seeds_2026 = seeds_2026.merge(
    momentum[momentum.Season == 2026][['Season', 'TeamID', 'Momentum', 'Last10_WP']],
    on=['Season', 'TeamID'], how='left')

print(f"2026 Tournament field: {len(seeds_2026)} teams")

print(f"\nTOP 5 BY NET EFFICIENCY:")
for _, r in seeds_2026.nlargest(5, 'NetEff').iterrows():
    name = team_names.get(r.TeamID, '???')
    print(f"  ({int(r.SeedNum)}) {name}: NetEff={r.NetEff:.1f}, OffEff={r.OffEff:.1f}, DefEff={r.DefEff:.1f}")

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

print(f"\nHOTTEST TEAMS ENTERING TOURNAMENT:")
for _, r in seeds_2026.dropna(subset=['Momentum']).nlargest(5, 'Momentum').iterrows():
    name = team_names.get(r.TeamID, '???')
    print(f"  ({int(r.SeedNum)}) {name}: Last 10 WP={r.Last10_WP:.0%}, Momentum={r.Momentum:+.2f}")

print(f"\nCOLDEST TEAMS ENTERING TOURNAMENT:")
for _, r in seeds_2026.dropna(subset=['Momentum']).nsmallest(5, 'Momentum').iterrows():
    name = team_names.get(r.TeamID, '???')
    print(f"  ({int(r.SeedNum)}) {name}: Last 10 WP={r.Last10_WP:.0%}, Momentum={r.Momentum:+.2f}")

# --- FIGURE 9: 2026 Field ---
fig, ax = plt.subplots(figsize=(16, 10))
has_data = seeds_2026.dropna(subset=['Momentum', 'NetEff'])
scatter = ax.scatter(has_data.SeedNum, has_data.NetEff,
                     c=has_data.Momentum, cmap='RdYlGn',
                     s=120, edgecolors='white', linewidths=0.5, vmin=-0.3, vmax=0.3, zorder=5)
cbar = plt.colorbar(scatter, ax=ax, label='Late-Season Momentum', shrink=0.8)
cbar.ax.yaxis.label.set_color('#e0e0e0')
cbar.ax.tick_params(colors='#aaaaaa')

for _, r in has_data.iterrows():
    name = team_names.get(r.TeamID, '???')
    short = name[:14] if len(name) > 14 else name
    ax.annotate(short, (r.SeedNum, r.NetEff),
                xytext=(6, 3), textcoords='offset points', fontsize=6.5, color='#cccccc')

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
for bar, score in zip(bars, brier_scores):
    ax.text(bar.get_width() + 0.003, bar.get_y() + bar.get_height()/2,
            f'{score:.4f}', va='center', fontsize=11, color='#e0e0e0', fontweight='bold')
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
print("Saved: 10_model_comparison.png")

print("\nDone - all 10 figures complete!")
