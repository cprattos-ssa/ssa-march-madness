"""Generate clean, simple table images for Medium article."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

matplotlib.rcParams['font.family'] = 'sans-serif'


def make_table(headers, rows, title, filename, col_widths=None):
    """Create a clean, simple table image."""
    n_cols = len(headers)
    n_rows = len(rows)

    if col_widths is None:
        col_widths = [1.0 / n_cols] * n_cols

    fig_width = 14
    row_h = 0.45
    header_h = 0.5
    title_h = 0.6
    fig_height = title_h + header_h + n_rows * row_h + 0.3

    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')
    ax.axis('off')
    ax.set_xlim(0, 1)
    ax.set_ylim(0, fig_height)

    # Title
    ax.text(0.5, fig_height - 0.15, title,
            fontsize=14, fontweight='bold', color='#1a1a2e',
            ha='center', va='top')

    table_top = fig_height - title_h

    # Header background
    ax.fill_between([0.02, 0.98], table_top, table_top - header_h,
                    color='#f1f5f9', zorder=1)

    # Header text
    x = 0.04
    for j, header in enumerate(headers):
        ax.text(x, table_top - header_h / 2, header,
                fontsize=10, fontweight='bold', color='#475569',
                ha='left', va='center')
        x += col_widths[j]

    # Header bottom line
    ax.plot([0.02, 0.98], [table_top - header_h, table_top - header_h],
            color='#cbd5e1', linewidth=1.5)

    # Data rows
    for i, row in enumerate(rows):
        y_top = table_top - header_h - i * row_h
        y_center = y_top - row_h / 2

        # Alternate row shading
        if i % 2 == 1:
            ax.fill_between([0.02, 0.98], y_top, y_top - row_h,
                            color='#f8fafc', zorder=1)

        # Row text
        x = 0.04
        for j, cell in enumerate(row):
            weight = 'bold' if j == 0 else 'normal'
            fontsize = 9.5 if '\n' in cell else 10
            ax.text(x, y_center, cell,
                    fontsize=fontsize, fontweight=weight, color='#1e293b',
                    ha='left', va='center', linespacing=1.3)
            x += col_widths[j]

        # Row separator
        ax.plot([0.02, 0.98], [y_top - row_h, y_top - row_h],
                color='#e2e8f0', linewidth=0.5)

    plt.savefig(filename, dpi=150, bbox_inches='tight',
                facecolor='white', pad_inches=0.2)
    plt.close()
    print(f'Saved: {filename}')


# === Table 1: Part 3 - Five biggest misses ===
make_table(
    headers=['Game', 'Our Prediction', 'What Actually Happened', 'Brier'],
    rows=[
        ['(9) Iowa 73, (1) Florida 72',           'Florida wins, 97.1%',     "Folgueiras' go-ahead 3, 4.5 sec left; first 1-seed to fall", '0.943'],
        ['(11) Texas 74, (3) Gonzaga 68',          'Gonzaga wins, 96.1%',     'First Four team reaches the Sweet 16',                       '0.923'],
        ['(12) High Point 83, (5) Wisconsin 82',   'Wisconsin wins, 95.7%',   "Chase Johnston's fastbreak layup, 11.2 sec left",            '0.916'],
        ["(10) Texas A&M 63, (7) St. Mary's 50",   "St. Mary's wins, 91.5%",  "A&M led wire-to-wire; held St. Mary's to season-low 50",    '0.838'],
        ['(4) Nebraska 74, (5) Vanderbilt 72',     'Vanderbilt wins, 89.1%',  "Frager's layup, 2.2 sec left; Nebraska's first Sweet 16",    '0.795'],
    ],
    title='Five Predictions That Wrecked Our Brier Score',
    filename='results/figures/21_top5_misses_table.png',
    col_widths=[0.27, 0.19, 0.38, 0.08],
)

# === Table 2: Part 4 - What the model saw vs missed ===
make_table(
    headers=['What the Model Weighted Heavily', 'What It Underweighted'],
    rows=[
        ['Wisconsin: 5-seed, 1825 Elo, 0.93 BARTHAG',    'High Point: 20.2 net efficiency (vs 10.0), 64% seniors'],
        ["St. Mary's: 27-6, 1869 Elo",                     'Texas A&M: 58% seniors, Team WAR 50 vs 35, SEC schedule'],
        ['Florida: 1-seed, 1978 Elo, 0.97 BARTHAG',       'Iowa: Team WAR 38 vs 30; even Vegas only had Florida at ~85%'],
        ['Gonzaga: 3-seed, 1933 Elo',                      'Texas: Team WAR 86 vs 39, plus Gonzaga missing Huff (17.8 PPG)'],
        ['BYU: 6-seed, 1760 Elo',                          'Texas: Team WAR 86 vs 42, coach with 22 tourney wins'],
        ['Vanderbilt: 5-seed, 1873 Elo',                   'Nebraska: 4-seed (favored), better net efficiency\nand win rate - but lower WAR and fewer seniors'],
    ],
    title='What the Model Saw vs. What It Missed',
    filename='results/figures/22_model_saw_vs_missed_table.png',
    col_widths=[0.45, 0.50],
)
