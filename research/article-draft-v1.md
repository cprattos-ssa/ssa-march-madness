# We Added 30,000 Player Records to Our March Madness Model. It Got Worse.

Every March, millions of people fill out brackets with some combination of gut feel, school loyalty, and whatever ESPN told them to think. We wanted to do it with data. So we entered Kaggle's $50K March Machine Learning Mania competition, built a full prediction pipeline, trained five models, generated a bracket, and submitted our predictions before the first tip-off. And then we did what every data person eventually does: we went looking for more data, convinced that if we could just capture who was actually on each roster, their individual talent, their experience, we'd unlock something the team-level stats were missing.

We downloaded 30,000 player records. Engineered eight new features. Reran the full pipeline.

The model got worse. Across every configuration. And the tournament's first day proved it in ways we didn't expect.

*A quick note on methodology: the Kaggle competition evaluates predictions on **Brier score**, a calibration metric that punishes overconfidence quadratically. Predict 95% and get it wrong, and you pay roughly 20x the penalty of predicting 55% and getting it wrong. Everything below reflects real predictions submitted before tipoff, scored against real tournament results.*

---

## Part 1: What We Built

Here's the context. Last year, building a tournament prediction model took two to three weeks of data engineering, feature selection, model training, and tuning. This year, we used **Claude Code** (Anthropic's AI coding agent) to build the entire pipeline in a single working session, with a second session for the post-mortem analysis and player data experiment.

What the pipeline produced: 101 data files ingested from four sources (Kaggle historical data, KenPom-equivalent efficiency metrics, Barttorvik player stats, and coaching records), 57 features engineered per team-season covering Elo ratings, offensive and defensive efficiency, strength of schedule, four factors, seed transformations, and coaching tournament history, and five model architectures trained and compared (logistic regression, Bradley-Terry, XGBoost, LightGBM, and a neural network). Over 40 AI agents ran in parallel across the two sessions, handling everything from data cleaning to hyperparameter sweeps to generating publication-quality visualizations.

The result: a **LightGBM** model with a cross-validated Brier score of 0.050, which is competitive with the Kaggle leaderboard. For context, the realistic performance ceiling on this competition sits around 0.04 to 0.06, and the most successful competitor in the competition's history (over $47,000 in prizes, 10+ gold medals) doesn't use machine learning at all. They just convert betting odds to probabilities with a 10-line bias correction. That's it. We built an entire pipeline and they beat us with arithmetic.

**[VISUAL: Process infographic showing pipeline stages and parallel agent orchestration]**

---

## Part 2: The Player Data Experiment

So we had a competitive model, and the natural instinct kicked in: individual players win games. If you could capture who's actually on each roster, their **WAR** (Wins Above Replacement, a cumulative value metric), their experience level, how dependent the team is on one star player, surely that gives you an edge the team-level aggregates miss.

We pulled 30,000 player records from Barttorvik spanning six seasons and engineered eight team-level features: total roster WAR, best player's WAR, star usage rate, experience mix (average class year, senior percentage), roster height, and a WAR concentration metric measuring star dependency. We matched 99.3% of players to their Kaggle team IDs and reran the full model pipeline across 30 configurations.

The Brier score went from 0.0503 to 0.0544. Not one configuration improved. Every player feature had a correlation with tournament outcomes below r = 0.12, and not one cracked the top 15 in feature importance. We plotted total roster WAR against tournament wins across five years of data and got ... a cloud (r = 0.037). No relationship whatsoever.

The reason sounds obvious in retrospect but wasn't obvious when we started: team efficiency metrics already capture what players do. When your best player scores 25 on good efficiency, that shows up in offensive rating, eFG%, and adjusted offensive efficiency. The player stat is redundant with the team stat, except noisier, because individual college basketball statistics are spectacularly unreliable. [Research has shown](https://pubmed.ncbi.nlm.nih.gov/31046653/) that you need approximately 100 games for individual stats to stabilize to reliable estimates, and a college season is only 30 to 35 games. The noise floor is enormous.

And here's the fact that would have saved us the trouble: no winning Kaggle March Madness solution has ever used player-level data. The most successful competitor uses zero ML and zero player features. Sometimes the most sophisticated answer to "should we add more data?" is just … no.

**[VISUAL: Team WAR vs. Tournament Wins scatter plot (r=0.037, 2021-2025). Caption: "We expected a correlation. We got a cloud."]**

---

## Part 3: The Scorecard

Then the tournament started, and we got to find out how the model actually performed against real games.

Thursday's first round: **11 out of 16 correct (68.8%)**. Every chalk pick we made hit (9 for 9), and two of our three upset picks landed. We called VCU over North Carolina at 60.8% confidence, and VCU completed the largest first-round comeback in tournament history, rallying from 19 points down to win in overtime behind Terrence Hill Jr.'s career-high 34 points. We called St. Louis over Georgia at 63.7%, and St. Louis won by 25. Those felt good.

And then there were the three games that wrecked us:

| Game | Our Prediction | What Actually Happened | Brier |
|------|---------------|----------------------|-------|
| (12) High Point 83, (5) Wisconsin 82 | Wisconsin wins, 95.7% | Chase Johnston's fastbreak layup with 11.2 sec left | 0.916 |
| (10) Texas A&M 63, (7) St. Mary's 50 | St. Mary's wins, 91.5% | A&M led wire-to-wire, held StM to season-low 50 pts | 0.838 |
| (11) Texas 79, (6) BYU 71 | BYU wins, 92.4% | Texas dominated despite Dybantsa's 35-point farewell | 0.779 |

Three games, all predicted at 90%+ confidence for the wrong team, and together they accounted for 64% of our total prediction error across all 16 games. On Brier score, being confidently wrong is catastrophic, and we were exactly that.

**[VISUAL: Prediction accuracy chart, model confidence per game, green for correct picks, red for wrong]**

---

## Part 4: Why the Model Missed (and the Irony)

The fascinating thing about these three upsets is that they weren't random. They shared a pattern.

In all three cases, the team that won had more experienced players (64%, 58%, and 52% seniors respectively, vs. 30%, 10%, and 18% for our picks), higher total roster WAR, and in High Point's case, *better* net efficiency than Wisconsin (20.2 vs 10.0) along with a better win percentage (87% vs 71%). Texas brought a coaching staff with 22 tournament wins to BYU's two.

But our model saw Wisconsin's 5-seed and 1825 Elo. It saw St. Mary's 27-6 record and 1869 Elo, inflated by a lighter WCC schedule. It saw BYU's 6-seed. And it treated those signals as near-certainties.

| What the Model Saw | What It Missed |
|----|-----|
| Wisconsin: 5-seed, 1825 Elo, 0.93 BARTHAG | High Point: 20.2 net efficiency (vs 10.0), 64% seniors, better win rate |
| St. Mary's: 27-6 record, 1869 Elo | Texas A&M: 58% seniors, Team WAR 50.4 vs 34.8, SEC-tested |
| BYU: 6-seed, 1760 Elo | Texas: Team WAR 85.5 vs 42.1, coach with 22 tourney wins vs 2 |

Which brings us to the irony at the heart of this whole project. The player-derived features that made our aggregate model worse (Team WAR, senior percentage, experience metrics) are exactly the features that would have flagged all three of these upsets. They don't improve predictions across 1,400 historical tournament games because the signal is already captured in team efficiency stats. But in the 3 or 4 games per year where the model is most dangerously overconfident, they're precisely what's missing. The aggregate model doesn't need them. The edge cases desperately do.

We also missed a technical step that winning Kaggle solutions consistently use: **probability clipping**. Past winners cap their predictions at a floor and ceiling (typically 2.5% and 97.5%) so that no single wrong pick generates a catastrophic Brier penalty. Our model was outputting 95.7% and 99.4% without guardrails, and even basic clipping would have limited our downside on these misses. Lesson learned.

**[VISUAL: Feature comparison chart for the three biggest misses, Elo favored our pick but WAR, experience, and efficiency favored the actual winner]**

---

## Part 5: The One Insight Nobody Talks About

One more thing that stuck with us, and it's the one that translates most directly outside of basketball.

Eight players in the 2026 tournament field were injured or ruled out before the bracket was even set. Every announcement was public, reported by beat writers and team accounts anywhere from 3 to 64 days before tipoff. Our model had no idea.

Duke was listed at 99.4% to beat Siena, but Duke was missing Caleb Foster (broken foot, announced March 7) and Patrick Ngongba (foot fracture, announced March 2), together representing 26% of their roster's total WAR. When we manually adjusted for their absence, the prediction dropped to 86.6%, a 13-point swing. Duke won that game by 6 and trailed by 13 in the second half. The injury-adjusted number was much closer to the truth.

This is the one place where player data genuinely matters: not as a model feature, but as a real-time correction to stale team-level stats. When a key player goes down, the team's season-long averages become a lagging indicator, and you need the individual-level data to re-estimate what the remaining roster can actually do.

The business parallel writes itself. How many of us are reporting last quarter's metrics as though they still reflect today's reality? Stale data isn't an analytics inconvenience. It's a blind spot, and it tends to show up at exactly the moment the stakes are highest.

---

## The Closer

Claude Code built a pipeline in hours that used to take weeks. It trained five models, generated 19 visualizations, and predicted 132,000 matchups. It also gave Wisconsin a 96% chance of beating a 12-seed that outperformed them in almost every metric that mattered. The game-winning basket came from Chase Johnston, a bench player who hadn't made a two-point field goal all season. His first one ended Wisconsin's tournament with 11 seconds left.

The AI builds the pipeline. The analyst asks the right questions.

Thanks for reading! The full technical breakdown, code, and game-by-game analysis are all on our GitHub. And if your team is sitting on data and isn't sure what to do with it, that's literally what we do. Let's connect!

#MarchMadness #DataScience #MachineLearning #AI #Analytics #ClaudeCode

---

*Built by [South Shore Analytics](https://www.southshoreanalytics.com) using Claude Code. March Madness 2026.*

---

## DRAFT NOTES (not for publication)

### Visuals (4 total, all regenerated and verified 2026-03-20):
1. **Process infographic** (Part 1) - `results/ss_full_final.png` - factual claims verified
2. **Team WAR scatter** (Part 2) - `results/figures/11_team_war_vs_tourney.png` - CORRECTED: r=0.037 (was 0.001), n=337, 2021-2025
3. **Day 1 prediction accuracy** (Part 3) - `results/figures/16_day1_prediction_accuracy.png` - all 16 values verified against parquet + web sources
4. **Feature comparison for misses** (Part 4) - `results/figures/17_day1_wrong_picks_features.png` - all values verified against team_features.parquet, improved to 2-decimal precision

### Research validation notes:
- "More features isn't always better" - Validated: Hughes phenomenon (1968), curse of dimensionality, 2025 ACM paper ("Less Is More"). Textbook ML.
- "Player stats too noisy" - Validated: Gomez et al. (2019, Research Quarterly for Exercise and Sport) shows ~100 games needed for reliable individual stats. College seasons are 30-35 games.
- "No winning solution used player data" - Validated: goto_conversion ($47K+ prizes) uses no ML, no player features. No documented Kaggle winner used player-level data.
- "Probability clipping" - Validated: ArunkumarRamanan (1st place 2019) clipped to [0.025, 0.975]. Standard practice.
- "Prediction ceiling 0.04-0.06" - Validated: Matthews and Lopez (2014 winners) published paper showing luck is a significant factor.
- "Team efficiency captures player contributions" - Validated: KenPom AdjOE/AdjDE implicitly aggregate all player contributions.
- "r=0.037 for WAR vs tournament wins" - Verified: 337 data points, 2021-2025, deduplicated. Original figure incorrectly showed r=0.001 due to data duplication bug.

### V1 → V2 changelog:
- Fixed r=0.001 → r=0.037 (data verification caught duplication bug in original figure)
- Warmer intro: added opening sentence that sets personal context before diving into Kaggle
- Bolded key terms on first use (Brier score, Claude Code, LightGBM, WAR, probability clipping) per SSA guide
- Connected staccato sentences into compound structures throughout
- Added connective tissue between sections ("The fascinating thing about..." / "Which brings us to...")
- Softened business parallel framing from "How many dashboards are reporting..." to "How many of us are reporting..." (inclusive, not accusatory)
- Added hyperlink to Gomez et al. research citation for 100-game reliability claim
- Removed "More on that in a minute" tease that didn't pay off cleanly
- Strengthened goto_conversion mention ("We built an entire pipeline and they beat us with arithmetic")
- Named Chase Johnston in the closer (concrete > generic, per SSA guide)
- Added exclamation to CTA closer per SSA guide ("Let's connect!")
- Tightened Part 3 header (removed parenthetical "Tournament Day 1")
- Improved flow in Part 1: connected feature list as one compound sentence instead of four fragments

### Open decisions for Nick:
- **Title**: Current working title is the pitch #3 headline. Alternatives still available.
- **Length**: ~1,200 words (within 800-1,500 target).
- **Friday results**: Draft uses Thursday-only data (16 games). Can update when Friday results are final.
- **Tone check**: Does the business parallel in Part 5 (stale dashboards) feel natural or forced?
- **goto_conversion detail**: Currently a brief mention. The "10 lines of Python, $47K in prizes" fact is great but could distract from our story.
