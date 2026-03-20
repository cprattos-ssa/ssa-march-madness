"""
Regenerate key figures with structural era markers and create modern-era-only versions.

Produces:
  02v2_upset_rate_eras.png        - Upset rate over time with era markers
  04v2_three_point_eras.png       - Three-point paradox with era markers
  03v2_seed_efficiency_modern.png - Seed vs efficiency, portal era only (2021-2025)
  05v2_momentum_modern.png        - Momentum scatter, portal era only (2021-2025)
  15_structural_timeline.png      - Infographic timeline of structural breaks
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path("C:/dev/ssa-march-madness")
RAW = ROOT / "data" / "raw" / "kaggle"
PROC = ROOT / "data" / "processed"
FIG = ROOT / "results" / "figures"
FIG.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Style (matching existing dark theme)
# ---------------------------------------------------------------------------
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

ACCENT  = '#ff6b35'   # Orange
ACCENT2 = '#00d4aa'   # Teal
ACCENT3 = '#7b68ee'   # Purple
ACCENT4 = '#ff4757'   # Red
ACCENT5 = '#ffd93d'   # Yellow

# Era colors
ERA_PRE2016 = '#5a6d8a'     # Muted blue-gray
ERA_SHOTCLOCK = '#ff6b35'   # Orange (ACCENT)
ERA_PORTAL = '#00d4aa'      # Teal (ACCENT2)

# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
print("=" * 80)
print("REGENERATING FIGURES WITH ERA MARKERS")
print("=" * 80)

print("\n[Loading data...]")
tourney = pd.read_csv(RAW / "MNCAATourneyCompactResults.csv")
seeds = pd.read_csv(RAW / "MNCAATourneySeeds.csv")
reg_det = pd.read_csv(RAW / "MRegularSeasonDetailedResults.csv")
reg_compact = pd.read_csv(RAW / "MRegularSeasonCompactResults.csv")
teams = pd.read_csv(RAW / "MTeams.csv")

seeds['SeedNum'] = seeds['Seed'].str.extract(r'(\d+)').astype(int)
team_names = dict(zip(teams['TeamID'], teams['TeamName']))

print(f"  Tourney games: {len(tourney)}")
print(f"  Regular season detailed: {len(reg_det)}")
print(f"  Seeds: {len(seeds)}")


# ---------------------------------------------------------------------------
# Helper: add structural break lines to an axes
# ---------------------------------------------------------------------------
def add_era_markers(ax, breaks, y_frac=0.92, fontsize=8):
    """Draw vertical dashed lines and labels for structural breaks."""
    ymin, ymax = ax.get_ylim()
    y_label = ymin + (ymax - ymin) * y_frac
    for year, label, color in breaks:
        ax.axvline(x=year, color=color, linestyle='--', alpha=0.7, linewidth=1.5)
        ax.text(year + 0.3, y_label, label, fontsize=fontsize,
                color=color, rotation=90, va='top', ha='left',
                fontweight='bold', alpha=0.9,
                bbox=dict(boxstyle='round,pad=0.2', facecolor='#0e1117',
                          edgecolor=color, alpha=0.8))


# ---------------------------------------------------------------------------
# Compute efficiency (reused across multiple figures)
# ---------------------------------------------------------------------------
def compute_efficiency(df, season_min=2003):
    df = df[df.Season >= season_min].copy()

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

    merged = w.merge(l, on=['Season', 'TeamID'], how='outer').fillna(0)

    merged['Games'] = merged['W_Games'] + merged['L_Games']
    merged['Wins'] = merged['W_Games']
    merged['WinPct'] = merged['Wins'] / merged['Games']

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

    merged['Opp_FGA'] = merged['L_FGA_opp'] + merged['W_FGA_opp']
    merged['Opp_FTA'] = merged['L_FTA_opp'] + merged['W_FTA_opp']
    merged['Opp_ORB'] = merged['L_OR_opp'] + merged['W_OR_opp']
    merged['Opp_TO'] = merged['L_TO_opp'] + merged['W_TO_opp']

    merged['Poss'] = merged['FGA'] - merged['ORB'] + merged['TO'] + 0.475 * merged['FTA']
    merged['OppPoss'] = merged['Opp_FGA'] - merged['Opp_ORB'] + merged['Opp_TO'] + 0.475 * merged['Opp_FTA']

    merged['OffEff'] = merged['Pts'] / merged['Poss'] * 100
    merged['DefEff'] = merged['PtsAllowed'] / merged['OppPoss'] * 100
    merged['NetEff'] = merged['OffEff'] - merged['DefEff']

    merged['eFGPct'] = (merged['FGM'] + 0.5 * merged['FGM3']) / merged['FGA']
    merged['TORate'] = merged['TO'] / merged['Poss']
    merged['FG3Rate'] = merged['FGA3'] / merged['FGA']
    merged['FG3Pct'] = merged['FGM3'] / merged['FGA3']
    merged['PPG'] = merged['Pts'] / merged['Games']
    merged['OppPPG'] = merged['PtsAllowed'] / merged['Games']

    return merged[['Season', 'TeamID', 'Games', 'Wins', 'WinPct', 'Pts', 'PtsAllowed',
                    'Poss', 'OffEff', 'DefEff', 'NetEff', 'eFGPct', 'TORate',
                    'FG3Rate', 'FG3Pct', 'PPG', 'OppPPG', 'FGA3', 'FGM3', 'FGA', 'FGM']]


print("[Computing efficiency stats...]")
eff = compute_efficiency(reg_det)

# Merge with seeds and tourney wins
eff_seeded = eff.merge(seeds[['Season', 'TeamID', 'SeedNum']], on=['Season', 'TeamID'], how='inner')
tourney_wins = tourney.groupby(['Season', 'WTeamID']).size().reset_index(name='TourneyWins')
tourney_wins.rename(columns={'WTeamID': 'TeamID'}, inplace=True)
eff_seeded = eff_seeded.merge(tourney_wins, on=['Season', 'TeamID'], how='left')
eff_seeded['TourneyWins'] = eff_seeded['TourneyWins'].fillna(0).astype(int)

seed_avg_wins = eff_seeded.groupby('SeedNum')['TourneyWins'].mean()
eff_seeded['ExpectedWins'] = eff_seeded['SeedNum'].map(seed_avg_wins)
eff_seeded['WinsOverExpected'] = eff_seeded['TourneyWins'] - eff_seeded['ExpectedWins']
eff_seeded['NetEffRank'] = eff_seeded.groupby('Season')['NetEff'].rank(ascending=False)


# ===========================================================================
# FIGURE 02v2: Upset Rate Over Time WITH Era Markers
# ===========================================================================
print("\n--- Figure 02v2: Upset Rate with Era Markers ---")

# Prepare upset data
t = tourney.copy()
t = t.merge(seeds[['Season', 'TeamID', 'SeedNum']].rename(
    columns={'TeamID': 'WTeamID', 'SeedNum': 'WSeed'}), on=['Season', 'WTeamID'], how='left')
t = t.merge(seeds[['Season', 'TeamID', 'SeedNum']].rename(
    columns={'TeamID': 'LTeamID', 'SeedNum': 'LSeed'}), on=['Season', 'LTeamID'], how='left')
t = t.dropna(subset=['WSeed', 'LSeed'])
t['Upset'] = t['WSeed'] > t['LSeed']

yearly_upsets = t.groupby('Season').agg(
    games=('Upset', 'count'),
    upsets=('Upset', 'sum'),
).reset_index()
yearly_upsets['upset_rate'] = yearly_upsets['upsets'] / yearly_upsets['games']

fig, ax = plt.subplots(figsize=(16, 7))

# Color-code bars by era
bar_colors = []
for s in yearly_upsets.Season:
    if s < 2016:
        bar_colors.append(ERA_PRE2016)
    elif s < 2020:
        bar_colors.append(ERA_SHOTCLOCK)
    elif s == 2020:
        bar_colors.append('#444444')  # COVID - no tournament
    else:
        bar_colors.append(ERA_PORTAL)

ax.bar(yearly_upsets.Season, yearly_upsets.upset_rate * 100,
       color=bar_colors, alpha=0.7, width=0.8, edgecolor='none')

# Rolling average
window = 5
rolling = yearly_upsets.set_index('Season')['upset_rate'].rolling(window, center=True).mean() * 100
ax.plot(rolling.index, rolling.values, color='white', linewidth=2.5,
        label=f'{window}-year rolling avg', zorder=5)

# Shaded portal/NIL era
ymin, ymax = 0, yearly_upsets.upset_rate.max() * 100 + 8
ax.set_ylim(ymin, ymax)
ax.axvspan(2021, yearly_upsets.Season.max() + 0.5, alpha=0.08, color=ERA_PORTAL,
           label='Portal/NIL Era')

# Era marker vertical lines
era_breaks = [
    (2016, 'Shot clock\n35->30 sec', ACCENT5, 0.92),
    (2020, 'COVID cancels\ntournament', ACCENT4, 0.78),
    (2021, 'Transfer portal\n+ NIL era', ACCENT2, 0.92),
]
for year, label, color, y_frac in era_breaks:
    ax.axvline(x=year, color=color, linestyle='--', alpha=0.8, linewidth=1.5, zorder=4)
    ax.text(year + 0.4, ymax * y_frac, label, fontsize=8.5,
            color=color, rotation=0, va='top', ha='left',
            fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#0e1117',
                      edgecolor=color, alpha=0.95), zorder=6)

# Mark notable high-upset years
for _, r in yearly_upsets.nlargest(3, 'upset_rate').iterrows():
    ax.annotate(f"{int(r.Season)}", (r.Season, r.upset_rate * 100 + 1.5),
                ha='center', fontsize=8, color=ACCENT4, fontweight='bold')

# Legend for eras
legend_elements = [
    mpatches.Patch(facecolor=ERA_PRE2016, alpha=0.7, label='Pre-2016 (35-sec clock)'),
    mpatches.Patch(facecolor=ERA_SHOTCLOCK, alpha=0.7, label='2016-2019 (30-sec clock)'),
    mpatches.Patch(facecolor=ERA_PORTAL, alpha=0.7, label='2021+ (Portal/NIL)'),
    Line2D([0], [0], color='white', linewidth=2.5, label=f'{window}-yr rolling avg'),
]
ax.legend(handles=legend_elements, framealpha=0.3, facecolor='#1a1a2e', loc='upper left')

ax.set_xlabel('Season', fontsize=12)
ax.set_ylabel('Upset Rate (%)', fontsize=12)
ax.set_title('Are Upsets Dying? 40 Years of Tournament Chaos (with Structural Breaks)',
             fontsize=15, pad=15)
ax.grid(axis='y', alpha=0.3)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.tight_layout()
plt.savefig(FIG / '02v2_upset_rate_eras.png', dpi=200, bbox_inches='tight')
plt.close()
print("  Saved: 02v2_upset_rate_eras.png")


# ===========================================================================
# FIGURE 04v2: Three-Point Paradox WITH Era Markers
# ===========================================================================
print("\n--- Figure 04v2: Three-Point Paradox with Era Markers ---")

season_3pt = eff.groupby('Season').agg(
    FGA3=('FGA3', 'sum'), FGM3=('FGM3', 'sum'),
    FGA=('FGA', 'sum'), FGM=('FGM', 'sum'),
    teams=('TeamID', 'nunique'),
).reset_index()
season_3pt['FG3Rate'] = season_3pt['FGA3'] / season_3pt['FGA']
season_3pt['FG3Pct'] = season_3pt['FGM3'] / season_3pt['FGA3']

fig, ax1 = plt.subplots(figsize=(16, 7))
ax2 = ax1.twinx()

# Volume - fill + line
ax1.fill_between(season_3pt.Season, season_3pt.FG3Rate * 100, alpha=0.25, color=ACCENT)
ax1.plot(season_3pt.Season, season_3pt.FG3Rate * 100, color=ACCENT, linewidth=2.5,
         label='3PT share of all shots (%)', marker='o', markersize=4)

# Accuracy line
ax2.plot(season_3pt.Season, season_3pt.FG3Pct * 100, color=ACCENT2, linewidth=2.5,
         label='3PT accuracy (%)', marker='s', markersize=4)

# Shade post-2020 era
ax1.axvspan(2020, season_3pt.Season.max() + 0.5, alpha=0.07, color=ACCENT2)

# Structural break markers
three_pt_breaks = [
    (2008, '3PT line moved\nto 20\'9"', ACCENT3),
    (2016, 'Shot clock\n35->30 sec', ACCENT5),
    (2020, '3PT line to 22\'1"\n+ COVID', ACCENT4),
]

rate_max = season_3pt.FG3Rate.max() * 100
for year, label, color in three_pt_breaks:
    ax1.axvline(x=year, color=color, linestyle='--', alpha=0.8, linewidth=1.5, zorder=4)
    # Stagger vertical position to avoid overlap
    if year == 2008:
        y_pos = rate_max * 0.55
    elif year == 2016:
        y_pos = rate_max * 0.75
    else:
        y_pos = rate_max * 0.92
    ax1.text(year + 0.4, y_pos, label, fontsize=8.5,
             color=color, va='top', ha='left', fontweight='bold',
             bbox=dict(boxstyle='round,pad=0.3', facecolor='#0e1117',
                       edgecolor=color, alpha=0.85))

ax1.set_xlabel('Season', fontsize=12)
ax1.set_ylabel('3PT Share of All Shots (%)', fontsize=12, color=ACCENT)
ax2.set_ylabel('3PT Accuracy (%)', fontsize=12, color=ACCENT2)
ax1.set_title('The Three-Point Paradox: Every Rule Change Made It Worse',
              fontsize=15, pad=15)

lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left',
           framealpha=0.3, facecolor='#1a1a2e')

ax1.grid(axis='y', alpha=0.2)
ax1.spines['top'].set_visible(False)
ax2.spines['top'].set_visible(False)
ax1.tick_params(axis='y', labelcolor=ACCENT)
ax2.tick_params(axis='y', labelcolor=ACCENT2)
plt.tight_layout()
plt.savefig(FIG / '04v2_three_point_eras.png', dpi=200, bbox_inches='tight')
plt.close()
print("  Saved: 04v2_three_point_eras.png")


# ===========================================================================
# FIGURE 03v2: Seed vs Efficiency - MODERN ERA ONLY (2021-2025)
# ===========================================================================
print("\n--- Figure 03v2: Seed vs Efficiency (Modern Era) ---")

modern = eff_seeded[eff_seeded.Season >= 2021].copy()
modern['NetEffRank'] = modern.groupby('Season')['NetEff'].rank(ascending=False)

# Fool's gold: high seed (low number) but bad efficiency
fools_gold_m = modern[(modern.SeedNum <= 4) & (modern.NetEffRank > 30)]
fools_gold_m = fools_gold_m.sort_values('NetEffRank', ascending=False)

# Hidden gems: low seed (high number) but great efficiency
hidden_gems_m = modern[(modern.SeedNum >= 10) & (modern.NetEffRank <= 30)]
hidden_gems_m = hidden_gems_m.sort_values('TourneyWins', ascending=False)

fig, ax = plt.subplots(figsize=(14, 9))
scatter = ax.scatter(modern['SeedNum'], modern['NetEff'],
                     c=modern['TourneyWins'], cmap='plasma',
                     alpha=0.55, s=40, edgecolors='none')
cbar = plt.colorbar(scatter, ax=ax, label='Tournament Wins', shrink=0.8)
cbar.ax.yaxis.label.set_color('#e0e0e0')
cbar.ax.tick_params(colors='#aaaaaa')

# Highlight fool's gold and hidden gems
fg = fools_gold_m.head(5)
hg = hidden_gems_m.head(5)

# Collect all annotation positions for collision avoidance
used_positions = []

def smart_offset(x, y, default_dx, default_dy, used, spread=22):
    """Find a non-overlapping offset for an annotation."""
    for attempt in range(20):
        dx = default_dx + (attempt % 4) * spread * (1 if default_dx >= 0 else -1)
        dy = default_dy + (attempt // 4) * spread * (-1 if attempt % 2 == 0 else 1)
        conflict = False
        for ux, uy in used:
            if abs((x + dx) - ux) < spread and abs((y + dy) - uy) < spread:
                conflict = True
                break
        if not conflict:
            used.append((x + dx, y + dy))
            return dx, dy
    used.append((x + default_dx, y + default_dy))
    return default_dx, default_dy

if len(fg) > 0:
    ax.scatter(fg.SeedNum, fg.NetEff, s=160, facecolors='none',
               edgecolors=ACCENT4, linewidths=2.5, label="Fool's Gold", zorder=5)
    for _, r in fg.iterrows():
        name = team_names.get(r.TeamID, '???')
        dx, dy = smart_offset(r.SeedNum, r.NetEff, 14, 10, used_positions)
        ax.annotate(f"{name} '{int(r.Season) % 100:02d}",
                    (r.SeedNum, r.NetEff),
                    xytext=(dx, dy), textcoords='offset points',
                    fontsize=9, color='#ffffff', fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='#1a1a2e',
                              edgecolor=ACCENT4, alpha=0.95, linewidth=1.2),
                    arrowprops=dict(arrowstyle='->', color=ACCENT4, alpha=0.7, lw=1.0),
                    zorder=10)

if len(hg) > 0:
    ax.scatter(hg.SeedNum, hg.NetEff, s=160, facecolors='none',
               edgecolors=ACCENT2, linewidths=2.5, label="Hidden Gems", zorder=5)
    for _, r in hg.iterrows():
        name = team_names.get(r.TeamID, '???')
        dx, dy = smart_offset(r.SeedNum, r.NetEff, 14, -14, used_positions)
        ax.annotate(f"{name} '{int(r.Season) % 100:02d}",
                    (r.SeedNum, r.NetEff),
                    xytext=(dx, dy), textcoords='offset points',
                    fontsize=9, color='#ffffff', fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='#1a1a2e',
                              edgecolor=ACCENT2, alpha=0.95, linewidth=1.2),
                    arrowprops=dict(arrowstyle='->', color=ACCENT2, alpha=0.7, lw=1.0),
                    zorder=10)

# Add subtitle with stats
n_teams = len(modern)
n_seasons = modern.Season.nunique()
ax.text(0.02, 0.02,
        f"{n_teams} tournament teams across {n_seasons} seasons (2021-2025)\n"
        f"Portal era: free transfers + NIL money reshaped rosters",
        transform=ax.transAxes, fontsize=9, color='#888888', va='bottom')

ax.set_xlabel('Tournament Seed', fontsize=12)
ax.set_ylabel('Net Efficiency (Off - Def per 100 poss)', fontsize=12)
ax.set_title("Seeds vs Reality: The Portal Era (2021-2025)", fontsize=15, pad=15)
ax.legend(framealpha=0.3, facecolor='#1a1a2e', loc='upper left')
ax.invert_xaxis()
ax.grid(alpha=0.2)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.tight_layout()
plt.savefig(FIG / '03v2_seed_efficiency_modern.png', dpi=200, bbox_inches='tight')
plt.close()
print("  Saved: 03v2_seed_efficiency_modern.png")


# ===========================================================================
# FIGURE 05v2: Momentum - MODERN ERA ONLY (2021-2025)
# ===========================================================================
print("\n--- Figure 05v2: Momentum (Modern Era) ---")

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

# Filter to modern era
momentum_modern = momentum_seeded[momentum_seeded.Season >= 2021].copy()

# Correlation
corr_momentum = momentum_modern[['Momentum', 'WinsOverExpected']].corr().iloc[0, 1]

fig, ax = plt.subplots(figsize=(12, 8))
colors_by_seed = np.where(momentum_modern.SeedNum <= 4, ACCENT,
                   np.where(momentum_modern.SeedNum <= 8, ACCENT3,
                   np.where(momentum_modern.SeedNum <= 12, ACCENT2, ACCENT5)))
ax.scatter(momentum_modern.Momentum * 100, momentum_modern.WinsOverExpected,
           c=colors_by_seed, alpha=0.45, s=35, edgecolors='none')

# Trend line
z = np.polyfit(momentum_modern.Momentum, momentum_modern.WinsOverExpected, 1)
p = np.poly1d(z)
x_line = np.linspace(momentum_modern.Momentum.min(), momentum_modern.Momentum.max(), 100)
ax.plot(x_line * 100, p(x_line), color=ACCENT4, linewidth=2, linestyle='--',
        label=f'Trend (r={corr_momentum:+.3f})')

ax.axhline(y=0, color='white', alpha=0.3, linewidth=0.5)
ax.axvline(x=0, color='white', alpha=0.3, linewidth=0.5)

# Legend for seed groups
legend_elements = [
    Line2D([0], [0], marker='o', color='w', markerfacecolor=ACCENT, markersize=8, label='1-4 seeds'),
    Line2D([0], [0], marker='o', color='w', markerfacecolor=ACCENT3, markersize=8, label='5-8 seeds'),
    Line2D([0], [0], marker='o', color='w', markerfacecolor=ACCENT2, markersize=8, label='9-12 seeds'),
    Line2D([0], [0], marker='o', color='w', markerfacecolor=ACCENT5, markersize=8, label='13+ seeds'),
    Line2D([0], [0], color=ACCENT4, linewidth=2, linestyle='--',
           label=f'Trend (r={corr_momentum:+.3f})'),
]
ax.legend(handles=legend_elements, framealpha=0.3, facecolor='#1a1a2e')

# Subtitle
ax.text(0.02, 0.02,
        f"Portal era (2021-2025): {len(momentum_modern)} tournament teams\n"
        f"Roster turnover from transfers makes momentum even less predictive",
        transform=ax.transAxes, fontsize=9, color='#888888', va='bottom')

ax.set_xlabel('Late-Season Momentum (Last 10 Win% - Season Win%)', fontsize=12)
ax.set_ylabel('Tournament Wins Over Expected', fontsize=12)
ax.set_title("Peaking at the Right Time? Still a Myth in the Portal Era",
             fontsize=15, pad=15)
ax.xaxis.set_major_formatter(mticker.PercentFormatter())
ax.grid(alpha=0.2)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.tight_layout()
plt.savefig(FIG / '05v2_momentum_modern.png', dpi=200, bbox_inches='tight')
plt.close()
print("  Saved: 05v2_momentum_modern.png")


# ===========================================================================
# FIGURE 15: Structural Breaks Timeline (Infographic)
# ===========================================================================
print("\n--- Figure 15: Structural Breaks Timeline ---")

# Compute sparkline metrics by season
# 1) Average scoring (PPG across all teams)
scoring_by_season = eff.groupby('Season')['PPG'].mean()

# 2) 3-point attempt rate
three_rate_by_season = season_3pt.set_index('Season')['FG3Rate']

# 3) Upset rate by season (already computed)
upset_by_season = yearly_upsets.set_index('Season')['upset_rate']

# Focus on 2003-2025 range (where we have detailed stats)
years_range = range(2003, 2026)

fig, axes = plt.subplots(4, 1, figsize=(18, 12),
                         gridspec_kw={'height_ratios': [1.2, 1, 1, 1], 'hspace': 0.3})

# ---- Top panel: Timeline with structural break annotations ----
ax_top = axes[0]
ax_top.set_xlim(2002.5, 2026.5)
ax_top.set_ylim(-0.5, 3.5)
ax_top.set_yticks([])
ax_top.set_xticks(range(2003, 2027))
ax_top.tick_params(axis='x', rotation=45, labelsize=9)

# Draw the timeline spine
ax_top.axhline(y=1.5, color='#555555', linewidth=2, zorder=1)
for yr in years_range:
    ax_top.plot(yr, 1.5, 'o', color='#555555', markersize=3, zorder=2)

# Structural breaks with descriptions
breaks_info = [
    (2008, "3PT line moved\nto 20'9\"", ACCENT3, 2.8, 'above'),
    (2010, "First Four\ngames added", '#888888', 0.2, 'below'),
    (2016, "Shot clock cut\n35 -> 30 sec", ACCENT5, 2.8, 'above'),
    (2018, "Shot clock resets\nto 20 on ORB", '#888888', 0.2, 'below'),
    (2020, "COVID cancels\ntournament", ACCENT4, 2.8, 'above'),
    (2021, "Transfer portal\n(free transfer)", ACCENT2, 0.2, 'below'),
    (2021.6, "NIL era begins\n(player pay)", ACCENT, 2.8, 'above'),
    (2023, "Expanded NIL +\ntransfer windows", '#888888', 0.2, 'below'),
]

for yr, label, color, y_pos, side in breaks_info:
    ax_top.plot(yr, 1.5, 'D', color=color, markersize=10, zorder=5,
                markeredgecolor='white', markeredgewidth=0.5)
    # Draw connector
    if side == 'above':
        ax_top.plot([yr, yr], [1.5, y_pos - 0.3], color=color, linewidth=1, alpha=0.7)
        va = 'bottom'
    else:
        ax_top.plot([yr, yr], [1.5, y_pos + 0.3], color=color, linewidth=1, alpha=0.7)
        va = 'top'
    ax_top.text(yr, y_pos, label, ha='center', va=va, fontsize=8,
                color=color, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='#0e1117',
                          edgecolor=color, alpha=0.85))

ax_top.set_title("How the Game Changed: A Timeline of College Basketball's Structural Breaks",
                 fontsize=16, pad=15, fontweight='bold')
ax_top.spines['top'].set_visible(False)
ax_top.spines['right'].set_visible(False)
ax_top.spines['left'].set_visible(False)
ax_top.spines['bottom'].set_visible(False)

# ---- Sparkline 1: Average PPG ----
ax_s1 = axes[1]
s1_data = scoring_by_season.reindex(years_range)
ax_s1.fill_between(s1_data.index, s1_data.values, alpha=0.2, color=ACCENT)
ax_s1.plot(s1_data.index, s1_data.values, color=ACCENT, linewidth=2, marker='o', markersize=3)
for yr in [2008, 2016, 2020, 2021]:
    ax_s1.axvline(x=yr, color='#555555', linestyle='--', alpha=0.5, linewidth=1)
ax_s1.set_ylabel('Avg PPG', fontsize=10, color=ACCENT)
ax_s1.set_xlim(2002.5, 2026.5)
ax_s1.set_xticks(range(2003, 2027))
ax_s1.tick_params(axis='x', rotation=45, labelsize=8)
ax_s1.grid(axis='y', alpha=0.2)
ax_s1.spines['top'].set_visible(False)
ax_s1.spines['right'].set_visible(False)
# Annotate the shot clock change effect
min_ppg_yr = s1_data.idxmin()
ax_s1.annotate(f"Low: {s1_data[min_ppg_yr]:.1f}\n({int(min_ppg_yr)})",
               (min_ppg_yr, s1_data[min_ppg_yr]),
               xytext=(20, -15), textcoords='offset points', fontsize=8, color=ACCENT4,
               arrowprops=dict(arrowstyle='->', color=ACCENT4, lw=1))

# ---- Sparkline 2: 3PT rate ----
ax_s2 = axes[2]
s2_data = three_rate_by_season.reindex(years_range)
ax_s2.fill_between(s2_data.index, s2_data.values * 100, alpha=0.2, color=ACCENT3)
ax_s2.plot(s2_data.index, s2_data.values * 100, color=ACCENT3, linewidth=2, marker='o', markersize=3)
for yr in [2008, 2016, 2020, 2021]:
    ax_s2.axvline(x=yr, color='#555555', linestyle='--', alpha=0.5, linewidth=1)
ax_s2.set_ylabel('3PT Rate (%)', fontsize=10, color=ACCENT3)
ax_s2.set_xlim(2002.5, 2026.5)
ax_s2.set_xticks(range(2003, 2027))
ax_s2.tick_params(axis='x', rotation=45, labelsize=8)
ax_s2.grid(axis='y', alpha=0.2)
ax_s2.spines['top'].set_visible(False)
ax_s2.spines['right'].set_visible(False)

# ---- Sparkline 3: Upset rate ----
ax_s3 = axes[3]
s3_data = upset_by_season.reindex(list(years_range))
# Remove 2020 (no tournament)
if 2020 in s3_data.index:
    s3_data = s3_data.drop(2020)
ax_s3.fill_between(s3_data.index, s3_data.values * 100, alpha=0.2, color=ACCENT2)
ax_s3.plot(s3_data.index, s3_data.values * 100, color=ACCENT2, linewidth=2, marker='o', markersize=3)
for yr in [2008, 2016, 2020, 2021]:
    ax_s3.axvline(x=yr, color='#555555', linestyle='--', alpha=0.5, linewidth=1)
ax_s3.set_ylabel('Upset Rate (%)', fontsize=10, color=ACCENT2)
ax_s3.set_xlabel('Season', fontsize=11)
ax_s3.set_xlim(2002.5, 2026.5)
ax_s3.set_xticks(range(2003, 2027))
ax_s3.tick_params(axis='x', rotation=45, labelsize=8)
ax_s3.grid(axis='y', alpha=0.2)
ax_s3.spines['top'].set_visible(False)
ax_s3.spines['right'].set_visible(False)

# Mark the COVID gap
ax_s3.annotate('No tourney\n(COVID)', (2020, ax_s3.get_ylim()[0] + 2),
               ha='center', fontsize=8, color=ACCENT4, fontweight='bold',
               bbox=dict(boxstyle='round,pad=0.2', facecolor='#0e1117',
                         edgecolor=ACCENT4, alpha=0.8))

plt.tight_layout()
plt.savefig(FIG / '15_structural_timeline.png', dpi=200, bbox_inches='tight')
plt.close()
print("  Saved: 15_structural_timeline.png")


# ===========================================================================
# Summary
# ===========================================================================
print("\n" + "=" * 80)
print("ALL FIGURES GENERATED SUCCESSFULLY")
print("=" * 80)

output_files = [
    '02v2_upset_rate_eras.png',
    '04v2_three_point_eras.png',
    '03v2_seed_efficiency_modern.png',
    '05v2_momentum_modern.png',
    '15_structural_timeline.png',
]
for f in output_files:
    path = FIG / f
    if path.exists():
        size_kb = path.stat().st_size / 1024
        print(f"  [OK] {f} ({size_kb:.0f} KB)")
    else:
        print(f"  [MISSING] {f}")
