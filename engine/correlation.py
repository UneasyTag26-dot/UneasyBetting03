import numpy as np
from typing import List, Tuple, Dict
import logging

logger = logging.getLogger(__name__)


def compute_correlated_probability(probabilities: List[float],
                                   legs: List[Tuple[str, str]],
                                   same_player_corr: float = 0.3,
                                   same_game_corr: float = 0.1) -> float:
    """
    Compute correlated parlay probability.
    - probabilities: list of individual leg hit probabilities.
    - legs: list of tuples (player_id, game_id) for each leg.
    - same_player_corr: correlation coefficient for legs on the same player.
    - same_game_corr: correlation coefficient for legs in the same game (different players).
    """
    n = len(probabilities)
    corr_matrix = np.eye(n)
    for i in range(n):
        for j in range(i + 1, n):
            player_i, game_i = legs[i]
            player_j, game_j = legs[j]
            if player_i == player_j:
                corr = same_player_corr
            elif game_i == game_j:
                corr = same_game_corr
            else:
                corr = 0.0
            corr_matrix[i, j] = corr_matrix[j, i] = corr

    from .probability import compute_parlay_probability
    return compute_parlay_probability(probabilities, correlation_matrix=corr_matrix)
