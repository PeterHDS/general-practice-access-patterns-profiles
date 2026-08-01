"""Deterministic profile models, label alignment and comparison metrics."""

from __future__ import annotations

import numpy as np
from scipy.optimize import linear_sum_assignment
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score

from .config import KMeansConfig


def fit_primary_kmeans(matrix: np.ndarray, settings: KMeansConfig) -> KMeans:
    values = np.asarray(matrix, dtype=float)
    if values.ndim != 2 or not np.isfinite(values).all():
        raise ValueError("K-Means input must be a finite two-dimensional matrix")
    return KMeans(
        n_clusters=settings.clusters,
        init="k-means++",
        n_init=settings.n_init,
        max_iter=settings.max_iter,
        random_state=settings.random_seed,
        algorithm=settings.algorithm,
    ).fit(values)


def align_labels(reference: np.ndarray, candidate: np.ndarray) -> np.ndarray:
    reference = np.asarray(reference)
    candidate = np.asarray(candidate)
    if reference.ndim != 1 or candidate.ndim != 1 or reference.shape != candidate.shape:
        raise ValueError("Reference and candidate labels must be one-dimensional and equal length")
    labels_ref = np.sort(np.unique(reference))
    labels_new = np.sort(np.unique(candidate))
    if len(labels_ref) != len(labels_new):
        raise ValueError("Reference and candidate must contain the same number of clusters")
    agreement = np.array(
        [[np.sum((reference == r) & (candidate == c)) for c in labels_new] for r in labels_ref]
    )
    rows, cols = linear_sum_assignment(-agreement)
    mapping = {labels_new[col]: labels_ref[row] for row, col in zip(rows, cols, strict=True)}
    return np.array([mapping[label] for label in candidate])


def compare_partitions(reference: np.ndarray, candidate: np.ndarray) -> dict[str, float | int]:
    aligned = align_labels(reference, candidate)
    return {
        "adjusted_rand_index": float(adjusted_rand_score(reference, candidate)),
        "normalised_mutual_information": float(normalized_mutual_info_score(reference, candidate)),
        "aligned_agreement": float(np.mean(np.asarray(reference) == aligned)),
        "reassigned_practices": int(np.sum(np.asarray(reference) != aligned)),
    }
