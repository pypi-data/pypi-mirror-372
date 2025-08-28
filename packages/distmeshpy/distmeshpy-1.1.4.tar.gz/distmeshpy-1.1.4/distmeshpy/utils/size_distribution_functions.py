"""Predefined size distribution functions."""

from typing import Any

import numpy as np

from distmeshpy._typing import Array


def huniform(p: Array, **kwargs: dict[str, Any]) -> Array:  # noqa: ARG001
    """Return uniform size distribution."""
    return np.ones((p.shape[0],))
