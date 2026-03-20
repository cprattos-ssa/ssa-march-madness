# Phase 7: Player Data Integration & Injury Analysis

## Summary

We downloaded Barttorvik player-level data (30,066 players across 2021-2026, 67 columns each) and integrated 8 player-derived features into the prediction pipeline. Player features made the model WORSE (Brier 0.0544 vs 0.0503 baseline). This is consistent with the entire Kaggle competition history - no winning solution has ever used player data.

## Player Data Source

- **Barttorvik API**: `barttorvik.com/getadvstats.php?year={year}&csv=1`
- **Coverage**: ~5,000 players/year, 2021-2026
- **Key columns**: Name, School, Games, MinPct, eFGPct, Usage, Class, Height, Rating, WAR, OffRtg, DefRtg, Position
- **Match rate**: 99.3% of players matched to Kaggle TeamIDs via name normalization
- **Saved to**: `data/raw/external/player_data/barttorvik_players_{year}.csv`

## Features Engineered

8 team-level aggregations from player data, computed for teams with players having >=10% minutes and >=5 games:

| Feature | Description | Correlation with WoE |
|---------|-------------|---------------------|
| Team_WAR | Sum of all player WAR | -0.022 |
| Star_WAR | Top player's WAR | -0.047 |
| WAR_Gini | Gini coefficient of WAR distribution (roster balance) | +0.019 |
| Avg_ClassNum | Average class year (1=Fr, 4=Sr) | +0.028 |
| Star_Usage | Top player's usage rate | -0.074 |
| Top3_WAR | Sum of top 3 players' WAR | -0.100 |
| Avg_Height | Average roster height (inches) | -0.105 |
| Sr_Pct | Percentage of roster that are seniors | -0.011 |

All correlations are weak (|r| < 0.12). No player feature cracked the top 15 in LightGBM feature importance.

## Model Results

| Model | CV Brier | Change |
|-------|----------|--------|
| LightGBM (team only) | **0.0503** | Baseline |
| LightGBM + 8 player features | 0.0544 | +0.004 (WORSE) |
| XGBoost (team only) | 0.0536 | Unchanged |

Best LGBM+Player config: depth=3, lr=0.05, trees=300, leaves=8, colsample=0.8, min_child_samples=5

## Why Player Data Doesn't Help (Research Consensus)

### 1. Team efficiency already captures player contributions
When a star performs well, it shows up in per-possession efficiency metrics. KenPom AdjOE/AdjDE implicitly aggregate every player's contribution. Adding player inputs on top of team outputs is redundant.

### 2. Player-level stats are extremely noisy in college basketball
KenPom simulation: a player with ZERO actual impact still showed -5.7 pts/40min from random noise alone. College seasons are only ~30 games. Stars play nearly all non-garbage minutes so there's almost no comparison data.

### 3. Roster turnover destroys continuity
~2,000 players enter the transfer portal annually. Historical player-team associations are unstable, making it hard for models to learn stable patterns from player features.

### 4. Prediction ceiling effect
Multiple studies found accuracy concentrates at 65-80% regardless of whether features are player-derived or team-derived.

### 5. Consistent with Kaggle competition history
- **goto_conversion** ($47K prizes, 10+ gold medals): Zero player data. Converts betting odds with favorite-longshot bias correction.
- **maze508** (Top 1% Gold, 2023): External ratings + XGBoost. No player data.
- **Landgraf** (1st place, 2017): Meta-gaming strategy. No player features.
- **No documented winning solution has used player-level features.**

## Where Player Data DOES Add Value: Injury Adjustment

### 2026 Tournament Injuries - All Known Pre-Tournament

| Player | Team (Seed) | Injury | Date Public | Days Before Tournament |
|--------|-------------|--------|-------------|----------------------|
| Braden Huff | Gonzaga (3) | Dislocated kneecap | Jan 14 | 64 days |
| Richie Saunders | BYU (6) | Torn ACL | Feb 15 | 32 days |
| JT Toppin | Texas Tech (5) | Torn ACL | Feb 17 | 29 days |
| Mikel Brown Jr. | Louisville (6) | Back injury | Feb 28 | 19 days |
| Caleb Wilson | UNC (6) | Broken thumb | Mar 5 | 14 days |
| Caleb Foster | Duke (1) | Broken foot | Mar 7 | 12 days |
| Patrick Ngongba II | Duke (1) | Foot soreness | ~Mar 2 | 17 days |
| Aden Holloway | Alabama (4) | Arrested (marijuana) | Mar 16 | 3 days |

### Impact Quantification (via Barttorvik WAR)

| Matchup | Fav WAR (full) | Fav WAR (adjusted) | Underdog WAR | Adjusted Gap |
|---------|---------------|-------------------|--------------|-------------|
| UNC vs VCU | 30.3 | 27.9 (-Wilson) | 36.1 | **Underdog leads by 29%** |
| Duke vs Siena | 29.3 | 24.4 (-Foster, -Ngongba) | 26.3 | **Underdog leads by 8%** |
| Gonzaga vs Kennesaw | 38.7 | 34.8 (-Huff) | 46.7 | **Underdog leads by 34%** |
| Texas Tech vs Akron | 37.6 | 34.3 (-Toppin) | 32.5 | Gap narrows to 5% |
| BYU vs Texas | 42.1 | 39.3 (-Saunders) | 85.5* | Underdog dominant |
| Alabama vs Hofstra | 39.9* | 37.4* (-Holloway) | 35.2 | Gap narrows |

*Note: Some WAR totals inflated by large rosters. Relative comparisons still meaningful.

### Model Predictions vs Reality (First Round)

| Game | Model Prediction | Result | Player Data Would Have... |
|------|-----------------|--------|--------------------------|
| (8) Ohio St vs (9) TCU | Ohio St 81.9% | **TCU won 66-64** | Flagged TCU's better star players (Pierre 3.5, Punch 3.6 WAR vs Thornton 2.0) |
| (5) Wisconsin vs (12) High Point | Wisconsin 95.7% | Wisconsin won 52-48 | Flagged High Point had MORE team WAR (48.2 vs 39.7) |
| (6) Louisville vs (11) South Florida | Louisville 34.2% | **Louisville won 66-44** | N/A - model already picked USF (wrong) |
| (4) Nebraska vs (13) Troy | Nebraska 93.9% | Nebraska won 76-47 | Confirmed (no upset signal) |

### Injury Data Sources for Future Models

1. **NCAA PAReports** (ncaa.com/PAReports): New in 2026. Available/Questionable/Out posted night before + 2 hours before tip. No API.
2. **Barttorvik PRPG!**: Quantifies player value for "without player X" analysis. Free.
3. **EvanMiya**: Most direct injury-adjusted team ratings. Subscription required.
4. **Betting line movement**: Opening-to-closing spread differential as implicit injury signal. TeamRankings has 78K+ games since 2008.
5. **The Odds API**: Programmatic NCAA odds from ~2020. Paid API.

### NCAA Injury Reporting Rules (New 2026)
- Pilot program for 2026 D1 basketball championships only
- Players listed as Available (>75%), Questionable (<=75%), or Out
- Reports due: 9 PM night before + 2 hours before tip
- Published publicly at ncaa.com/PAReports
- Penalties: $10K-$30K for institutions, up to $10K for coaches (3rd offense)
- Conferences (Big Ten, SEC, ACC, Big 12, Big East) already require reports during conference play

## 2026 Field Insights from Player Data

### Most Underseeded by Talent (Team WAR much higher than seed suggests)
- Missouri (10): Team WAR 93.4 (highest in field)
- Tennessee (6): Team WAR 88.1
- Texas (11): Team WAR 85.5

### Most Overseeded by Talent
- Duke (1): Team WAR 29.3 (youngest roster, avg class 1.89, 4 freshmen)
- Arizona (1): Team WAR 25.1
- Nebraska (4): Team WAR 23.0

### Most Star-Dependent
- St. Louis (9): Top player = 12.5% of team WAR
- North Carolina (6): Top player = 10.9%
- Arizona (1): Top player = 10.4%

### Most Experienced
- Prairie View (16): Avg class 3.60, 7 seniors
- High Point (12): Avg class 3.36, 7 seniors
- Akron (12): Avg class 3.33, 5 seniors

## Key Takeaway

Player data adds no aggregate predictive value over team-level efficiency metrics. The one clear exception is injury adjustment - when a key player is missing, team-level season stats are stale and player WAR enables re-estimation of team strength. All 2026 tournament injuries were public 3-64 days before tip-off, making this actionable for pre-tournament models.

The frontier of March Madness prediction isn't more features - it's knowing when your features are stale.
