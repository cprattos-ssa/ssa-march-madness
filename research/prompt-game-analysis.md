# Prompt for Claude Code: Day 1 Game-by-Game Analysis

Copy and paste everything below this line into a fresh Claude Code terminal opened in this repo (C:\dev\ssa-march-madness).

---

## Context

This is a March Madness 2026 prediction project built with Claude Code. We entered Kaggle's $50K March Machine Learning Mania competition. Our LightGBM model achieved 0.050 Brier score on cross-validation. Yesterday (March 19, 2026) was the first day of the tournament. We need a thorough analysis of every **men's tournament** game that was played, focused on what our model got right and wrong and WHY. This analysis is men's bracket only - ignore the women's tournament entirely.

## What Already Exists

The repo has a full ML pipeline. Key files you'll need:

- **Our predictions**: `data/processed/preds_lgbm.parquet` - columns: Season, TeamLow, TeamHigh, Pred (P(TeamLow wins))
- **Team IDs**: `data/raw/kaggle/MTeams.csv` - columns: TeamID, TeamName
- **2026 seeds**: `data/raw/kaggle/MNCAATourneySeeds.csv` - filter to Season=2026
- **Team features**: `data/processed/team_features.parquet` - 65 features per team-season including Elo, efficiency, SOS, seeds, coaching, Sundberg stats, and player-level features (Team_WAR, Star_WAR, WAR_Gini, Avg_ClassNum, etc.)
- **Player data**: `data/raw/external/player_data/barttorvik_players_2026.csv` - no header, col 0=Name, 1=School, 4=MinPct, 24=Usage, 29=Rating, 30=WAR, 25=Class, 26=Height, 64=Position
- **Our chalk bracket**: `results/bracket_chalk.txt` - our model's full bracket predictions
- **Injury analysis**: `results/injury_adjusted_predictions.txt` - injury-adjusted predictions we already computed
- **Team name mapping**: Use MTeams.csv + MTeamSpellings.csv. TeamIDs are integers (men's 1000-1999). Predictions are stored with the LOWER TeamID as TeamLow.

## Our Bracket Predictions (Round of 64)

Here's what our model predicted for every first-round game. The "Win Prob" is the model's confidence in the predicted winner:

```
(1) Duke def. (16) Siena (99.4%)
(2) Connecticut def. (15) Furman (98.1%)
(3) Michigan St def. (14) N Dakota St (95.0%)
(4) Kansas def. (13) Cal Baptist (90.9%)
(5) St John's def. (12) Northern Iowa (97.3%)
(11) South Florida def. (6) Louisville (65.8%) ** UPSET PICK **
(7) UCLA def. (10) UCF (96.1%)
(8) Ohio St def. (9) TCU (81.9%)
(1) Florida def. (16) Lehigh (99.3%)
(2) Houston def. (15) Idaho (98.2%)
(3) Illinois def. (14) Penn (92.7%)
(4) Nebraska def. (13) Troy (93.9%)
(5) Vanderbilt def. (12) McNeese St (87.5%)
(11) VCU def. (6) North Carolina (60.8%) ** UPSET PICK **
(7) St Mary's CA def. (10) Texas A&M (91.5%)
(8) Clemson def. (9) Iowa (79.7%)
(1) Michigan def. (16) UMBC (97.4%)
(2) Iowa St def. (15) Tennessee St (95.9%)
(3) Virginia def. (14) Wright St (97.1%)
(4) Alabama def. (13) Hofstra (85.7%)
(12) Akron def. (5) Texas Tech (72.7%) ** UPSET PICK **
(6) Tennessee def. (11) Miami OH (56.6%)
(10) Santa Clara def. (7) Kentucky (70.4%) ** UPSET PICK **
(9) St Louis def. (8) Georgia (63.7%) ** UPSET PICK **
(1) Arizona def. (16) LIU Brooklyn (99.1%)
(2) Purdue def. (15) Queens NC (93.7%)
(3) Gonzaga def. (14) Kennesaw (94.8%)
(4) Arkansas def. (13) Hawaii (97.1%)
(5) Wisconsin def. (12) High Point (95.7%)
(6) BYU def. (11) NC State (92.4%)
(7) Miami FL def. (10) Missouri (94.7%)
(9) Utah St def. (8) Villanova (94.3%) ** UPSET PICK **
```

Also First Four play-in games:
```
(16) Lehigh def. (16) Prairie View (76.5%)
(11) Miami OH def. (11) SMU (91.7%)
(16) UMBC def. (16) Howard (65.8%)
(11) NC State def. (11) Texas (68.9%)
```

## What We Already Know From Yesterday (partial results)

These games were confirmed during our earlier session:
- **TCU 66, Ohio State 64** - We predicted Ohio St at 81.9%. WRONG. 8v9 game, should have been closer to 50/50.
- **Nebraska 76, Troy 47** - We predicted Nebraska at 93.9%. CORRECT.
- **Louisville 66, South Florida 44** - We predicted South Florida at 65.8%. WRONG. Louisville won easily despite missing Mikel Brown Jr.
- **Wisconsin 52, High Point 48** - We predicted Wisconsin at 95.7%. CORRECT but the game was much closer than expected.

## Your Task

### Step 1: Get All Day 1 Results
Search the web for ALL March Madness first round results from March 19 AND March 20, 2026 (both days of first-round play). Get exact scores for every game. Also get First Four results from March 18-19.

### Step 2: Build the Full Scorecard
For EVERY game, create a comparison table:
- Game (seeds + teams)
- Our prediction (which team, what confidence %)
- Actual result (winner, score)
- Correct? (yes/no)
- Prediction error (how far off was our confidence?)
- Category: correct chalk, correct upset pick, missed upset, wrong upset pick

### Step 3: Deep Analysis of Games We Got WRONG
For each game we predicted incorrectly, do a thorough analysis:

1. **Look up both teams in our feature data** (`team_features.parquet` for 2026). Compare their Elo, efficiency (OffEff, DefEff, NetEff), SOS, seed features, and any player features (Team_WAR, Star_WAR, etc.).

2. **Check if our prediction was overconfident or just wrong direction**. An 82% prediction that loses is different from a 55% prediction that loses.

3. **Search the web for what actually happened in the game**. Look for:
   - Was there an injury we didn't account for?
   - Did a specific player have an outlier performance?
   - Was there a matchup problem (e.g., tempo mismatch, size mismatch)?
   - Did the game flow match what the stats predicted, or was it a fluky outcome?

4. **Check our player data** for both teams. Load `barttorvik_players_2026.csv` and look at the top players on each team. Did the underdog have a star player our team-level model missed?

5. **Was there public information available before the game** (injuries, suspensions, lineup changes) that could have adjusted our prediction?

6. **Categorize the miss**: Was it (a) a calibration error (predicted too confidently), (b) a missing data problem (injury/suspension we could have known about), (c) a genuine upset where the underdog overperformed, or (d) a systematic model blind spot?

### Step 4: Summary of Games We Got RIGHT
For games we predicted correctly, provide a brief analysis:
- Did the game play out as expected? (Score margin vs our confidence)
- Were there any close calls where we could have easily been wrong?
- Which correct predictions are we most proud of? (e.g., correctly picking upsets like VCU over UNC, Akron over Texas Tech)

### Step 5: Synthesize Findings
Produce a summary report that answers:
1. How many games did we get right vs wrong?
2. What was our overall Brier score for Day 1?
3. What were the common themes in our misses?
4. What data could we have incorporated to do better? (injuries, betting lines, momentum, etc.)
5. Which of our upset picks hit and which missed?
6. If we could go back, what would we change about the model?

### Step 6: Save Everything
- Save the full scorecard and analysis to `research/day1-game-analysis.md`
- Save any interesting visualizations to `results/figures/`

## Technical Notes

- Activate the virtual environment: `source .venv/Scripts/activate`
- Predictions use TeamLow/TeamHigh convention (lower TeamID first). Pred = P(TeamLow wins).
- To look up a prediction: find TeamIDs from MTeams.csv, compute min/max, filter preds_lgbm.parquet.
- Player data CSV has no header. Use positional column indices.
- The 2026 season is complete in all feature files.

## What This Is For

We're writing an article about building this prediction pipeline with Claude Code. The game-by-game analysis will be a key section showing where the model worked, where it failed, and what we learned. We want this to be honest and data-driven - not just "the model was bad" but specifically WHY each miss happened and whether it was preventable.
