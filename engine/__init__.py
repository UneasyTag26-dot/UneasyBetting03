
---

### `engine/__init__.py`
```python
"""
Engine package responsible for core probability calculations and odds processing.
"""

from .odds import american_to_probability, devig_market
from .probability import build_probability_curve, interpolate_probability, compute_parlay_probability
from .correlation import compute_correlated_probability

__all__ = [
    "american_to_probability",
    "devig_market",
    "build_probability_curve",
    "interpolate_probability",
    "compute_parlay_probability",
    "compute_correlated_probability",
]
