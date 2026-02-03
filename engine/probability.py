import numpy as np
from typing import List, Tuple, Dict
import logging

logger = logging.getLogger(__name__)


def build_probability_curve(lines: List[Tuple[float, float]]) -> Dict[float, float]:
    """
    Build a probability curve from alternate lines.
    Lines should be a list of tuples: (line_value, probability).
    The result is a sorted dictionary mapping line to probability.
    """
    try:
        sorted_lines = sorted(lines, key=lambda x: x[0])
        return {lv: prob for lv, prob in sorted_lines}
    except Exception as e:
        logger.exception("Error building probability curve: %s", e)
        raise


def interpolate_probability(curve: Dict[float, float], target_line: float) -> float:
    """
    Interpolate probability for a given target_line based on the curve.
    Uses linear interpolation between the nearest two points.
    """
    try:
        xs = list(curve.keys())
        ys = list(curve.values())
        if not xs:
            return 0.5  # default to 50% if no data
        if target_line <= xs[0]:
            return ys[0]
        if target_line >= xs[-1]:
            return ys[-1]

        # Find interval
        for i in range(1, len(xs)):
            if target_line < xs[i]:
                x0, y0 = xs[i - 1], ys[i - 1]
                x1, y1 = xs[i], ys[i]
                # linear interpolation
                m = (y1 - y0) / (x1 - x0)
                return y0 + m * (target_line - x0)
        return ys[-1]
    except Exception as e:
        logger.exception("Error interpolating probability for line %s: %s", target_line, e)
        return 0.5


def compute_parlay_probability(probabilities: List[float], correlation_matrix: np.ndarray = None) -> float:
    """
    Compute parlay probability given individual leg probabilities and an optional correlation matrix.
    If no correlation matrix is provided, assumes independence (product of probabilities).
    When provided, uses a Gaussian copula approximation.
    """
    try:
        if not probabilities:
            return 0.0
        if correlation_matrix is None:
            prod = float(np.prod(probabilities))
            return prod

        # Gaussian copula approximation: map probabilities to quantiles, apply correlation, then integrate
        # Basic approach: approximate joint probability by Monte Carlo sampling.
        n = len(probabilities)
        probs = np.array(probabilities)
        # convert to z-scores
        z = np.array([np.clip(np.quantile(np.random.normal(size=10000), p), -6, 6) for p in probs])
        # draw samples
        mean = np.zeros(n)
        cov = correlation_matrix
        samples = np.random.multivariate_normal(mean, cov, size=5000)
        hits = (samples < z).all(axis=1)
        return hits.mean()
    except Exception as e:
        logger.exception("Error computing parlay probability: %s", e)
        return float(np.prod(probabilities))
