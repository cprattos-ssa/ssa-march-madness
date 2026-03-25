"""Generate updated visualizations covering all 48 R64+R32 games.
V2: Reduced clutter on Chart 1, 3-over-2 layout on Chart 2, larger fonts."""
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
from matplotlib.patches import Patch

matplotlib.rcParams['font.family'] = 'sans-serif'

# All 48 games (R64 + R32), data from r32-data-reference.md
games = [
    # R64 Thursday
    ("Duke def Siena", 0.994, True, 0.0000, "R64"),
    ("Mich St def NDSU", 0.950, True, 0.0025, "R64"),
    ("Louisville def USF", 0.342, False, 0.4330, "R64"),
    ("TCU def Ohio St", 0.181, False, 0.6713, "R64"),
    ("Nebraska def Troy", 0.939, True, 0.0037, "R64"),
    ("Vandy def McNeese", 0.875, True, 0.0157, "R64"),
    ("VCU def UNC (OT)", 0.608, True, 0.1537, "R64"),
    ("Houston def Idaho", 0.982, True, 0.0003, "R64"),
    ("Illinois def Penn", 0.927, True, 0.0053, "R64"),
    ("TAMU def St Marys", 0.085, False, 0.8376, "R64"),
    ("HP def Wisconsin", 0.043, False, 0.9160, "R64"),
    ("Arkansas def Hawaii", 0.971, True, 0.0008, "R64"),
    ("Texas def BYU", 0.117, False, 0.7792, "R64"),
    ("Gonzaga def Kennesaw", 0.948, True, 0.0027, "R64"),
    ("Michigan def Howard", 0.969, True, 0.0010, "R64"),
    ("StLouis def Georgia", 0.637, True, 0.1320, "R64"),
    # R64 Friday
    ("Florida def Prairie View", 0.977, True, 0.0005, "R64"),
    ("Purdue def Queens NC", 0.937, True, 0.0040, "R64"),
    ("Iowa St def Tenn St", 0.959, True, 0.0016, "R64"),
    ("UConn def Furman", 0.981, True, 0.0004, "R64"),
    ("Arizona def LIU", 0.991, True, 0.0001, "R64"),
    ("Alabama def Hofstra", 0.857, True, 0.0206, "R64"),
    ("Kansas def Cal Baptist", 0.909, True, 0.0084, "R64"),
    ("Virginia def Wright St", 0.971, True, 0.0008, "R64"),
    ("Tex Tech def Akron", 0.273, False, 0.5281, "R64"),
    ("St John's def N Iowa", 0.973, True, 0.0007, "R64"),
    ("Tennessee def Miami OH", 0.566, True, 0.1887, "R64"),
    ("Miami FL def Missouri", 0.947, True, 0.0028, "R64"),
    ("UCLA def UCF", 0.961, True, 0.0016, "R64"),
    ("Kentucky def S Clara", 0.296, False, 0.4951, "R64"),
    ("Iowa def Clemson", 0.203, False, 0.6354, "R64"),
    ("Utah St def Villanova", 0.943, True, 0.0032, "R64"),
    # R32 Saturday
    ("Duke def TCU", 0.928, True, 0.0052, "R32"),
    ("Mich St def Louisville", 0.842, True, 0.0251, "R32"),
    ("Houston def TAMU", 0.987, True, 0.0002, "R32"),
    ("Texas def Gonzaga", 0.039, False, 0.9227, "R32"),
    ("Illinois def VCU", 0.768, True, 0.0539, "R32"),
    ("Nebraska def Vandy", 0.109, False, 0.7945, "R32"),
    ("Arkansas def HP", 0.826, True, 0.0303, "R32"),
    ("Michigan def StLouis", 0.962, True, 0.0014, "R32"),
    # R32 Sunday
    ("Purdue def Miami FL", 0.977, True, 0.0005, "R32"),
    ("Iowa St def Kentucky", 0.955, True, 0.0020, "R32"),
    ("St John's def Kansas", 0.952, True, 0.0024, "R32"),
    ("Tennessee def Virginia", 0.193, False, 0.6509, "R32"),
    ("Iowa def Florida", 0.029, False, 0.9432, "R32"),
    ("Arizona def Utah St", 0.921, True, 0.0063, "R32"),
    ("UConn def UCLA", 0.862, True, 0.0191, "R32"),
    ("Alabama def Tex Tech", 0.899, True, 0.0102, "R32"),
]

# ============================================================
# CHART 1: Focused view - Top 10 correct + all 12 wrong
# ============================================================

# Split into correct and wrong
wrong = [(n, p, c, b, r) for n, p, c, b, r in games if not c]
correct = [(n, p, c, b, r) for n, p, c, b, r in games if c]

# Top 10 most confident correct picks
top_correct = sorted(correct, key=lambda x: x[1], reverse=True)[:10]

# Combine: all wrong + top correct, sort by P(Winner)
focused = wrong + top_correct
focused_sorted = sorted(focused, key=lambda x: x[1], reverse=True)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 12), gridspec_kw={'width_ratios': [1.1, 1]})
fig.patch.set_facecolor('#1a1a2e')
fig.suptitle('How the Model Performed Through Two Rounds (R64 + R32)',
             fontsize=16, fontweight='bold', color='white', y=0.98)

# Left panel: confidence in actual winner
y_pos = np.arange(len(focused_sorted))
colors_l = ['#2ecc71' if s[2] else '#e74c3c' for s in focused_sorted]

labels_l = []
for s in focused_sorted:
    prefix = "[R32] " if s[4] == "R32" else ""
    labels_l.append(f"{prefix}{s[0]}")

ax1.barh(y_pos, [s[1] for s in focused_sorted], color=colors_l, height=0.72, alpha=0.9)
ax1.set_yticks(y_pos)
ax1.set_yticklabels(labels_l, fontsize=9, color='white')
ax1.set_xlabel('Model P(Actual Winner)', fontsize=12, color='white')
ax1.set_title('Model Confidence in Actual Winner\nGreen = Correct, Red = Wrong',
              fontsize=13, fontweight='bold', color='white', pad=12)
ax1.axvline(x=0.5, color='white', linestyle='--', alpha=0.3, linewidth=0.8)
ax1.set_facecolor('#16213e')
ax1.tick_params(colors='white', labelsize=9)
ax1.invert_yaxis()
ax1.set_xlim(0, 1.18)

for i, s in enumerate(focused_sorted):
    ax1.text(s[1] + 0.012, i, f"{s[1]*100:.1f}%",
             va='center', fontsize=8, color='white', alpha=0.9)

legend_elements = [
    Patch(facecolor='#2ecc71', label=f'Correct pick (36 total, top 10 shown)'),
    Patch(facecolor='#e74c3c', label=f'Wrong pick (all 12 shown)'),
]
ax1.legend(handles=legend_elements, loc='lower right', fontsize=9,
           facecolor='#16213e', edgecolor='white', labelcolor='white',
           framealpha=0.95)

# Right panel: Brier score for all wrong picks only (the ones that matter)
wrong_sorted = sorted(wrong, key=lambda x: x[3], reverse=True)

y_pos2 = np.arange(len(wrong_sorted))
# Color gradient: darker red for worse Brier
brier_vals = [s[3] for s in wrong_sorted]
max_b = max(brier_vals)
bar_colors = [plt.cm.Reds(0.4 + 0.6 * (b / max_b)) for b in brier_vals]

labels_r = []
for s in wrong_sorted:
    prefix = "[R32] " if s[4] == "R32" else ""
    labels_r.append(f"{prefix}{s[0]}")

bars = ax2.barh(y_pos2, brier_vals, color=bar_colors, height=0.65, alpha=0.9)
ax2.set_yticks(y_pos2)
ax2.set_yticklabels(labels_r, fontsize=9.5, color='white')
ax2.set_xlabel('Brier Score (Lower = Better)', fontsize=12, color='white')
ax2.set_title('Brier Score: All 12 Wrong Picks\nThese 12 games account for 92% of total error',
              fontsize=13, fontweight='bold', color='white', pad=12)
ax2.set_facecolor('#16213e')
ax2.tick_params(colors='white', labelsize=9)
ax2.set_xlim(0, 1.15)

for i, s in enumerate(wrong_sorted):
    ax2.text(s[3] + 0.015, i, f"{s[3]:.3f}",
             va='center', fontsize=10, color='white', fontweight='bold')

# Add the "top 5 = 47% of error" annotation
ax2.axhline(y=4.5, color='#f39c12', linestyle='--', alpha=0.6, linewidth=1.2)
ax2.text(0.55, 4.7, 'Top 5 = 47% of total prediction error',
         fontsize=8.5, color='#f39c12', alpha=0.9, fontstyle='italic')

for spine in ax1.spines.values():
    spine.set_color('white')
    spine.set_alpha(0.3)
for spine in ax2.spines.values():
    spine.set_color('white')
    spine.set_alpha(0.3)

plt.tight_layout(pad=2.5, rect=[0, 0, 1, 0.95])
plt.savefig('results/figures/19_full_tournament_accuracy.png', dpi=150,
            bbox_inches='tight', facecolor='#1a1a2e')
plt.close()
print("Chart 1 saved: results/figures/19_full_tournament_accuracy.png")


# ============================================================
# CHART 2: Feature Comparison - Top 5 Misses, 3-over-2 layout
# ============================================================
fig, axes = plt.subplots(2, 3, figsize=(20, 13))
fig.patch.set_facecolor('#1a1a2e')
fig.suptitle('Our 5 Biggest Misses: What the Model Saw vs. What It Missed',
             fontsize=17, fontweight='bold', color='white', y=0.99)

# Hide the 6th subplot (bottom-right)
axes[1, 2].set_visible(False)

# Flatten to get the 5 we need
ax_list = [axes[0, 0], axes[0, 1], axes[0, 2], axes[1, 0], axes[1, 1]]

misses = [
    {
        'title': '#1: Iowa 73, Florida 72\nBrier: 0.943 (R32)',
        'winner': 'Iowa (Winner)',
        'loser': 'Florida (Our Pick)',
        'features': ['Elo', 'Net\nEff', 'Team\nWAR', 'SOS', 'Sr\nPct', 'Win\nPct'],
        'winner_vals': [1719, 14.4, 38.0, 0.54, 0.20, 0.67],
        'loser_vals': [1978, 20.1, 29.9, 0.68, 0.25, 0.84],
        'winner_labels': ['1719', '14.4', '38', '0.54', '20%', '67%'],
        'loser_labels': ['1978', '20.1', '30', '0.68', '25%', '84%'],
    },
    {
        'title': '#2: Texas 74, Gonzaga 68\nBrier: 0.923 (R32)',
        'winner': 'Texas (Winner)',
        'loser': 'Gonzaga (Our Pick)',
        'features': ['Elo', 'Net\nEff', 'Team\nWAR', 'SOS', 'Sr\nPct', 'Win\nPct'],
        'winner_vals': [1667, 8.3, 85.5, 0.60, 0.52, 0.55],
        'loser_vals': [1933, 26.7, 38.7, 0.62, 0.45, 0.82],
        'winner_labels': ['1667', '8.3', '86', '0.60', '52%', '55%'],
        'loser_labels': ['1933', '26.7', '39', '0.62', '45%', '82%'],
    },
    {
        'title': '#3: High Point 83, Wisconsin 82\nBrier: 0.916 (R64)',
        'winner': 'High Point (Winner)',
        'loser': 'Wisconsin (Our Pick)',
        'features': ['Elo', 'Net\nEff', 'Team\nWAR', 'SOS', 'Sr\nPct', 'Win\nPct'],
        'winner_vals': [1752, 20.2, 48.2, 0.60, 0.64, 0.87],
        'loser_vals': [1825, 10.0, 39.7, 0.54, 0.30, 0.71],
        'winner_labels': ['1752', '20.2', '48', '0.60', '64%', '87%'],
        'loser_labels': ['1825', '10.0', '40', '0.54', '30%', '71%'],
    },
    {
        'title': "#4: Texas A&M 63, St. Mary's 50\nBrier: 0.838 (R64)",
        'winner': 'Texas A&M (Winner)',
        'loser': "St. Mary's (Our Pick)",
        'features': ['Elo', 'Net\nEff', 'Team\nWAR', 'SOS', 'Sr\nPct', 'Win\nPct'],
        'winner_vals': [1707, 10.8, 50.4, 0.56, 0.58, 0.66],
        'loser_vals': [1869, 18.3, 34.8, 0.62, 0.10, 0.84],
        'winner_labels': ['1707', '10.8', '50', '0.56', '58%', '66%'],
        'loser_labels': ['1869', '18.3', '35', '0.62', '10%', '84%'],
    },
    {
        'title': '#5: Nebraska 74, Vanderbilt 72\nBrier: 0.795 (R32)',
        'winner': 'Nebraska (Winner)',
        'loser': 'Vanderbilt (Our Pick)',
        'features': ['Elo', 'Net\nEff', 'Team\nWAR', 'SOS', 'Sr\nPct', 'Win\nPct'],
        'winner_vals': [1783, 16.1, 23.0, 0.60, 0.50, 0.77],
        'loser_vals': [1873, 15.4, 40.6, 0.55, 0.60, 0.76],
        'winner_labels': ['1783', '16.1', '23', '0.60', '50%', '77%'],
        'loser_labels': ['1873', '15.4', '41', '0.55', '60%', '76%'],
    },
]

for idx, (ax, miss) in enumerate(zip(ax_list, misses)):
    ax.set_facecolor('#16213e')
    features = miss['features']
    x = np.arange(len(features))
    width = 0.33

    # Normalize values to 0-1 scale for visual comparison
    w_vals = np.array(miss['winner_vals'], dtype=float)
    l_vals = np.array(miss['loser_vals'], dtype=float)
    max_vals = np.maximum(w_vals, l_vals)
    w_norm = w_vals / max_vals
    l_norm = l_vals / max_vals

    bars1 = ax.bar(x - width/2, w_norm, width, color='#2ecc71', alpha=0.85,
                   label=miss['winner'])
    bars2 = ax.bar(x + width/2, l_norm, width, color='#e74c3c', alpha=0.85,
                   label=miss['loser'])

    # Value labels on bars
    for bar, label in zip(bars1, miss['winner_labels']):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                label, ha='center', va='bottom', fontsize=8, color='#2ecc71',
                fontweight='bold')
    for bar, label in zip(bars2, miss['loser_labels']):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                label, ha='center', va='bottom', fontsize=8, color='#e74c3c',
                fontweight='bold')

    ax.set_xticks(x)
    ax.set_xticklabels(features, fontsize=9, color='white')
    ax.set_ylim(0, 1.3)
    ax.set_title(miss['title'], fontsize=11, fontweight='bold', color='white', pad=10)
    ax.tick_params(colors='white', labelsize=8)
    ax.set_yticklabels([])
    ax.legend(fontsize=8, loc='upper right', facecolor='#16213e',
              edgecolor='white', labelcolor='white', framealpha=0.9)

    for spine in ax.spines.values():
        spine.set_color('white')
        spine.set_alpha(0.3)


plt.tight_layout(pad=2, rect=[0, 0, 1, 0.95])
plt.savefig('results/figures/20_top5_misses_features.png', dpi=150,
            bbox_inches='tight', facecolor='#1a1a2e')
plt.close()
print("Chart 2 saved: results/figures/20_top5_misses_features.png")

print("\nDone! Both charts generated.")
