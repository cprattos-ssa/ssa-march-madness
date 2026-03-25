# Article Draft Notes

## Folder Contents
- `draft.md` - The publishable article (~1,250 words)
- `outline.md` - Original structural outline with options for each section
- `notes.md` - This file (research validation, visual index, decisions log)
- `visual-1-pipeline-overview.png` - Clean 5-stage pipeline diagram (Part 1)
- `visual-1b-session2-flowchart.png` - Session 2 post-mortem flowchart showing the player data experiment (Part 2)
- `visual-2-war-scatter.png` - Team WAR vs Tournament Wins (r=0.037, verified)
- `visual-3-day1-accuracy.png` - Model confidence vs outcomes, 16 games (verified)
- `visual-4-feature-comparison.png` - Feature comparison for 3 biggest misses (verified)
- `visual-1-process-infographic.png` - Original full process infographic (archived, too large for article)

## Visual Verification (2026-03-20)
All data-driven visuals regenerated from source parquet files and cross-checked:

| Visual | Data Source | Verification |
|--------|-----------|-------------|
| Process infographic | Design asset | Factual claims (101 files, 57 features, 5 models) verified against phase reports |
| WAR scatter | team_features.parquet + MNCAATourneyCompactResults.csv | CORRECTED: r=0.037 (original incorrectly showed r=0.001 due to duplicate rows). n=337, 2021-2025, deduplicated |
| Day 1 accuracy | preds_lgbm.parquet + verified game results | All 16 P(winner) values and Brier scores match parquet. All game results confirmed via ESPN, Yahoo Sports, CBS Sports, On3 |
| Feature comparison | team_features.parquet | All 18 values (6 metrics x 3 games) verified against parquet. Improved to 2-decimal precision for ratios |

## Research Validation
Every factual claim in the article has been validated:

| Claim | Source | Status |
|-------|--------|--------|
| More features can hurt performance | Hughes phenomenon (1968), 2025 ACM "Less Is More" paper | Validated |
| ~100 games needed for reliable individual stats | Gomez et al. 2019, Research Quarterly for Exercise and Sport | Validated, linked |
| No Kaggle winner used player data | goto_conversion docs, ArunkumarRamanan writeup, competition history | Validated |
| goto_conversion: $47K+, no ML | GitHub repo, Kaggle profile | Validated |
| Probability clipping [0.025, 0.975] | ArunkumarRamanan 1st place 2019 writeup | Validated |
| Brier ceiling 0.04-0.06 | Matthews & Lopez 2014 paper, competition leaderboards | Validated |
| Team efficiency captures player contributions | KenPom methodology docs | Validated |
| r=0.037 for WAR vs tournament wins | Computed from deduplicated data, 337 points | Verified |
| LightGBM 0.050 vs XGBoost 0.054 vs NN 0.115 | phase4-model-training-report.md | Verified |
| All 16 game scores | ESPN, Yahoo Sports, CBS Sports, On3, NBC News | Cross-referenced |
| Duke injury details (Foster, Ngongba) | injury_adjusted_predictions.txt, web sources | Verified |
| VCU 19-point comeback, largest first-round ever | ESPN, Yahoo Sports | Verified |
| Chase Johnston 0-for-season on 2-pointers | CBS Sports, ESPN, Yahoo Sports | Verified |

## V2 to V3 Key Changes
- Reframed Claude Code as a tool we used, not the protagonist. Mentioned once in Part 1 as an accelerant, not repeated throughout
- Replaced "The AI builds the pipeline. The analyst asks the right questions." closer with a more earned, personal conclusion about blind spots and knowing which predictions to trust
- Added more personal voice: "Our kind of problem," "Those felt very good," Jackson Pollock joke for the scatter plot
- Removed #ClaudeCode from hashtags to avoid looking like a product placement
- Restructured Part 1 to lead with the decisions and learnings, not the tool
- Changed "The Closer" header to "The Takeaway" (less formulaic)
- Softened business parallel: "How many of us have been in a version of this situation?" (self-inclusive)
- Added ellipses for pacing in two spots per SSA style
- Connected more clauses into compound sentences throughout
- Made the intro arc toward the conclusion (thesis planted: more data doesn't always help)
