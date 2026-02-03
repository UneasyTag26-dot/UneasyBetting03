from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from services.odds_service import fetch_odds, parse_props, aggregate_and_rank
from db.database import SessionLocal, init_db
from db import models
from engine.correlation import compute_correlated_probability

init_db()
app = FastAPI(title="NBA Prop Analyzer API")

# Allow frontend requests during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class EntryRequest(BaseModel):
    legs: List[int]
    payout_multiplier: Optional[float] = 1.0


@app.get("/scan")
def scan(edge: float = 0.05, min_books: int = 1, top: int = 10):
    data = fetch_odds()
    props = parse_props(data)
    candidates = aggregate_and_rank(props, min_books=min_books, min_edge=edge)
    return candidates[:top]


@app.get("/prop/{pick_id}")
def get_prop(pick_id: int):
    session = SessionLocal()
    pick = session.query(models.Pick).filter(models.Pick.id == pick_id).first()
    if not pick:
        raise HTTPException(status_code=404, detail="Pick not found")
    return {
        "id": pick.id,
        "player": pick.player,
        "market": pick.market,
        "line": pick.line,
        "side": pick.side,
        "model_prob": pick.model_prob,
        "market_prob": pick.market_prob,
        "edge": pick.edge,
        "result": pick.result,
    }


@app.post("/entry/evaluate")
def evaluate_entry(req: EntryRequest):
    if not (2 <= len(req.legs) <= 5):
        raise HTTPException(status_code=400, detail="Entry must have between 2 and 5 legs")
    session = SessionLocal()
    probs = []
    legs_info = []
    for pid in req.legs:
        pick = session.query(models.Pick).filter(models.Pick.id == pid).first()
        if not pick:
            raise HTTPException(status_code=404, detail=f"Pick ID {pid} not found")
        probs.append(pick.model_prob)
        legs_info.append((pick.player_id or pick.player, pick.game_id))
    combined_prob = compute_correlated_probability(probs, legs_info)
    fair_odds = 1 / combined_prob if combined_prob > 0 else None
    ev = combined_prob * (req.payout_multiplier or 1.0) - 1
    return {
        "combined_probability": combined_prob,
        "fair_odds": fair_odds,
        "expected_value": ev,
    }


@app.get("/history")
def history():
    session = SessionLocal()
    picks = session.query(models.Pick).all()
    return [
        {
            "id": p.id,
            "timestamp": p.timestamp,
            "player": p.player,
            "market": p.market,
            "line": p.line,
            "side": p.side,
            "model_prob": p.model_prob,
            "market_prob": p.market_prob,
            "edge": p.edge,
            "result": p.result,
        }
        for p in picks
    ]
