# March Madness Content Ideas

We built a full ML prediction pipeline for Kaggle's $50K March Madness competition using Claude Code. 101 data files, 57 features, 5 models, 30K player records, 19 visualizations. Here are 5 angles we can take for a post. They range from short LinkedIn hit to longer Medium piece.

---

## 1. "Our AI-Built Bracket Picked Ohio State at 82%. They Lost."

**Format:** Brief LinkedIn post (~200 words + 1-2 visuals)
**Angle:** The honest post-mortem. Personal hook (our team lost), humility about what the model missed, Claude Code as the tool that built it all.

**What we'd cover:**
- Claude Code built a full prediction pipeline in hours - Elo ratings, efficiency metrics, 5 model architectures, bracket simulations
- Model gave Ohio State 82% against TCU. They lost 66-64
- Duke listed at 99.4%. They were missing two starters to injuries (26% of roster WAR). Injury-adjusted: 86.6%
- All 8 major injuries were public 3-64 days before tip-off. The model had no idea
- Closer: "AI can build a better model than most humans in a fraction of the time. But it can't read the injury report."

**Visuals:** Model comparison bar chart, injury impact table

**Why this one:** Timely (tournament is live), personal, demonstrates both capability and intellectual honesty. Mirrors the Saquon piece energy.

---

## 2. "Everything You Think You Know About March Madness Is Wrong"

**Format:** Medium-length LinkedIn or Medium post (~500 words, visual-heavy)
**Angle:** Counterintuitive data findings. Less about Claude Code, more about the insights. Each finding is its own conversation starter.

**What we'd cover:**
- "Peaking at the right time" is a myth - r=0.02 correlation with tournament performance
- Upset rates haven't changed in 40 years (~27%) despite transfer portal, NIL, and conference realignment
- The 3-point paradox: volume up 25% since 2003, accuracy hasn't budged. Every rule change made it worse
- Champions shoot fewer 3s than the tournament field but make them at a higher rate
- 3-point defense predicts success better than 3-point offense
- The best Kaggle March Madness predictor ($47K in prizes) uses zero machine learning - just betting odds with a bias correction

**Visuals:** Era-marked upset rate chart, three-point paradox with rule changes, momentum scatter, structural timeline

**Why this one:** Pure shareability. Surprising stats + clean visuals = engagement. Positions SSA as people who find things others miss.

---

## 3. "We Added 30,000 Player Records to Our Model. It Got Worse."

**Format:** Brief LinkedIn post (~250 words)
**Angle:** One counterintuitive finding with a business lesson. The headline does the heavy lifting.

**What we'd cover:**
- Everyone assumes more data = better predictions. We tested it
- Downloaded player-level stats (WAR, experience, height, star dependency) for 30K college basketball players across 6 seasons
- Engineered 8 new features, reran the full model pipeline
- Result: Brier score went from 0.0503 to 0.0544. Worse across every configuration
- Why: team efficiency metrics already capture what players do in aggregate. Player stats in college basketball are extremely noisy (KenPom demonstrated a zero-impact player still shows -5.7 pts/40min from random noise)
- No winning Kaggle March Madness solution has ever used player data
- The one exception: injuries. When a star is out, team stats are stale and player data genuinely helps
- Business parallel: before adding more data sources to your pipeline, ask if the signal is already in what you have

**Visuals:** Team WAR vs tournament wins scatter (flat line, r=0.001), feature importance ranking

**Why this one:** Counterintuitive, teaches a real lesson about feature engineering that applies beyond sports. Extends SSA's technical credibility.

---

## 4. "Duke Was a 99.4% Favorite. They Were Missing 26% of Their Roster."

**Format:** Short LinkedIn post (~150 words + 1 visual)
**Angle:** Single-stat bombshell. The most compact, shareable version of the injury finding.

**What we'd cover:**
- Our model: Duke 99.4% vs Siena. But Duke lost Caleb Foster (broken foot, Mar 7) and Patrick Ngongba (foot fracture, Mar 2) - together 26% of their roster WAR
- Injury-adjusted prediction: 86.6%. A 13-point swing
- Table showing all 8 tournament injuries, when they were announced, and the WAR impact
- Every one was public knowledge before the bracket was set
- Closer: "Your dashboards have the same problem. Are you reporting last month's numbers as if they're still true?"

**Visuals:** Injury impact table (8 players, dates, WAR lost, prediction shift)

**Why this one:** Shortest, punchiest. Good standalone post or teaser that links to a longer piece. The business parallel at the end ties it back to what SSA does.

---

## 5. "I Gave Claude Code a $50K Data Science Challenge. Here's What It Built."

**Format:** Brief LinkedIn post (~250 words)
**Angle:** AI capability showcase. What can Claude Code actually do on a real project? Less basketball, more "look what's possible now."

**What we'd cover:**
- The challenge: enter Kaggle's March Madness prediction competition, build everything from scratch
- What Claude Code built autonomously:
  - Ingested 101 CSV files from 4 data sources
  - Engineered Elo ratings, per-possession efficiency, strength of schedule from raw game logs
  - Trained and compared 5 model architectures (logistic regression through LightGBM)
  - Ran 30+ hyperparameter configurations
  - Downloaded 30K player records via Barttorvik API and tested if they helped (they didn't)
  - Generated 10,000 Monte Carlo bracket simulations
  - Produced 19 publication-quality visualizations
  - Generated two Kaggle-ready submission files
- Total time: hours, not weeks
- The catch: it can't read an injury report. Duke at 99.4% while missing two starters
- Closer: "The AI builds the pipeline. The analyst asks the right questions."

**Visuals:** Model comparison chart or pipeline flow diagram

**Why this one:** Extends SSA's existing AI content ("If AI Can Write SQL," "Agentic AI: Are You Ready?"). Demonstrates SSA is using these tools on real projects, not just writing about them.

---

## Recommendation

**Quick hit now (while tournament is live):** #1 or #4 - short, timely, shareable
**Deeper follow-up (next week):** #2 or #3 - the insights or the player data lesson
**If we want to tie back to SSA's AI content series:** #5

All of these can reference the same underlying work. Pick 1-2, the visuals are ready to go.
