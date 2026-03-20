"""Build a single-file HTML showcase with all figures embedded as base64."""
import base64
import os

FIG_DIR = os.path.join(os.path.dirname(__file__), '..', 'results', 'figures')
OUT_PATH = os.path.join(os.path.dirname(__file__), '..', 'results', 'march_madness_showcase.html')

# Load all images as base64
images = {}
for f in sorted(os.listdir(FIG_DIR)):
    if not f.endswith('.png'):
        continue
    with open(os.path.join(FIG_DIR, f), 'rb') as img:
        images[f] = base64.b64encode(img.read()).decode()


def img(filename, source=""):
    src_html = f'<div class="data-source">{source}</div>' if source else ''
    return f'<img src="data:image/png;base64,{images[filename]}" alt="{filename}" loading="lazy">{src_html}'


# Simple term references - no tooltips, glossary at bottom instead
T_LGBM = "LightGBM"
T_XGBOOST = "XGBoost"
T_BRIER = "Brier score"
T_WAR = "WAR"
T_WAR_SHARE = "WAR share"
T_EFG = "eFG%"
T_NET_EFF = "net efficiency"
T_ELO = "Elo ratings"
T_CALIBRATED = "calibrated probabilities"
T_GRADIENT = "Gradient boosting"
T_GINI = "WAR Gini"
T_NEURAL = "neural net"
T_TURNOVER = "turnover rates"
T_PORTAL = "transfer portal"
T_SEED = "seed"

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>March Madness 2026 - Data Science Deep Dive</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

  :root {{
    --bg-primary: #0a0e17;
    --bg-card: #111827;
    --bg-card-hover: #1a2332;
    --accent-teal: #14b8a6;
    --accent-orange: #f97316;
    --accent-red: #ef4444;
    --accent-blue: #3b82f6;
    --accent-purple: #a855f7;
    --accent-yellow: #eab308;
    --text-primary: #f1f5f9;
    --text-secondary: #94a3b8;
    --text-muted: #64748b;
    --border: #1e293b;
  }}

  * {{ margin: 0; padding: 0; box-sizing: border-box; }}

  body {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    background: var(--bg-primary);
    color: var(--text-primary);
    line-height: 1.6;
    -webkit-font-smoothing: antialiased;
  }}

  /* Progress bar */
  .progress-bar {{
    position: fixed;
    top: 0;
    left: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--accent-teal), var(--accent-orange));
    width: 0%;
    z-index: 1000;
    transition: width 0.1s linear;
  }}

  /* Sticky nav */
  .sticky-nav {{
    position: fixed;
    top: 3px;
    left: 0;
    right: 0;
    z-index: 999;
    background: rgba(10, 14, 23, 0.0);
    backdrop-filter: blur(0px);
    border-bottom: 1px solid transparent;
    padding: 0;
    max-height: 0;
    overflow: hidden;
    transition: all 0.3s ease;
  }}

  .sticky-nav.visible {{
    background: rgba(10, 14, 23, 0.92);
    backdrop-filter: blur(12px);
    border-bottom-color: var(--border);
    padding: 0.6rem 0;
    max-height: 50px;
  }}

  .sticky-nav-inner {{
    max-width: 1100px;
    margin: 0 auto;
    display: flex;
    align-items: center;
    gap: 0.25rem;
    padding: 0 2rem;
  }}

  .sticky-nav a {{
    color: var(--text-muted);
    text-decoration: none;
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    padding: 0.35rem 0.75rem;
    border-radius: 6px;
    transition: all 0.2s;
    white-space: nowrap;
  }}

  .sticky-nav a:hover {{ color: var(--text-primary); background: rgba(255,255,255,0.05); }}
  .sticky-nav a.active {{ color: var(--accent-teal); background: rgba(20, 184, 166, 0.1); }}

  .sticky-nav-title {{
    color: var(--text-primary);
    font-size: 0.8rem;
    font-weight: 700;
    margin-right: auto;
    white-space: nowrap;
  }}

  /* Scroll animations */
  .reveal {{
    opacity: 0;
    transform: translateY(40px);
    transition: opacity 0.7s ease, transform 0.7s ease;
  }}

  .reveal.visible {{
    opacity: 1;
    transform: translateY(0);
  }}

  /* Hero */
  .hero {{
    min-height: 80vh;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    padding: 4rem 2rem;
    position: relative;
    overflow: hidden;
    background: radial-gradient(ellipse at 50% 0%, rgba(20, 184, 166, 0.08) 0%, transparent 60%),
                radial-gradient(ellipse at 80% 80%, rgba(249, 115, 22, 0.05) 0%, transparent 50%),
                var(--bg-primary);
  }}

  .hero::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.015'%3E%3Ccircle cx='30' cy='30' r='1'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
    pointer-events: none;
  }}

  .hero-badge {{
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1.25rem;
    background: rgba(20, 184, 166, 0.1);
    border: 1px solid rgba(20, 184, 166, 0.25);
    border-radius: 100px;
    font-size: 0.8rem;
    font-weight: 600;
    color: var(--accent-teal);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 2rem;
  }}

  .hero h1 {{
    font-size: clamp(2.5rem, 6vw, 4.5rem);
    font-weight: 900;
    line-height: 1.1;
    margin-bottom: 1.5rem;
    background: linear-gradient(135deg, #f1f5f9 0%, #94a3b8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    max-width: 900px;
  }}

  .hero-sub {{
    font-size: 1.25rem;
    color: var(--text-secondary);
    max-width: 700px;
    margin-bottom: 3rem;
    font-weight: 300;
  }}

  .hero-stats {{
    display: flex;
    gap: 3rem;
    flex-wrap: wrap;
    justify-content: center;
  }}

  .hero-stat {{
    text-align: center;
  }}

  .hero-stat .number {{
    font-size: 2.5rem;
    font-weight: 800;
    color: var(--accent-teal);
    line-height: 1;
  }}

  .hero-stat .label {{
    font-size: 0.75rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-top: 0.25rem;
  }}

  /* Sections */
  .act {{
    padding: 3rem 2rem 2rem;
    max-width: 1100px;
    margin: 0 auto;
  }}

  .act-header {{
    margin-bottom: 3rem;
  }}

  .act-number {{
    font-size: 0.75rem;
    font-weight: 700;
    color: var(--accent-teal);
    text-transform: uppercase;
    letter-spacing: 0.15em;
    margin-bottom: 0.75rem;
  }}

  .act-title {{
    font-size: clamp(1.75rem, 4vw, 2.75rem);
    font-weight: 800;
    line-height: 1.15;
    margin-bottom: 1rem;
  }}

  .act-subtitle {{
    font-size: 1.1rem;
    color: var(--text-secondary);
    max-width: 700px;
    font-weight: 300;
  }}

  /* Pull-quote stat between sections */
  .pull-stat {{
    text-align: center;
    padding: 3rem 2rem;
    max-width: 800px;
    margin: 0 auto;
  }}

  .pull-stat .big-number {{
    font-size: clamp(3rem, 8vw, 5rem);
    font-weight: 900;
    line-height: 1;
    margin-bottom: 0.5rem;
  }}

  .pull-stat .big-number.teal {{ color: var(--accent-teal); }}
  .pull-stat .big-number.orange {{ color: var(--accent-orange); }}
  .pull-stat .big-number.red {{ color: var(--accent-red); }}
  .pull-stat .big-number.purple {{ color: var(--accent-purple); }}

  .pull-stat .context {{
    font-size: 1.1rem;
    color: var(--text-secondary);
    font-weight: 300;
    max-width: 500px;
    margin: 0 auto;
  }}

  /* Cards */
  .card {{
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 2rem;
    margin-bottom: 2.5rem;
    transition: all 0.4s ease;
    overflow: hidden;
  }}

  .card:hover {{
    border-color: rgba(20, 184, 166, 0.3);
    background: var(--bg-card-hover);
    transform: translateY(-2px);
    box-shadow: 0 12px 40px rgba(0,0,0,0.35), 0 0 0 1px rgba(20, 184, 166, 0.1);
  }}

  .card img {{
    width: 100%;
    border-radius: 10px;
    margin-bottom: 0.5rem;
    border: 1px solid var(--border);
  }}

  .data-source {{
    font-size: 0.7rem;
    color: var(--text-muted);
    margin-bottom: 1.25rem;
    font-style: italic;
    padding-left: 0.25rem;
  }}

  .card-label {{
    display: inline-block;
    font-size: 0.65rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    padding: 0.3rem 0.75rem;
    border-radius: 6px;
    margin-bottom: 1rem;
  }}

  .label-insight {{ background: rgba(20, 184, 166, 0.15); color: var(--accent-teal); }}
  .label-myth {{ background: rgba(239, 68, 68, 0.15); color: var(--accent-red); }}
  .label-paradox {{ background: rgba(249, 115, 22, 0.15); color: var(--accent-orange); }}
  .label-model {{ background: rgba(59, 130, 246, 0.15); color: var(--accent-blue); }}
  .label-finding {{ background: rgba(168, 85, 247, 0.15); color: var(--accent-purple); }}
  .label-warning {{ background: rgba(234, 179, 8, 0.15); color: var(--accent-yellow); }}

  .card h3 {{
    font-size: 1.35rem;
    font-weight: 700;
    margin-bottom: 1rem;
    line-height: 1.3;
  }}

  .card ul {{
    list-style: none;
    padding: 0;
  }}

  .card ul li {{
    position: relative;
    padding-left: 1.5rem;
    margin-bottom: 0.6rem;
    color: var(--text-secondary);
    font-size: 0.95rem;
    line-height: 1.5;
  }}

  .card ul li::before {{
    content: '';
    position: absolute;
    left: 0;
    top: 0.6rem;
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: var(--accent-teal);
  }}

  .card ul li strong {{
    color: var(--text-primary);
  }}

  .stat-callout {{
    background: rgba(20, 184, 166, 0.08);
    border-left: 3px solid var(--accent-teal);
    padding: 1rem 1.25rem;
    border-radius: 0 8px 8px 0;
    margin-top: 1rem;
    font-size: 0.9rem;
    color: var(--text-secondary);
  }}

  .stat-callout strong {{
    color: var(--accent-teal);
  }}

  .warning-callout {{
    background: rgba(249, 115, 22, 0.08);
    border-left: 3px solid var(--accent-orange);
    padding: 1rem 1.25rem;
    border-radius: 0 8px 8px 0;
    margin-top: 1rem;
    font-size: 0.9rem;
    color: var(--text-secondary);
  }}

  .warning-callout strong {{
    color: var(--accent-orange);
  }}

  /* Two-column */
  .two-col {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 2rem;
    margin-bottom: 2.5rem;
  }}
  .two-col .card {{ margin-bottom: 0; }}

  /* Injury table */
  .injury-table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 0.85rem;
    margin-top: 1rem;
  }}

  .injury-table th {{
    text-align: left;
    padding: 0.75rem 1rem;
    border-bottom: 2px solid var(--accent-orange);
    color: var(--accent-orange);
    font-weight: 700;
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
  }}

  .injury-table td {{
    padding: 0.6rem 1rem;
    border-bottom: 1px solid var(--border);
    color: var(--text-secondary);
  }}

  .injury-table tr:hover td {{
    background: rgba(249, 115, 22, 0.05);
  }}

  .war-impact {{ color: var(--accent-red); font-weight: 600; }}

  /* Finale */
  .finale {{
    text-align: center;
    padding: 3rem 2rem 4rem;
    max-width: 800px;
    margin: 0 auto;
  }}

  .finale-quote {{
    font-size: clamp(1.5rem, 3.5vw, 2.25rem);
    font-weight: 300;
    font-style: italic;
    color: var(--text-secondary);
    line-height: 1.4;
    margin-bottom: 1.5rem;
  }}

  .finale-quote em {{
    color: var(--accent-teal);
    font-style: normal;
    font-weight: 600;
  }}

  /* Footer */
  .footer {{
    text-align: center;
    padding: 2rem 2rem;
    border-top: 1px solid var(--border);
    color: var(--text-muted);
    font-size: 0.8rem;
  }}

  .footer-stats {{
    display: flex;
    justify-content: center;
    gap: 2.5rem;
    margin-bottom: 1.5rem;
    flex-wrap: wrap;
  }}

  .footer-stat {{
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
  }}

  .footer-stat span {{
    color: var(--accent-teal);
    font-weight: 700;
  }}

  /* Glossary */
  .glossary {{
    max-width: 1100px;
    margin: 0 auto;
    padding: 2rem 2rem 3rem;
  }}

  .glossary h2 {{
    font-size: 1.5rem;
    font-weight: 700;
    margin-bottom: 1.5rem;
  }}

  .glossary-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0;
  }}

  .glossary-item {{
    display: flex;
    gap: 0.75rem;
    padding: 0.7rem 1rem;
    border-bottom: 1px solid var(--border);
  }}

  .glossary-item dt {{
    color: var(--accent-teal);
    font-weight: 600;
    font-size: 0.85rem;
    min-width: 140px;
    flex-shrink: 0;
  }}

  .glossary-item dd {{
    color: var(--text-secondary);
    font-size: 0.85rem;
    margin: 0;
    line-height: 1.45;
  }}

  .glossary-category {{
    grid-column: 1 / -1;
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    padding: 1.25rem 1rem 0.4rem;
    border-bottom: 1px solid var(--border);
  }}

  .glossary-category.ml {{ color: var(--accent-blue); }}
  .glossary-category.bball {{ color: var(--accent-orange); }}

  /* Responsive */
  @media (max-width: 768px) {{
    .two-col {{ grid-template-columns: 1fr; }}
    .hero-stats {{ gap: 2rem; }}
    .card {{ padding: 1.25rem; }}
    .act {{ padding: 2rem 1.25rem 1.5rem; }}
    .injury-table {{ font-size: 0.75rem; }}
    .injury-table th, .injury-table td {{ padding: 0.5rem 0.5rem; }}
    .glossary-grid {{ grid-template-columns: 1fr; }}
  }}

  html {{ scroll-behavior: smooth; }}

  .section-break {{
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--border), transparent);
    max-width: 1100px;
    margin: 0 auto;
  }}
</style>
</head>
<body>

<!-- HERO -->
<section class="hero">
  <div class="hero-badge">SSA Data Science</div>
  <h1>Predicting March Madness with Machine Learning</h1>
  <p class="hero-sub">We entered Kaggle's $50K NCAA prediction competition. 40 years of data, 5 model architectures, 10,000 bracket simulations. Here's what we found - and what the models can't see.</p>
  <div class="hero-stats">
    <div class="hero-stat"><div class="number">101</div><div class="label">Data Files</div></div>
    <div class="hero-stat"><div class="number">57</div><div class="label">Features</div></div>
    <div class="hero-stat"><div class="number">5</div><div class="label">Models</div></div>
    <div class="hero-stat"><div class="number">30K</div><div class="label">Player Records</div></div>
    <div class="hero-stat"><div class="number">10K</div><div class="label">Bracket Sims</div></div>
  </div>
</section>

<div class="section-break"></div>

<!-- ACT I -->
<section class="act">
  <div class="act-header">
    <div class="act-number">Act I</div>
    <div class="act-title">What 40 Years of Data Actually Shows</div>
    <div class="act-subtitle">Some of these confirm what you'd expect. Others might surprise you. Either way, the data is clear.</div>
  </div>

  <div class="card">
    <span class="card-label label-insight">The Baseline</span>
    <h3>Not All Upsets Are Created Equal</h3>
    {img("01_upset_rates_by_matchup.png", "Source: Kaggle NCAA Tournament results, 1985-2025 | 160 games per matchup type")}
    <ul>
      <li>5-vs-12 upsets happen <strong>36% of the time</strong> - more than one in three. This is not a fluke; it's a structural feature of the bracket</li>
      <li>The 8-vs-9 game hits 52% - it's a coin flip. Seed means nothing here</li>
      <li>True Cinderellas (16 over 1) remain nearly impossible at just <strong>1% across 40 years</strong></li>
    </ul>
  </div>

  <div class="card">
    <span class="card-label label-myth">Myth Busted</span>
    <h3>Chaos Is Constant: Upset Rates Haven't Changed in 40 Years</h3>
    {img("02v2_upset_rate_eras.png", "Source: Kaggle NCAA Tournament results, 1985-2025 | Structural breaks from NCAA rule changes")}
    <ul>
      <li>Transfer portal, NIL money, conference realignment, shot clock changes - <strong>none of it moved the needle</strong></li>
      <li>The upset rate has hovered around <strong>27% since 1985</strong>. The 5-year rolling average is remarkably flat</li>
      <li>Every era of "parity" narratives has been wrong. The tournament's chaos is baked in - it's a feature, not a trend</li>
    </ul>
  </div>

  <div class="card">
    <span class="card-label label-myth">Myth Busted</span>
    <h3>"Peaking at the Right Time" Is a Myth</h3>
    {img("05v2_momentum_modern.png", "Source: Kaggle NCAA Tournament data, 2021-2025 | 408 tournament teams")}
    <ul>
      <li>Late-season momentum vs. tournament wins over expected: <strong>r = 0.096</strong>. Essentially zero</li>
      <li>Teams on hot streaks entering March perform no better than teams that stumble in</li>
      <li>In the {T_PORTAL} era, roster turnover makes momentum even less predictive</li>
    </ul>
  </div>

  <div class="card">
    <span class="card-label label-paradox">Paradox</span>
    <h3>The Three-Point Paradox</h3>
    {img("04v2_three_point_eras.png", "Source: Kaggle NCAA season stats, 2003-2026 | Rule changes annotated from NCAA records")}
    <ul>
      <li>3-point volume is <strong>up 25% since 2003</strong>. Accuracy? Flat - or worse</li>
      <li>Every rule change (line moved back, shot clock shortened) temporarily <strong>made shooting worse</strong></li>
      <li>Champions shoot <strong>fewer</strong> 3s than the field but make them at a higher rate. Quality over quantity</li>
    </ul>
  </div>

  <div class="card">
    <span class="card-label label-insight">Insight</span>
    <h3>Games Get Tighter as the Stakes Rise</h3>
    {img("07_margin_by_round.png", "Source: Kaggle NCAA Tournament detailed results, 1985-2025 | All rounds")}
    <ul>
      <li>Median margin of victory <strong>shrinks every round</strong> - from 11 pts in R64 to 8 in the championship</li>
      <li>By the Elite Eight, blowouts disappear. Talent converges, every game becomes a coinflip</li>
      <li>Your model's edge matters most in early rounds. By the Final Four, variance dominates</li>
    </ul>
  </div>

  <div class="card">
    <span class="card-label label-insight">Insight</span>
    <h3>The Cinderella DNA: Take Care of the Ball</h3>
    {img("08_cinderella_dna.png", "Source: Kaggle NCAA Tournament detailed results, 1985-2025 | Cinderellas = 2+ upset wins")}
    <ul>
      <li>Teams with 2+ upset wins share one trait: <strong>low {T_TURNOVER}</strong></li>
      <li>The "Cinderella sweet spot" - low turnovers + high {T_EFG} - is clearly visible in the scatter</li>
      <li>You can't out-talent a 1-seed, but you can out-execute them by not giving the ball away</li>
    </ul>
  </div>

  <div class="card">
    <span class="card-label label-insight">Insight</span>
    <h3>Where the True Shocks Come From</h3>
    {img("06_surprise_distribution.png", "Source: Kaggle NCAA Tournament results, 1985-2025 | Surprise score = seed differential x round weight")}
    <ul>
      <li>Most "upsets" aren't truly surprising - they cluster near zero on the shock scale</li>
      <li>Genuine shocks (95th percentile+) are rare: UMBC over Virginia (2018) lives in the far right tail</li>
      <li>For prediction models: <strong>don't overfit to upsets</strong>. Most are just noise, not signal</li>
    </ul>
  </div>
</section>

<div class="section-break"></div>

<!-- ACT II -->
<section class="act">
  <div class="act-header">
    <div class="act-number">Act II</div>
    <div class="act-title">Building the Prediction Engine</div>
    <div class="act-subtitle">Seeds tell part of the story. Efficiency metrics tell the rest. We tested 5 architectures to find what actually predicts tournament outcomes.</div>
  </div>

  <div class="card">
    <span class="card-label label-model">Foundation</span>
    <h3>Seeds Encode Real Information - But Not All of It</h3>
    {img("03v2_seed_efficiency_modern.png", "Source: Kaggle NCAA Tournament + KenPom efficiency data, 2021-2025 | 408 teams")}
    <ul>
      <li>"Hidden gems" (high-efficiency low {T_SEED}s) and "fool's gold" (low-efficiency high seeds) are visible in the {T_PORTAL} era</li>
      <li>{T_NET_EFF} separates winners from pretenders far better than seeding alone</li>
      <li>The committee gets it mostly right, but the <strong>outliers are where the edge lives</strong></li>
    </ul>
  </div>

  <div class="card">
    <span class="card-label label-model">The Engine</span>
    <h3>LightGBM Wins: 2.3x Better Than the Next Best</h3>
    {img("10_model_comparison.png", "Source: 5-fold cross-validation on 2021-2025 tournament results | Brier score (lower = better)")}
    <ul>
      <li>Tested 5 architectures: Bradley-Terry, Logistic Regression, {T_NEURAL}, {T_XGBOOST}, {T_LGBM}</li>
      <li>{T_LGBM} achieved a <strong>{T_BRIER} of 0.0503</strong> - 2.3x better than {T_XGBOOST}, 4x better than the {T_NEURAL}</li>
      <li>{T_GRADIENT} dominates because the signal is tabular and interaction-heavy. Deep learning adds complexity, not accuracy</li>
      <li>30+ hyperparameter configs tested. Best: depth=4, 500 trees, lr=0.05, heavy regularization</li>
    </ul>
    <div class="stat-callout">
      <strong>Why {T_BRIER}?</strong> Unlike accuracy (right/wrong), Brier rewards <strong>{T_CALIBRATED}</strong>. Saying "60% chance" and being right 60% of the time beats confidently guessing wrong.
    </div>
  </div>

  <div class="card">
    <span class="card-label label-model">2026 Predictions</span>
    <h3>The 2026 Field: Seed vs. Reality vs. Momentum</h3>
    {img("09_2026_field_analysis.png", "Source: 2026 Kaggle tournament seeds + KenPom efficiency + last-10-game win% momentum")}
    <ul>
      <li>Each dot is a 2026 tournament team. Position = seed vs. efficiency. Color = late-season momentum</li>
      <li><strong>Duke</strong> sits top right - highest seed, highest efficiency. On paper, the clear favorite</li>
      <li>Several mid-seeds (St. Mary's, Michigan St.) show efficiency that rivals top seeds - classic upset candidates</li>
      <li>Low seeds with hot momentum (green dots, bottom-left) are this year's Cinderella watch list</li>
    </ul>
  </div>

  <div class="card">
    <span class="card-label label-insight">The Big Picture</span>
    <h3>How the Game Changed: 20 Years of Structural Breaks</h3>
    {img("15_structural_timeline.png", "Source: Kaggle NCAA season/tournament data, 2003-2026 | Rule changes from NCAA records")}
    <ul>
      <li>Three panels track possessions, 3-point rate, and upset rate against every major rule/policy change</li>
      <li>The shot clock cut (35 to 30 sec) increased pace but <strong>didn't change outcomes</strong></li>
      <li>The {T_PORTAL} and NIL reshaped rosters but upset rates stayed flat</li>
      <li>Key insight: the game's <strong>structure</strong> has changed, but its <strong>competitive balance</strong> hasn't</li>
    </ul>
  </div>
</section>

<div class="section-break"></div>

<!-- ACT III -->
<section class="act">
  <div class="act-header">
    <div class="act-number">Act III</div>
    <div class="act-title">We Added 30,000 Player Records. It Got Worse.</div>
    <div class="act-subtitle">The most counterintuitive finding. More data doesn't always mean better predictions - especially when the signal is already captured.</div>
  </div>

  <div class="card">
    <span class="card-label label-finding">Key Finding</span>
    <h3>Roster Talent Does Not Predict March Success</h3>
    {img("11_team_war_vs_tourney.png", "Source: Barttorvik player WAR aggregated to team level, 2021-2025 | 30,066 players")}
    <ul>
      <li>Total team {T_WAR} vs. tournament wins: <strong>r = 0.001</strong>. Literally zero correlation</li>
      <li>Teams with 90+ {T_WAR} won zero tournament games. Teams with 25 {T_WAR} made the Final Four</li>
      <li>Team efficiency metrics already capture what players contribute in aggregate - player inputs on top of team outputs are redundant</li>
    </ul>
    <div class="stat-callout">
      <strong>{T_BRIER} impact:</strong> Adding 8 player features moved the model from <strong>0.0503 to 0.0544</strong> - an 8% degradation. No player feature cracked the top 15 in importance.
    </div>
  </div>

  <div class="card">
    <span class="card-label label-finding">Finding</span>
    <h3>Star Dependency Doesn't Predict Vulnerability</h3>
    {img("12_star_dependency.png", "Source: Barttorvik player WAR, 2021-2025 | Top-4 seeds only (n=100)")}
    <ul>
      <li>Star player {T_WAR_SHARE} vs. tournament performance: <strong>r = -0.053</strong></li>
      <li>Teams built around one star don't collapse more often than balanced rosters</li>
      <li>Exception: when that star is <strong>injured</strong>. Then everything changes</li>
    </ul>
  </div>

  <div class="card">
    <span class="card-label label-finding">Finding</span>
    <h3>Experience Doesn't Matter in the Portal Era</h3>
    {img("14_experience_portal_era.png", "Source: Barttorvik player data, 2021-2025 | ~5,000 players/year, 408 tournament teams")}
    <ul>
      <li>Roster experience (r=0.028) and senior % (r=-0.011) - <strong>both flat</strong></li>
      <li>The {T_PORTAL} broke the old "experienced teams win in March" heuristic</li>
      <li>~2,000 players enter the portal annually. Historical player-team associations are unstable</li>
    </ul>
  </div>

  <div class="card">
    <span class="card-label label-model">2026 Context</span>
    <h3>2026 Field: Talent vs. Seeding Tells a Different Story</h3>
    {img("13_2026_team_war.png", "Source: Barttorvik 2026 player WAR + Kaggle tournament seeds | Color = WAR Gini (roster balance)")}
    <ul>
      <li><strong>Missouri (10-seed)</strong> has the highest team {T_WAR} in the field at 93.4 - massively underseeded by talent</li>
      <li><strong>Duke (1-seed)</strong> has one of the lowest team {T_WAR}s at 29.3 - youngest roster in the field (avg class: 1.89)</li>
      <li>Color = depth ({T_GINI}). Green = balanced roster, red = top-heavy</li>
      <li>But remember: <strong>none of this predicts tournament outcomes</strong>. The model is better off ignoring it</li>
    </ul>
  </div>
</section>

<div class="section-break"></div>

<!-- ACT IV -->
<section class="act">
  <div class="act-header">
    <div class="act-number">Act IV</div>
    <div class="act-title">The One Thing the Model Can't See</div>
    <div class="act-subtitle">Player data is useless in aggregate - with one critical exception. When a star goes down, team stats become stale. And every injury was public knowledge.</div>
  </div>

  <div class="card" style="border-color: rgba(249, 115, 22, 0.3);">
    <span class="card-label label-warning">The Blind Spot</span>
    <h3>Duke Was a 99.4% Favorite. They Were Missing 26% of Their Roster.</h3>
    <table class="injury-table">
      <thead>
        <tr>
          <th>Player</th>
          <th>Team (Seed)</th>
          <th>Injury</th>
          <th>Date Public</th>
          <th>Days Before</th>
          <th>WAR Lost</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Braden Huff</td>
          <td>Gonzaga (3)</td>
          <td>Dislocated kneecap</td>
          <td>Jan 14</td>
          <td>64 days</td>
          <td class="war-impact">3.90</td>
        </tr>
        <tr>
          <td>Richie Saunders</td>
          <td>BYU (6)</td>
          <td>Torn ACL</td>
          <td>Feb 15</td>
          <td>32 days</td>
          <td class="war-impact">2.80</td>
        </tr>
        <tr>
          <td>JT Toppin</td>
          <td>Texas Tech (5)</td>
          <td>Torn ACL</td>
          <td>Feb 17</td>
          <td>29 days</td>
          <td class="war-impact">3.30</td>
        </tr>
        <tr>
          <td>Mikel Brown Jr.</td>
          <td>Louisville (6)</td>
          <td>Back injury</td>
          <td>Feb 28</td>
          <td>19 days</td>
          <td class="war-impact">2.20</td>
        </tr>
        <tr>
          <td>Caleb Wilson</td>
          <td>UNC (6)</td>
          <td>Broken thumb</td>
          <td>Mar 5</td>
          <td>14 days</td>
          <td class="war-impact">2.40</td>
        </tr>
        <tr>
          <td>Caleb Foster</td>
          <td>Duke (1)</td>
          <td>Broken foot</td>
          <td>Mar 7</td>
          <td>12 days</td>
          <td class="war-impact">4.10</td>
        </tr>
        <tr>
          <td>Patrick Ngongba II</td>
          <td>Duke (1)</td>
          <td>Foot soreness</td>
          <td>~Mar 2</td>
          <td>17 days</td>
          <td class="war-impact">3.50</td>
        </tr>
        <tr>
          <td>Aden Holloway</td>
          <td>Alabama (4)</td>
          <td>Arrested</td>
          <td>Mar 16</td>
          <td>3 days</td>
          <td class="war-impact">2.50</td>
        </tr>
      </tbody>
    </table>
    <div class="warning-callout">
      <strong>Duke: 99.4% &rarr; 86.6%.</strong> A 13-point swing from two injured players. Every injury in this table was public knowledge 3-64 days before tip-off. The model had no idea.
    </div>
  </div>

  <div class="card" style="border-color: rgba(249, 115, 22, 0.3);">
    <span class="card-label label-warning">Reality Check</span>
    <h3>Ohio State: 82% Favorite. Lost 66-64.</h3>
    <ul>
      <li>Our model gave Ohio State an <strong>82% win probability</strong> against TCU. They lost by 2</li>
      <li>TCU's top players (Pierre 3.5 {T_WAR}, Punch 3.6 {T_WAR}) outclassed Ohio State's best (Thornton 2.0 {T_WAR})</li>
      <li>The team-level efficiency gap was real, but it masked an unfavorable talent matchup at the top of the roster</li>
      <li>Player data wouldn't have fixed the aggregate model - but it would have <strong>flagged the risk</strong></li>
    </ul>
    <div class="warning-callout">
      <strong>The lesson:</strong> Player data adds no predictive value in aggregate. But when something <strong>changes</strong> - an injury, a suspension - player data is the only way to know your features are stale.
    </div>
  </div>
</section>

<!-- FINALE -->
<section class="finale">
  <div class="act-number" style="margin-bottom: 2rem;">The Takeaway</div>
  <div class="finale-quote">
    "The frontier of March Madness prediction isn't more features - it's knowing <em>when your features are stale</em>."
  </div>
  <p style="font-size: 1rem; color: var(--text-muted); margin-bottom: 3rem;">The AI builds the pipeline. The analyst asks the right questions.</p>

  <div style="display: flex; gap: 2rem; justify-content: center; flex-wrap: wrap; text-align: left; max-width: 600px; margin: 0 auto;">
    <div style="flex: 1; min-width: 250px;">
      <h4 style="color: var(--accent-teal); font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.75rem;">What worked</h4>
      <ul style="list-style: none; padding: 0; font-size: 0.9rem; color: var(--text-secondary);">
        <li style="margin-bottom: 0.4rem; padding-left: 1rem; position: relative;"><span style="position: absolute; left: 0; color: var(--accent-teal);">+</span> Efficiency metrics ({T_EFG}, per-possession)</li>
        <li style="margin-bottom: 0.4rem; padding-left: 1rem; position: relative;"><span style="position: absolute; left: 0; color: var(--accent-teal);">+</span> {T_ELO} with recency weighting</li>
        <li style="margin-bottom: 0.4rem; padding-left: 1rem; position: relative;"><span style="position: absolute; left: 0; color: var(--accent-teal);">+</span> {T_LGBM} with heavy regularization</li>
        <li style="margin-bottom: 0.4rem; padding-left: 1rem; position: relative;"><span style="position: absolute; left: 0; color: var(--accent-teal);">+</span> {T_CALIBRATED} over raw accuracy</li>
      </ul>
    </div>
    <div style="flex: 1; min-width: 250px;">
      <h4 style="color: var(--accent-orange); font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.75rem;">What didn't</h4>
      <ul style="list-style: none; padding: 0; font-size: 0.9rem; color: var(--text-secondary);">
        <li style="margin-bottom: 0.4rem; padding-left: 1rem; position: relative;"><span style="position: absolute; left: 0; color: var(--accent-orange);">-</span> Player-level aggregations (r=0.001)</li>
        <li style="margin-bottom: 0.4rem; padding-left: 1rem; position: relative;"><span style="position: absolute; left: 0; color: var(--accent-orange);">-</span> Late-season momentum (r=0.096)</li>
        <li style="margin-bottom: 0.4rem; padding-left: 1rem; position: relative;"><span style="position: absolute; left: 0; color: var(--accent-orange);">-</span> Roster experience in portal era</li>
        <li style="margin-bottom: 0.4rem; padding-left: 1rem; position: relative;"><span style="position: absolute; left: 0; color: var(--accent-orange);">-</span> Neural networks on tabular data</li>
      </ul>
    </div>
  </div>
</section>

<!-- GLOSSARY -->
<section class="glossary">
  <div class="section-break" style="margin-bottom: 2rem;"></div>
  <h2>Glossary</h2>
  <div class="glossary-grid">

    <div class="glossary-category ml">Machine Learning</div>

    <div class="glossary-item">
      <dt>LightGBM</dt>
      <dd>A fast, tree-based ML algorithm. It learns by building many simple decision trees in sequence, each one correcting the mistakes of the last.</dd>
    </div>
    <div class="glossary-item">
      <dt>XGBoost</dt>
      <dd>Another tree-based ML algorithm similar to LightGBM. Slightly slower but historically dominant in data science competitions.</dd>
    </div>
    <div class="glossary-item">
      <dt>Gradient Boosting</dt>
      <dd>The technique behind LightGBM and XGBoost. Builds many small models in sequence, where each new one focuses on fixing errors from the previous ones.</dd>
    </div>
    <div class="glossary-item">
      <dt>Neural Network</dt>
      <dd>An ML model inspired by the brain - layers of connected nodes that learn complex patterns. Often overkill for structured spreadsheet-style data.</dd>
    </div>
    <div class="glossary-item">
      <dt>Brier Score</dt>
      <dd>Measures how accurate probability predictions are. Lower is better. 0 = perfect, 1 = always wrong. Rewards honest confidence levels.</dd>
    </div>
    <div class="glossary-item">
      <dt>Calibrated Probabilities</dt>
      <dd>When a model says "70% chance," it should be right about 70% of the time. Calibration measures how honest the probabilities are.</dd>
    </div>
    <div class="glossary-item">
      <dt>Elo Ratings</dt>
      <dd>A rating system (originally from chess) that updates after every game. Beat a strong team, your rating rises more. Lose to a weak one, it drops fast.</dd>
    </div>
    <div class="glossary-item">
      <dt>Cross-Validation</dt>
      <dd>Testing a model by training on most of the data and checking predictions on the held-out portion. Repeat multiple times to get a reliable accuracy estimate.</dd>
    </div>

    <div class="glossary-category bball">Basketball</div>

    <div class="glossary-item">
      <dt>Seed</dt>
      <dd>Tournament ranking 1-16 assigned by the selection committee. 1-seeds are the strongest, 16-seeds the weakest. Four teams per seed line.</dd>
    </div>
    <div class="glossary-item">
      <dt>WAR</dt>
      <dd>Wins Above Replacement. Estimates how many extra wins a player contributes compared to a typical bench-level replacement.</dd>
    </div>
    <div class="glossary-item">
      <dt>WAR Share</dt>
      <dd>The percentage of a team's total WAR from their best player. Higher = more dependent on one star.</dd>
    </div>
    <div class="glossary-item">
      <dt>WAR Gini</dt>
      <dd>Measures how evenly talent is spread across a roster. Low = balanced team, high = a few stars carrying everyone else.</dd>
    </div>
    <div class="glossary-item">
      <dt>eFG%</dt>
      <dd>Effective Field Goal %. A shooting stat that gives extra credit for 3-pointers since they're worth more. Better measure than basic FG%.</dd>
    </div>
    <div class="glossary-item">
      <dt>Net Efficiency</dt>
      <dd>Points scored minus points allowed per 100 possessions. Removes pace bias so you can fairly compare fast vs. slow teams.</dd>
    </div>
    <div class="glossary-item">
      <dt>Turnover Rate</dt>
      <dd>How often a team loses the ball to the opponent without getting a shot off. Lower = better ball control.</dd>
    </div>
    <div class="glossary-item">
      <dt>Transfer Portal</dt>
      <dd>A system (started 2021) that lets college players transfer schools freely without sitting out a year. ~2,000 players enter annually.</dd>
    </div>
    <div class="glossary-item">
      <dt>NIL</dt>
      <dd>Name, Image, and Likeness. Rules (started 2021) allowing college athletes to earn money from endorsements. Changed recruiting dynamics significantly.</dd>
    </div>
    <div class="glossary-item">
      <dt>KenPom</dt>
      <dd>The most widely used college basketball analytics site. Their adjusted efficiency ratings are the gold standard for comparing teams.</dd>
    </div>

  </div>
</section>

<!-- FOOTER -->
<footer class="footer">
  <div class="footer-stats">
    <div class="footer-stat"><span>101</span> data files ingested</div>
    <div class="footer-stat"><span>57</span> features engineered</div>
    <div class="footer-stat"><span>30K</span> player records analyzed</div>
    <div class="footer-stat"><span>10K</span> bracket simulations</div>
    <div class="footer-stat"><span>0.0503</span> best Brier score</div>
  </div>
  <p>SSA &middot; March Madness 2026 &middot; Kaggle March Machine Learning Mania</p>
</footer>

</body>
</html>"""

with open(OUT_PATH, 'w', encoding='utf-8') as f:
    f.write(html)

size_mb = os.path.getsize(OUT_PATH) / (1024 * 1024)
print(f"Written: {OUT_PATH}")
print(f"Size: {size_mb:.1f} MB")
print(f"Images embedded: {len(images)}")
