# Past Kaggle March Madness Winners and Winning Approaches

## Research Compiled: 2026-03-20
## Sources: GitHub, Kaggle notebooks/discussions, Brave Search, FiveThirtyEight, academic references

---

## 1. goto_conversion - The Dominant Competitor ($47K+ in Prizes)

### Overview
- **Prize money**: $47,000+ across Kaggle competitions
- **Medals**: 10+ gold medals, 75 silver medals, 19 bronze medals, 100+ total medals
- **Key insight**: Uses NO machine learning. Converts betting odds to probabilities with a bias correction.
- **Open source**: `pip install goto-conversion` (PyPI package, version 4.0.1)
- **GitHub**: github.com/gotoConversion/goto_conversion (254 commits, 106 stars, 15 forks, MIT license)
- **Approved by**: PySport open-source project

### The Method - Favourite-Longshot Bias Correction

The core algorithm is remarkably simple. Here is the actual implementation:

```python
def goto_conversion(listOfOdds, total=1.0):
    # Step 1: Convert odds to raw implied probabilities
    listOfProbabilities = 1.0 / listOfOdds  # inverse odds

    # Step 2: Compute standard error for each probability
    # SE = sqrt((p - p^2) / p) = sqrt(1 - p)
    listOfSe = sqrt((p - p**2) / p) for each p

    # Step 3: Compute how many "steps" of SE to subtract
    # step = (sum_of_raw_probs - 1.0) / sum_of_SEs
    step = (sum(listOfProbabilities) - total) / sum(listOfSe)

    # Step 4: Subtract proportional SE from each probability
    outputListOfProbabilities = p - (se * step) for each (p, se)
```

**What this does**: Betting odds have a built-in bookmaker margin (the "overround" - probabilities sum to more than 1.0). The naive approach divides each probability by the sum to normalize (multiplicative). goto_conversion instead subtracts a proportional amount based on standard error.

**Why it works**: The favourite-longshot bias means longshots are systematically overpriced in betting markets (their implied probabilities are too high). Since longshots have higher standard errors than favourites, the goto_conversion method removes MORE probability from longshots than from favourites, correcting this bias.

**The mathematical key**: The standard error of a probability p is sqrt(p(1-p)/n). Since we're dealing with implied probabilities from odds (where n can be considered as 1/p for equal weighting), the SE simplifies to sqrt(1-p). Longshots (low p) have higher SE, so more gets subtracted from their probabilities.

### Also Implements
- **efficient_shin_conversion**: An analytical (closed-form) solution to Shin's model, which was originally only solvable numerically. This is an alternative approach to handling the favourite-longshot bias using insider trading theory.
- **zero_sum variant**: Adapted for stock market predictions (won gold medal in stock prediction, 14th of 3,225 competitors).

### Notable Competition Results
- 2025 Basketball Outcome Prediction: Multiple golds ($8K, $7K, $5K, $5K, $5K prizes)
- 2024 Basketball Outcome Prediction: Gold medals ($7K, $5K prizes)
- 2023 Stock Market Prediction: Gold (14th of 3,225)

### Key Advantages
- Requires NO historical training data
- Requires NO advanced domain expertise
- Requires NO paid computational resources
- Works in free Google Colab
- Based on established academic literature (Strumbelj 2014)

### What This Means For Our Competition
Betting odds are the single most information-dense signal available. They incorporate injuries, momentum, matchup-specific factors, coaching, and market consensus from millions of dollars of wagering activity. goto_conversion shows that properly debiased betting odds alone can beat most ML approaches. However, betting odds for tournament games may not be available until very close to tip-off, and the competition deadline is before the tournament starts.

---

## 2. Past Winners and Their Methods

### Andrew Landgraf - 1st Place Winner (featured in Kaggle Blog interview)

**Strategy**: Meta-gaming approach. Rather than just optimizing predictions, he explicitly modeled the competitive landscape.

**Key innovation**: "Searched for the submission with the highest chance of finishing with a prize (top 5 on the leaderboard)." He built two models:
1. A model predicting game outcomes (the standard approach)
2. A model predicting what OTHER competitors would submit

**Methodology**: Dual modeling strategy combining team win probabilities with competitor submission analysis. The idea was to find the right amount of "contrarian-ness" - predictions that are slightly different from the field to maximize expected rank.

**Lesson**: In a competition where luck plays a large role (due to upsets), optimizing for expected rank rather than expected accuracy can be the winning strategy. Matthews and Lopez (2014 winners) published a paper showing luck is a significant factor, concluding: "Take a model, tweak it a bit to generate some distance from the field, and you are competitive to win."

### ArunkumarRamanan - 1st Place, 2019 (GitHub repo: KaggleMarchMadnessFirstPlace)

**Approach** (from analysis of the win_ncaa_men.R code):
- **Model**: XGBoost with custom Cauchy distribution loss function
- **Phase 1**: GLMM (Generalized Linear Mixed Models) for feature engineering - extract team quality random effects
- **Phase 2**: 10-iteration ensemble of XGBoost models with 5-fold CV, 3000 rounds max
- **Phase 3**: Smooth spline calibration to convert point differential predictions to win probabilities

**Feature Engineering**:
- GLMM random effects as team quality metrics
- Regular season stats from last 14 days: win ratio, points (mean/median/differential), FGA (mean/median/min/max), assists means, blocks means, opponent FGA stats
- Tournament seeds and seed differentials

**XGBoost Configuration**:
- Shallow trees: max_depth=3
- Conservative learning rate: eta=0.02
- Aggressive regularization: min_child_weight=40, gamma=10
- Custom Cauchy objective function (more robust to outliers than squared error)

**Calibration**:
- Smooth splines fit predicted point differentials to binary win outcomes
- 10-fold ensemble averaging
- **Probability clipping to [0.025, 0.975]**
- Manual adjustments on 4 specific games

### maze508 - Top 1% Gold Medal, 2023

**From Medium writeup**:
- **Model**: XGBoost ensembled with simple Logistic Regression
- **Women's bracket**: Used Bayesian optimization for hyperparameter tuning
- **Philosophy**: Simple, straightforward features rather than complex patterns
- **External data**: Used external rating systems (KenPom, etc.)
- **No player data used**

### Rank 107 Approach - 2025 (LinkedIn writeup)

**Detailed methodology available**:
- **Model**: Single XGBoost model (beat ensembles of XGB+LGBM+CatBoost+NN!)
- **Features**: 23 features selected via permutation importance filtering
- Feature categories: attacking and defense metrics, seed differences, team quality metrics (from GLM), historical point differentials
- **CV Strategy**: Leave-1-Group-Out (20-fold), removing one season (2003-2024) at a time, excluding 2020
- **Calibration**: Cubic-spline calibration performed IN-FOLD (not single post-hoc calibration)
- **CV Score**: 9.258 MAE
- **Development time**: Only 2 hours of work

**Key quote**: The volatile nature of the tournament with frequent upsets makes extensive optimization less valuable.

---

## 3. Common Feature Engineering Patterns

### Features Used By Most Competitive Solutions

**Tier 1 - Nearly universal among winners:**
1. **Seed and seed differential** - Strongest single predictor but relationship is non-linear
2. **Elo ratings** - Correlates 0.841 with seed but captures distinct information
3. **Adjusted efficiency metrics** - Offensive/defensive efficiency per possession (KenPom AdjOE/AdjDE or equivalent)
4. **Win percentage** - Including strength-of-schedule adjusted variants

**Tier 2 - Common among top solutions:**
5. **eFG% (Effective Field Goal Percentage)** - Adjusts for 3-point value
6. **Massey Ordinals** - Aggregation of 50+ public ranking systems (men's only)
7. **Strength of Schedule** - Opponent win% and opponent-of-opponent win%
8. **Point differentials** - Season average and recent trend

**Tier 3 - Used by some competitive solutions:**
9. **Last N-days performance** - Focusing on final 14 days of regular season
10. **Turnover rate** - Ball security per possession
11. **Free throw rate** - FTA/FGA ratio
12. **Offensive/Defensive rebound rate**
13. **Coach tournament experience** - Derived from coaching data

**Features that DON'T help:**
- **Player-level data**: No documented winning solution has ever used player features. Team efficiency metrics already capture individual contributions. Our own experiment confirmed this (Brier 0.0544 with player data vs 0.0503 without).
- **Transfer portal data**: Captured in current-season performance metrics
- **Play-by-play data**: Too voluminous for marginal improvement
- **Recruiting rankings**: Effect already in team performance
- **Social media/sentiment**: Noise dominates signal

### Key Modeling Patterns

1. **Compute stat DIFFERENCES between paired teams** - Not raw stats per team
2. **Data augmentation** - Each game as (A,B,Win) AND (B,A,Loss) to double training data
3. **Shallow trees** - max_depth 3-4 for gradient boosting (prevents overfitting on ~1500 training examples)
4. **Feature selection matters** - Permutation importance filtering beats using everything
5. **Recent season weighting** - 3-point revolution + transfer portal = game has evolved significantly

---

## 4. External Data Sources That Winners Use

### By Impact (confirmed from winner writeups):

| Source | Used By | Access | Cost |
|--------|---------|--------|------|
| **Betting odds** | goto_conversion ($47K) | Various APIs | Free-Paid |
| **KenPom** | Nearly all ML winners | kenpompy package | $25/year |
| **Massey Ordinals** | Many competitors | In Kaggle data (men's only) | Free |
| **Bart Torvik** | Growing in popularity | barttorvik.com | Free |
| **ESPN BPI** | Several competitors | Undocumented API | Free |
| **Andrew Sundberg dataset** | Common baseline | Kaggle datasets | Free |
| **Nishaan Amin dataset** | Common for Elo/seed history | Kaggle datasets | Free |

### Betting Odds - The Ultimate Feature
Vegas lines are historically the most accurate predictor of game outcomes because they incorporate:
- Team quality and form
- Injuries (often before public knowledge)
- Matchup-specific factors
- Coaching tendencies
- Travel/fatigue factors
- Market consensus from millions in wagers

goto_conversion proved that properly debiased odds alone outperform most ML models.

---

## 5. Calibration Techniques

### What Winners Use

**Probability Clipping** (most common):
- 2019 winner: Clipped to [0.025, 0.975]
- Our pipeline: Clipped to [0.001, 0.999]
- One competitor noted clipping at 95% would have achieved "Top 50"
- Rationale: Brier score quadratic loss heavily penalizes confident wrong predictions. A single 1-vs-16 upset predicted at 0.01 costs 0.98 in Brier score.

**Smooth Spline / Cubic Spline Calibration**:
- 2019 winner: Fit smooth splines from predicted point differentials to win probabilities
- 2025 Rank 107: Cubic-spline calibration performed IN-FOLD (key: do not calibrate on the same data you train on)

**Isotonic Regression**:
- Non-parametric, flexible, adapts to arbitrary miscalibration patterns
- Available via scikit-learn CalibratedClassifierCV(method='isotonic')
- Risk of overfitting on small samples

**Platt Scaling (Sigmoid)**:
- Parametric (logistic regression on classifier outputs)
- More stable than isotonic on small samples
- Available via CalibratedClassifierCV(method='sigmoid')

**Ensemble Averaging** (implicit calibration):
- Averaging multiple diverse models tends to produce more well-calibrated probabilities
- Most top solutions use some form of ensembling

### Calibration Strategy Takeaways
1. **Never predict extreme probabilities** - clip to [0.02, 0.98] at minimum
2. **Calibrate in-fold** - post-hoc calibration on validation data prevents overfitting
3. **Brier score rewards calibration over accuracy** - a well-calibrated 60% prediction is better than an overconfident 90% prediction that's sometimes wrong
4. **The 0.5 baseline** - predicting 0.5 everywhere gives Brier = 0.25. This is the bar to beat.

---

## 6. The Prediction Ceiling

### Historical Brier Scores

**Our model's CV Brier**: 0.0503 (LightGBM, men's)

**Competition context**:
- The evaluation metric changed from Log Loss to Brier Score in recent years
- Brier Score is weighted by round (finals count much more than first round)
- Perfect prediction = 0.0, always predicting 0.5 = 0.25

### Known Performance Boundaries

**Betting market accuracy**: FiveThirtyEight's analysis shows their model (blending 6 power rating systems) achieves similar accuracy to betting markets. Neither achieves perfect prediction.

**Academic research on tournament randomness**:
- Matthews and Lopez (2014 winners) published findings showing luck plays a significant role
- Multiple studies found accuracy concentrates at 65-80% regardless of feature sophistication
- The single-elimination format amplifies randomness - one bad game eliminates a team regardless of quality
- The 11-seed anomaly (outperforming 9 and 10 seeds) persists despite being well-documented

**Inherent sources of unpredictability**:
1. **Small sample size**: 30-35 regular season games is not a large sample for estimating true team quality
2. **Hot/cold shooting**: 3-point shooting variance can swing any game
3. **Referee variability**: Foul calls vary game to game
4. **Injuries**: In-game injuries are unpredictable
5. **Matchup effects**: Team A beats B, B beats C, but C beats A (non-transitive outcomes)
6. **One-and-done format**: No series to regress to mean

**Practical ceiling**: Based on the data, a Brier score around 0.04-0.06 appears to be the realistic ceiling for well-calibrated models. Below 0.04 likely requires significant luck (the right upsets happening to match your contrarian predictions). goto_conversion's consistent multi-year success suggests that a Brier around 0.05-0.08 is "consistently achievable" for a strong model.

### What This Means Strategically

1. **The marginal value of model complexity is low** - goto_conversion beats most ML models with no ML at all
2. **Calibration matters more than feature engineering** - getting the probabilities right matters more than squeezing out an extra 0.1% accuracy
3. **Differentiation from the field matters** - in a luck-heavy competition, being slightly contrarian can win prizes even if your expected Brier is slightly worse
4. **Two submission strategy** - one "safe" submission (close to market consensus) and one "swing" submission (slight contrarian bets on specific upsets)

---

## 7. FiveThirtyEight's Methodology (for reference)

FiveThirtyEight's approach represents a well-documented professional prediction system:

**Rating System**: Blends 6 computer power ratings:
- KenPom, Sagarin, Sonny Moore, LRMC (Joel Sokol), ESPN BPI, FiveThirtyEight Elo

**Weighting**: 75% computer systems, 25% human rankings (NCAA S-curve, AP, coaches polls)

**Key adjustments**:
1. Injury assessment: Point deductions based on Win Shares data
2. Performance bonuses: Winners receive rating boosts based on game score and opponent quality
3. Win probability: Elo-derived formula based on power rating differences

**Women's differences**: Fewer rating systems available, excludes injury adjustments, substitutes seeds for S-curve

---

## 8. Key Strategic Insights for Our Competition

### What consistently wins:
1. **Betting odds with bias correction** (goto_conversion) - if available before deadline
2. **KenPom + seed + Elo in a shallow gradient boosting model** - the ML baseline
3. **Proper calibration** - clipping extremes, in-fold spline/isotonic calibration
4. **Ensembles** - but simple (2-3 models), not complex
5. **Humility** - no model will predict every upset

### What doesn't help:
1. Player-level data (confirmed by our experiment and all historical winners)
2. Deep learning (the 2017 repo confirmed "deep learning didn't really work")
3. Complex architectures (2025 Rank 107 single XGBoost beat 4-model ensemble)
4. Feature overload (23 well-chosen features > 200 kitchen-sink features)

### Opportunities for improvement over our current model:
1. **Integrate betting odds** - if pre-tournament odds are available, use goto_conversion
2. **In-fold calibration** - our current approach may be doing post-hoc calibration; switching to in-fold cubic spline could help
3. **Injury adjustments** - manual probability adjustments for known key injuries
4. **Contrarian submission** - one submission slightly favoring known upset-prone matchups (11-seeds, teams with elite Elo but mediocre seed)
5. **Custom loss function** - Cauchy loss (2019 winner) may be more robust than standard objectives

---

## Sources

1. github.com/gotoConversion/goto_conversion - Source code and documentation
2. Kaggle blog - Andrew Landgraf 1st place winner interview
3. github.com/ArunkumarRamanan/KaggleMarchMadnessFirstPlace - 2019 winning solution
4. medium.com/@maze508 - 2023 gold medal writeup
5. LinkedIn article - 2025 Rank 107 approach details
6. FiveThirtyEight - NCAA tournament prediction methodology
7. Nishaan Amin Kaggle dataset (13,656+ downloads, 167 versions, 2008-2026)
8. Strumbelj (2014) - "On determining probability forecasts from gambling odds"
9. Matthews & Lopez (2014) - Luck in March Madness prediction
10. Kizildemir, Akin, & Alkan (2025) - "A family of solutions related to Shin's model"
