# Article Outline: Option A - "The Experiment"

**Working title options:**
1. "We Added 30,000 Player Records to Our March Madness Model. It Got Worse."
2. "We Built a March Madness Model in One Session. Here's What It Got Right (and Very Wrong)."
3. "Our AI-Built March Madness Model Was 96% Sure About Wisconsin. A Guy Who'd Never Made a 2-Pointer Ended Their Season."

**Target length:** 1,000-1,200 words (newsletter/LinkedIn sweet spot)
**Target publish:** While tournament is still live (this week)
**Format:** LinkedIn article or newsletter

---

## SECTION 1: The Hook (~100-150 words)

**Goal:** Plant the thesis with a specific, concrete image. Set up the contrarian premise.

**Option 1A: Lead with the player data paradox (pitch #3 headline)**
Open with: "We added 30,000 player records to our March Madness prediction model. It got worse." Then immediately pull the reader in: you'd think more data helps. We thought so too. We were wrong, and the tournament's first day proved it in ways we didn't expect.

**Option 1B: Lead with the High Point story (the emotional gut-punch)**
Open with Chase Johnston's game-winning layup: a bench player who hadn't made a two-point basket all season hits a fastbreak layup with 11 seconds left to knock off a 5-seed. Our model gave Wisconsin 95.7%. March Madness doesn't care about your model.

**Option 1C: Lead with the speed contrast (the process story)**
Open with: "Last year, building a tournament prediction model took me two to three weeks. This year, an AI coding agent did it in one working session." Then tease: the interesting part isn't that it worked. The interesting part is how it broke.

**Recommendation:** 1A. The headline does the heavy lifting and it's the most SSA-voice move (contrarian data claim). 1B is the most engaging story but buries the thesis. 1C is the most "AI content" but could feel like a product pitch.

*Style note: Include a brief methodology aside early, per SSA pattern. Something like: "A quick note on methodology: we entered Kaggle's $50K March Machine Learning Mania competition, which evaluates predictions on Brier score (a calibration metric that punishes overconfidence). Everything below is real predictions made before tipoff, scored against real results."*

---

## SECTION 2: What We Built (~150-200 words)

**Goal:** Establish credibility and the Claude Code speed story. This is the "wow" section but keep it tight. Not a product pitch, just context for why the experiment matters.

**Key beats to hit:**
- The challenge: Kaggle's $50K March Madness competition, predict every possible matchup
- The old way: 2-3 weeks of manual data engineering, feature selection, model tuning
- The new way: Claude Code built the full pipeline in one working session
- The stat line (pick 3-4, don't list everything):
  - 101 data files ingested from 4 sources
  - 57 features engineered (Elo, efficiency, strength of schedule, coaching history)
  - 5 model architectures trained and compared
  - 40+ parallel AI agents working simultaneously
- The result: LightGBM model, 0.050 Brier score on cross-validation (competitive with Kaggle leaderboard)

**Tone:** Matter-of-fact, not breathless. "Here's what it built" not "Look how amazing this is." Let the numbers speak.

**Transition to next section:** Something like "The model was good. So naturally, we tried to make it better." or "So we had a working model. And then we did what every data person does: we went looking for more data."

**Visual: Process Infographic**
Use the existing `ss_full_final.png` process visual showing the pipeline stages and agent orchestration. This is the money shot for the "how we built it" story. Alternatively, a simplified version showing: Data (101 files) -> Features (57) -> Models (5) -> Predictions -> Bracket.

---

## SECTION 3: The Player Data Experiment (~200-250 words)

**Goal:** This is the thesis section. The contrarian claim, the evidence, the business lesson. Should feel like a detective story: hypothesis, test, surprise, explanation.

**The narrative arc:**
1. The hypothesis: "Individual players win games. If we could capture who's actually on each roster, their talent levels, their experience, we'd have an edge the team-level stats miss."
2. What we did: Downloaded 30,000 player records across 6 seasons from Barttorvik. Engineered 8 new features (Team WAR, star player talent, experience mix, height, star dependency).
3. The result: Brier score went from 0.0503 to 0.0544. Worse across every model configuration.
4. Why: Team efficiency metrics already capture what players do in aggregate. And player stats in college basketball are spectacularly noisy. (This is where you drop the KenPom finding: "A player with literally zero impact on winning still shows -5.7 points per 40 minutes from random variance alone. The noise floor is enormous.")
5. The kicker: No winning Kaggle March Madness solution has ever used player-level features. We learned this the hard way.

**The business parallel (1-2 sentences, not heavy-handed):**
"Before you add another data source to your pipeline, ask whether the signal is already captured in what you have. More columns isn't always more insight."

**Tone:** Self-deprecating but educational. "We thought we were being clever. The data humbled us." This is the contrarian-but-fair move from the SSA playbook.

**Visual: Team WAR vs. Tournament Wins scatter**
Use existing `results/figures/11_team_war_vs_tourney.png`. The flat line (r=0.001) is devastating and tells the whole story in one image. Caption: "We expected a correlation. We got a cloud."

---

## SECTION 4: Day 1 Results - The Scorecard (~200-250 words)

**Goal:** Transition from "the model we built" to "how it actually performed." Keep this tight. Hit the highlights, don't recite every game.

**What to include:**

*The headline stat:* 11/16 correct in the Round of 64 (68.8%). Not bad. Not great.

*What worked:*
- Every chalk pick we made was correct (9/9)
- Two upset picks hit: VCU over North Carolina (called at 60.8%, VCU came back from 19 down to win in OT) and St. Louis over Georgia (called at 63.7%, St. Louis won by 25)
- The VCU call is worth a sentence of its own: largest first-round comeback in tournament history

*What didn't work (the good stuff):*
- Three games where the model was 90%+ confident in the wrong team
- High Point 83, Wisconsin 82 (we said 95.7% Wisconsin)
- Texas A&M 63, St. Mary's 50 (we said 91.5% St. Mary's)
- Texas 79, BYU 71 (we said 92.4% BYU, despite AJ Dybantsa's 35 points in his only college tournament game)
- These three games alone accounted for 64% of our total prediction error

**Tone:** Honest. "We nailed the chalk. We nailed two upsets. And then we got absolutely torched on three games where we were catastrophically overconfident."

**Visual options (pick 1-2):**

*Option A: Day 1 Scorecard Table*
Clean table showing all 16 games: our pick, our confidence, actual result, Brier score. Color-coded green/red. This is the SSA "tables for data" pattern.

*Option B: Prediction Accuracy Chart*
Use existing `results/figures/16_day1_prediction_accuracy.png` (the horizontal bar chart showing model confidence in the actual winner, green=correct, red=wrong). The visual contrast between the green cluster at 90%+ and the red cluster below 20% tells the story instantly.

---

## SECTION 5: Why the Model Missed - The Irony (~200-250 words)

**Goal:** This is the analytical payoff. Connect the player data experiment back to the Day 1 misses. The irony is the article's core insight.

**The pattern across all three big misses:**

The "underdogs" that beat our model's favorites all shared something: they had more experienced rosters, more total player talent (WAR), and in High Point's case, better net efficiency than the team we picked. But the model's heavy reliance on Elo ratings and seed numbers buried those signals.

| What the model saw | What it missed |
|---|---|
| Wisconsin: 5-seed, 1825 Elo | High Point: 20.2 net efficiency (vs Wisconsin's 10.0), 64% seniors (vs 30%) |
| St. Mary's: 27-6 record, 1869 Elo | Texas A&M: 58% seniors, Team WAR 50.4 (vs 34.8), SEC-hardened roster |
| BYU: 6-seed, higher Elo | Texas: Team WAR 85.5 (vs 42.1), coach with 22 tournament wins (vs 2) |

**The irony:** The player-level features that made our overall model worse are exactly what would have flagged these specific upsets. Team WAR, senior percentage, experience metrics: they don't improve predictions across 1,400 games, but they're precisely the signal that matters in the 3-4 games where the model is most dangerously wrong. The aggregate model doesn't need them. The edge cases desperately do.

**Tone:** Analytical but with a "well, would you look at that" energy. This is the "data as detective story" pattern from the SSA guide.

**Visual: Feature Comparison Chart**
Use existing `results/figures/17_day1_wrong_picks_features.png` (the three-panel bar chart comparing winner vs. our pick across key metrics). The visual immediately shows: on Elo, the model's pick wins. On everything else, the actual winner wins.

---

## SECTION 6: The Cool Insight (~100-150 words)

**Goal:** One non-conventional finding that sticks with the reader. Something they'll repeat at the bar.

**Option 6A: The Injury Blind Spot**
All 8 major injuries in the tournament field were public knowledge, announced 3 to 64 days before tipoff. Our model had no idea. Duke was listed at 99.4% against Siena while missing two starters (26% of their roster WAR). When we manually adjusted for injuries, their probability dropped to 86.6%, a 13-point swing. Duke won by 6 and trailed by 13 in the second half. "Your dashboards have the same problem. Are you reporting last month's reality as if it's still true?"

**Option 6B: Chase Johnston's 2-Pointer (The Irreducible Chaos)**
The player who hit the game-winning shot for High Point (Chase Johnston, fastbreak layup, 11.2 seconds left) had not made a single two-point field goal all season. He was 0-for-4. His first career 2-pointer ended Wisconsin's tournament. No amount of data accounts for that. That's March Madness. Some variance is irreducible, and any model that claims otherwise is lying to you.

**Option 6C: Upset Rates Haven't Changed in 40 Years**
Despite the transfer portal, NIL, conference realignment, and the 3-point revolution: the tournament upset rate has held steady at roughly 27% since the field expanded in 1985. The game keeps changing. The chaos doesn't. We found a correlation of r=0.02 between "late-season momentum" and tournament performance. Peaking at the right time is a myth the data destroyed years ago.

**Recommendation:** 6A ties back to the business lesson most cleanly (stale data is a universal problem). 6B is the most memorable image (great for social sharing). 6C is the most intellectually interesting. If the article is for LinkedIn with a business audience, go 6A. If it's more sports/general audience, go 6B.

---

## SECTION 7: The Close (~50-75 words)

**Goal:** Short. Earned. One strong sentence. Per SSA guide: don't re-summarize, trust the reader, land the plane fast.

**Option 7A: The builder vs. questioner**
"Claude Code built a pipeline in hours that used to take weeks. It trained five models, generated 19 visualizations, and predicted 132,000 matchups. It also gave Wisconsin a 96% chance of beating a 12-seed that outperformed them in almost every metric that mattered. The AI builds the pipeline. The analyst asks the right questions."

**Option 7B: The data lesson**
"We started this project thinking more data would make us smarter. It didn't. But it taught us where to look when the model is lying to us. Sometimes the most valuable analysis isn't the model's prediction. It's knowing which predictions not to trust."

**Option 7C: The March Madness lesson**
"Our model went 11 for 16. Not bad for a machine that was built in a single session. But the three it got wrong, it got catastrophically wrong, and every miss pointed to the same blind spot: overweighting what a team has done and underweighting who's actually on the floor. March doesn't care about your Elo rating."

**Recommendation:** 7A. It's the strongest landing and echoes the process story. Plus "The AI builds the pipeline. The analyst asks the right questions" is a clean, shareable closer.

**Soft CTA (per SSA pattern):**
"Thanks for reading! If you're interested in the full technical breakdown, the code, visualizations, and game-by-game analysis are all open on our GitHub. And if your team is sitting on data but not sure what to do with it, that's literally what we do. [link]"

*Include hashtags: #MarchMadness #DataScience #MachineLearning #AI #ClaudeCode #Analytics*

---

## VISUALS SUMMARY

**Must-include (3-4 for a LinkedIn article):**

| Visual | Source | Purpose |
|--------|--------|---------|
| **Process infographic** | `results/ss_full_final.png` | Shows the pipeline: 101 files -> 57 features -> 5 models -> bracket. Establishes the "built in one session" claim visually |
| **Team WAR vs. Tournament Wins scatter** | `results/figures/11_team_war_vs_tourney.png` | The flat line (r=0.001) that proves player data doesn't help. One image tells the whole Section 3 story |
| **Day 1 Prediction Accuracy** | `results/figures/16_day1_prediction_accuracy.png` | Green/red bar chart showing model confidence for each game. The visual contrast between correct high-confidence picks and wrong high-confidence picks is striking |
| **Feature Comparison (3 biggest misses)** | `results/figures/17_day1_wrong_picks_features.png` | Shows Elo favored our pick but WAR, experience, efficiency favored the actual winner in all 3 cases |

**Nice-to-have (if space):**

| Visual | Source | Purpose |
|--------|--------|---------|
| Session 2 flowchart | `results/ss_s2_fixed.png` | Shows the player data experiment + pivot to injury analysis. Good for showing human-AI collaboration |
| Upset picks scorecard | `results/figures/18_day1_upset_picks.png` | Visual scorecard of upset picks (2 hit, 1 miss, 3 pending) |
| Injury impact table | From `injury_adjusted_predictions.txt` | Table showing 8 injuries, dates announced, WAR lost, prediction shift. Supports the "stale data" insight |
| Model comparison | `results/figures/10_model_comparison.png` | Shows LightGBM dominance over 5 architectures |

**Potentially create:**

| Visual | What it would show |
|--------|-------------------|
| **Day 1 scorecard table** | Clean, formatted table of all 16 R64 games: game, our pick, confidence, result, correct/wrong. Could be done as a styled HTML table or a simple clean graphic. This might be the single most shareable visual. |
| **The irony diagram** | A simple 2x2 or Venn showing: "Player features in aggregate model: hurt performance" vs "Player features in the 3 biggest misses: would have caught them all." Visual representation of the paradox. |

---

## ARTICLE FLOW AT A GLANCE

```
HOOK: "We added 30,000 player records. It got worse."
  |
  v
CONTEXT: Built full ML pipeline with Claude Code in one session
  (40+ agents, 101 files, 57 features, 5 models)
  |
  v
THE EXPERIMENT: Player data hypothesis -> test -> failure
  (30K records, 8 features, Brier went from .050 to .054)
  (Why: noise floor, signal already captured, business lesson)
  |
  v
THE SCORECARD: Tournament Day 1 results (11/16)
  (2 upset picks hit, 3 catastrophic misses at 90%+ confidence)
  |
  v
THE IRONY: The player features that hurt the model overall
  would have caught the exact games it got wrong
  (experience, WAR, coaching: underweighted by Elo/seed)
  |
  v
COOL INSIGHT: The injury blind spot / irreducible chaos
  |
  v
CLOSE: "The AI builds the pipeline. The analyst asks the right questions."
```

---

## OPEN QUESTIONS FOR NICK

1. **Title preference?** The "30,000 player records" headline is strongest for contrarian hook. But "96% sure about Wisconsin" is more emotionally grabby. Or do we go with something that leads with Claude Code / the process?

2. **Visuals budget?** LinkedIn articles do well with 3-4 visuals. Do we want to create a clean scorecard table graphic, or is the existing bar chart sufficient?

3. **Business lesson emphasis?** The "stale data / injury blind spot" parallel maps directly to SSA's consulting work (dashboards reporting outdated reality). How hard do we lean into this? One sentence? A full paragraph?

4. **Which cool insight?** The injury blind spot (most business-relevant), Chase Johnston's 2-pointer (most memorable/shareable), or upset rate stability (most intellectually interesting)?

5. **Friday results?** If we wait a day, we can include full first-round results (32 games instead of 16). This gives us a complete picture and our 3 remaining upset picks resolve. But timeliness matters while the tournament is live.

6. **Publish where?** LinkedIn article, newsletter, Medium, or SSA blog? This affects length and tone slightly.
