# Article Fact Audit Checklist

Every verifiable claim from `draft.md`, with verification status and sources.

**Legend:** `[x]` = verified true, `[!]` = incorrect/needs fix, `[~]` = partially true/needs nuance, `OUR DATA` = model-specific (no external source needed)

---

## Introduction (Lines 1-11)

### Player Data Experiment (Headline Claims)
- [x] 30,000 individual player records were downloaded — `OUR DATA` (phase7: 30,066 actual)
- [x] 8 new features were engineered from player data — `OUR DATA` (phase7: Team_WAR, Star_WAR, WAR_Gini, Avg_ClassNum, Star_Usage, Top3_WAR, Avg_Height, Sr_Pct). Note: article only names 7 - Top3_WAR is omitted from prose
- [x] "Every single" model configuration got worse (not one improved) — `OUR DATA` (phase7: "Not one configuration improved")

### Methodology Note
- [x] Brier score punishes overconfidence quadratically — correct by definition: Brier = (p - actual)^2
- [!] **"Predict 95% and get it wrong = ~20x penalty of predicting 55% wrong"** — WRONG. (0.95)^2 = 0.9025 vs (0.55)^2 = 0.3025 = ratio of ~3x, not 20x. **NEEDS FIX IN DRAFT**

---

## Part 1: The Pipeline (Lines 15-26)

### Data Ingestion
- [x] 101 data files ingested — `OUR DATA` (data-sources.md)
- [x] Four data sources listed — `OUR DATA`
- [~] Barttorvik described as "KenPom-equivalent efficiency metrics" — reasonable shorthand; both provide adjusted per-possession efficiency. Barttorvik adds recency bias and garbage time filtering that KenPom does not. SOURCE: oreateai.com/blog/kenpom-vs-torvik, the-boneyard.com/threads/kenpom-vs-barttorvik

### Feature Engineering
- [x] 57 features per team-season — `OUR DATA` (team_features.parquet)
- [x] All feature categories listed (Elo, efficiency, SOS, four factors, seed, coaching) — `OUR DATA`

### Model Training & CV Scores
- [x] 5 architectures: LR, BT, XGB, LGBM, NN — `OUR DATA`
- [x] LightGBM CV Brier: 0.050 (rounds from 0.0503) — `OUR DATA` (phase4)
- [x] XGBoost CV Brier: 0.054 (rounds from 0.0536) — `OUR DATA` (phase4)
- [x] Neural net CV Brier: 0.115 (rounds from 0.1152) — `OUR DATA` (phase4)

### General Claims
- [x] "Tree-based models dominate small tabular prediction problems" — SOURCE: Grinsztajn et al., "Why do tree-based models still outperform deep learning on typical tabular data?", NeurIPS 2022 (arxiv.org/abs/2207.08815). Also confirmed in PLOS ONE 2024 (journals.plos.org/plosone/article?id=10.1371/journal.pone.0301541)
- [x] "Realistic ceiling sits around 0.04 to 0.06" — SOURCE: past-winners-research.md line 261, derived from goto_conversion's multi-year performance and historical competition results
- [x] 132,000 matchups predicted — `OUR DATA` (66,430 men's + 65,703 women's = 132,133)

---

## Part 2: The Player Data Experiment (Lines 29-43)

### Ohio State vs TCU (Inciting Incident)
- [~] Model gave Ohio State "82%" chance — `OUR DATA` (actual: 81.9% per day1-game-analysis.md line 50/97; 82% is acceptable rounding)
- [x] TCU won 66-64 — SOURCE: day1-game-analysis.md line 50, 110 (confirmed from ESPN box score)
- [x] "TCU won on a layup with 4.3 seconds left" — SOURCE: day1-game-analysis.md line 110: "Xavier Edmonds for a go-ahead layup with 4.3 seconds left"
- [~] "The very first game I predicted went wrong" — IMPRECISE. First Four had 3 wrong picks before R64. Even in Thursday R64, Louisville/USF (game #3) was wrong before TCU (game #4). Games may have tipped simultaneously, but "very first" is a stretch

### Player Data Collection
- [x] 30,000 player records — `OUR DATA` (phase7: 30,066 actual)
- [x] Records span six seasons — `OUR DATA` (phase7: 2021-2026)
- [~] 8 team-level features engineered — `OUR DATA` (phase7 confirms 8: Team_WAR, Star_WAR, WAR_Gini, Avg_ClassNum, Star_Usage, Top3_WAR, Avg_Height, Sr_Pct). Article prose names only 7 - Top3_WAR is omitted
- [x] 99.3% match rate — `OUR DATA` (phase7 line 12)
- [x] 30 model configurations rerun — `OUR DATA`
- [x] Brier score went from 0.0503 to 0.0544 — `OUR DATA` (phase7 line 36-37)

### Results
- [x] Every player feature correlation below r = 0.12 — `OUR DATA` (phase7 line 19-28: highest is Avg_Height at -0.105)
- [x] "Not one cracked the top 15 in feature importance" — `OUR DATA` (phase7 line 30)
- [x] Total roster WAR vs tournament wins: r = 0.037 — `OUR DATA` (figure 11)

### Research Claims
- [!] **PubMed citation: "individual player stats need ~100 games to stabilize"** — WRONG ON TWO COUNTS. Paper (PMID 31046653, Perez-Ferreiros et al. 2019) studies **team-level stats**, not individual player stats. Also studied Spanish pro basketball (ACB league), not NCAA. 100-game finding is real but applies to teams. **NEEDS FIX IN DRAFT** — SOURCE: pubmed.ncbi.nlm.nih.gov/31046653
- [x] "College season is 30-35 games" — CORRECT. NCAA.com: "roughly 30 to 32 if it doesn't [make tournament]", up to 35-40 with postseason. 30-35 is accurate for regular season + conference tournament. SOURCE: ncaa.com/news/basketball-men/article/2020-10-27/how-many-games-are-college-basketball-season
- [x] "No winning Kaggle March Madness solution has ever used player-level data" — consistent with all documented winners (Landgraf, ArunkumarRamanan 2019, maze508 2023). maze508 explicitly said "No player data used." No counter-example found. Note: draft was revised from "across a decade" to "ever" which is stronger but still supported. SOURCE: past-winners-research.md, Kaggle discussion threads, winner GitHub repos
- [x] goto_conversion GitHub link works — SOURCE: github.com/gotoConversion/goto_conversion (107 stars, 15 forks, MIT license)
- [~] goto_conversion "corrects a well-known statistical bias" — README describes correcting the "favourite-longshot bias" which IS well-documented in economics literature (since 1940s). "Well-known" is editorial but defensible. SOURCE: GitHub README
- [x] goto_conversion "$47,000 in prize money" — SOURCE: GitHub repo description: "Powered $47,000 of prize money." Individual prizes add up correctly ($8K+$7K+$5K+$5K+$5K+$5K+$7K+$5K = $47K)
- [x] goto_conversion "10+ gold medals" — SOURCE: GitHub repo description
- [x] goto_conversion "100+ medals on Kaggle" — SOURCE: GitHub repo description. Note: these include medals won by other Kaggle users who used the open-source package, not all by one person
- [x] goto_conversion "a few lines of math" with "no ML, no training data, no feature engineering" — core algorithm is ~4 lines. README: "does not require historical data for model fit, advanced domain knowledge, nor paid computational resources." Substantively accurate. SOURCE: GitHub README + past-winners-research.md line 20-37

---

## Part 3: The Scorecard (Lines 47-66)

### Overall Record
- [x] 36 of 48 correct through two rounds (75%) — `OUR DATA`
- [x] "48 games" through two rounds — 32 R64 + 16 R32 = 48

### Correct Upset Picks
- [x] VCU upset North Carolina — SOURCE: ESPN box score (espn.com/mens-college-basketball/recap?gameId=401856490); VCU 82, UNC 78 OT
- [x] Model predicted VCU at 60.8% — `OUR DATA` (day1-game-analysis.md line 53, 254)
- [x] "VCU completed the largest first-round comeback in tournament history" — CORRECT. Sixth-largest comeback in NCAA tournament history overall, but largest ever specifically in the first round (19 points). SOURCE: Yahoo Sports ("largest 1st-round comeback in NCAA Tournament history"), SI ("The Biggest Comeback in Every Round of the NCAA Men's Tournament")
- [x] VCU "rallied from 19 down" — CORRECT. Trailed 56-37. SOURCE: Yahoo Sports, ESPN recap, Fox News
- [x] VCU won in overtime — CORRECT. 82-78 OT. SOURCE: ESPN box score
- [x] Terrence Hill Jr. career-high 34 — CORRECT. 34 pts, 13-of-23 FG, 7-of-10 from 3. SOURCE: NBA.com, VCU Athletics official recap (vcuathletics.com), ESPN box score, Chicago Tribune
- [x] St. Louis over Georgia — CORRECT. StL 102, Georgia 77. SOURCE: day1-game-analysis.md line 62, 259
- [x] Model predicted St. Louis at 63.7% — `OUR DATA` (day1-game-analysis.md line 62)
- [x] "St. Louis won by 25" — CORRECT. 102-77 = 25. SOURCE: day1-game-analysis.md line 259

### Top 5 Misses Table

#### Game 1: Iowa 73, Florida 72
- [x] Final score: Iowa 73, Florida 72 — SOURCE: ESPN (espn.com/mens-college-basketball/game/_/gameId/401856563/iowa-florida)
- [x] Seeds: (9) Iowa vs (1) Florida — SOURCE: ESPN
- [x] Model prediction: Florida wins at 97.1% — `OUR DATA`
- [x] "Folgueiras' go-ahead 3" — CORRECT. Alvaro Folgueiras (junior, from Malaga, Spain, transfer from Robert Morris). SOURCE: ESPN (espn.com/mens-college-basketball/story/_/id/48283943/iowa-takes-no-1-florida), Iowa Athletics (hawkeyesports.com)
- [x] "4.5 sec left" — CORRECT. SOURCE: ESPN, CBS Sports, CNN
- [~] "First 1-seed to fall" — CORRECT for 2026 tournament, but needs context. Florida was the first No. 1 seed eliminated in the 2026 tournament. Not a historical claim. SOURCE: CBS Sports ("Florida becomes first No. 1 seed to fall"), CNN
- [x] Brier penalty: 0.943 — math: (0.971)^2 = 0.943

#### Game 2: Texas 74, Gonzaga 68
- [x] Final score: Texas 74, Gonzaga 68 — SOURCE: CBS Sports
- [x] Seeds: (11) Texas vs (3) Gonzaga — SOURCE: CBS Sports
- [x] Model prediction: Gonzaga wins at 96.1% — `OUR DATA`
- [x] "First Four team reaches the Sweet 16" — CORRECT. Texas beat NC State in First Four, then BYU (R64), then Gonzaga (R32). Sixth team ever to go from First Four to Sweet 16. SOURCE: CBS Sports ("Texas dancing into Sweet 16 from play-in game"), Texas Athletics
- [x] Brier penalty: 0.923 — math: (0.961)^2 = 0.923

#### Game 3: High Point 83, Wisconsin 82
- [x] Final score: High Point 83, Wisconsin 82 — SOURCE: day1-game-analysis.md line 57, 149; NCAA.com, Fox Sports
- [x] Seeds: (12) High Point vs (5) Wisconsin — SOURCE: day1-game-analysis.md
- [x] Model prediction: Wisconsin wins at 95.7% — `OUR DATA` (day1-game-analysis.md line 57)
- [x] "Chase Johnston's fastbreak layup" — CORRECT. SOURCE: NCAA.com ("High Point sharpshooter hits his first 2-point shot to beat Wisconsin"), Fox Sports, SI
- [x] "11.2 sec left" — CORRECT. SOURCE: day1-game-analysis.md line 167; consistent with Fox Sports and SI reports
- [x] Brier penalty: 0.916 — math: (0.957)^2 = 0.916

#### Game 4: Texas A&M 63, St. Mary's 50
- [x] Final score: Texas A&M 63, St. Mary's 50 — SOURCE: day1-game-analysis.md line 56, 119
- [x] Seeds: (10) Texas A&M vs (7) St. Mary's — SOURCE: day1-game-analysis.md
- [x] Model prediction: St. Mary's wins at 91.5% — `OUR DATA` (day1-game-analysis.md line 56)
- [x] "A&M led wire-to-wire" — SOURCE: day1-game-analysis.md line 135: "Texas A&M led wire-to-wire in a dominant defensive performance"
- [x] "Held StM to season-low 50" — SOURCE: day1-game-analysis.md line 135: "St. Mary's scored only 50 points - their lowest output all season"
- [~] Brier penalty: 0.838 — math gives 0.837225, article rounds to 0.838. Minor rounding, acceptable

#### Game 5: Nebraska 74, Vanderbilt 72
- [x] Final score: Nebraska 74, Vanderbilt 72 — SOURCE: ESPN (espn.com/mens-college-basketball/recap/_/gameId/401856534)
- [x] Seeds: (4) Nebraska vs (5) Vanderbilt — SOURCE: ESPN
- [x] Model prediction: Vanderbilt wins at 89.1% — `OUR DATA`
- [x] "Frager's layup, 2.2 sec left" — CORRECT. Braden Frager (freshman, off bench) driving layup with 2.2 seconds left. SOURCE: ESPN, NBA.com, Nebraska Athletics (huskers.com)
- [x] "Nebraska reaches first Sweet 16" — CORRECT. First-ever Sweet 16 in program history. Had never won an NCAA tournament game before 2026. SOURCE: Yahoo Sports ("Nebraska advances to first Sweet 16 in program history"), Omaha World-Herald
- [~] Brier penalty: 0.795 — math gives 0.79388, article rounds to 0.795. Minor rounding, acceptable

### Aggregate Miss Claims
- [x] "Five games, all predicted at 89% or higher" — verified: 97.1%, 96.1%, 95.7%, 91.5%, 89.1%
- [x] "Together accounted for 47% of total prediction error" — `OUR DATA` (verified at 47.4%)
- [!] **"Iowa stunning No. 1 overall seed Florida"** — WRONG. Florida was a No. 1 seed but the **4th overall seed** (Duke was #1, Arizona #2, Michigan #3, Florida #4). Should say "No. 1 seed" not "No. 1 overall seed." SOURCE: ESPN (espn.com/mens-college-basketball/story/_/id/48217804/duke-arizona-michigan-florida-top-ncaa-tournament-seeds), NBA.com **NEEDS FIX IN DRAFT**
- [x] "97.1% was the single worst miss" — `OUR DATA` (0.943 was highest Brier penalty)

---

## Part 4: Why We Missed / The Irony (Lines 69-93)

### First Round Experience Pattern
The "three" first-round misses referenced are High Point/Wisconsin, Texas A&M/St. Mary's, Texas/BYU:
- [x] Senior %s: 64% (High Point), 58% (Texas A&M), 52% (Texas) for winners — `OUR DATA` (day1-game-analysis.md lines 161, 130, 199)
- [x] Senior %s: 30% (Wisconsin), 10% (St. Mary's), 18% (BYU) for picked teams — `OUR DATA` (day1 lines 161, 130, 199)
- [x] "All three winners had higher total roster WAR" — `OUR DATA`: HP 48.2 vs WI 39.7; A&M 50.4 vs StM 34.8; TX 85.5 vs BYU 42.1 (day1 lines 159, 128, 196)

### High Point vs Wisconsin Deep Dive
- [x] High Point net efficiency: 20.2 — `OUR DATA` (day1: 20.17, rounds to 20.2)
- [x] Wisconsin net efficiency: 10.0 — `OUR DATA` (day1: 10.01, rounds to 10.0)
- [x] High Point win %: 87% — `OUR DATA` (day1 line 160)
- [x] Wisconsin win %: 71% — `OUR DATA` (day1 line 160)

### Texas vs BYU
- [x] Texas coaching: 22 tournament wins — `OUR DATA` (day1 line 198: "Coach Tourney Wins | 22 | 2")
- [x] BYU coaching: 2 tournament wins — `OUR DATA` (day1 line 198)

### Texas vs Gonzaga (Round of 32)
- [x] Texas given 3.9% chance — `OUR DATA` (100% - 96.1% = 3.9%)
- [x] Texas beat Gonzaga by 6 — SOURCE: CBS Sports (74-68)
- [x] Texas reached Sweet 16 as First Four team — SOURCE: CBS Sports, Texas Athletics
- [x] "Wrong about Texas in all three games" — `OUR DATA`: First Four (NC State favored at 68.9%), R64 (BYU favored at 88.3%), R32 (Gonzaga favored at 96.1%)
- [x] Texas prediction progression: 68.9%, then 88.3%, then 96.1% — `OUR DATA` **Previously FIXED from 92.4%**
  - [x] Game 1: NC State favored at 68.9% in First Four — `OUR DATA` (day1 line 23)
  - [x] Game 2: BYU favored at 88.3% in R64 — `OUR DATA` **FIXED from 92.4%**
  - [x] Game 3: Gonzaga favored at 96.1% in R32 — `OUR DATA`
- [x] Texas Team WAR: 85.5 — `OUR DATA` (day1 line 196, 211; phase7 line 120)
- [x] "Second-highest in tournament field" — `OUR DATA` **Previously FIXED**: Tennessee 88.1 was highest (phase7 line 119). Note: phase7 line 118 shows Missouri at 93.4 was actually highest, then Tennessee 88.1, then Texas 85.5. "Second-highest" is also wrong - Texas was THIRD. **NEEDS REVIEW**

### Gonzaga Coach Quote
- [~] Mark Few quote — PARAPHRASE, not exact. Actual quote: "No, [Texas] is not a Cinderella team. That's a really talented basketball team with a really, really, really good coach **that has incredible resources**." Article omits the ending clause and changes "No, [Texas] is not" to "That's not." Core message is preserved. SOURCE: ClutchPoints (clutchpoints.com), SI (si.com/college/texas/basketball/are-the-texas-longhorns-a-cinderella)
- [x] Said postgame after Texas-Gonzaga R32 game — SOURCE: ClutchPoints, SI

### Gonzaga Injury
- [!] **Braden Huff "second-leading scorer"** — WRONG. Huff was Gonzaga's **leading scorer** at 17.8 PPG before injury. Multiple sources call him "Gonzaga's leading scorer." Graham Ike's season-long average rose after Huff went down. **NEEDS FIX IN DRAFT.** SOURCE: Spokesman-Review, SI, MyNorthwest, Fox Sports
- [x] Huff averaged 17.8 PPG — CORRECT. Through 18 games. SOURCE: ESPN player stats (espn.com/mens-college-basketball/player/gamelog/_/id/4894445/braden-huff)
- [x] Huff dislocated kneecap — CORRECT. Suffered in practice. SOURCE: SWX Local Sports, Spokesman-Review
- [x] Injury since January — CORRECT. January 14, 2026. SOURCE: phase7 line 68; SWX Local Sports, Spokesman-Review

### Model Overconfidence Pattern Table (Elo, seeds, BARTHAG, WAR values)
All Elo, BARTHAG, WAR, seed values in this table are from our feature data — `OUR DATA` (day1-game-analysis.md feature comparison tables):
- [x] Wisconsin: 5-seed, 1825 Elo (actual 1824.8), 0.93 BARTHAG — day1 lines 156, 162
- [x] St. Mary's: 1869 Elo (actual 1869.3) — day1 line 126
- [~] St. Mary's: 27-6 record — needs external verification of exact W-L record
- [x] Florida: 1-seed, 1978 Elo, 0.97 BARTHAG — `OUR DATA`
- [x] Gonzaga: 3-seed, 1933 Elo — `OUR DATA`
- [x] BYU: 6-seed, 1760 Elo (actual 1760.2) — day1 line 195
- [x] High Point: 20.2 net efficiency, 64% seniors — `OUR DATA` (day1 lines 157, 161)
- [x] Texas A&M: 58% seniors, Team WAR 50 (actual 50.4) — `OUR DATA` (day1 lines 128, 130)
- [x] St. Mary's Team WAR: 35 (actual 34.8) — `OUR DATA` (day1 line 128)
- [x] Iowa Team WAR: 38 — `OUR DATA`
- [x] Florida Team WAR: 30 — `OUR DATA`
- [x] "Even Vegas only had Florida at ~85%" — CORRECT. Moneyline -575 implies 85.2%. FanDuel's vig-adjusted figure was 81.8%. ~85% is defensible. SOURCE: FanDuel Research, CBS Sports odds, OddsShark (oddsshark.com/ncaab/iowa-florida-odds-march-22-2026)
- [x] Gonzaga Team WAR: 39 (actual 38.7 per phase7 line 83) — `OUR DATA`
- [~] **Texas Team WAR: article says "85.5" (line 75) and "86" (lines 84-85)** — actual is 85.5 (`OUR DATA` day1 line 196). The "86" in the table is rounded. Inconsistency is minor but should pick one. **SUGGEST: use 85.5 everywhere or round to 86 everywhere**
- [x] BYU Team WAR: 42 (actual 42.1) — `OUR DATA` (day1 line 196)

### Irony Claim
- [x] "Player-derived features that made model worse are exactly what would have flagged these upsets" — `OUR DATA`. Verified: in all three R64 misses (HP/WI, A&M/StM, TX/BYU), the upset winner had higher Team WAR, higher Sr%, and more experience (day1 feature tables)

### Probability Clipping
- [x] "Winning Kaggle solutions consistently use probability clipping" — SOURCE: past-winners-research.md line 102: 2019 winner clipped to [0.025, 0.975]; line 200-204: "Probability Clipping (most common)" among winners
- [x] "Typically 2.5% to 97.5%" — SOURCE: past-winners-research.md line 102, 201
- [x] "Model outputting raw values like 97.1% and 96.1% without guardrails" — `OUR DATA`
- [x] Iowa upset cost 0.943 Brier penalty, worst of tournament — `OUR DATA`
- [x] 12 wrong picks across two rounds — `OUR DATA` (48 - 36 = 12)
- [ ] "Vegas was more calibrated than we were" in all 12 — partially verified. Vegas ~85% for Iowa-Florida vs our 97.1% confirms this for that game. Full verification of all 12 would require Vegas odds for each game
- [ ] "In four of them, we picked the opposite team entirely" — needs Vegas odds for all 12 wrong picks to verify which ones we picked the opposite team from Vegas

---

## Part 5: Injury Analysis (Lines 96-108)

### Injury Count
- [x] 8 players injured/ruled out before bracket set — CORRECT. SOURCE: phase7 lines 66-75: Huff, Saunders, Toppin, Brown Jr., Wilson, Foster, Ngongba, Holloway
- [x] "Every announcement was public" — CORRECT. All reported by beat writers, team accounts, or official injury reports. SOURCE: phase7 lines 66-75 lists dates; ESPN, CBS Sports, team athletics sites for each
- [x] "3 to 64 days before tipoff" — CORRECT. Earliest: Huff (Jan 14, 64 days). Latest: Holloway (Mar 16, 3 days). SOURCE: phase7 lines 68, 75

### Duke vs Siena
- [x] Duke at 99.4% — `OUR DATA` (injury_adjusted_predictions.txt: 0.9943)
- [~] **Caleb Foster: "broken foot, March 7"** — Injury type CORRECT (fractured right foot, had surgery). Date is IMPRECISE: Foster was injured during the UNC game on **March 8**, surgery March 9, announced by Coach Scheyer on **March 10**. Article says "March 7" which is 1-2 days off. SOURCE: ESPN (espn.com/mens-college-basketball/story/_/id/48162553), WRAL, CBS Sports **SUGGEST: change to "March 8" or "early March"**
- [!] **Patrick Ngongba: "foot fracture, March 2"** — WRONG INJURY TYPE. Ngongba had **"right foot soreness"**, NOT a fracture. Only Foster had a fracture. Multiple sources distinguish these. Date ~March 2 is approximately when he last played, but announcement was March 10. SOURCE: WRAL, ESPN, SI (si.com/college/duke/blue-devils-patrick-ngongba-injury-leaves-massive-hole-defense) **NEEDS FIX IN DRAFT**
- [x] Foster + Ngongba = 26% of Duke's roster WAR — `OUR DATA` (injury file: WAR lost = 7.60; phase7: Duke total WAR = 29.3; 7.60/29.3 = 25.9% ≈ 26%)
- [x] Injury-adjusted prediction: 86.6% — `OUR DATA` (injury_adjusted_predictions.txt: 0.8661)
- [~] "13-point swing" — actual difference is 12.8 percentage points. Rounds to "~13" which is acceptable
- [x] Duke won by 6 — CORRECT. Duke 71, Siena 65. SOURCE: day1-game-analysis.md line 47
- [x] "Duke trailed by 13 in the second half" — SOURCE: day1-game-analysis.md line 226: "Duke trailed by as many as 13 in the second half"

### Gonzaga Injury (repeated)
- [x] Huff 17.8 PPG — SOURCE: ESPN stats (see above)
- [x] Dislocated kneecap since January — SOURCE: SWX, Spokesman-Review (see above)
- [x] Gonzaga given 96.1% against Texas — `OUR DATA`

### BYU Injury
- [x] Richie Saunders: 18.0 PPG — CORRECT. Career highs in points (18.0). SOURCE: CBS Sports, ESPN (espn.com/mens-college-basketball/story/_/id/47941092), BYU Athletics, Deseret News
- [x] Torn ACL — CORRECT. February 15, 2026, 45 seconds into BYU's OT win over Colorado. SOURCE: CBS Sports, ESPN, BYU Athletics (byucougars.com)
- [x] BYU given 88.3% against Texas — `OUR DATA` **Previously FIXED from 92.4%**
- [x] AJ Dybantsa on BYU — CORRECT. #1 overall recruit in 2025 class who reclassified and enrolled at BYU. SOURCE: BYU Athletics (byucougars.com), ESPN player page, CBS Sports
- [x] "BYU bench scored zero points" — SOURCE: day1-game-analysis.md line 206: "BYU's bench scored zero points"

### General Injury Claims
- [x] "Injury info public weeks before tipoff" for Gonzaga and BYU — CORRECT. Huff: Jan 14 (64 days); Saunders: Feb 15 (32 days). SOURCE: phase7 lines 68-69
- [x] "In both cases, the team we favored lost" — Gonzaga lost to Texas (R32), BYU lost to Texas (R64). SOURCE: CBS Sports, day1-game-analysis.md

---

## The Takeaway (Lines 112-118)

### Summary Claims (consistency with earlier sections)
- [x] "Five model architectures" — consistent
- [x] "30,000-record player data hypothesis" — consistent
- [x] "132,000 tournament matchups" — consistent
- [x] "36 for 48 through two rounds" — consistent
- [x] "Nailed four upset picks" — **Previously FIXED from "three"**
- [x] "Florida a 97% chance of beating a 9-seed" — consistent; Iowa was (9) seed

### Chase Johnston Claim
- [x] Chase Johnston was a "bench player" — CORRECT. Lost starting spot after 10 games. Started 11 of 32 games. SOURCE: NCAA.com, Fox Sports, SI (si.com/college-basketball/march-madness-chase-johnston-only-two-point-shot)
- [x] "Had not made a single two-point field goal all season" — CORRECT. Was 0-for-4 on 2PT attempts in regular season. 132 of 136 shot attempts were from 3PT range. SOURCE: NCAA.com ("High Point sharpshooter hits his first 2-point shot"), Fox Sports, SI, Pro Football Network
- [~] "His first one ended Wisconsin's season with 11 seconds left" — CORRECT but table says 11.2 seconds. Prose rounds to "11 seconds." Minor inconsistency, both accurate. SOURCE: Fox Sports, NCAA.com

---

## Cross-Cutting Consistency Checks

- [~] Texas Team WAR: 85.5 (line 75) vs 86 (lines 84-85) — actual is 85.5. The "86" is rounded. Minor but should unify
- [~] Johnston timing: 11.2 sec (table) vs 11 sec (takeaway) — both acceptable, 11.2 is more precise
- [~] "13-point swing" vs 12.8 actual — acceptable rounding
- [~] Brier 0.838 vs 0.837 and 0.795 vs 0.794 — acceptable rounding
- [x] $50K Kaggle prize pool — CORRECT. SOURCE: Kaggle on X/Twitter (x.com/kaggle/status/2024824505210691863)
- [~] "Thousands of data scientists worldwide" — plausible based on historical competition size but exact count not independently verified

---

## Errors Requiring Fixes in Draft

| # | Location | Error | Fix |
|---|----------|-------|-----|
| 1 | Line 11 (intro) | "~20x the penalty" | Should be "~3x the penalty" |
| 2 | Line 63 | "No. 1 overall seed Florida" | Florida was 4th overall seed (Duke was #1 overall). Change to "No. 1 seed Florida" |
| 3 | Line 75 | Huff "second-leading scorer" | Huff was Gonzaga's **leading** scorer |
| 4 | Line 102 | Foster "March 7" | Injury was March 8 (game), announced March 10 |
| 5 | Line 102 | Ngongba "foot fracture" | Was "foot soreness", not a fracture |
| 6 | Line 41 | PubMed "individual player stats" | Paper studied **team-level** stats, not individual |

## Items Needing Further Attention

| # | Location | Issue | Severity |
|---|----------|-------|----------|
| 1 | Line 75 | "second-highest [WAR] in tournament field" — phase7 shows Missouri (93.4) > Tennessee (88.1) > Texas (85.5), making Texas THIRD, not second | Medium |
| 2 | Lines 84-85 | Texas WAR shown as "86" vs "85.5" elsewhere | Low (rounding) |
| 3 | Line 33 | Article says "eight" features but prose only names seven (Top3_WAR omitted) | Low |
| 4 | Line 31 | "Very first game I predicted went wrong" — not literally the first miss | Low (dramatic license) |
| 5 | Line 75 | Mark Few quote is paraphrased, not exact — omits "that has incredible resources" | Low |
| 6 | Line 43 | "no winning...solution has **ever** used player data" is stronger than "across a decade" (original). Both supported but "ever" is harder to fully verify | Low |
| 7 | Lines 84-85 | Gonzaga WAR shown as "39" in table — actual is 38.7 from phase7 | Low (rounding) |
| 8 | N/A | St. Mary's "27-6" record not independently verified | Low |
| 9 | N/A | Vegas calibration for "all 12" wrong picks and "4 opposite team" claims — only Iowa-Florida verified | Medium |
