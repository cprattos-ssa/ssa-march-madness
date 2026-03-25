"""Create clean, light-themed process diagrams for the LinkedIn article."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

# ============================================================
# VISUAL 1: Pipeline Overview
# ============================================================

fig, ax = plt.subplots(figsize=(14, 5.5))
fig.patch.set_facecolor('#FAFBFC')
ax.set_facecolor('#FAFBFC')
ax.axis('off')

# Title
ax.text(0.5, 0.95, 'The Prediction Pipeline', fontsize=22, fontweight='bold',
        ha='center', va='top', transform=ax.transAxes, color='#1a1a2e')
ax.text(0.5, 0.88, 'From raw data to tournament predictions in two working sessions',
        fontsize=11, ha='center', va='top', transform=ax.transAxes, color='#6b7280')

stages = [
    {'label': 'Data\nIngestion', 'detail': '101 files\n4 sources', 'color': '#3B82F6'},
    {'label': 'Feature\nEngineering', 'detail': '57 features\nElo, efficiency,\nSOS, coaching', 'color': '#8B5CF6'},
    {'label': 'Model\nTraining', 'detail': '5 architectures\n30+ configs', 'color': '#EC4899'},
    {'label': 'Calibration &\nSubmission', 'detail': '132K matchups\n2 submissions', 'color': '#F59E0B'},
    {'label': 'Post-Mortem\nAnalysis', 'detail': '30K players\ninjury analysis', 'color': '#10B981'},
]

n = len(stages)
box_w = 0.14
box_h = 0.38
gap = 0.035
total_w = n * box_w + (n - 1) * gap
start_x = (1 - total_w) / 2
y_center = 0.45

for i, stage in enumerate(stages):
    x = start_x + i * (box_w + gap)

    # Main box
    rect = FancyBboxPatch((x, y_center - box_h / 2), box_w, box_h,
                           boxstyle="round,pad=0.012",
                           facecolor='white', edgecolor=stage['color'],
                           linewidth=2.5, transform=ax.transAxes)
    ax.add_patch(rect)

    # Color bar at top
    bar = FancyBboxPatch((x, y_center + box_h / 2 - 0.06), box_w, 0.06,
                          boxstyle="round,pad=0.008",
                          facecolor=stage['color'], edgecolor='none',
                          transform=ax.transAxes)
    ax.add_patch(bar)

    # Stage label
    ax.text(x + box_w / 2, y_center + box_h / 2 - 0.12, stage['label'],
            fontsize=9.5, fontweight='bold', ha='center', va='top',
            transform=ax.transAxes, color='#1a1a2e')

    # Detail text
    ax.text(x + box_w / 2, y_center - 0.02, stage['detail'],
            fontsize=8, ha='center', va='center',
            transform=ax.transAxes, color='#6b7280', linespacing=1.4)

    # Arrow between boxes
    if i < n - 1:
        arrow_x = x + box_w + 0.005
        ax.annotate('', xy=(arrow_x + gap - 0.01, y_center),
                    xytext=(arrow_x + 0.005, y_center),
                    xycoords='axes fraction', textcoords='axes fraction',
                    arrowprops=dict(arrowstyle='->', color='#9CA3AF', lw=1.8))

# Session labels
s1_mid = start_x + 1.9 * (box_w + gap)
ax.text(s1_mid, 0.14, 'Session 1: Pipeline Build',
        fontsize=9, fontstyle='italic', ha='center', va='top',
        transform=ax.transAxes, color='#3B82F6')

s2_x = start_x + 4 * (box_w + gap)
ax.text(s2_x + box_w / 2, 0.14, 'Session 2:\nPost-Mortem',
        fontsize=9, fontstyle='italic', ha='center', va='top',
        transform=ax.transAxes, color='#10B981')

# Result bar at bottom
result_w = 0.55
result_x = (1 - result_w) / 2
rect = FancyBboxPatch((result_x, 0.02), result_w, 0.065,
                       boxstyle="round,pad=0.01",
                       facecolor='#EFF6FF', edgecolor='#3B82F6',
                       linewidth=1.5, transform=ax.transAxes)
ax.add_patch(rect)
ax.text(0.5, 0.053, 'Result: LightGBM model, 0.050 Brier score (competitive with Kaggle leaderboard)',
        fontsize=9, fontweight='bold', ha='center', va='center',
        transform=ax.transAxes, color='#1e40af')

plt.savefig('research/article-draft/visual-1-pipeline-overview-v2.png',
            dpi=200, bbox_inches='tight', facecolor='#FAFBFC', pad_inches=0.3)
plt.close()
print("Visual 1 saved")


# ============================================================
# VISUAL 2: Session 2 Flowchart
# ============================================================

fig, ax = plt.subplots(figsize=(12, 8.5))
fig.patch.set_facecolor('#FAFBFC')
ax.set_facecolor('#FAFBFC')
ax.axis('off')
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)


def draw_box(x, y, w, h, text, detail='', color='#3B82F6', fs=9, dfs=7.5):
    rect = FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                           boxstyle="round,pad=0.15",
                           facecolor='white', edgecolor=color, linewidth=2)
    ax.add_patch(rect)
    ty = y + (0.18 if detail else 0)
    ax.text(x, ty, text, fontsize=fs, fontweight='bold',
            ha='center', va='center', color='#1a1a2e')
    if detail:
        ax.text(x, y - 0.22, detail, fontsize=dfs, ha='center', va='center',
                color='#6b7280', linespacing=1.3)


def arrow(x1, y1, x2, y2):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', color='#9CA3AF', lw=1.5))


# Title
ax.text(5, 9.65, 'Session 2: Post-Mortem Analysis', fontsize=18,
        fontweight='bold', ha='center', va='center', color='#1a1a2e')
ax.text(5, 9.25, 'Player data experiment + injury analysis + article prep',
        fontsize=10, ha='center', va='center', color='#6b7280')

# Row 1: Starting question
draw_box(5, 8.35, 5.8, 0.75,
         'Tournament starts. Model misses key upsets on Day 1.',
         'Could individual player stats have predicted these?',
         color='#EF4444', fs=10.5)

# Arrows to Row 2
arrow(3.2, 7.88, 2.5, 7.4)
arrow(5, 7.88, 5, 7.4)
arrow(6.8, 7.88, 7.5, 7.4)

# Row 2: Three parallel tracks
draw_box(2.5, 6.95, 3.2, 0.7,
         'Pull player data', 'Barttorvik API\n30K records, 6 seasons', color='#8B5CF6')
draw_box(5, 6.95, 2.0, 0.7,
         'Audit repo', '67 files checked\nno player data found', color='#8B5CF6')
draw_box(7.5, 6.95, 3.0, 0.7,
         'Pull live scores', 'ESPN results vs\nour predictions', color='#8B5CF6')

# Arrows to Row 3
arrow(2.5, 6.5, 5, 6.0)
arrow(5, 6.5, 5, 6.0)

# Row 3: Feature engineering + retraining
draw_box(5, 5.55, 6.0, 0.7,
         'Engineer 8 player features, retrain 30 model configs',
         'Team WAR, Star WAR, Sr%, experience mix, roster height, star dependency',
         color='#3B82F6', fs=9.5)

# Arrow to result
arrow(5, 5.1, 5, 4.55)

# Row 4: The result
draw_box(5, 4.1, 5.8, 0.75,
         'Brier score went from 0.050 to 0.054. Every config worse.',
         'Player features add noise, not signal. Team stats already capture it.',
         color='#EF4444', fs=10.5)

# Arrow to insight
arrow(5, 3.62, 5, 3.15)

# Row 5: The irony (dashed box)
rect = FancyBboxPatch((1.5, 2.35), 7, 0.9,
                       boxstyle="round,pad=0.15",
                       facecolor='#FEF3C7', edgecolor='#F59E0B', linewidth=2,
                       linestyle='--')
ax.add_patch(rect)
ax.text(5, 2.95, "The irony: features that hurt the model are exactly what flagged the upsets.",
        fontsize=10, fontstyle='italic', fontweight='bold',
        ha='center', va='center', color='#92400E')
ax.text(5, 2.6, "Team WAR flagged the winner in 7 of 12 wrong picks. The model doesn't need them. The edge cases do.",
        fontsize=8.5, ha='center', va='center', color='#92400E')

# Arrows to bottom row
arrow(3.5, 2.25, 2.8, 1.75)
arrow(6.5, 2.25, 7.2, 1.75)

# Row 6: Two parallel outputs
draw_box(2.8, 1.3, 3.6, 0.7,
         'Research & validation', 'Kaggle winners, noise research,\nacademic papers, prob clipping',
         color='#10B981')
draw_box(7.2, 1.3, 3.6, 0.7,
         'Injury analysis', '8 players out pre-tipoff\nDuke, Gonzaga, BYU adjustments',
         color='#10B981')

# Arrows to final bar
arrow(2.8, 0.85, 5, 0.5)
arrow(7.2, 0.85, 5, 0.5)

# Final result bar
rect = FancyBboxPatch((1.25, 0.0), 7.5, 0.55,
                       boxstyle="round,pad=0.1",
                       facecolor='#EFF6FF', edgecolor='#3B82F6', linewidth=1.5)
ax.add_patch(rect)
ax.text(5, 0.28, '19 figures + game-by-game analysis + injury-adjusted predictions + article draft',
        fontsize=9.5, fontweight='bold', ha='center', va='center', color='#1e40af')

plt.savefig('research/article-draft/visual-1b-session2-flowchart-v2.png',
            dpi=200, bbox_inches='tight', facecolor='#FAFBFC', pad_inches=0.3)
plt.close()
print("Visual 2 saved")
