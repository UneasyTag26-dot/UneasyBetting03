# UneasyBetting03
# NBA Prop Analyzer

This repository provides a complete, end‑to‑end application to scan NBA player prop markets, estimate fair probabilities, compute expected value, and suggest picks.  It includes both a Streamlit UI for rapid iteration and a FastAPI + React UI for a more scalable solution.  The core engine and database are shared between both UIs.

## Features

- Pulls current player‑prop odds from The Odds API (multiple books, alt‑lines).
- Converts American odds to implied probabilities and de‑viggs them:contentReference[oaicite:0]{index=0}.
- Builds probability curves from alternate lines and interpolates probabilities.
- Computes parlay probabilities, fair odds, and expected value, including simple correlation modeling.
- Scans all upcoming NBA events and ranks candidate props by edge.
- Provides CLI commands for scanning, evaluating entries, and updating results.
- Streamlit UI with dashboard, entry builder, history, and settings tabs.
- FastAPI backend with REST endpoints and a React (Vite) frontend.
- SQLite persistence using SQLAlchemy.
- Uses environment variables for all API keys; no keys are hard‑coded.
- Robust error handling, basic caching, and logging.

## Setup

1. **Clone the repository**

```bash
git clone <your-git-url>
cd nba_prop_analyzer
