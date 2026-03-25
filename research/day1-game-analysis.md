# Day 1 Game-by-Game Analysis - 2026 NCAA Tournament

Generated: 2026-03-20

## Executive Summary

Our LightGBM model went **12/20 (60%)** across the First Four and Thursday's Round of 64. In the Round of 64 alone, we were **11/16 (68.8%)**. Our mean Brier score for the 16 Thursday games was **0.2472** - dragged up significantly by three massively overconfident misses (High Point/Wisconsin, Texas A&M/St. Mary's, Texas/BYU).

**Upset picks: 2 hits, 1 miss** (3 pending for Friday)
- VCU over North Carolina - HIT (60.8% confidence)
- St. Louis over Georgia - HIT (63.7% confidence)
- South Florida over Louisville - MISS (65.8% confidence)

**Biggest problems**: The model was catastrophically overconfident on three games where the actual underdog had clear advantages in experience, player talent (WAR), and/or net efficiency that the model's heavy reliance on Elo and seed suppressed.

---

## First Four Results (March 17-18)

| Game | Our Pick | Actual Winner | Score | P(Winner) | Brier | Result |
|------|----------|---------------|-------|-----------|-------|--------|
| (16) Howard vs (16) UMBC | UMBC (65.8%) | **Howard** | 86-83 | 34.2% | 0.4328 | WRONG |
| (11) Texas vs (11) NC State | NC State (68.9%) | **Texas** | 68-66 | 31.1% | 0.4747 | WRONG |
| (16) Prairie View vs (16) Lehigh | Lehigh (76.5%) | **Prairie View** | 67-55 | 23.5% | 0.5853 | WRONG |
| (11) Miami OH vs (11) SMU | Miami OH (91.7%) | **Miami OH** | 89-79 | 91.7% | 0.0069 | CORRECT |

**First Four record: 1/4 (25%)**

The First Four is a known weakness for models - these are games between similarly-seeded teams where the difference between them is razor-thin. Going 1/4 is bad but not catastrophic in Brier terms since 3 of 4 games were close to coin flips in reality.

Notable: Howard's win gave them their first NCAA tournament victory in program history. Prairie View's 12-point win over Lehigh was the most decisive of the play-in games, despite our model favoring Lehigh at 76.5%.

### Impact on Round of 64
The wrong First Four picks cascaded:
- We predicted Michigan vs UMBC - Michigan actually played Howard (Michigan still won easily, 101-80)
- We predicted BYU vs NC State - BYU actually played Texas (Texas won 79-71, and we would have predicted BYU regardless)
- We predicted Florida vs Lehigh (Friday) - Florida actually plays Prairie View

---

## Round of 64 - Thursday, March 19

### Full Scorecard

| # | Game | Score | Margin | Our Pick (Conf) | P(Winner) | Brier | Category |
|---|------|-------|--------|-----------------|-----------|-------|----------|
| 1 | (1) Duke def (16) Siena | 71-65 | +6 | Duke (99.4%) | 99.4% | 0.0000 | Correct chalk |
| 2 | (3) Michigan St def (14) N Dakota St | 92-67 | +25 | Mich St (95.0%) | 95.0% | 0.0025 | Correct chalk |
| 3 | (6) Louisville def (11) South Florida | 83-79 | +4 | South Florida (65.8%) | 34.2% | 0.4330 | **Wrong upset pick** |
| 4 | (9) TCU def (8) Ohio St | 66-64 | +2 | Ohio St (81.9%) | 18.1% | 0.6713 | **Missed upset** |
| 5 | (4) Nebraska def (13) Troy | 76-47 | +29 | Nebraska (93.9%) | 93.9% | 0.0037 | Correct chalk |
| 6 | (5) Vanderbilt def (12) McNeese | 78-68 | +10 | Vanderbilt (87.5%) | 87.5% | 0.0157 | Correct chalk |
| 7 | (11) VCU def (6) North Carolina | 82-78 OT | +4 | VCU (60.8%) | 60.8% | 0.1537 | **UPSET PICK HIT** |
| 8 | (2) Houston def (15) Idaho | 78-47 | +31 | Houston (98.2%) | 98.2% | 0.0003 | Correct chalk |
| 9 | (3) Illinois def (14) Penn | 105-70 | +35 | Illinois (92.7%) | 92.7% | 0.0053 | Correct chalk |
| 10 | (10) Texas A&M def (7) St Mary's | 63-50 | +13 | St Mary's (91.5%) | 8.5% | 0.8376 | **MISSED UPSET** |
| 11 | (12) High Point def (5) Wisconsin | 83-82 | +1 | Wisconsin (95.7%) | 4.3% | 0.9160 | **MISSED UPSET** |
| 12 | (4) Arkansas def (13) Hawaii | 97-78 | +19 | Arkansas (97.1%) | 97.1% | 0.0008 | Correct chalk |
| 13 | (11) Texas def (6) BYU | 79-71 | +8 | BYU (92.4%) | 11.7% | 0.7792 | **MISSED UPSET** |
| 14 | (3) Gonzaga def (14) Kennesaw | 73-64 | +9 | Gonzaga (94.8%) | 94.8% | 0.0027 | Correct chalk |
| 15 | (1) Michigan def (16) Howard | 101-80 | +21 | Michigan (97.4%) | 96.9% | 0.0010 | Correct chalk |
| 16 | (9) St Louis def (8) Georgia | 102-77 | +25 | St Louis (63.7%) | 63.7% | 0.1320 | **UPSET PICK HIT** |

**Round of 64 record: 11/16 (68.8%)**
**Mean Brier score: 0.2472**

---

## Deep Analysis of Wrong Predictions

### WRONG #1: (6) Louisville 83, (11) South Florida 79
**Category: Wrong upset pick | Brier: 0.4330**
**Our prediction: South Florida wins (65.8%)**

#### Feature Comparison
| Metric | Louisville (Winner) | South Florida (Our Pick) | Edge |
|--------|-------------------|------------------------|------|
| Elo | 1790.6 | 1801.3 | USF +10.7 |
| ADJOE | 124.0 | 116.8 | Louisville +7.2 |
| ADJDE | 98.2 | 101.4 | Louisville +3.2 |
| BARTHAG | 0.94 | 0.84 | Louisville +0.10 |
| eFG% | 56% | 51% | Louisville +5% |
| Coach Tourney Apps | 5 | 0 | Louisville +5 |

#### What Happened
Louisville built a massive 23-point lead behind Isaac McKneely's historic shooting night (23 points, 7-of-10 from three). USF mounted a furious comeback fueled by full-court pressure that exploited Louisville's 22 turnovers, but ran out of time. Louisville was missing starting PG Mikel Brown Jr. (5th straight game with back issues), which contributed to the turnover problems.

#### Why We Were Wrong
Our model slightly favored South Florida's Elo (1801 vs 1791), but Louisville was clearly the better team by almost every other metric: ADJOE (+7.2), BARTHAG (+0.10), eFG% (+5%). The model overweighted Elo and win percentage while underweighting Louisville's massive offensive efficiency advantage. Our upset pick here was a **calibration error** - the model was only at 65.8% and the game was close (4-point final margin), so this wasn't an egregious miss.

#### Miss Category: Calibration error (picked wrong side of a close game)

---

### WRONG #2: (9) TCU 66, (8) Ohio State 64
**Category: Missed upset (8v9 game) | Brier: 0.6713**
**Our prediction: Ohio St wins (81.9%)**

#### Feature Comparison
| Metric | TCU (Winner) | Ohio St (Our Pick) | Edge |
|--------|-------------|-------------------|------|
| Elo | 1753.3 | 1770.4 | OSU +17.1 |
| NetEff | 8.71 | 10.26 | OSU +1.55 |
| Win% | 67% | 64% | TCU +3% |
| Coach Tourney Apps | 15 | 0 | TCU +15 |
| Coach Tourney Wins | 14 | 0 | TCU +14 |
| Team WAR | 25.6 | 37.7 | OSU +12.1 |

#### What Happened
TCU dominated the first half (39-24) behind 7-of-13 three-point shooting, then collapsed offensively in the second half (missed 18 of first 22 shots). Ohio State stormed back to take a 55-50 lead. TCU regrouped, and David Punch (16 pts, 13 reb) found Xavier Edmonds for a go-ahead layup with 4.3 seconds left. Bruce Thornton's desperation heave hit all backboard.

#### Why We Were Wrong
**81.9% confidence in an 8-vs-9 game is indefensible.** Historical 8-vs-9 games are essentially coin flips (~52% for the 8 seed historically). Our model was nearly 30 percentage points more confident than it should have been. Ohio St had a slight edge in most metrics, but the gap was tiny. Meanwhile, TCU's Jamie Dixon brought 15 tournament appearances and 14 wins to Ohio State's coach with zero - a massive experience factor the model underweighted.

#### Miss Category: Systematic calibration error - model doesn't properly calibrate 8v9 matchups

---

### WRONG #3: (10) Texas A&M 63, (7) St. Mary's 50
**Category: Missed upset | Brier: 0.8376**
**Our prediction: St. Mary's wins (91.5%)**

#### Feature Comparison
| Metric | Texas A&M (Winner) | St. Mary's (Our Pick) | Edge |
|--------|--------------------|----------------------|------|
| Elo | 1706.8 | 1869.3 | StM +162.5 |
| NetEff | 10.82 | 18.31 | StM +7.49 |
| Team WAR | 50.4 | 34.8 | **A&M +15.6** |
| Star WAR | 3.50 | 2.10 | **A&M +1.40** |
| Sr% | 58% | 10% | **A&M +48%** |
| Avg Class | 3.42 | 2.30 | **A&M +1.12** |
| ADJOE | 119.9 | 119.4 | Tied |

#### What Happened
Texas A&M led wire-to-wire in a dominant defensive performance. They forced a 10-second violation on St. Mary's very first possession, jumped to a 9-0 lead, and held the Gaels scoreless for nearly 4.5 minutes. By halftime it was 37-26. The lead hit 20 with 10 minutes left. St. Mary's scored only 50 points - their lowest output all season. Rashaun Agee dominated inside with 22 points and 9 rebounds.

#### Why We Were Wrong
The Elo gap (162.5 points!) drove the model to 91.5% confidence, but this masked critical factors:

1. **Experience gap was enormous**: A&M was 58% seniors vs St. Mary's 10% seniors. In March Madness, experience matters immensely.
2. **Team WAR strongly favored A&M**: 50.4 vs 34.8 - A&M had significantly more player talent despite the worse record.
3. **Elo distortion**: St. Mary's 27-6 record (0.84 win%) and 1869 Elo were inflated by WCC conference play. Their SOS (0.62) was respectable but their Elo overstated their quality relative to A&M's SEC-hardened roster.
4. **Physical mismatch**: A&M's lineup featured experienced big men (Zach Clemence, Rashaun Agee) who physically overwhelmed St. Mary's smaller roster.

#### Miss Category: Systematic model blind spot - Elo/win% inflation from weaker conferences + ignoring experience

---

### WRONG #4: (12) High Point 83, (5) Wisconsin 82
**Category: Missed upset | Brier: 0.9160 (WORST)**
**Our prediction: Wisconsin wins (95.7%)**

#### Feature Comparison
| Metric | High Point (Winner) | Wisconsin (Our Pick) | Edge |
|--------|---------------------|---------------------|------|
| Elo | 1752.4 | 1824.8 | UW +72.4 |
| NetEff | **20.17** | 10.01 | **HP +10.16** |
| DefEff | **98.88** | 107.20 | **HP +8.32** |
| Team WAR | **48.2** | 39.7 | **HP +8.50** |
| Win% | **87%** | 71% | **HP +16%** |
| Sr% | **64%** | 30% | **HP +34%** |
| BARTHAG | 0.70 | 0.93 | UW +0.23 |
| ADJOE | 115.7 | 127.2 | UW +11.5 |
| Seed | 12 | 5 | UW better seed |

#### What Happened
Wisconsin opened on a 15-5 run but High Point clawed back to trail 41-39 at halftime. Wisconsin extended the lead to 70-62 with 7:08 remaining, but High Point erupted on a run led by Rob Martin, Chase Johnston, and Cam'Ron Hunter hitting five consecutive shots. Wisconsin retook the lead 82-81 in the final minute, but Chase Johnston - who had not made a single two-point basket all season (0-for-4) - hit a fastbreak layup with 11.2 seconds left for the 83-82 lead. Nick Boyd's shot was blocked to seal it.

**Key Players:**
- Rob Martin (High Point): 23 points, 10 assists
- Chase Johnston (High Point): 14 points off bench, hit game-winning layup (his first 2-pointer of the season!)
- Nick Boyd (Wisconsin): 27 points, 5 reb, 6 ast
- John Blackwell (Wisconsin): 22 points, 10 rebounds

#### Why We Were Wrong - This Was Our Most Preventable Miss

**95.7% confidence was absurdly overconfident.** Look at the feature comparison: High Point had BETTER net efficiency (+10.16), BETTER defensive efficiency (+8.32), BETTER team WAR (+8.5), a HIGHER win percentage (+16%), and far more experience (64% seniors vs 30%). The only things favoring Wisconsin were Elo, BARTHAG, ADJOE, and seed.

Our model was essentially saying: "Seed 5 vs Seed 12 + higher Elo = 96% lock." But the underlying team quality metrics told a completely different story. High Point was arguably the better team on paper by several key measures, and the model ignored this.

**The BARTHAG discrepancy is revealing**: BARTHAG (0.70 vs 0.93) strongly favored Wisconsin despite High Point having much better efficiency metrics. BARTHAG incorporates strength of schedule heavily, and High Point's Big South schedule produced a misleading gap. But the raw efficiency numbers told the truth.

#### Miss Category: Systematic model blind spot - seed/Elo overweighting, failure to properly weight mid-major quality metrics

---

### WRONG #5: (11) Texas 79, (6) BYU 71
**Category: Missed upset | Brier: 0.7792**
**Our prediction: BYU wins (92.4%, via bracket prediction of BYU over NC State/11-seed)**
**Model's actual P(Texas wins over BYU): 11.7%**

#### Feature Comparison
| Metric | Texas (Winner) | BYU (Our Pick) | Edge |
|--------|---------------|----------------|------|
| Elo | 1667.0 | 1760.2 | BYU +93.2 |
| Team WAR | **85.5** | 42.1 | **Texas +43.4** |
| Coach Tourney Apps | **13** | 1 | **Texas +12** |
| Coach Tourney Wins | **22** | 2 | **Texas +20** |
| Sr% | **52%** | 18% | **Texas +34%** |
| Avg Class | **3.24** | 2.36 | **Texas +0.88** |
| NetEff | 8.34 | 11.89 | BYU +3.55 |
| Win% | 55% | 68% | BYU +13% |
| ADJOE | 124.0 | 124.7 | Tied |

#### What Happened
Texas dominated from the start - BYU led for only 22 seconds the entire game. Matas Vokietaitis controlled the paint with 23 points and 16 rebounds (9 offensive boards), while Texas doubled BYU's 3-point production. AJ Dybantsa put up a monster 35-point, 10-rebound effort (becoming the first freshman since Steph Curry in 2007 to score 30+ in his first NCAA Tournament game), but got zero help from teammates. BYU's bench scored zero points. BYU shot just 18% from three.

**Key context**: AJ Dybantsa is the projected #1 overall pick in the 2026 NBA Draft. This was widely viewed as his "one and done" NCAA appearance.

#### Why We Were Wrong
1. **Team WAR gap was the largest of any game**: Texas had 85.5 Team WAR vs BYU's 42.1 - a 43.4 difference. This was a clear signal the model ignored.
2. **BYU was dangerously young**: Only 18% seniors, average class number 2.36 (freshman/sophomore heavy). In high-pressure tournament games, experience matters enormously.
3. **Coaching experience**: Texas coach had 13 tournament appearances and 22 wins. BYU's coach had 1 appearance and 2 wins.
4. **Star dependency**: BYU was heavily reliant on Dybantsa (Star WAR only 1.9, but star usage was high), and when the supporting cast failed (zero bench points, 18% from three), they had no fallback.
5. **Richie Saunders injury**: BYU was missing Richie Saunders, their second-best player (noted in our injury analysis with 2.8 WAR impact). This compounded the one-man-show problem.

#### Miss Category: Multiple blind spots - experience/WAR underweighting + one-player dependency not modeled + injury impact

---

## Games We Got Right - Brief Analysis

### Correct Chalk Picks (9 games)

**1. (1) Duke 71, (16) Siena 65 - P(Duke)=99.4% | Brier: 0.0000**
Closer than expected! Duke trailed by as many as 13 in the second half before Cameron Boozer (22 pts, 13 reb) led the comeback. Duke was missing Caleb Foster and Patrick Ngongba. Our injury analysis flagged this and adjusted from 99.4% down to 86.6%. The game proved the injury adjustment was directionally correct - the 6-point final margin matches ~87% confidence better than 99.4%.

**2. (3) Michigan St 92, (14) N Dakota St 67 - P(MSU)=95.0% | Brier: 0.0025**
Dominant chalk win. MSU led by as many as 28. Carson Cooper scored 20 on 7-9 shooting.

**3. (4) Nebraska 76, (13) Troy 47 - P(Neb)=93.9% | Brier: 0.0037**
Blowout. Nebraska hit 14 three-pointers (Pryce Sandfort 23 pts). The 29-point margin exceeded even our high confidence.

**4. (5) Vanderbilt 78, (12) McNeese 68 - P(Vandy)=87.5% | Brier: 0.0157**
Comfortable win. Tyler Tanner led with 26 points.

**5. (2) Houston 78, (15) Idaho 47 - P(Houston)=98.2% | Brier: 0.0003**
31-point blowout. Led 48-24 at half. Textbook chalk.

**6. (3) Illinois 105, (14) Penn 70 - P(Illinois)=92.7% | Brier: 0.0053**
Dominant. David Mirkovic with 29 points and 17 rebounds (!). 35-point margin.

**7. (4) Arkansas 97, (13) Hawaii 78 - P(Ark)=97.1% | Brier: 0.0008**
Arkansas brought SEC tournament momentum. 19-point win.

**8. (3) Gonzaga 73, (14) Kennesaw 64 - P(Zaga)=94.8% | Brier: 0.0027**
Graham Ike led with 19 points and 8 rebounds. Gonzaga was missing Braden Huff but still handled it.

**9. (1) Michigan 101, (16) Howard 80 - P(Mich)=96.9% | Brier: 0.0010**
Michigan shot 67.3% from the field. 21-point win despite Howard's excitement from their historic First Four victory.

### Correct Upset Picks (2 games)

**10. (11) VCU 82, (6) North Carolina 78 OT - P(VCU)=60.8% | Brier: 0.1537**
**Our model called this upset.** VCU completed the sixth-largest comeback in NCAA Tournament history and the largest ever in the first round, rallying from 19 points down. Terrence Hill Jr. scored a career-high 34 points. UNC's Caleb Wilson was out injured. Our injury analysis noted this and adjusted slightly in VCU's favor.

This was a great call by the model. VCU's Elo (1755 vs UNC's 1706), efficiency metrics, and overall profile justified the upset pick. The 60.8% confidence was appropriately cautious for an upset. Brier of 0.1537 is solid.

**11. (9) St. Louis 102, (8) Georgia 77 - P(StL)=63.7% | Brier: 0.1320**
**Another great upset call.** St. Louis dominated from start to finish, leading by 17 at half. The 25-point blowout suggests our model's 63.7% confidence was actually too conservative - this should have been higher.

---

## Synthesis

### Record Summary
| Category | Record | Percentage |
|----------|--------|------------|
| First Four | 1/4 | 25% |
| Round of 64 (Thursday) | 11/16 | 68.8% |
| **Total** | **12/20** | **60.0%** |
| Correct chalk picks | 9/9 | 100% |
| Upset picks that hit | 2/3 | 66.7% |
| Upsets we missed | 4 | - |

### Brier Score Analysis
| Segment | Mean Brier | Games |
|---------|-----------|-------|
| First Four | 0.3749 | 4 |
| R64 Thursday | 0.2472 | 16 |
| All Day 1 | 0.2727 | 20 |
| Correct picks only | 0.0291 | 11 |
| Wrong picks only | 0.7274 | 5 |

Our mean Brier of 0.2472 for the R64 is significantly worse than our CV score of 0.050. This is partly expected (tournament variance) but the three 0.8+ Brier scores are the real problem.

### Brier Score Breakdown - Top 5 Worst Games
| Game | Brier | Our Confidence (in loser) |
|------|-------|--------------------------|
| High Point def Wisconsin | 0.9160 | 95.7% (Wisconsin) |
| Texas A&M def St. Mary's | 0.8376 | 91.5% (St. Mary's) |
| Texas def BYU | 0.7792 | 92.4% (BYU) |
| TCU def Ohio St | 0.6713 | 81.9% (Ohio St) |
| Louisville def South Florida | 0.4330 | 65.8% (South Florida) |

These 5 games account for 3.6371 of our total 3.9549 Brier sum (92% of the error from 31% of games).

### Common Themes in Our Misses

**1. Elo/Seed Overweighting**
The model's biggest blind spot: it gives enormous weight to Elo ratings and seed numbers, which are themselves derived from overall record and conference strength. When a team has a strong record in a weaker conference (St. Mary's in WCC, Wisconsin with a loaded but inconsistent B1G season), Elo inflates their quality. Meanwhile, teams with worse records but better underlying metrics (Texas A&M, High Point) get penalized.

**2. Experience Matters in March**
In our three biggest misses, the winning team had dramatically more experience:
- Texas A&M: 58% seniors vs St. Mary's 10%
- High Point: 64% seniors vs Wisconsin 30%
- Texas: 52% seniors vs BYU 18%

The model includes Avg_ClassNum and Sr_Pct as features, but they're clearly underweighted relative to their actual importance in tournament settings.

**3. Team WAR Undervalued**
All three biggest upsets had the winner with significantly higher Team WAR:
- Texas A&M: 50.4 vs 34.8
- High Point: 48.2 vs 39.7
- Texas: 85.5 vs 42.1

The model has Team_WAR as a feature but Elo dominates the prediction, overriding the player-level signal.

**4. 8v9 Calibration Failure**
The TCU/Ohio State miss (81.9% for Ohio St) exposes a fundamental calibration problem with 8-vs-9 matchups. Historically these are near coin flips (~52-48), but our model treated it like an 80/20 game.

**5. Coaching Experience Not Modeled Well Enough**
TCU's Jamie Dixon (15 tournament apps, 14 wins) vs Ohio State's first-year tournament coach. Texas's coach (13 apps, 22 wins) vs BYU's (1 app). This experience gap matters enormously in March and our model underweights it.

### What Data Could Have Helped

1. **Betting lines/market odds**: Vegas lines would have flagged TCU/Ohio St as a coin flip and High Point as a potential upset. Market information aggregates much more data than our model sees.

2. **Lineup-adjusted efficiency**: Knowing not just that injuries happened, but how the remaining lineup performs together (lineups data from Synergy or similar).

3. **Momentum/form features**: Texas won 4 of their last 5 entering the tournament despite their 55% overall record. Hot-streak features would have helped.

4. **Conference tournament performance**: Arkansas rode SEC tournament momentum. Texas came through the First Four on a high.

5. **Matchup-specific features**: Texas A&M's size advantage over St. Mary's, BYU's dependency on a single player (Dybantsa) - these require more granular modeling.

6. **Public perception/bracket data**: High Point was literally the most-picked 12-over-5 upset in ESPN bracket pools (we found this in research). The wisdom of crowds had useful signal we ignored.

### Upset Picks Scorecard
| Pick | Confidence | Result | Notes |
|------|-----------|--------|-------|
| (11) South Florida over (6) Louisville | 65.8% | **MISS** | Louisville won 83-79 |
| (11) VCU over (6) North Carolina | 60.8% | **HIT** | VCU won 82-78 OT - historic comeback |
| (12) Akron over (5) Texas Tech | 72.7% | Pending (Friday) | |
| (10) Santa Clara over (7) Kentucky | 70.4% | Pending (Friday) | |
| (9) St. Louis over (8) Georgia | 63.7% | **HIT** | StL won 102-77 blowout |
| (9) Utah St over (8) Villanova | 94.3% | Pending (Friday) | |

**Thursday upset picks: 2/3 (66.7%)** - VCU and St. Louis were excellent calls.

### Upsets We Missed (Didn't Predict)
| Game | Our Prediction | What Happened |
|------|---------------|---------------|
| (9) TCU def (8) Ohio St | Ohio St at 81.9% | TCU won 66-64 on last-second layup |
| (10) Texas A&M def (7) St. Mary's | St. Mary's at 91.5% | A&M won 63-50 wire-to-wire |
| (12) High Point def (5) Wisconsin | Wisconsin at 95.7% | HP won 83-82 on game-winner |
| (11) Texas def (6) BYU | BYU at 92.4% | Texas won 79-71 behind Vokietaitis |

### If We Could Go Back: Model Improvements

1. **Recalibrate seed-matchup priors**: Force the model to respect historical upset rates. An 8v9 game should never be >65% for either side. A 5v12 should cap around 80%.

2. **Increase weight on Team WAR and experience features**: The player-level data we already have (Team_WAR, Sr_Pct, Avg_ClassNum) contains exactly the signal that would have flagged High Point, Texas A&M, and Texas as dangerous underdogs.

3. **Conference strength adjustment for Elo**: St. Mary's 1869 Elo from the WCC should be discounted relative to Texas A&M's 1707 from the SEC. A "conference multiplier" on Elo would help.

4. **Add market data**: Even just using the spread as a feature would dramatically improve calibration.

5. **Add coaching tournament experience as a more prominent feature**: It's in the model but clearly underweighted.

6. **Star dependency metric**: A feature measuring "what percentage of team output comes from the top player" would flag teams like BYU (Dybantsa-dependent) as high-variance.

---

## Visualizations

See `results/figures/`:
- `16_day1_prediction_accuracy.png` - Model confidence vs outcomes for all 16 Thursday games
- `17_day1_wrong_picks_features.png` - Feature comparison for our 3 biggest misses
- `18_day1_upset_picks.png` - Upset picks scorecard

---

## Friday Games Preview (March 20)

These 16 games are scheduled for today. Our predictions:

| Game | Our Pick | Confidence | Upset? |
|------|----------|------------|--------|
| (2) Connecticut vs (15) Furman | Connecticut | 98.1% | No |
| (4) Kansas vs (13) Cal Baptist | Kansas | 90.9% | No |
| (5) St John's vs (12) Northern Iowa | St John's | 97.3% | No |
| (7) UCLA vs (10) UCF | UCLA | 96.1% | No |
| (1) Florida vs (16) Prairie View | Florida | ~99% | No |
| (8) Clemson vs (9) Iowa | Clemson | 79.7% | No |
| (2) Iowa St vs (15) Tennessee St | Iowa St | 95.9% | No |
| (3) Virginia vs (14) Wright St | Virginia | 97.1% | No |
| (4) Alabama vs (13) Hofstra | Alabama | 85.7% | No |
| (6) Tennessee vs (11) Miami OH | Tennessee | 56.6% | No |
| (10) Santa Clara vs (7) Kentucky | Santa Clara | 70.4% | Yes |
| (12) Akron vs (5) Texas Tech | Akron | 72.7% | Yes |
| (1) Arizona vs (16) LIU Brooklyn | Arizona | 99.1% | No |
| (2) Purdue vs (15) Queens NC | Purdue | 93.7% | No |
| (7) Miami FL vs (10) Missouri | Miami FL | 94.7% | No |
| (9) Utah St vs (8) Villanova | Utah St | 94.3% | Yes |

**Watch for**: Based on Thursday's lessons, any game where the underdog has significantly higher Team WAR, more experience (Sr%), or better net efficiency despite lower Elo/seed should be flagged. The Clemson/Iowa game (79.7% for Clemson) has similar 8v9 calibration concerns as TCU/Ohio State.

---

*Analysis generated by SSA March Madness prediction pipeline. All predictions from `preds_lgbm.parquet`. Team features from `team_features.parquet`. Player data from `barttorvik_players_2026.csv`.*
