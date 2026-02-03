import os
import time
import logging
from typing import List, Dict, Any
import requests
from dotenv import load_dotenv
from collections import defaultdict

from ..engine.odds import american_to_probability, devig_market
from ..engine.probability import build_probability_curve, interpolate_probability

load_dotenv()
logger = logging.getLogger(__name__)

ODDS_API_KEY = os.getenv("ODDS_API_KEY")
ODDS_API_URL = os.getenv("ODDS_API_URL", "https://api.the-odds-api.com/v4/sports/basketball_nba/odds")
REGION = os.getenv("REGION", "us")
MARKETS = os.getenv("MARKETS", "player_points,player_assists,player_rebounds").split(",")
CACHE_EXPIRY = int(os.getenv("CACHE_EXPIRY_SECONDS", "300"))

# Simple in-memory cache
_odds_cache: Dict[str, Any] = {}
_cache_timestamp: float = 0.0


def fetch_odds() -> List[Dict[str, Any]]:
    """
    Fetch player prop odds from The Odds API.
    Returns a list of event dictionaries.
    Implements basic caching to prevent redundant API calls.
    """
    global _odds_cache, _cache_timestamp
    now = time.time()
    if _odds_cache and (now - _cache_timestamp) < CACHE_EXPIRY:
        return _odds_cache["data"]

    params = {
        "api_key": ODDS_API_KEY,
        "regions": REGION,
        "markets": ",".join(MARKETS),
        "oddsFormat": "american",
    }
    try:
        resp = requests.get(ODDS_API_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        _odds_cache = {"data": data}
        _cache_timestamp = now
        return data
    except Exception as e:
        logger.exception("Error fetching odds: %s", e)
        return []


def parse_props(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Parse odds API response and yield a list of props with implied probabilities.
    Each item contains:
    - player
    - market
    - line
    - side
    - model_prob (placeholder, to be replaced by your model)
    - market_prob (devigged)
    - edge (model_prob - market_prob)
    """
    props = []
    for event in data:
        game_id = event.get("id")
        commence_time = event.get("commence_time")
        for bookmaker in event.get("bookmakers", []):
            book_name = bookmaker.get("title")
            for market in bookmaker.get("markets", []):
                market_key = market.get("key")
                outcomes = market.get("outcomes", [])
                # Group by player
                for outcome in outcomes:
                    player = outcome.get("description")
                    line = float(outcome.get("point")) if outcome.get("point") is not None else None
                    price = outcome.get("price")  # American odds
                    side = "over" if market_key.endswith("_over") else "under"
                    implied = american_to_probability(price)
                    props.append({
                        "player": player,
                        "market": market_key,
                        "line": line,
                        "side": side,
                        "book": book_name,
                        "game_id": game_id,
                        "price": price,
                        "implied_prob": implied,
                        "commence_time": commence_time,
                    })
    return props


def aggregate_and_rank(props: List[Dict[str, Any]], min_books: int = 1, min_edge: float = 0.05) -> List[Dict[str, Any]]:
    """
    Aggregate prop probabilities across books, compute devigged market probability and placeholder model probability.
    Returns a sorted list of candidate props with edge.
    """
    # Group by (player, market, line, side)
    grouped: Dict[tuple, List[Dict[str, Any]]] = defaultdict(list)
    for p in props:
        key = (p["player"], p["market"], p["line"], p["side"], p["game_id"])
        grouped[key].append(p)

    candidates = []
    for key, group in grouped.items():
        if len(group) < min_books:
            continue
        # Build odds dict for devig
        odds_dict = {}
        for g in group:
            if g["book"] not in odds_dict:
                odds_dict[g["book"]] = {"over": None, "under": None}
            odds_dict[g["book"]][g["side"]] = g["price"]
        # Remove vig
        devigged = devig_market(odds_dict)
        # Average devigged probability across books
        probs = [v[g["side"]] for g, v in zip(group, devigged.values())]
        market_prob = sum(probs) / len(probs)
        # Placeholder model probability: assume model equals market_prob + random small edge
        model_prob = min(max(market_prob + 0.05, 0.01), 0.99)  # +5% edge by default
        edge = model_prob - market_prob

        if edge < min_edge:
            continue

        player, market, line, side, game_id = key
        candidates.append({
            "player": player,
            "market": market,
            "line": line,
            "side": side,
            "model_prob": model_prob,
            "market_prob": market_prob,
            "edge": edge,
            "game_id": game_id,
            "player_id": None,  # to fill in if you fetch player IDs
        })

    candidates.sort(key=lambda x: x["edge"], reverse=True)
    return candidates
