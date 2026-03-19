# Data Sources — Kaggle Competition + External

## Part 1: Kaggle Competition Data (~35 CSV Files)

The competition provides data prefixed with `M` (men's) and `W` (women's). Based on prior years and documentation, the complete file list is:

### Team & Season Reference
| File | Description |
|---|---|
| `MTeams.csv` | TeamID, TeamName, FirstD1Season, LastD1Season |
| `WTeams.csv` | Same for women |
| `MSeasons.csv` | Season, DayZero (reference date), RegionW/X/Y/Z names |
| `WSeasons.csv` | Same for women |
| `Conferences.csv` | ConfAbbrev, Description (shared men/women) |
| `MTeamConferences.csv` | Season, TeamID, ConfAbbrev — team-conference mapping |
| `WTeamConferences.csv` | Same for women |

### Game Results — Compact (score-only)
| File | Description |
|---|---|
| `MRegularSeasonCompactResults.csv` | Season, DayNum, WTeamID, LTeamID, WScore, LScore, WLoc, NumOT |
| `WRegularSeasonCompactResults.csv` | Same for women |
| `MNCAATourneyCompactResults.csv` | Tournament games, same columns |
| `WNCAATourneyCompactResults.csv` | Same for women |

### Game Results — Detailed (box scores)
| File | Description |
|---|---|
| `MRegularSeasonDetailedResults.csv` | Compact cols + FGM/FGA, FGM3/FGA3, FTM/FTA, OR/DR, Ast, TO, Stl, Blk, PF for W and L teams |
| `WRegularSeasonDetailedResults.csv` | Same for women |
| `MNCAATourneyDetailedResults.csv` | Tournament games, same columns |
| `WNCAATourneyDetailedResults.csv` | Same for women |

### Tournament Structure
| File | Description |
|---|---|
| `MNCAATourneySeeds.csv` | Season, Seed (e.g. "W01"), TeamID |
| `WNCAATourneySeeds.csv` | Same for women |
| `MNCAATourneySlots.csv` | Bracket structure — slot, strongseed, weakseed, advancement paths |
| `WNCAATourneySlots.csv` | Same for women |

### Geography
| File | Description |
|---|---|
| `Cities.csv` | CityID, City, State, Lat, Lon (shared) |
| `MGameCities.csv` | Season, DayNum, WTeamID, LTeamID, CityID |
| `WGameCities.csv` | Same for women |

### Rankings & Coaching
| File | Description |
|---|---|
| `MMasseyOrdinals.csv` | Season, RankingDayNum, SystemName, TeamID, OrdinalRank — **MEN'S ONLY**, 2003+ |
| `MTeamCoaches.csv` | Season, TeamID, FirstDayNum, LastDayNum, CoachName |
| `WTeamCoaches.csv` | Same for women |

### Secondary/Conference Tournaments (Men's only)
| File | Description |
|---|---|
| `MConferenceTourneyGames.csv` | Conference tournament game results |
| `MSecondaryTourneyCompactResults.csv` | NIT, CBI, etc. results |
| `MSecondaryTourneyTeams.csv` | Teams in secondary tournaments |

### Submission Files
| File | Description |
|---|---|
| `SampleSubmissionStage1.csv` | 2022-2025 matchups for validation |
| `SampleSubmissionStage2.csv` | 2026 matchups for actual scoring |

### What's NOT in the Kaggle data
- No player-level stats (only team aggregates)
- No recruiting/transfer portal data
- No betting odds or spreads
- No advanced analytics (KenPom, BPI, NET)
- No injury data
- No attendance/arena data
- No TV viewership/momentum data
- Women's data has NO Massey Ordinals

---

## Part 2: External Data Sources

### Tier 1 — HIGH VALUE (used by virtually all competitive entries)

#### KenPom (kenpom.com) — PAID ($24.95/year)
**What it provides**: The gold standard for college basketball analytics.
- Adjusted Offensive Efficiency (AdjOE) — points per 100 possessions, adjusted for opponent
- Adjusted Defensive Efficiency (AdjDE) — points allowed per 100 possessions, adjusted
- Adjusted Tempo (AdjT) — possessions per 40 minutes, adjusted
- Luck — deviation from expected W-L based on game-by-game results
- Strength of Schedule (AdjEM SOS)
- Four Factors: eFG%, TO%, OR%, FTRate (for both offense and defense)
- Historical data back to 2002

**How to access**: `kenpompy` Python package (requires paid subscription)
```python
pip install kenpompy
```

**Verdict**: **STRONGLY RECOMMENDED**. $25 is trivial for a $50K competition. KenPom features are the single most impactful external data source.

---

#### Bart Torvik (barttorvik.com) — FREE
**What it provides**: Very similar to KenPom, widely considered the best free alternative.
- Adjusted Offensive/Defensive Efficiency
- Barthag (win probability metric)
- Adjusted Tempo
- Four Factors (eFG%, TO%, OR%, FTRate)
- Team Sheets (resume with quad wins, SOS, etc.)
- Player-level stats and ratings
- Data back to 2008

**How to access**:
- `cbbdata` R package / API (free API key) — nearly 30 endpoints, updated every 15 minutes
- `toRvik` R package (predecessor to cbbdata)
- Direct scraping with Python (data available at barttorvik.com/rpms.php)

**Verdict**: **MUST HAVE**. Free, comprehensive, frequently updated. Can substitute for KenPom if needed.

---

#### Massey Ordinals (included in Kaggle data — MEN'S ONLY)
**What it provides**: Rankings from 50+ public ranking systems including:
- POM (Pomeroy/KenPom)
- SAG (Sagarin)
- MOR (Morong)
- DOL (Dolphin)
- RPI, BPI, AP, Coaches Poll
- Updated throughout the season

**Verdict**: **ALREADY IN KAGGLE DATA** for men's. The challenge is selecting which ranking systems to use and how to aggregate them. For women's, we need to find alternative ranking sources.

---

### Tier 2 — HIGH VALUE (differentiation potential)

#### ESPN BPI — FREE (undocumented API)
**What it provides**:
- Basketball Power Index (BPI) — points above/below average
- Strength of Record (SOR) — difficulty of achieving a team's W-L record
- Tournament projections and matchup win probabilities
- Game-by-game predictions

**How to access**: ESPN undocumented API (no auth required)
```
https://sports.core.api.espn.com/v2/sports/basketball/leagues/mens-college-basketball/seasons/2026/powerindex
```

**Verdict**: **RECOMMENDED**. Free, easy to access, and BPI/SOR provide a different signal than KenPom.

---

#### NCAA NET Rankings — FREE
**What it provides**: The official NCAA selection committee ranking tool.
- Based on: Team Value Index, Net Efficiency, Win%, Adjusted Win%, Scoring Margin
- Quad system (Q1/Q2/Q3/Q4 wins/losses based on opponent NET + location)
- Used directly by the selection committee for seeding

**How to access**:
- ncaa.com/rankings (web scraping)
- college-hoops-data.com/rankings (free, all 362 teams, daily updates)
- warrennolan.com/basketball/2026/net

**Verdict**: **RECOMMENDED**. The committee uses NET for seeding, so it directly relates to the seeds we're predicting against.

---

#### Andrew Sundberg's College Basketball Dataset (Kaggle) — FREE
**What it provides**: Pre-computed advanced stats for all teams, 2013–2025.
- ADJOE (Adjusted Offensive Efficiency)
- ADJDE (Adjusted Defensive Efficiency)
- EFG% (Effective Field Goal %)
- ORB/DRB (Offensive/Defensive Rebound %)
- FTR (Free Throw Rate)
- WAB (Wins Above Bubble)
- Plus basic stats: G, W, 2P%, 3P%, etc.

**How to access**: `kaggle datasets download andrewsundberg/college-basketball-dataset`

**Verdict**: **RECOMMENDED**. Pre-cleaned, ready-to-use advanced stats. May not have 2026 data yet, but great for historical features.

---

#### Nishaan Amin's March Madness Data (Kaggle) — FREE
**What it provides**: Tournament-focused dataset, 2008–2025.
- Elo ratings for all tournament teams
- Seed and historical seed performance
- PASE (Performance Against Seed Expectations)
- Tournament win/loss records
- Team tournament history metrics

**How to access**: `kaggle datasets download nishaanamin/march-madness-data`

**Verdict**: **RECOMMENDED**. Pre-computed Elo and tournament history. Great for validation and as additional features.

---

#### Historical Betting Odds / Spreads — FREE (limited)
**What it provides**: Vegas lines are historically the best predictor of game outcomes.
- Pre-game point spreads (represent market consensus on team strength)
- Moneylines (implied win probabilities)
- Over/under totals (tempo/scoring expectations)

**How to access**:
- sportsbookreviewsonline.com — historical odds archives
- oddsportal.com — NCAA odds back to 2008/09
- The Odds API — JSON API, historical data from late 2020 (free tier available)

**Verdict**: **HIGHLY RECOMMENDED if accessible**. Vegas lines encode enormous amounts of information — injuries, momentum, matchup-specific factors — that no statistical model can fully capture. Even a single "closing spread" feature can dramatically improve predictions.

---

### Tier 3 — MODERATE VALUE (nice-to-have, diminishing returns)

#### Player-Level Stats & Ratings
**What it provides**: Individual player impact metrics.
- EvanMiya.com: OBPR (Offensive Bayesian Performance Rating), player-level lineup impact
- Sports-Reference.com: PER (Player Efficiency Rating), BPM, WS
- TeamRankings.com: Player-level NBA-style efficiency
- Barttorvik: Player-level stats and ratings

**Modeling challenge**: Aggregating player stats to team-level predictions is non-trivial. Requires roster knowledge and playing time data.

**Verdict**: **OPTIONAL**. High effort, moderate payoff. Better to use team-level aggregates (which already reflect player contributions) unless you have a specific hypothesis about roster composition.

---

#### Transfer Portal Data
**What it provides**: Which players transferred in/out of each program.
- 247sports.com/season/2026-basketball/transferportal/ — comprehensive tracker
- on3.com/transfer-portal/wire/basketball/ — similar coverage
- theportalreport.com — dedicated portal tracking

**Modeling use**: Could indicate team roster upheaval or upgrade. Teams with many transfers-in may be harder to predict (new chemistry). Teams losing key players may underperform their historical metrics.

**Challenge**: No clean API or downloadable dataset. Would require scraping. Hard to quantify "impact" without player-level models.

**Verdict**: **SKIP FOR NOW**. The effect of transfers is already captured in current-season performance metrics (KenPom, Barttorvik, etc.). The portal data itself adds limited marginal value over "how is the team actually performing this season?"

---

#### Injury Data
**What it provides**: Current tournament injuries and their impact.
- covers.com/sport/basketball/ncaab/injuries — full injury report
- rotowire.com — detailed injury updates
- ESPN API `/teams/{id}/injuries` — programmatic access

**2026 notable injuries**:
- Duke: Caleb Foster (broken foot) — likely season-ending
- BYU: Richie Saunders (knee) — season-ending
- Louisville: Mikel Brown Jr. (back) — out first weekend
- Gonzaga: Braden Huff (knee) — out since January
- UNC: Caleb Wilson (hand fractures) — season-ending

**Verdict**: **RECOMMENDED for final submission tuning**. Can't build a model around injuries (too few data points historically), but manually adjusting predictions for known injuries to key players before the deadline is smart.

---

#### Coach Tournament Experience (in Kaggle data — MTeamCoaches.csv)
**What it provides**: Coach identity and tenure per team per season.
- Already in the competition data
- Can derive: tournament appearances, tournament wins, years as head coach
- Research shows experienced coaches (Izzo, Few, etc.) consistently overperform

**Verdict**: **WORTH ENGINEERING**. Low effort since the data is already in Kaggle. Create features like coach_tournament_appearances, coach_tournament_win_pct.

---

#### Geography / Travel Distance (in Kaggle data)
**What it provides**: Cities.csv + GameCities.csv let you compute travel distances.
- Home court advantage diminishes in neutral sites
- Teams playing closer to home may have fan/comfort advantage
- Tournament venue locations are known

**Verdict**: **MINOR VALUE**. Worth computing distance-to-venue as a feature, but unlikely to be a top predictor.

---

#### NCAA Free API (github.com/henrygd/ncaa-api) — FREE
**What it provides**: Live scores, stats, standings, rankings from ncaa.com.
- Scoreboard, box scores, play-by-play
- Team and player stats
- Rankings (AP, Coaches, NET)
- Standings

**Verdict**: **USEFUL for filling gaps**. Good fallback for getting current-season stats if other sources are unavailable.

---

### Tier 4 — LOW VALUE (not worth the effort for this competition)

| Source | Why Skip |
|---|---|
| Play-by-play data | Enormous volume, complex to engineer features, marginal improvement |
| Recruiting rankings (247Sports) | Effect already reflected in team performance metrics |
| Social media / fan sentiment | Noise > signal for game outcomes |
| Attendance data | Very weak predictor |
| TV ratings | No causal relationship to outcomes |
| Arena/venue details | Minimal impact in tournament (neutral sites) |

---

## Summary: Recommended Data Collection Plan

### Must Collect (Day 1)
1. **Kaggle competition data** — all 35 CSVs (5 min via API)
2. **Bart Torvik data** — team ratings, four factors, tempo (free, cbbdata API or scrape)
3. **Andrew Sundberg's Kaggle dataset** — pre-computed ADJOE/ADJDE/WAB (free, 1 min)
4. **Nishaan Amin's March Madness dataset** — Elo ratings, seed history (free, 1 min)

### Should Collect (Day 1-2)
5. **KenPom data** — if we subscribe ($25), use kenpompy to pull AdjOE/AdjDE/tempo/four factors
6. **ESPN BPI** — scrape or API call for current BPI rankings
7. **NCAA NET rankings** — scrape current NET + quad records
8. **Current injury report** — manual review for final prediction adjustments

### Nice to Have (if time permits)
9. **Historical betting odds** — closing spreads from sportsbookreviewsonline.com
10. **Coach tournament history** — derived from Kaggle's MTeamCoaches.csv + MNCAATourneyCompactResults.csv
11. **Deep Metric Analytics** — deepmetricanalytics.com has Elo and NET-style rankings

### Skip
- Transfer portal data (captured in current-season metrics)
- Player-level stats (too complex to aggregate properly under time pressure)
- Play-by-play data (enormous, marginal value)
- Recruiting/social media/attendance (noise)
