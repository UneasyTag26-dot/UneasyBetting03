import os
import requests
import logging
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

BALLDONTLIE_API_URL = os.getenv("BALLDONTLIE_API_URL", "https://api.balldontlie.io/v1")
BALLDONTLIE_API_KEY = os.getenv("BALLDONTLIE_API_KEY")


def fetch_game_results(game_id: str) -> Optional[Dict[str, Any]]:
    """
    Fetch game results by game ID from balldontlie.
    This function assumes the game ID from The Odds API matches balldontlie's ID,
    which may not always be the case. In production, implement a proper mapping.
    """
    try:
        headers = {"Authorization": f"Bearer {BALLDONTLIE_API_KEY}"} if BALLDONTLIE_API_KEY else {}
        url = f"{BALLDONTLIE_API_URL}/games/{game_id}"
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logger.exception("Error fetching game results for %s: %s", game_id, e)
        return None
