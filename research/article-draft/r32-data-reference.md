# Full Tournament Data Reference - Through Round of 32

Generated: 2026-03-23. All predictions from `preds_lgbm.parquet` (LightGBM model). Brier = (1 - P(actual winner))^2.

---

## Overall Record

| Round | Record | Pct | Mean Brier | Total Brier |
|-------|--------|-----|------------|-------------|
| First Four | 1/4 | 25.0% | 0.3749 | 1.4996 |
| R64 Thursday | 11/16 | 68.8% | 0.2472 | 3.9549 |
| R64 Friday | 13/16 | 81.2% | 0.1183 | 1.8920 |
| R32 Saturday | 6/8 | 75.0% | 0.2292 | 1.8332 |
| R32 Sunday | 6/8 | 75.0% | 0.2043 | 1.6346 |
| **R64 Total** | **24/32** | **75.0%** | **0.1827** | **5.8469** |
| **R32 Total** | **12/16** | **75.0%** | **0.2167** | **3.4678** |
| **Bracket games (R64+R32)** | **36/48** | **75.0%** | **0.1940** | **9.3147** |
| **All incl. First Four** | **37/52** | **71.2%** | **0.2080** | **10.8143** |

---

## Every Game with Predictions

### First Four (March 17-18)

| # | Winner | Seed | Loser | Seed | Score | P(Winner) | Correct? | Brier |
|---|--------|------|-------|------|-------|-----------|----------|-------|
| 1 | Howard | 16 | UMBC | 16 | 86-83 | 34.2% | NO | 0.4328 |
| 2 | Texas | 11 | NC State | 11 | 68-66 | 31.1% | NO | 0.4747 |
| 3 | Prairie View | 16 | Lehigh | 16 | 67-55 | 23.5% | NO | 0.5853 |
| 4 | Miami OH | 11 | SMU | 11 | 89-79 | 91.7% | YES | 0.0069 |

### Round of 64 - Thursday, March 19

| # | Winner | Seed | Loser | Seed | Score | P(Winner) | Correct? | Brier | Notes |
|---|--------|------|-------|------|-------|-----------|----------|-------|-------|
| 1 | Duke | 1 | Siena | 16 | 71-65 | 99.4% | YES | 0.0000 | Closer than expected; Duke missing Foster + Ngongba |
| 2 | Michigan St | 3 | N Dakota St | 14 | 92-67 | 95.0% | YES | 0.0025 | Dominant |
| 3 | Louisville | 6 | South Florida | 11 | 83-79 | 34.2% | **NO** | 0.4330 | Wrong upset pick. McKneely 23 pts, 7/10 from 3 |
| 4 | TCU | 9 | Ohio St | 8 | 66-64 | 18.1% | **NO** | 0.6713 | 81.9% for OSU in an 8v9 game. Edmonds layup 4.3 sec left |
| 5 | Nebraska | 4 | Troy | 13 | 76-47 | 93.9% | YES | 0.0037 | Blowout. Sandfort 23 pts |
| 6 | Vanderbilt | 5 | McNeese St | 12 | 78-68 | 87.5% | YES | 0.0157 | Comfortable |
| 7 | VCU | 11 | North Carolina | 6 | 82-78 OT | 60.8% | YES | 0.1537 | **UPSET PICK HIT.** Largest first-round comeback in tourney history (19 pts). Hill Jr. 34 pts |
| 8 | Houston | 2 | Idaho | 15 | 78-47 | 98.2% | YES | 0.0003 | 31-pt blowout |
| 9 | Illinois | 3 | Penn | 14 | 105-70 | 92.7% | YES | 0.0053 | Mirkovic 29 pts, 17 reb |
| 10 | Texas A&M | 10 | St. Mary's | 7 | 63-50 | 8.5% | **NO** | 0.8376 | A&M led wire-to-wire. Agee 22 pts, 9 reb. StM season-low 50 |
| 11 | High Point | 12 | Wisconsin | 5 | 83-82 | 4.3% | **NO** | 0.9160 | Johnston's fastbreak layup 11.2 sec left (first 2-pointer of season) |
| 12 | Arkansas | 4 | Hawaii | 13 | 97-78 | 97.1% | YES | 0.0008 | 19-pt win |
| 13 | Texas | 11 | BYU | 6 | 79-71 | 11.7% | **NO** | 0.7792 | Vokietaitis 23 pts, 16 reb. Dybantsa 35 pts in NBA farewell |
| 14 | Gonzaga | 3 | Kennesaw | 14 | 73-64 | 94.8% | YES | 0.0027 | Ike 19 pts, 8 reb |
| 15 | Michigan | 1 | Howard | 16 | 101-80 | 96.9% | YES | 0.0010 | Michigan shot 67.3% |
| 16 | St. Louis | 9 | Georgia | 8 | 102-77 | 63.7% | YES | 0.1320 | **UPSET PICK HIT.** 25-pt blowout |

**Thursday: 11/16 (68.8%), Mean Brier: 0.2472**

### Round of 64 - Friday, March 20

| # | Winner | Seed | Loser | Seed | Score | P(Winner) | Correct? | Brier | Notes |
|---|--------|------|-------|------|-------|-----------|----------|-------|-------|
| 1 | Florida | 1 | Prairie View | 16 | 114-55 | 97.7% | YES | 0.0005 | 59-pt blowout |
| 2 | Purdue | 2 | Queens NC | 15 | 104-71 | 93.7% | YES | 0.0040 | 33-pt win |
| 3 | Iowa St | 2 | Tennessee St | 15 | 108-74 | 95.9% | YES | 0.0016 | 34-pt rout |
| 4 | Connecticut | 2 | Furman | 15 | 82-71 | 98.1% | YES | 0.0004 | |
| 5 | Arizona | 1 | LIU Brooklyn | 16 | 92-58 | 99.1% | YES | 0.0001 | 34-pt win |
| 6 | Alabama | 4 | Hofstra | 13 | 90-70 | 85.7% | YES | 0.0206 | |
| 7 | Kansas | 4 | Cal Baptist | 13 | 68-60 | 90.9% | YES | 0.0084 | |
| 8 | Virginia | 3 | Wright St | 14 | 82-73 | 97.1% | YES | 0.0008 | |
| 9 | Texas Tech | 5 | Akron | 12 | 91-71 | 27.3% | **NO** | 0.5281 | Wrong upset pick (picked Akron at 72.7%). TT won by 20 |
| 10 | St. John's | 5 | Northern Iowa | 12 | 79-53 | 97.3% | YES | 0.0007 | |
| 11 | Tennessee | 6 | Miami OH | 11 | 78-56 | 56.6% | YES | 0.1887 | Close call in probability, easy win on court |
| 12 | Miami FL | 7 | Missouri | 10 | 80-66 | 94.7% | YES | 0.0028 | |
| 13 | UCLA | 7 | UCF | 10 | 75-71 | 96.1% | YES | 0.0016 | Close game (4 pts) but model was confident |
| 14 | Kentucky | 7 | Santa Clara | 10 | 89-84 OT | 29.6% | **NO** | 0.4951 | Wrong upset pick (picked Santa Clara at 70.4%). Oweh halfcourt buzzer-beater forced OT, then hit go-ahead FTs. 35 pts career high |
| 15 | Iowa | 9 | Clemson | 8 | 67-61 | 20.3% | **NO** | 0.6354 | Picked Clemson at 79.7% in an 8v9 game. Same calibration problem as TCU/OSU |
| 16 | Utah St | 9 | Villanova | 8 | 86-76 | 94.3% | YES | 0.0032 | **UPSET PICK HIT** (8v9 - we had USU heavily favored) |

**Friday: 13/16 (81.2%), Mean Brier: 0.1183**

### Round of 32 - Saturday, March 21

| # | Winner | Seed | Loser | Seed | Score | P(Winner) | Correct? | Brier | Notes |
|---|--------|------|-------|------|-------|-----------|----------|-------|-------|
| 1 | Duke | 1 | TCU | 9 | 81-58 | 92.8% | YES | 0.0052 | No. 1 overall seed cruises |
| 2 | Michigan St | 3 | Louisville | 6 | 77-69 | 84.2% | YES | 0.0251 | Coen Carr 21 pts, 10 reb |
| 3 | Houston | 2 | Texas A&M | 10 | 88-57 | 98.7% | YES | 0.0002 | 31-pt blowout |
| 4 | Texas | 11 | Gonzaga | 3 | 74-68 | 3.9% | **NO** | 0.9227 | **UPSET.** First Four team to Sweet 16. Camden Heide's 3 iced it |
| 5 | Illinois | 3 | VCU | 11 | 76-55 | 76.8% | YES | 0.0539 | |
| 6 | Nebraska | 4 | Vanderbilt | 5 | 74-72 | 10.9% | **NO** | 0.7945 | **UPSET.** Frager game-winning layup with 2.2 sec left. Nebraska reaches first-ever Sweet 16 |
| 7 | Arkansas | 4 | High Point | 12 | 94-88 | 82.6% | YES | 0.0303 | High Point (12-seed) kept it close to the end |
| 8 | Michigan | 1 | St. Louis | 9 | 95-72 | 96.2% | YES | 0.0014 | Lendeborg 25 pts. 9 team blocks (program tourney record) |

**Saturday: 6/8 (75.0%), Mean Brier: 0.2292**

### Round of 32 - Sunday, March 22

| # | Winner | Seed | Loser | Seed | Score | P(Winner) | Correct? | Brier | Notes |
|---|--------|------|-------|------|-------|-----------|----------|-------|-------|
| 1 | Purdue | 2 | Miami FL | 7 | 79-69 | 97.7% | YES | 0.0005 | |
| 2 | Iowa St | 2 | Kentucky | 7 | 82-63 | 95.5% | YES | 0.0020 | Dominant 19-pt win |
| 3 | St. John's | 5 | Kansas | 4 | 67-65 | 95.2% | YES | 0.0024 | Dylan Darling buzzer-beating driving layup. Model was right! |
| 4 | Tennessee | 6 | Virginia | 3 | 79-72 | 19.3% | **NO** | 0.6509 | **UPSET.** Model had Virginia at 80.7% |
| 5 | Iowa | 9 | Florida | 1 | 73-72 | 2.9% | **NO** | 0.9432 | **MASSIVE UPSET.** Folgueiras go-ahead 3 with 4.5 sec left. First 1-seed eliminated |
| 6 | Arizona | 1 | Utah St | 9 | 78-66 | 92.1% | YES | 0.0063 | |
| 7 | Connecticut | 2 | UCLA | 7 | 73-57 | 86.2% | YES | 0.0191 | Karaban 27 pts |
| 8 | Alabama | 4 | Texas Tech | 5 | 90-65 | 89.9% | YES | 0.0102 | 25-pt dominant win |

**Sunday: 6/8 (75.0%), Mean Brier: 0.2043**

---

## All 12 Wrong Picks (Ranked by Brier)

| Rank | Round | Game | Our Pick (Conf.) | Actual Winner | Brier | Key Story |
|------|-------|------|------------------|---------------|-------|-----------|
| 1 | R32 Sun | Iowa 73, Florida 72 | Florida (97.1%) | Iowa | 0.9432 | Folgueiras' 3 with 4.5 sec. First 1-seed out. |
| 2 | R32 Sat | Texas 74, Gonzaga 68 | Gonzaga (96.1%) | Texas | 0.9227 | First Four team to Sweet 16. Texas won 3 straight games we called wrong. |
| 3 | R64 Thu | High Point 83, Wisconsin 82 | Wisconsin (95.7%) | High Point | 0.9160 | Johnston's first 2-pointer of season wins it. HP had better NetEff. |
| 4 | R64 Thu | Texas A&M 63, St. Mary's 50 | St. Mary's (91.5%) | Texas A&M | 0.8376 | Wire-to-wire. Agee 22/9. StM season-low 50 pts. |
| 5 | R32 Sat | Nebraska 74, Vanderbilt 72 | Vanderbilt (89.1%) | Nebraska | 0.7945 | Frager layup at 2.2 sec. Nebraska reaches first-ever Sweet 16. |
| 6 | R64 Thu | Texas 79, BYU 71 | BYU (92.4%) | Texas | 0.7792 | Dybantsa's 35-pt NBA farewell wasn't enough. Texas WAR: 85.5. |
| 7 | R64 Thu | TCU 66, Ohio St 64 | Ohio St (81.9%) | TCU | 0.6713 | 8v9 game at 82% confidence. Edmonds layup at 4.3 sec. |
| 8 | R32 Sun | Tennessee 79, Virginia 72 | Virginia (80.7%) | Tennessee | 0.6509 | Tennessee WAR 88.1 vs Virginia 30.8. Coach: 29 tourney apps vs 3. |
| 9 | R64 Fri | Iowa 67, Clemson 61 | Clemson (79.7%) | Iowa | 0.6354 | Another 8v9 game with overconfident pick. |
| 10 | R64 Fri | Texas Tech 91, Akron 71 | Akron (72.7%) | Texas Tech | 0.5281 | Wrong upset pick. TT won by 20. |
| 11 | R64 Fri | Kentucky 89, Santa Clara 84 OT | Santa Clara (70.4%) | Kentucky | 0.4951 | Wrong upset pick. Oweh halfcourt buzzer-beater forced OT. |
| 12 | R64 Thu | Louisville 83, South Florida 79 | S. Florida (65.8%) | Louisville | 0.4330 | Wrong upset pick. Close game, mild error. |

**These 12 misses account for 8.61 of 9.31 total Brier (92.4% of all prediction error).**
**Top 5 misses alone: 4.41 of 9.31 (47.4% of error from 10.4% of games).**

---

## Upset Pick Scorecard

### R64 Upset Picks We Made

| Pick | Confidence | Result | Brier | Notes |
|------|-----------|--------|-------|-------|
| (11) VCU over (6) North Carolina | 60.8% | **HIT** | 0.154 | Largest first-round comeback ever |
| (9) St. Louis over (8) Georgia | 63.7% | **HIT** | 0.132 | 25-pt blowout |
| (11) South Florida over (6) Louisville | 65.8% | MISS | 0.433 | Louisville won 83-79 |
| (10) Santa Clara over (7) Kentucky | 70.4% | MISS | 0.495 | Kentucky won 89-84 OT (halfcourt buzzer) |
| (12) Akron over (5) Texas Tech | 72.7% | MISS | 0.528 | TT dominated 91-71 |
| (9) Utah St over (8) Villanova | 94.3% | **HIT** | 0.003 | Comfortable 10-pt win |

**R64 upset picks: 3/6 (50%)**

### Upsets That Happened That We Missed

| Game | Our Pick (Conf.) | What Happened |
|------|------------------|---------------|
| (9) TCU over (8) Ohio St | Ohio St (81.9%) | 8v9 calibration failure |
| (10) Texas A&M over (7) St. Mary's | St. Mary's (91.5%) | Wire-to-wire domination |
| (12) High Point over (5) Wisconsin | Wisconsin (95.7%) | Game-winning layup at buzzer |
| (11) Texas over (6) BYU | BYU (92.4%) | Texas controlled entire game |
| (9) Iowa over (8) Clemson | Clemson (79.7%) | Another 8v9 miss |
| (11) Texas over (3) Gonzaga | Gonzaga (96.1%) | First Four team beats 3-seed |
| (4) Nebraska over (5) Vanderbilt | Vanderbilt (89.1%) | Buzzer-beater; NEB first Sweet 16 |
| (6) Tennessee over (3) Virginia | Virginia (80.7%) | Tennessee WAR/coaching edge |
| (9) Iowa over (1) Florida | Florida (97.1%) | Last-second 3; first 1-seed out |

---

## Feature Comparisons for Key Misses

### #1: Iowa 73, Florida 72 (R32) - Brier: 0.943

| Feature | Iowa (Winner) | Florida (Our Pick) | Edge |
|---------|--------------|-------------------|------|
| Elo | 1719.0 | 1978.3 | Florida +259 |
| NetEff | 14.4 | 20.1 | Florida +5.7 |
| ADJOE | 122.1 | 126.1 | Florida +4.0 |
| ADJDE | 100.2 | 92.3 | Florida +7.9 (better D) |
| BARTHAG | 0.91 | 0.97 | Florida +0.06 |
| **Team WAR** | **38.0** | **29.9** | **Iowa +8.1** |
| Sr% | 20% | 25% | Florida +5% |
| Coach Tourney Apps | 1 | 3 | Florida +2 |
| Coach Tourney Wins | 1 | 6 | Florida +5 |

**Story**: Florida was genuinely the better team by most metrics. But 97.1% for a 1v9 matchup was absurd overconfidence - historical 1v9 upset rate is ~4.5%. Iowa had higher Team WAR (38.0 vs 29.9). The game was a 1-point affair decided by a single 3-pointer. This is a pure calibration/clipping miss. Even if we picked Florida, anything above ~95% was reckless.

**Key detail**: Alvaro Folgueiras' go-ahead three-pointer with 4.5 seconds left. Iowa first-year coach Fran McCaffery Jr.'s biggest win. Florida was the first No. 1 seed eliminated from the 2026 tournament.

---

### #2: Texas 74, Gonzaga 68 (R32) - Brier: 0.923

| Feature | Texas (Winner) | Gonzaga (Our Pick) | Edge |
|---------|---------------|-------------------|------|
| Elo | 1667.0 | 1933.0 | Gonzaga +266 |
| NetEff | 8.3 | 26.7 | Gonzaga +18.3 |
| ADJOE | 124.0 | 120.3 | Texas +3.7 |
| ADJDE | 106.4 | 94.0 | Gonzaga +12.4 |
| BARTHAG | 0.85 | 0.94 | Gonzaga +0.09 |
| **Team WAR** | **85.5** | **38.7** | **Texas +46.8** |
| **Sr%** | **52%** | **45%** | **Texas +7%** |
| Coach Tourney Apps | 13 | 25 | Gonzaga +12 |
| Coach Tourney Wins | 22 | 44 | Gonzaga +22 |

**Story**: This is the most dramatic WAR signal of the entire tournament. Texas's Team WAR of 85.5 was the highest in the field, more than double Gonzaga's 38.7. But Gonzaga's Elo (1933) and BARTHAG dominated the model. Texas came in as a First Four team (beat NC State, then beat BYU) riding massive momentum. Camden Heide's 3 iced the game.

**Narrative thread**: We were wrong about Texas THREE times:
1. First Four: NC State at 68.9% - Texas won 68-66
2. R64: BYU at 92.4% (Texas 11.7%) - Texas won 79-71
3. R32: Gonzaga at 96.1% (Texas 3.9%) - Texas won 74-68

Each time MORE confident, each time MORE wrong. Texas had the tournament's highest Team WAR and we never listened.

---

### #3: High Point 83, Wisconsin 82 (R64) - Brier: 0.916

| Feature | High Point (Winner) | Wisconsin (Our Pick) | Edge |
|---------|---------------------|---------------------|------|
| Elo | 1752.4 | 1824.8 | Wisconsin +72 |
| **NetEff** | **20.2** | **10.0** | **HP +10.2** |
| ADJOE | 115.7 | 127.2 | Wisconsin +11.5 |
| **ADJDE** | **98.9** | **107.2** | **HP +8.3** |
| BARTHAG | 0.70 | 0.93 | Wisconsin +0.23 |
| **Team WAR** | **48.2** | **39.7** | **HP +8.5** |
| **Win%** | **87%** | **71%** | **HP +16%** |
| **Sr%** | **64%** | **30%** | **HP +34%** |

**Story**: Our most preventable miss. High Point was better than Wisconsin in net efficiency, defensive efficiency, Team WAR, win percentage, and experience. The model saw Wisconsin's 5-seed and 0.93 BARTHAG and called it 95.7%. Chase Johnston - who had not made a single two-point basket all season (0-for-4) - hit a fastbreak layup with 11.2 seconds left for the win.

---

### #4: Texas A&M 63, St. Mary's 50 (R64) - Brier: 0.838

| Feature | Texas A&M (Winner) | St. Mary's (Our Pick) | Edge |
|---------|--------------------|-----------------------|------|
| Elo | 1706.8 | 1869.3 | StM +163 |
| NetEff | 10.8 | 18.3 | StM +7.5 |
| ADJOE | 119.9 | 119.4 | Tied |
| **Team WAR** | **50.4** | **34.8** | **A&M +15.6** |
| **Star WAR** | **3.5** | **2.1** | **A&M +1.4** |
| **Sr%** | **58%** | **10%** | **A&M +48%** |
| **Avg Class** | **3.4** | **2.3** | **A&M +1.1** |
| SOS | 0.55 | 0.62 | StM +0.07 |

**Story**: Elo gap of 163 drove the model to 91.5%, but A&M had massive experience and WAR advantages. St. Mary's Elo was inflated by WCC schedule. A&M led wire-to-wire; Rashaun Agee dominated with 22/9. St. Mary's scored only 50, their season low.

---

### #5: Nebraska 74, Vanderbilt 72 (R32) - Brier: 0.795

| Feature | Nebraska (Winner) | Vanderbilt (Our Pick) | Edge |
|---------|-------------------|-----------------------|------|
| Elo | 1782.8 | 1873.2 | Vanderbilt +90 |
| **NetEff** | **16.1** | **15.4** | **Nebraska +0.7** |
| ADJOE | 117.2 | 127.5 | Vanderbilt +10.3 |
| ADJDE | 93.5 | 99.3 | Nebraska +5.8 |
| BARTHAG | 0.93 | 0.95 | Vanderbilt +0.02 |
| Team WAR | 23.0 | 40.6 | Vanderbilt +17.6 |
| Sr% | 50% | 60% | Vanderbilt +10% |
| Coach Tourney Apps | 5 | 2 | Nebraska +3 |

**Story**: This one doesn't fit the WAR/experience pattern - Vanderbilt was ahead on most metrics. Nebraska won on Braden Frager's layup with 2.2 seconds left, sending them to their first-ever Sweet 16 (they won their first-ever tournament game against Troy in R64). The model had Vanderbilt at 89.1%, which was excessive for a 4v5 matchup (similar to the 8v9 calibration problem). Sometimes buzzer-beaters just happen.

---

### #6: Texas 79, BYU 71 (R64) - Brier: 0.779

| Feature | Texas (Winner) | BYU (Our Pick) | Edge |
|---------|---------------|----------------|------|
| Elo | 1667.0 | 1760.2 | BYU +93 |
| **Team WAR** | **85.5** | **42.1** | **Texas +43.4** |
| **Coach Tourney Wins** | **22** | **2** | **Texas +20** |
| **Sr%** | **52%** | **18%** | **Texas +34%** |
| NetEff | 8.3 | 11.9 | BYU +3.6 |
| ADJOE | 124.0 | 124.7 | Tied |

**Story**: Largest WAR gap in R64. Vokietaitis 23 pts/16 reb. AJ Dybantsa (projected #1 NBA pick) had 35/10 but got no help - BYU bench scored zero. Texas coach had 22 tourney wins vs BYU's 2. Richie Saunders injury compounded BYU's problems.

---

### #7: TCU 66, Ohio State 64 (R64) - Brier: 0.671

**Story**: 81.9% confidence in an 8v9 game that should have been ~52-55% max. Jamie Dixon's 15 tourney appearances vs OSU's zero. Edmonds layup at 4.3 sec.

---

### #8: Tennessee 79, Virginia 72 (R32) - Brier: 0.651

| Feature | Tennessee (Winner) | Virginia (Our Pick) | Edge |
|---------|--------------------|--------------------|------|
| Elo | 1813.6 | 1871.1 | Virginia +58 |
| NetEff | 14.6 | 17.7 | Virginia +3.1 |
| BARTHAG | 0.94 | 0.94 | Tied |
| **Team WAR** | **88.1** | **30.8** | **Tennessee +57.3** |
| **Coach Tourney Apps** | **29** | **3** | **Tennessee +26** |
| **Coach Tourney Wins** | **33** | **1** | **Tennessee +32** |
| Sr% | 21% | 56% | Virginia +35% |

**Story**: Team WAR gap of 57.3 was the second-largest of any game in the tournament (after Texas's 46.8 vs Gonzaga, 43.4 vs BYU). Tennessee's coach (Rick Barnes) had 29 tournament appearances and 33 wins vs Virginia's 3 apps and 1 win. Virginia had the experience edge in roster age (56% seniors), but Tennessee had raw talent depth. Model had Virginia at 80.7% as a 3-seed.

---

### #9: Iowa 67, Clemson 61 (R64) - Brier: 0.635

**Story**: Another 8v9 calibration failure (79.7% for Clemson). Iowa had better NetEff (14.4 vs 11.1), ADJOE (+5.5), and Team WAR (+4.5). Same Iowa team that later upset Florida.

---

## Pattern Analysis Across All Misses

### Where Team WAR flagged the upset winner:

| Game | Winner WAR | Loser WAR | WAR Edge | Brier |
|------|-----------|-----------|----------|-------|
| Texas vs BYU (R64) | 85.5 | 42.1 | +43.4 | 0.779 |
| Texas vs Gonzaga (R32) | 85.5 | 38.7 | +46.8 | 0.923 |
| Tennessee vs Virginia (R32) | 88.1 | 30.8 | +57.3 | 0.651 |
| Texas A&M vs St. Mary's (R64) | 50.4 | 34.8 | +15.6 | 0.838 |
| High Point vs Wisconsin (R64) | 48.2 | 39.7 | +8.5 | 0.916 |
| Iowa vs Florida (R32) | 38.0 | 29.9 | +8.1 | 0.943 |
| Iowa vs Clemson (R64) | 38.0 | 33.5 | +4.5 | 0.635 |

**7 of 12 misses (58%) had the upset winner with higher Team WAR.**

### Where experience (Sr%) flagged the upset winner:

| Game | Winner Sr% | Loser Sr% | Sr Edge | Brier |
|------|-----------|-----------|---------|-------|
| High Point vs Wisconsin | 64% | 30% | +34% | 0.916 |
| Texas A&M vs St. Mary's | 58% | 10% | +48% | 0.838 |
| Texas vs BYU | 52% | 18% | +34% | 0.779 |
| Nebraska vs Vanderbilt | 50% | 60% | -10% | 0.795 |
| Texas vs Gonzaga | 52% | 45% | +7% | 0.923 |

**5 of the top 6 misses had the winner with more seniors (exception: Nebraska).**

### 8v9 / Close-Seed Calibration Problem

| Game | Seeds | Our Confidence | Historical baseline |
|------|-------|---------------|-------------------|
| TCU vs Ohio St | 8v9 | 81.9% for 8 | ~52% for 8 seed |
| Iowa vs Clemson | 8v9 | 79.7% for 8 | ~52% for 8 seed |
| Nebraska vs Vanderbilt | 4v5 | 89.1% for 5 | ~65% for 4 seed |

The model is systematically overconfident in close-seed matchups.

---

## Interesting Stories for Article Narrative

### 1. Texas's Cinderella Run (strongest narrative thread)
- First Four: beat NC State 68-66 (we picked NC State 68.9%)
- R64: beat BYU 79-71 (we picked BYU 92.4%, gave Texas 11.7%)
- R32: beat Gonzaga 74-68 (we picked Gonzaga 96.1%, gave Texas 3.9%)
- **We were wrong about Texas 3 times, each time more confidently wrong**
- Their Team WAR of 85.5 was the HIGHEST in the entire tournament field
- Coach had 13 tourney appearances, 22 wins
- 52% seniors
- Now in the Sweet 16 as an 11-seed from the First Four

### 2. Iowa's 1-Seed Takedown
- Beat Clemson 67-61 in R64 (we gave Clemson 79.7%)
- Beat #1 Florida 73-72 in R32 (we gave Florida 97.1%)
- Folgueiras' three-pointer with 4.5 seconds left
- Florida was the first 1-seed eliminated
- Iowa's Team WAR (38.0) higher than Florida's (29.9) - not a huge gap but notable
- This is more a calibration/clipping story than a "hidden signal" story

### 3. The Chase Johnston Detail (already in article)
- Chase Johnston had 0 two-point field goals all season
- His first one ended Wisconsin's season with 11.2 seconds left
- Great "you can't model everything" detail

### 4. Nebraska Makes History
- First-ever tourney win vs Troy in R64, then first-ever Sweet 16 via buzzer-beater over Vanderbilt
- Model had Vanderbilt at 89.1% for a 4v5 matchup
- This is a calibration story, not a feature story (Vanderbilt was better on paper)

### 5. Dybantsa's 35-Point Farewell
- AJ Dybantsa, projected #1 NBA pick, scored 35 in what was expected to be his only NCAA game
- Texas still won by 8 because BYU's bench scored zero
- Star dependency problem

### 6. Kentucky's Halfcourt Miracle
- Otega Oweh hit a halfcourt buzzer-beater to force OT vs Santa Clara
- We had Santa Clara at 70.4% (wrong upset pick)
- Kentucky won 89-84 in OT
- Then got dispatched by Iowa State 82-63 in R32

### 7. Big Ten Dominance
- 6 Big Ten teams in Sweet 16: Michigan, Michigan State, Purdue, Iowa, Illinois, Nebraska
- Strongest conference showing

---

## Sweet 16 Teams and Our Model's Rankings

| Seed | Team | R64 Result | R32 Result | Model's Avg Win% (pre-tourney) |
|------|------|-----------|-----------|-------------------------------|
| 1 | Duke | 71-65 vs Siena | 81-58 vs TCU | 94.8% |
| 3 | Michigan State | 92-67 vs NDSU | 77-69 vs Louisville | |
| 2 | Houston | 78-47 vs Idaho | 88-57 vs Texas A&M | 90.1% |
| 11 | **Texas** | 79-71 vs BYU | 74-68 vs Gonzaga | Lowest-seeded S16 team |
| 3 | Illinois | 105-70 vs Penn | 76-55 vs VCU | |
| 4 | Nebraska | 76-47 vs Troy | 74-72 vs Vanderbilt | First tourney win + first Sweet 16 |
| 4 | Arkansas | 97-78 vs Hawaii | 94-88 vs High Point | |
| 1 | Michigan | 101-80 vs Howard | 95-72 vs St. Louis | 92.2% |
| 2 | Purdue | 104-71 vs Queens | 79-69 vs Miami FL | |
| 2 | Iowa State | 108-74 vs Tenn St | 82-63 vs Kentucky | |
| 5 | St. John's | 79-53 vs N Iowa | 67-65 vs Kansas | Buzzer-beater over Kansas |
| 6 | Tennessee | 78-56 vs Miami OH | 79-72 vs Virginia | |
| 9 | **Iowa** | 67-61 vs Clemson | 73-72 vs Florida | Knocked out a 1-seed |
| 1 | Arizona | 92-58 vs LIU | 78-66 vs Utah St | 95.1% (model's #1) |
| 2 | UConn | 82-71 vs Furman | 73-57 vs UCLA | |
| 4 | Alabama | 90-70 vs Hofstra | 90-65 vs Texas Tech | |

---

## Deep Dive: Why We Missed Each Game

### Model vs Vegas Comparison

| Game | Our Pick (Conf.) | Vegas Line | Vegas Implied | Gap |
|------|-----------------|------------|---------------|-----|
| Iowa 73, Florida 72 | Florida 97.1% | Florida -10.5 | ~85% | **12 pts too confident** |
| Texas 74, Gonzaga 68 | Gonzaga 96.1% | Gonzaga -6.5 | ~72% | **24 pts too confident** |
| High Point 83, Wisconsin 82 | Wisconsin 95.7% | Wisconsin -10.5 | ~82% | **14 pts too confident** |
| Texas A&M 63, St. Mary's 50 | St. Mary's 91.5% | St. Mary's -2.5 | ~60% | **32 pts too confident** |
| Nebraska 74, Vanderbilt 72 | Vanderbilt 89.1% | Vanderbilt -2.5 | ~58% | **31 pts too confident** |
| Texas 79, BYU 71 | BYU 92.4% | BYU ~-4 | ~65% | **27 pts too confident** |
| TCU 66, Ohio St 64 | Ohio St 81.9% | Ohio St -4.5 | ~62% | **20 pts too confident** |
| Tennessee 79, Virginia 72 | Virginia 80.7% | Tennessee favored | ~45% Virg. | **36 pts too confident** |
| Iowa 67, Clemson 61 | Clemson 79.7% | Iowa -1.5 | ~45% Clem. | **35 pts too confident; OPPOSITE SIDE from Vegas** |
| Texas Tech 91, Akron 71 | Akron 72.7% | Texas Tech -6.5 | ~73% TT | **46 pts wrong; OPPOSITE SIDE from Vegas** |
| Kentucky 89, Santa Clara 84 OT | Santa Clara 70.4% | Kentucky -3.5 | ~60% UK | **30 pts wrong; OPPOSITE SIDE from Vegas** |
| Louisville 83, S. Florida 79 | S. Florida 65.8% | Louisville -4.5 | ~65% Lou. | **31 pts wrong; OPPOSITE SIDE from Vegas** |

**In 4 of 12 misses, we picked the OPPOSITE team from Vegas.** In all 12, we were more extreme than the market.

---

### Root Cause Categories

#### Category 1: Elo/Seed Overweighting (5 games)
**Games**: High Point/Wisconsin, Texas A&M/St. Mary's, Texas/BYU, Texas/Gonzaga, Tennessee/Virginia

The model's heaviest feature (Elo_diff) drove extreme confidence in teams with inflated ratings. In each case, the favored team's Elo was boosted by either a weak conference schedule (St. Mary's in WCC, High Point's BARTHAG penalized by Big South SOS) or seed prestige (Wisconsin 5-seed, BYU 6-seed) that masked inferior underlying quality.

**Key evidence**:
- St. Mary's Elo was 1869 but they were 1-5 in Quad 1 games. Vegas had them as just a 2.5-point favorite.
- High Point had better NetEff, DefEff, Team WAR, Win%, and Sr% than Wisconsin. ESPN BPI gave HP a 24% chance; our model gave 4.3%.
- Gonzaga was missing Braden Huff (second-leading scorer, 17.8 PPG, out since January with dislocated kneecap). Model had no injury data.
- Tennessee was actually FAVORED by Vegas despite being the lower seed, yet our model gave Virginia 80.7%.

#### Category 2: Close-Seed Calibration Failure (3 games)
**Games**: TCU/Ohio St (8v9), Iowa/Clemson (8v9), Nebraska/Vanderbilt (4v5)

The model has no seed-matchup prior constraining predictions toward historical upset rates. It treated these games with 80-89% confidence when history says they should be 52-65%.

**Key evidence**:
- 8v9 games are historically ~52/48. We had Ohio St at 81.9% and Clemson at 79.7%.
- 4v5 second-round games: the 5-seed wins ~45% of the time. We had Vanderbilt at 89.1%.
- In the Iowa/Clemson game, **Vegas actually favored Iowa by 1.5 points** - we were on the opposite side at 79.7% for Clemson.
- 9-seeds went 3-1 against 8-seeds in this tournament.

#### Category 3: Wrong Upset Picks (3 games)
**Games**: Texas Tech/Akron, Kentucky/Santa Clara, Louisville/South Florida

Our model picked the underdog and was wrong. In all three cases, Vegas favored the team that won.

**Key evidence**:
- **Akron**: Our model was seduced by Akron's raw efficiency numbers (NetEff +5.9) without properly adjusting for MAC schedule strength. When SOS-adjusted, the metrics flipped completely: Texas Tech's ADJOE was 126.3 vs Akron's 117.2 (a 9.1-point swing). Texas Tech was missing All-American JT Toppin (ACL) but still won by 20. **Vegas had Texas Tech -6.5; we had Akron at 72.7%.** This was our largest disagreement with the market.
- **Santa Clara**: Model was right to see Santa Clara as competitive (WCC had a good year), but Kentucky's star power (Oweh, 18.2 PPG) was undervalued. A banked half-court buzzer-beater forced OT - without it, Santa Clara wins in regulation. Partly bad luck, partly underweighting Star WAR.
- **Louisville**: Model overweighted USF's slightly higher Elo (+10.7) while missing Louisville's massive BARTHAG advantage (0.94 vs 0.84). Louisville was also missing starting PG Mikel Brown Jr. (18.2 PPG, back injury), which the model couldn't account for. Vegas had Louisville -4.5.

#### Category 4: Overconfidence Against a 1-Seed (1 game)
**Games**: Iowa/Florida

97.1% for Florida was our worst Brier score. Even Vegas only had Florida at ~85% implied. Florida was genuinely the better team by most metrics, but:
- Iowa's coach Ben McCollum (.818 career winning percentage, 4 D-II national titles) was captured as "1 tournament appearance" - massively understating his quality
- 5 Iowa players transferred from McCollum's Drake team, giving pre-built chemistry invisible to box-score features
- Florida's star center Rueben Chinyelu (SEC DPOY) had 0 pts, 1 reb, 4 fouls in 19 min
- The game was decided by a single 3-pointer with 4.5 seconds left
- Even if Florida is the right pick, anything above ~95% was reckless for a 1v9

---

### Systemic Model Failures Identified

#### 1. No probability clipping
Raw model outputs reached 97.1% and 96.1%. Past Kaggle winners clip to [2.5%, 97.5%]. Even basic clipping at 95% would have reduced our top 3 Brier penalties from 2.78 to ~0.15 combined.

#### 2. Elo dominates all other features
Elo_diff is the model's #1 feature by importance. When Elo disagrees with Team WAR, Sr%, NetEff, and coaching experience, Elo wins. This created extreme confidence in teams with inflated Elo from weak schedules (St. Mary's, Santa Clara) or seed prestige.

#### 3. No injury integration
Gonzaga missing Braden Huff (17.8 PPG), BYU missing Richie Saunders (18.0 PPG), Louisville missing Mikel Brown Jr. (18.2 PPG), Duke missing Foster/Ngongba, and Vanderbilt's Duke Miles playing with a taped thumb. Zero of this information reached the model.

#### 4. No seed-matchup calibration prior
The model doesn't respect that 8v9 games are coin flips or that 12-seeds upset 5-seeds ~35% of the time. It builds confidence purely from feature differences, producing 82-96% in games where 55-75% would be appropriate.

#### 5. Raw vs adjusted metrics not separated
The Akron/Texas Tech miss was caused by the model weighting raw efficiency (favoring Akron from MAC play) alongside SOS-adjusted efficiency (favoring Texas Tech). The raw metrics should be discarded in favor of adjusted metrics, or the model should learn the adjustment itself.

#### 6. Transfer portal cohesion invisible
Iowa's 5 Drake transfers playing for their former coach gave them chemistry no feature captured. Texas's portal-assembled roster with Sean Miller had similar hidden cohesion. College basketball's transfer era makes roster assembly a first-class signal, but our features only see aggregate team stats.

#### 7. No market data integration
In 4 of 12 misses, we picked the OPPOSITE team from Vegas. In all 12, Vegas was more calibrated. Even using the Vegas line as a single additional feature would have dramatically improved predictions. The most successful Kaggle competitor (goto_conversion) literally just converts betting odds with a bias correction.

---

## Sources

- NCAA.com Official Bracket: ncaa.com tournament bracket page
- ESPN Scoreboards: March 19, 20, 21, 22 (all games verified)
- ESPN Game Recaps for all 12 wrong picks (individual game IDs)
- CBS Sports Saturday/Sunday R32 Live Updates
- Yahoo Sports Day 3-4 Takeaways
- Vegas odds: DraftKings/FanDuel/Covers.com lines (per-game)
- All predictions: `data/processed/preds_lgbm.parquet`
- All features: `data/processed/team_features.parquet`
- Player data: `data/raw/external/barttorvik_players_*.csv`
