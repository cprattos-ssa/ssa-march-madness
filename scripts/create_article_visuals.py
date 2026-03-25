"""Create clean process visuals for the article."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import numpy as np

BG = '#0e1117'
CARD_BG = '#1a1f2e'
TEXT = '#e0e0e0'
TEXT_DIM = '#8892a0'
ACCENT = '#ff6b35'
ACCENT2 = '#00d4aa'
ACCENT3 = '#7b68ee'
ACCENT4 = '#ff4757'
ACCENT5 = '#ffd93d'
OUT = 'C:/dev/ssa-march-madness/research/article-draft'

# ============================================================
# VISUAL 1: Clean Pipeline Overview
# ============================================================
fig, ax = plt.subplots(figsize=(14, 5))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)
ax.axis('off')

ax.text(0.5, 0.95, 'The Prediction Pipeline', fontsize=18, fontweight='bold',
        color=TEXT, ha='center', va='top', transform=ax.transAxes)
ax.text(0.5, 0.87, 'From raw data to tournament predictions in two working sessions',
        fontsize=11, color=TEXT_DIM, ha='center', va='top', transform=ax.transAxes)

stages = [
    ('DATA\nINGESTION', '101 files\n4 sources', ACCENT),
    ('FEATURE\nENGINEERING', '57 features\nElo, efficiency,\nSOS, coaching', ACCENT2),
    ('MODEL\nTRAINING', '5 architectures\n30+ configs', ACCENT3),
    ('CALIBRATION &\nSUBMISSION', '132K matchups\n2 submissions', ACCENT5),
    ('POST-MORTEM\nANALYSIS', '30K players\ninjury adjustment', ACCENT4),
]

n = len(stages)
box_w = 0.14
box_h = 0.38
y_center = 0.42
gap = (0.88 - n * box_w) / (n - 1)

for i, (title, detail, color) in enumerate(stages):
    x = 0.06 + i * (box_w + gap)
    rect = FancyBboxPatch((x, y_center - box_h/2), box_w, box_h,
                           boxstyle="round,pad=0.015",
                           facecolor=CARD_BG, edgecolor=color, linewidth=2,
                           transform=ax.transAxes)
    ax.add_patch(rect)
    ax.text(x + box_w/2, y_center + box_h/2 - 0.06, title,
            fontsize=8, fontweight='bold', color=color,
            ha='center', va='top', transform=ax.transAxes, linespacing=1.2)
    ax.text(x + box_w/2, y_center - 0.02, detail,
            fontsize=7.5, color=TEXT_DIM,
            ha='center', va='center', transform=ax.transAxes, linespacing=1.3)
    if i < n - 1:
        arrow_x = x + box_w + 0.005
        arrow_w = gap - 0.01
        ax.annotate('', xy=(arrow_x + arrow_w, y_center),
                     xytext=(arrow_x, y_center),
                     xycoords='axes fraction', textcoords='axes fraction',
                     arrowprops=dict(arrowstyle='->', color=TEXT_DIM, lw=1.5))

# Session labels
s1_center = 0.06 + 1.5 * (box_w + gap) + box_w / 2
s2_center = 0.06 + 4 * (box_w + gap) + box_w / 2
ax.text(s1_center, 0.12, 'Session 1: Pipeline Build',
        fontsize=9, color=ACCENT2, ha='center', transform=ax.transAxes, style='italic')
ax.text(s2_center, 0.12, 'Session 2: Post-Mortem',
        fontsize=9, color=ACCENT4, ha='center', transform=ax.transAxes, style='italic')

# Result
ax.text(0.5, 0.03,
        'Result: LightGBM model, 0.050 Brier score (competitive with Kaggle leaderboard)',
        fontsize=10, color=TEXT, ha='center', va='center', transform=ax.transAxes,
        bbox=dict(boxstyle='round,pad=0.4', facecolor='#1e2636', edgecolor=ACCENT2, linewidth=1.5))

plt.savefig(f'{OUT}/visual-1-pipeline-overview.png', dpi=200, bbox_inches='tight', facecolor=BG)
plt.close()
print("Saved visual-1-pipeline-overview.png")


# ============================================================
# VISUAL 1b: Session 2 Flowchart (cleaned up)
# ============================================================
fig, ax = plt.subplots(figsize=(14, 8.5))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)
ax.axis('off')
ax.set_xlim(0, 14)
ax.set_ylim(-0.5, 10)

def draw_box(x, y, w, h, text, color=ACCENT2, fontsize=8, subtext=None):
    rect = FancyBboxPatch((x - w/2, y - h/2), w, h,
                           boxstyle="round,pad=0.12",
                           facecolor=CARD_BG, edgecolor=color, linewidth=1.8)
    ax.add_patch(rect)
    if subtext:
        ax.text(x, y + 0.12, text, fontsize=fontsize, fontweight='bold',
                color=color, ha='center', va='center')
        ax.text(x, y - 0.18, subtext, fontsize=fontsize - 1.5,
                color=TEXT_DIM, ha='center', va='center')
    else:
        ax.text(x, y, text, fontsize=fontsize, fontweight='bold',
                color=color, ha='center', va='center', linespacing=1.3)

def arrow(x1, y1, x2, y2, color=TEXT_DIM):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', color=color, lw=1.5))

def prompt(x, y, text):
    ax.text(x, y, text, fontsize=7.5, color=ACCENT4, ha='left', va='center',
            style='italic',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#2a1520',
                      edgecolor=ACCENT4, linewidth=1, alpha=0.8))

# Title
ax.text(7, 9.6, 'Session 2: Post-Mortem Analysis', fontsize=16, fontweight='bold', color=TEXT, ha='center')
ax.text(7, 9.2, '~18 agents  |  ~6 hours  |  Player data experiment + injury analysis + article prep',
        fontsize=9, color=TEXT_DIM, ha='center')

# Row 1
draw_box(3, 8.3, 3.2, 0.55, 'Scan full repo (31 files read)', ACCENT)
arrow(4.6, 8.05, 7, 7.55)

# Row 2: parallel
ax.text(7, 7.7, '3 AGENTS IN PARALLEL', fontsize=7, color=TEXT_DIM, ha='center')
draw_box(2.5, 7.05, 2.8, 0.55, 'Non-obvious basketball\ninsights (39 calls)', ACCENT2)
draw_box(7, 7.05, 2.8, 0.55, 'Game details + player\ndata sources (30 calls)', ACCENT2)
draw_box(11.5, 7.05, 2.8, 0.55, '500-line analysis script\n+ 10 new figures', ACCENT2)

# Prompt 1
prompt(0.5, 6.2, '"Add player-level data. Could individual stats have predicted these upsets?"')
arrow(7, 6.15, 7, 5.75)

# Row 3: parallel
ax.text(7, 5.9, '3 AGENTS IN PARALLEL', fontsize=7, color=TEXT_DIM, ha='center')
draw_box(2.5, 5.25, 3.0, 0.55, 'Discovered Barttorvik API\n30K players (6 seasons)', ACCENT2)
draw_box(7, 5.25, 2.8, 0.55, 'Audited 67 existing files\nconfirmed: no player data', ACCENT2)
draw_box(11.5, 5.25, 2.8, 0.55, 'Pulled live ESPN scores\ntest predictions vs reality', ACCENT2)

# Build + sweep
arrow(4, 4.97, 4.5, 4.5)
draw_box(4.5, 4.15, 3.2, 0.55, 'Name matching (99.3%)\n57 features -> 65 features', ACCENT3)
draw_box(10, 4.15, 3.5, 0.55, '30-config hyperparameter sweep\nXGBoost + LightGBM + Neural Net', ACCENT3)
arrow(6.1, 4.15, 8.25, 4.15)

# Result (bad news)
arrow(10, 3.87, 7, 3.35)
draw_box(7, 3.0, 5.5, 0.55, 'Player data made the model worse: 0.054 vs 0.050 Brier', ACCENT4)

# Prompt 2
prompt(0.5, 2.25, '"That doesn\'t make sense. Research why. Check Kaggle winners, academic papers, anything."')
arrow(7, 2.2, 7, 1.75)

# Row 5: research
ax.text(7, 1.9, '2 AGENTS IN PARALLEL', fontsize=7, color=TEXT_DIM, ha='center')
draw_box(4, 1.25, 3.8, 0.55, 'Kaggle winners, KenPom noise\nresearch, academic papers', ACCENT2)
draw_box(10.5, 1.25, 3.5, 0.55, 'Injury announcement dates\nNCAA rules, betting data', ACCENT2)

# Final output
arrow(7, 0.97, 7, 0.35)
draw_box(7, 0.05, 7.0, 0.5, 'Injury-adjusted predictions + era-marked figures + reports + article pitches', ACCENT2)

plt.savefig(f'{OUT}/visual-1b-session2-flowchart.png', dpi=200, bbox_inches='tight', facecolor=BG)
plt.close()
print("Saved visual-1b-session2-flowchart.png")

print("\nDone!")
