#!/usr/bin/env python3
"""
Simulate NCAA Men's March Madness brackets using model predictions.

Generates two brackets:
  1. Chalk — always pick the favorite using LightGBM predictions
  2. Upset-Aware Monte Carlo — 10K sims with ensemble predictions,
     pick upsets where underdog wins slot >30% of the time

Usage:
    python scripts/simulate_brackets.py
"""

import argparse
import csv
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw" / "kaggle"
SUB_DIR = DATA_DIR / "submissions"
RESULTS_DIR = BASE_DIR / "results"

SEEDS_PATH = RAW_DIR / "MNCAATourneySeeds.csv"
SLOTS_PATH = RAW_DIR / "MNCAATourneySlots.csv"
TEAMS_PATH = RAW_DIR / "MTeams.csv"
LGBM_PATH = SUB_DIR / "submission_lgbm.csv"
ENSEMBLE_PATH = SUB_DIR / "submission_ensemble.csv"

SEASON = 2026
NUM_SIMS = 10_000
FAVORITE_THRESHOLD = 0.70  # favorite must win slot >70% to be auto-picked
UPSET_THRESHOLD = 0.30     # underdog wins slot >30% -> pick the upset

ROUND_NAMES = {
    0: "First Four (Play-In)",
    1: "Round of 64",
    2: "Round of 32",
    3: "Sweet 16",
    4: "Elite 8",
    5: "Final Four",
    6: "Championship",
}

REGION_NAMES = {"W": "West", "X": "East", "Y": "South", "Z": "Midwest"}

# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_teams(path):
    """Return {TeamID: TeamName}."""
    teams = {}
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            teams[int(row["TeamID"])] = row["TeamName"]
    return teams


def load_seeds(path, season):
    """Return {Seed: TeamID} for the given season."""
    seeds = {}
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            if int(row["Season"]) == season:
                seeds[row["Seed"]] = int(row["TeamID"])
    return seeds


def load_slots(path, season):
    """Return list of (Slot, StrongSeed, WeakSeed) for the given season."""
    slots = []
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            if int(row["Season"]) == season:
                slots.append((row["Slot"], row["StrongSeed"], row["WeakSeed"]))
    return slots


def load_predictions(path, season):
    """Return {(TeamIdLow, TeamIdHigh): P(low wins)} for the given season."""
    preds = {}
    prefix = f"{season}_"
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            if row["ID"].startswith(prefix):
                parts = row["ID"].split("_")
                t1, t2 = int(parts[1]), int(parts[2])
                preds[(t1, t2)] = float(row["Pred"])
    return preds


def get_prob(preds, team_a, team_b):
    """Return P(team_a beats team_b)."""
    if team_a == team_b:
        return 0.5
    lo, hi = min(team_a, team_b), max(team_a, team_b)
    p_lo = preds.get((lo, hi), 0.5)
    return p_lo if team_a == lo else 1.0 - p_lo


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def slot_round(slot_name):
    """R1W1 -> 1, R6CH -> 6, play-in slots (X16, Y11) -> 0."""
    if slot_name.startswith("R"):
        return int(slot_name[1])
    return 0


def seed_number(seed_str):
    """'W01' -> 1, 'X16a' -> 16."""
    return int(seed_str[1:].rstrip("ab"))


def seed_region(seed_str):
    return seed_str[0]


def order_slots(slots):
    """Sort so play-in games come first, then R1 through R6."""
    return sorted(slots, key=lambda s: (slot_round(s[0]), s[0]))


def team_label(teams, seeds, team_id):
    """Return '(1) Duke' style label."""
    name = teams.get(team_id, f"Team{team_id}")
    for seed_str, tid in seeds.items():
        if tid == team_id:
            return f"({seed_number(seed_str)}) {name}"
    return name


def find_seed_for_team(seeds, team_id):
    """Return seed string for a team, or None."""
    for s, tid in seeds.items():
        if tid == team_id:
            return s
    return None


def is_upset(seeds, winner, loser):
    """Higher seed number beating lower seed number."""
    ws = find_seed_for_team(seeds, winner)
    ls = find_seed_for_team(seeds, loser)
    if ws and ls:
        return seed_number(ws) > seed_number(ls)
    return False


# ---------------------------------------------------------------------------
# Bracket 1: Chalk
# ---------------------------------------------------------------------------

def simulate_chalk(slots, seeds, preds):
    """Always pick the favorite. Returns (results_list, slot_winners)."""
    ordered = order_slots(slots)
    slot_winners = {}
    results = []

    for slot, strong, weak in ordered:
        team_a = seeds.get(strong) or slot_winners.get(strong)
        team_b = seeds.get(weak) or slot_winners.get(weak)
        if team_a is None or team_b is None:
            continue

        p_a = get_prob(preds, team_a, team_b)
        if p_a >= 0.5:
            winner, win_prob = team_a, p_a
        else:
            winner, win_prob = team_b, 1.0 - p_a

        slot_winners[slot] = winner
        loser = team_b if winner == team_a else team_a
        results.append((slot, winner, loser, win_prob))

    return results, slot_winners


# ---------------------------------------------------------------------------
# Bracket 2: Upset-Aware Monte Carlo
# ---------------------------------------------------------------------------

def simulate_monte_carlo(slots, seeds, preds, n_sims=NUM_SIMS):
    """
    Run n_sims Monte Carlo tournament simulations.
    For each slot, track how often each team wins it.
    Then build a bracket:
      - If favorite wins slot >70%, pick favorite
      - If underdog wins slot >30%, pick underdog
      - Otherwise pick the team that wins most often
    """
    ordered = order_slots(slots)
    rng = np.random.default_rng(42)

    # Track wins per slot per team
    slot_team_counts = defaultdict(Counter)

    for _ in range(n_sims):
        sw = {}
        for slot, strong, weak in ordered:
            ta = seeds.get(strong) or sw.get(strong)
            tb = seeds.get(weak) or sw.get(weak)
            if ta is None or tb is None:
                continue
            p_a = get_prob(preds, ta, tb)
            sw[slot] = ta if rng.random() < p_a else tb
            slot_team_counts[slot][sw[slot]] += 1

    # Build the actual bracket using upset-aware logic
    slot_winners = {}
    results = []

    for slot, strong, weak in ordered:
        team_a = seeds.get(strong) or slot_winners.get(strong)
        team_b = seeds.get(weak) or slot_winners.get(weak)
        if team_a is None or team_b is None:
            continue

        counts = slot_team_counts[slot]
        total = counts[team_a] + counts[team_b]
        if total == 0:
            total = 1

        p_a = get_prob(preds, team_a, team_b)

        # Determine favorite vs underdog by model probability
        if p_a >= 0.5:
            fav, dog = team_a, team_b
        else:
            fav, dog = team_b, team_a

        fav_frac = counts[fav] / total
        dog_frac = counts[dog] / total

        # Upset-aware pick
        if fav_frac > FAVORITE_THRESHOLD:
            winner = fav
        elif dog_frac > UPSET_THRESHOLD:
            winner = dog
        else:
            winner = fav if fav_frac >= dog_frac else dog

        slot_winners[slot] = winner
        loser = team_b if winner == team_a else team_a
        mc_pct = counts[winner] / total
        results.append((slot, winner, loser, mc_pct))

    return results, slot_winners, slot_team_counts


# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------

def format_bracket(results, seeds, teams, title, prob_label="Win Prob"):
    """Format bracket results as a string for display and file output."""
    lines = []
    lines.append("=" * 90)
    lines.append(f"  {title}")
    lines.append("=" * 90)

    current_round = None
    upsets = []

    for slot, winner, loser, prob in results:
        rnd = slot_round(slot)
        rnd_name = ROUND_NAMES.get(rnd, f"Round {rnd}")
        if rnd_name != current_round:
            current_round = rnd_name
            lines.append(f"\n--- {rnd_name} ---")

        w_label = team_label(teams, seeds, winner)
        l_label = team_label(teams, seeds, loser)
        upset_flag = ""
        if is_upset(seeds, winner, loser):
            upset_flag = "  ** UPSET **"
            ws = find_seed_for_team(seeds, winner)
            ls = find_seed_for_team(seeds, loser)
            upsets.append((rnd_name, w_label, seed_number(ws) if ws else 99,
                           l_label, seed_number(ls) if ls else 99, prob))

        lines.append(
            f"  {slot:8s}  {w_label:>28s}  def.  {l_label:<28s}  "
            f"({prob_label}: {prob:.1%}){upset_flag}"
        )

    # Champion
    champ_entries = [r for r in results if r[0] == "R6CH"]
    if champ_entries:
        _, champ, _, prob = champ_entries[0]
        champ_label = team_label(teams, seeds, champ)
        lines.append("")
        lines.append("*" * 60)
        lines.append(f"  CHAMPION:  {champ_label}")
        lines.append("*" * 60)

    # Upsets summary
    if upsets:
        lines.append("")
        lines.append("--- Key Upsets ---")
        for rnd_name, w_label, w_num, l_label, l_num, prob in upsets:
            lines.append(f"  {rnd_name:>18s}:  {w_label}  over  {l_label}  ({prob:.1%})")
    else:
        lines.append("\nNo upsets in this bracket (pure chalk).")

    lines.append("")
    return "\n".join(lines)


def format_mc_stats(slot_team_counts, seeds, teams, n_sims):
    """Format Monte Carlo championship and Final Four stats."""
    lines = []
    lines.append("")
    lines.append("-" * 90)
    lines.append(f"  Monte Carlo Simulation Statistics ({n_sims:,} simulations)")
    lines.append("-" * 90)

    # Championship winner distribution
    champ = slot_team_counts.get("R6CH", Counter())
    total = sum(champ.values())
    if total > 0:
        lines.append("\n  Championship Win Probability (top 10):")
        for tid, cnt in champ.most_common(10):
            lines.append(f"    {team_label(teams, seeds, tid):>30s}:  {cnt/total:.1%}")

    # Final Four appearance rates
    ff_slots = ["R4W1", "R4X1", "R4Y1", "R4Z1"]
    ff_counts = Counter()
    for sl in ff_slots:
        for tid, cnt in slot_team_counts.get(sl, Counter()).items():
            ff_counts[tid] += cnt
    if ff_counts:
        lines.append("\n  Final Four Appearance Rates (top 12):")
        for tid, cnt in ff_counts.most_common(12):
            lines.append(f"    {team_label(teams, seeds, tid):>30s}:  {cnt/n_sims:.1%}")

    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Simulate March Madness brackets")
    parser.add_argument("--season", type=int, default=SEASON)
    parser.add_argument("--sims", type=int, default=NUM_SIMS)
    args = parser.parse_args()

    season = args.season
    n_sims = args.sims

    print(f"Loading data for {season} season...")
    teams = load_teams(TEAMS_PATH)
    seeds = load_seeds(SEEDS_PATH, season)
    slots = load_slots(SLOTS_PATH, season)
    lgbm_preds = load_predictions(LGBM_PATH, season)
    ensemble_preds = load_predictions(ENSEMBLE_PATH, season)

    print(f"  {len(seeds)} seeds, {len(slots)} slots")
    print(f"  {len(lgbm_preds)} LightGBM predictions, {len(ensemble_preds)} ensemble predictions")

    # -------------------------------------------------------------------
    # Bracket 1: Chalk (LightGBM)
    # -------------------------------------------------------------------
    print("\nSimulating Bracket 1 (Chalk / LightGBM)...")
    chalk_results, chalk_winners = simulate_chalk(slots, seeds, lgbm_preds)
    chalk_text = format_bracket(chalk_results, seeds, teams,
                                "BRACKET 1: CHALK (LightGBM — always pick the favorite)",
                                "Win Prob")
    print(chalk_text)

    # -------------------------------------------------------------------
    # Bracket 2: Upset-Aware Monte Carlo (Ensemble)
    # -------------------------------------------------------------------
    print(f"\nSimulating Bracket 2 (Upset-Aware Monte Carlo, {n_sims:,} sims, Ensemble)...")
    mc_results, mc_winners, mc_counts = simulate_monte_carlo(
        slots, seeds, ensemble_preds, n_sims
    )
    mc_text = format_bracket(mc_results, seeds, teams,
                             f"BRACKET 2: UPSET-AWARE MONTE CARLO (Ensemble, {n_sims:,} sims)",
                             "MC Win%")
    print(mc_text)

    # MC statistics
    mc_stats = format_mc_stats(mc_counts, seeds, teams, n_sims)
    print(mc_stats)

    # -------------------------------------------------------------------
    # Side-by-side comparison of late-round picks
    # -------------------------------------------------------------------
    print("=" * 90)
    print("  SIDE-BY-SIDE: LATE-ROUND COMPARISON")
    print("=" * 90)
    key_slots = ["R4W1", "R4X1", "R4Y1", "R4Z1", "R5WX", "R5YZ", "R6CH"]
    labels = {
        "R4W1": "Elite 8 - West",
        "R4X1": "Elite 8 - East",
        "R4Y1": "Elite 8 - South",
        "R4Z1": "Elite 8 - Midwest",
        "R5WX": "Final Four (W/E)",
        "R5YZ": "Final Four (S/MW)",
        "R6CH": "CHAMPION",
    }
    for sl in key_slots:
        ct = chalk_winners.get(sl)
        mt = mc_winners.get(sl)
        if ct and mt:
            cl = team_label(teams, seeds, ct)
            ml = team_label(teams, seeds, mt)
            diff = "  <-- DIFFERENT" if ct != mt else ""
            print(f"  {labels[sl]:>22s}:  Chalk: {cl:>25s}  |  MC: {ml:<25s}{diff}")

    print()

    # -------------------------------------------------------------------
    # Save to files
    # -------------------------------------------------------------------
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    chalk_path = RESULTS_DIR / "bracket_chalk.txt"
    mc_path = RESULTS_DIR / "bracket_monte_carlo.txt"

    with open(chalk_path, "w") as f:
        f.write(chalk_text)
    print(f"Saved: {chalk_path}")

    with open(mc_path, "w") as f:
        f.write(mc_text + "\n" + mc_stats)
    print(f"Saved: {mc_path}")


if __name__ == "__main__":
    main()
