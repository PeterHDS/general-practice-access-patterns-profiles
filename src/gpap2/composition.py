"""Authoritative and explicitly non-reference composition utilities."""

from __future__ import annotations

import numpy as np

from .contracts import NHS_OUTCOME_ILR_NAMES, OUTCOME_SHARE_COLUMNS

NHS_OUTCOME_ILR_BASIS = np.array(
    [
        [
            1.0 / np.sqrt(12.0),
            -3.0 / np.sqrt(12.0),
            1.0 / np.sqrt(12.0),
            1.0 / np.sqrt(12.0),
        ],
        [
            2.0 / np.sqrt(6.0),
            0.0,
            -1.0 / np.sqrt(6.0),
            -1.0 / np.sqrt(6.0),
        ],
        [0.0, 0.0, 1.0 / np.sqrt(2.0), -1.0 / np.sqrt(2.0)],
    ],
    dtype=float,
)


def validate_orthonormal_basis(basis: np.ndarray, *, atol: float = 1e-12) -> None:
    candidate = np.asarray(basis, dtype=float)
    if candidate.shape != (3, 4):
        raise ValueError(f"The outcome ILR basis must have shape (3, 4), found {candidate.shape}")
    if not np.isfinite(candidate).all():
        raise ValueError("The outcome ILR basis contains a non-finite value")
    if not np.allclose(candidate.sum(axis=1), 0.0, atol=atol, rtol=0.0):
        raise ValueError("Every outcome ILR basis row must sum to zero")
    if not np.allclose(candidate @ candidate.T, np.eye(3), atol=atol, rtol=0.0):
        raise ValueError("The outcome ILR basis rows must be orthonormal")


def close_positive_composition(values: np.ndarray) -> np.ndarray:
    candidate = np.asarray(values, dtype=float)
    if candidate.ndim != 2 or candidate.shape[1] != len(OUTCOME_SHARE_COLUMNS):
        raise ValueError(
            "The reference outcome composition must be a two-dimensional four-part matrix"
        )
    if not np.isfinite(candidate).all():
        raise ValueError("The reference outcome composition contains a missing or non-finite value")
    if np.any(candidate <= 0):
        raise ValueError(
            "The reference outcome composition must be strictly positive; no pseudocount is used"
        )
    totals = candidate.sum(axis=1, keepdims=True)
    if np.any(totals <= 0):
        raise ValueError("Every reference outcome-composition total must be positive")
    closed = candidate / totals
    if not np.allclose(closed.sum(axis=1), 1.0, atol=1e-12, rtol=0.0):
        raise AssertionError("Outcome-composition closure failed")
    return closed


def nhs_outcome_ilr(values: np.ndarray) -> np.ndarray:
    """Return the three named NHS-aligned coordinates for the reference outcome order."""
    validate_orthonormal_basis(NHS_OUTCOME_ILR_BASIS)
    closed = close_positive_composition(values)
    coordinates = np.log(closed) @ NHS_OUTCOME_ILR_BASIS.T
    if coordinates.shape[1] != len(NHS_OUTCOME_ILR_NAMES) or not np.isfinite(coordinates).all():
        raise AssertionError("NHS outcome ILR calculation produced an invalid matrix")
    return coordinates


def inverse_nhs_outcome_ilr(coordinates: np.ndarray) -> np.ndarray:
    candidate = np.asarray(coordinates, dtype=float)
    if candidate.ndim != 2 or candidate.shape[1] != len(NHS_OUTCOME_ILR_NAMES):
        raise ValueError("NHS outcome ILR coordinates must have shape (n, 3)")
    if not np.isfinite(candidate).all():
        raise ValueError("NHS outcome ILR coordinates contain a non-finite value")
    validate_orthonormal_basis(NHS_OUTCOME_ILR_BASIS)
    positive = np.exp(candidate @ NHS_OUTCOME_ILR_BASIS)
    return positive / positive.sum(axis=1, keepdims=True)


def multiplicative_zero_replacement_for_nonreference_data(
    values: np.ndarray, *, delta: float = 1e-6
) -> np.ndarray:
    """Close and replace zeros for explicitly non-reference future data.

    This utility is not used by the GPAP² reference outcome analysis.
    """
    candidate = np.asarray(values, dtype=float)
    if candidate.ndim != 2 or candidate.shape[1] < 2:
        raise ValueError("A two-dimensional composition with at least two parts is required")
    if not np.isfinite(candidate).all():
        raise ValueError("Compositional parts must be finite")
    if np.any(candidate < 0):
        raise ValueError("Compositional parts cannot be negative")
    if not np.isfinite(delta) or not 0 < delta < 1:
        raise ValueError("delta must be finite and strictly between zero and one")
    totals = candidate.sum(axis=1, keepdims=True)
    if np.any(totals <= 0):
        raise ValueError("All-zero or non-positive-total rows cannot be replaced")
    closed = candidate / totals
    result = closed.copy()
    for index, row in enumerate(closed):
        zero_mask = row == 0
        if not zero_mask.any():
            continue
        replacement_total = delta * int(zero_mask.sum())
        if replacement_total >= 1:
            raise ValueError("delta is too large for the number of zero parts")
        positive_total = float(row[~zero_mask].sum())
        if positive_total <= 0:
            raise ValueError("A row must contain at least one positive part")
        result[index, zero_mask] = delta
        result[index, ~zero_mask] *= (1.0 - replacement_total) / positive_total
    if np.any(result <= 0) or not np.allclose(result.sum(axis=1), 1.0, atol=1e-12, rtol=0.0):
        raise AssertionError("Multiplicative zero replacement failed to preserve closure")
    return result
