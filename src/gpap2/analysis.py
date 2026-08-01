"""Reusable matched-cohort analytical comparisons used by notebooks and tests."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.metrics import silhouette_score

from .composition import close_positive_composition, nhs_outcome_ilr
from .config import ReferenceConfig
from .contracts import NHS_OUTCOME_ILR_NAMES, OUTCOME_SHARE_COLUMNS
from .models import align_labels, compare_partitions, fit_primary_kmeans
from .preprocessing import (
    PreparedFeatureSet,
    prepare_ilr_outcome_features,
    prepare_inbound_features,
    prepare_national_features,
    prepare_raw_outcome_features,
)


@dataclass(frozen=True)
class ComparisonResult:
    comparisons: pd.DataFrame
    assignments: pd.DataFrame
    diagnostics: pd.DataFrame
    prepared: dict[str, PreparedFeatureSet]


def canonical_assignment_frame(
    assignments: pd.DataFrame,
    identifier: str,
    label: str,
    canonical_label: str = "profile",
) -> pd.DataFrame:
    """Return the stable two-column representation used for public assignment hashes."""
    return (
        assignments[[identifier, label]]
        .rename(columns={label: canonical_label})
        .sort_values(identifier, kind="stable")
        .reset_index(drop=True)
    )


def canonical_assignment_sha256(
    assignments: pd.DataFrame,
    identifier: str,
    label: str,
    canonical_label: str = "profile",
) -> str:
    canonical = canonical_assignment_frame(assignments, identifier, label, canonical_label)
    payload = canonical.to_csv(index=False, lineterminator="\n").encode("utf-8")
    return hashlib.sha256(payload).hexdigest().upper()


def add_nhs_outcome_coordinates(frame: pd.DataFrame) -> tuple[pd.DataFrame, np.ndarray]:
    shares = frame.loc[:, OUTCOME_SHARE_COLUMNS].apply(pd.to_numeric, errors="raise")
    closed = close_positive_composition(shares.to_numpy(dtype=float))
    coordinates = nhs_outcome_ilr(shares.to_numpy(dtype=float))
    result = frame.copy()
    for index, name in enumerate(NHS_OUTCOME_ILR_NAMES):
        result[name] = coordinates[:, index]
    return result, closed


def _diagnostic(name: str, prepared: PreparedFeatureSet, labels: np.ndarray) -> dict[str, object]:
    counts = pd.Series(labels).value_counts().sort_index()
    return {
        "specification": name,
        "practices": prepared.matrix.shape[0],
        "features": prepared.matrix.shape[1],
        "silhouette": round(float(silhouette_score(prepared.matrix, labels)), 15),
        "cluster_counts_raw": "|".join(str(int(value)) for value in counts.tolist()),
    }


def compare_inbound_models(frame: pd.DataFrame, config: ReferenceConfig) -> ComparisonResult:
    national = prepare_national_features(frame, config)
    inbound = prepare_inbound_features(frame, config)
    prepared = {"national_14": national, "cbt_inbound_17": inbound}
    labels = {
        name: fit_primary_kmeans(item.matrix, config.model).labels_
        for name, item in prepared.items()
    }
    metrics = compare_partitions(labels["national_14"], labels["cbt_inbound_17"])
    comparisons = pd.DataFrame(
        [{"reference": "national_14", "candidate": "cbt_inbound_17", **metrics}]
    )
    assignments = pd.DataFrame(
        {
            config.identifier: frame[config.identifier].astype("string"),
            "national_14_raw": labels["national_14"] + 1,
            "cbt_inbound_17_raw": labels["cbt_inbound_17"] + 1,
            "cbt_inbound_17_aligned_to_national_14": align_labels(
                labels["national_14"], labels["cbt_inbound_17"]
            )
            + 1,
        }
    )
    diagnostics = pd.DataFrame(
        [_diagnostic(name, item, labels[name]) for name, item in prepared.items()]
    )
    return ComparisonResult(comparisons, assignments, diagnostics, prepared)


def compare_outcome_models(frame: pd.DataFrame, config: ReferenceConfig) -> ComparisonResult:
    working, _ = add_nhs_outcome_coordinates(frame)
    prepared = {
        "cbt_inbound_17": prepare_inbound_features(working, config),
        "cbt_outcome_raw_21": prepare_raw_outcome_features(working, config),
        "cbt_outcome_nhs_ilr_20": prepare_ilr_outcome_features(working, config),
    }
    labels = {
        name: fit_primary_kmeans(item.matrix, config.model).labels_
        for name, item in prepared.items()
    }
    pairs = [
        ("cbt_inbound_17", "cbt_outcome_nhs_ilr_20"),
        ("cbt_inbound_17", "cbt_outcome_raw_21"),
        ("cbt_outcome_raw_21", "cbt_outcome_nhs_ilr_20"),
    ]
    comparisons = pd.DataFrame(
        [
            {
                "reference": reference,
                "candidate": candidate,
                **compare_partitions(labels[reference], labels[candidate]),
            }
            for reference, candidate in pairs
        ]
    )
    assignments = pd.DataFrame({config.identifier: frame[config.identifier].astype("string")})
    for name, values in labels.items():
        assignments[f"{name}_raw"] = values + 1
    assignments["cbt_outcome_raw_21_aligned_to_inbound_17"] = (
        align_labels(labels["cbt_inbound_17"], labels["cbt_outcome_raw_21"]) + 1
    )
    assignments["cbt_outcome_nhs_ilr_20_aligned_to_inbound_17"] = (
        align_labels(labels["cbt_inbound_17"], labels["cbt_outcome_nhs_ilr_20"]) + 1
    )
    diagnostics = pd.DataFrame(
        [_diagnostic(name, item, labels[name]) for name, item in prepared.items()]
    )
    return ComparisonResult(comparisons, assignments, diagnostics, prepared)
