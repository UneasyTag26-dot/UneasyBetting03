import logging
from typing import Dict, Tuple, List

logger = logging.getLogger(__name__)


def american_to_probability(odds: int) -> float:
    """
    Convert American odds to implied probability.
    For positive odds (+150): implied probability = 100 / (odds + 100)
    For negative odds (-150): implied probability = -odds / (-odds + 100)
    Reference: standard implied probability formulas:contentReference[oaicite:2]{index=2}.
    """
    try:
        if odds > 0:
            prob = 100.0 / (odds + 100.0)
        else:
            prob = (-odds) / ((-odds) + 100.0)
        return prob
    except Exception as e:
        logger.exception("Failed to convert odds %s to probability: %s", odds, e)
        raise


def devig_market(odds_dict: Dict[str, Dict[str, int]]) -> Dict[str, Dict[str, float]]:
    """
    Remove the bookmaker's vig for a market.
    odds_dict: {book_name: {"over": american_odds, "under": american_odds}}
    Returns the same structure with implied probabilities normalized to sum to 1.
    """
    implied_probs = {}
    total_prob = 0.0

    # First compute implied probabilities (before vig)
    for book, sides in odds_dict.items():
        implied_probs[book] = {}
        over_prob = american_to_probability(sides["over"])
        under_prob = american_to_probability(sides["under"])
        implied_probs[book]["over"] = over_prob
        implied_probs[book]["under"] = under_prob
        total_prob += over_prob + under_prob

    # Normalize to remove vig
    if total_prob == 0:
        return {book: {"over": 0.0, "under": 0.0} for book in odds_dict}

    devigged = {}
    for book, sides in implied_probs.items():
        devigged[book] = {
            "over": sides["over"] / total_prob * 2,  # multiply by 2 so over+under sums to 1
            "under": sides["under"] / total_prob * 2,
        }
    return devigged
