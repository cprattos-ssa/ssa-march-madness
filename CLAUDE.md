# SSA March Madness - NCAA Tournament Prediction

## Project Overview
Kaggle competition entry for March Machine Learning Mania 2026. Predict P(TeamA beats TeamB) for every possible NCAA tournament matchup. Evaluated on Brier score.

## Repo Structure
- `config/` - YAML configs for pipeline, features, and model hyperparameters
- `data/` - raw (immutable downloads), interim (cleaned), processed (feature matrices), submissions
- `notebooks/` - EDA and experimentation (numbered for reading order)
- `src/` - Production pipeline code (data, features, models, evaluation, submission, utils)
- `scripts/` - Entry point scripts (pipeline, CV, submission generation)
- `research/` - Competition research notes and findings
- `models/` - Saved model artifacts
- `results/` - Experiment log and figures

## Key Commands
- `make setup` - Install dependencies
- `make data` - Download Kaggle data
- `make train` - Train active model
- `make cv` - Run cross-validation
- `make submit` - Generate submission CSV

## Strategy
- Build men's bracket model first, then apply same pipeline to women's (config-driven via `gender` field)
- Focus on efficiency metrics (eFG%, off/def efficiency), Elo ratings, seed features, and KenPom data
- Brier score rewards well-calibrated probabilities - calibration is a first-class concern
- Weight recent seasons more heavily (game has evolved significantly - 3-point revolution, transfer portal)

## Tech Stack
Python 3.12, pandas, scikit-learn, XGBoost, LightGBM, PyTorch, pyarrow

## Virtual Environment
Always activate before running Python: `source .venv/Scripts/activate`

## Style Rules
- Never include "Co-Authored-By" or any mention of Claude/AI in commit messages or PR descriptions
- Always use normal dashes/hyphens (-) instead of em dashes
- Keep commit messages concise and focused on the "why"
