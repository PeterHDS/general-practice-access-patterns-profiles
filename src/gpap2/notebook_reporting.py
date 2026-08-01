"""Compact, runtime-derived method-contract tables for public notebooks.

The functions in this module expose the tested package contract without
reimplementing validation, preprocessing, fitting or comparison logic inside
the notebooks.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

import numpy as np
import pandas as pd

from .config import ReferenceConfig
from .preprocessing import PreparedFeatureSet


def build_input_contract_table(
    config: ReferenceConfig,
    contracts: pd.DataFrame,
    validation: pd.DataFrame,
) -> pd.DataFrame:
    """Return one provenance and identity row per validated PCADI matrix."""
    observed = validation.set_index("filename")
    rows: list[dict[str, object]] = []
    for contract in contracts.to_dict("records"):
        filename = str(contract["filename"])
        result = observed.loc[filename]
        rows.append(
            {
                "public_filename": filename,
                "analytical_role": contract["analytical_role"],
                "observation_period": (
                    f"{config.observation_start} to {config.observation_end}"
                ),
                "rows": int(result["observed_rows"]),
                "numeric_features": int(result["observed_numeric_features"]),
                "identifier": config.identifier,
                "feature_names_in_order": " | ".join(
                    str(contract["columns_pipe"]).split("|")[1:]
                ),
                "sha256": contract["sha256"],
                "upstream_repository": config.pcadi.repository,
                "upstream_commit": config.pcadi.commit_sha,
                "upstream_tag": config.pcadi.tag,
            }
        )
    return pd.DataFrame(rows)


def build_quality_gate_table(
    validation: pd.DataFrame,
    cohort_validation: pd.DataFrame,
) -> pd.DataFrame:
    """Return concise observed values for matrix and cross-cohort gates."""
    filenames = validation["filename"].str.replace(".csv", "", regex=False).tolist()
    matrix_gates = (
        ("blank identifiers", "blank_practices", 0),
        ("duplicate identifiers", "duplicate_practices", 0),
        ("missing numerical values", "missing_numeric_values", 0),
        ("non-numeric values", "non_numeric_values", 0),
        ("non-finite values", "non_finite_numeric_values", 0),
        ("negative values", "negative_values", 0),
        ("shares outside permitted range", "out_of_range_share_values", 0),
        ("exact feature names and order", "exact_column_order", True),
        (
            "separate one-day and two-to-seven-day features",
            "required_booking_features_present",
            True,
        ),
        ("obsolete combined booking band absent", "forbidden_historical_features_absent", True),
    )
    rows: list[dict[str, object]] = []
    for label, column, expected in matrix_gates:
        values = validation[column].tolist()
        rows.append(
            {
                "scope": "all three PCADI matrices",
                "quality_gate": label,
                "expected": expected,
                "observed": " | ".join(
                    f"{name}={value}" for name, value in zip(filenames, values, strict=True)
                ),
                "passed": bool(validation[column].eq(expected).all()),
            }
        )
    for row in cohort_validation.to_dict("records"):
        rows.append(
            {
                "scope": "cross-cohort",
                "quality_gate": row["test"],
                "expected": row["expected"],
                "observed": row["observed"],
                "passed": bool(row["passed"]),
            }
        )
    return pd.DataFrame(rows)


def build_feature_contract_table(
    config: ReferenceConfig,
    specification_name: str,
) -> pd.DataFrame:
    """Return the ordered feature and transformation contract from configuration."""
    specification = config.specification(specification_name)
    log_features = set(specification.log1p_features)
    return pd.DataFrame(
        {
            "feature_order": range(1, len(specification.features) + 1),
            "feature": specification.features,
            "transformation": [
                "log1p" if feature in log_features else "unchanged"
                for feature in specification.features
            ],
            "included_in_model": True,
        }
    )


def build_transformation_contract_table(prepared: PreparedFeatureSet) -> pd.DataFrame:
    """Return fitted feature-level transformation and robust-scaling metadata."""
    log_features = set(prepared.metadata["log1p_features"])
    centers = prepared.metadata["centers"]
    scales = prepared.metadata["scales"]
    iqr = prepared.metadata["feature_iqr"]
    return pd.DataFrame(
        {
            "feature_order": range(1, len(prepared.feature_names) + 1),
            "feature": prepared.feature_names,
            "transformation": [
                "log1p" if feature in log_features else "unchanged"
                for feature in prepared.feature_names
            ],
            "fitted_median": centers,
            "pre_scaling_iqr": [iqr[feature] for feature in prepared.feature_names],
            "fitted_scale": scales,
            "iqr_gate_passed": [
                bool(np.isfinite(iqr[feature]) and iqr[feature] > 0)
                for feature in prepared.feature_names
            ],
        }
    )


def build_model_contract_table(
    config: ReferenceConfig,
    prepared: PreparedFeatureSet | None = None,
) -> pd.DataFrame:
    """Return configuration-controlled fitting and traceability settings."""
    settings: list[tuple[str, object, str]] = [
        ("algorithm", "K-Means", "src/gpap2/models.py"),
        ("clusters (k)", config.model.clusters, "reference configuration"),
        ("initialisation", "k-means++", "src/gpap2/models.py"),
        ("n_init", config.model.n_init, "reference configuration"),
        ("max_iter", config.model.max_iter, "reference configuration"),
        ("random_state", config.model.random_seed, "reference configuration"),
        ("implementation", config.model.algorithm, "reference configuration"),
        ("centering", "median", "reference configuration"),
        ("scaling", "interquartile range (IQR)", "reference configuration"),
        ("label alignment", "maximum-agreement Hungarian assignment", "src/gpap2/models.py"),
        ("identifier use", "traceability only; excluded from numerical model", "input contract"),
    ]
    if prepared is not None:
        passed = sum(
            np.isfinite(value) and value > 0
            for value in prepared.metadata["feature_iqr"].values()
        )
        settings.append(
            (
                "pre-fit IQR gate",
                f"{passed}/{len(prepared.feature_names)} features passed",
                "fitted preprocessing metadata",
            )
        )
    return pd.DataFrame(settings, columns=["setting", "value", "runtime_source"])


def build_output_contract_table(
    records: Mapping[str, Any] | Sequence[Mapping[str, Any]],
) -> pd.DataFrame:
    """Return output evidence supplied by the live analysis as a readable table."""
    if isinstance(records, Mapping):
        rows = [{"measure": name, "observed": value} for name, value in records.items()]
    else:
        rows = list(records)
    return pd.DataFrame(rows)


def build_comparison_contract_table(
    comparisons: pd.DataFrame,
    diagnostics: pd.DataFrame,
    assignment_checksums: Mapping[str, str],
) -> pd.DataFrame:
    """Combine computed partition metrics, silhouettes and canonical checksums."""
    silhouette = diagnostics.set_index("specification")["silhouette"].to_dict()
    rows: list[dict[str, object]] = []
    for row in comparisons.to_dict("records"):
        candidate = str(row["candidate"])
        rows.append(
            {
                **row,
                "reference_silhouette": silhouette.get(str(row["reference"])),
                "candidate_silhouette": silhouette.get(candidate),
                "canonical_aligned_assignment_sha256": assignment_checksums.get(candidate, ""),
            }
        )
    return pd.DataFrame(rows)


def build_composition_contract_table(
    shares: np.ndarray,
    closed: np.ndarray,
    basis: np.ndarray,
    part_names: Sequence[str],
    coordinate_names: Sequence[str],
    reconstruction_error: float,
    *,
    pseudocount_used: bool,
) -> pd.DataFrame:
    """Return the observed positivity, closure and ILR-basis checks."""
    row_sums = np.asarray(shares, dtype=float).sum(axis=1)
    orthonormal_error = float(
        np.max(np.abs(np.asarray(basis) @ np.asarray(basis).T - np.eye(len(coordinate_names))))
    )
    return build_output_contract_table(
        {
            "outcome part order": " | ".join(str(name) for name in part_names),
            "all source parts strictly positive": bool((np.asarray(shares) > 0).all()),
            "original row-sum minimum": float(row_sums.min()),
            "original row-sum median": float(np.median(row_sums)),
            "original row-sum maximum": float(row_sums.max()),
            "closed row-sum maximum error from one": float(
                np.max(np.abs(np.asarray(closed).sum(axis=1) - 1.0))
            ),
            "pseudocount used": pseudocount_used,
            "ILR coordinate order": " | ".join(str(name) for name in coordinate_names),
            "basis orthonormality maximum error": orthonormal_error,
            "inverse reconstruction maximum error": reconstruction_error,
        }
    )
