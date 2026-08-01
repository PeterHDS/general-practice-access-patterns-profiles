"""Contract-controlled preprocessing for national and telephone analyses."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.preprocessing import RobustScaler

from .config import FeatureSpecification, ReferenceConfig
from .contracts import NHS_OUTCOME_ILR_NAMES, OUTCOME_SHARE_COLUMNS


@dataclass(frozen=True)
class PreparedFeatureSet:
    specification: str
    feature_names: tuple[str, ...]
    matrix: np.ndarray
    transformed_frame: pd.DataFrame
    scaler: RobustScaler
    metadata: dict[str, object]


def prepare_feature_specification(
    frame: pd.DataFrame,
    specification: FeatureSpecification,
    config: ReferenceConfig,
) -> PreparedFeatureSet:
    missing = [name for name in specification.features if name not in frame.columns]
    if missing:
        raise ValueError(f"{specification.name} is missing required columns: {missing}")

    positions = [frame.columns.get_loc(name) for name in specification.features]
    if positions != sorted(positions):
        raise ValueError(f"{specification.name} feature columns are not in the authoritative order")

    values = frame.loc[:, specification.features].apply(pd.to_numeric, errors="raise").copy()
    array = values.to_numpy(dtype=float)
    if values.isna().any().any() or not np.isfinite(array).all():
        raise ValueError(f"{specification.name} contains missing or non-finite values")

    nonnegative = [
        name for name in specification.features if name not in specification.allow_negative_features
    ]
    if (values.loc[:, nonnegative] < 0).any().any():
        raise ValueError(
            f"{specification.name} contains a negative value in a non-negative feature"
        )

    transformed = values.copy()
    transformed.loc[:, specification.log1p_features] = np.log1p(
        transformed.loc[:, specification.log1p_features]
    )
    if not np.isfinite(transformed.to_numpy(dtype=float)).all():
        raise ValueError(f"{specification.name} log1p transformation produced a non-finite value")

    quantile_low, quantile_high = (value / 100 for value in config.scaling.quantile_range)
    quartile_1 = transformed.quantile(quantile_low)
    quartile_3 = transformed.quantile(quantile_high)
    iqr = quartile_3 - quartile_1
    invalid_iqr = iqr.index[(~np.isfinite(iqr.to_numpy(dtype=float))) | (iqr <= 0)].tolist()
    if invalid_iqr:
        details = ", ".join(f"{name}={iqr[name]!r}" for name in invalid_iqr)
        raise ValueError(f"{specification.name} contains invalid IQR features: {details}")

    scaling = config.scaling
    scaler = RobustScaler(
        with_centering=scaling.with_centering,
        with_scaling=scaling.with_scaling,
        quantile_range=scaling.quantile_range,
        unit_variance=scaling.unit_variance,
    )
    matrix = scaler.fit_transform(transformed)
    if not np.isfinite(matrix).all():
        raise ValueError(f"{specification.name} scaling produced a non-finite value")

    metadata = {
        "specification": specification.name,
        "source_file": specification.source_file,
        "rows": len(frame),
        "features": len(specification.features),
        "feature_names": list(specification.features),
        "log1p_features": list(specification.log1p_features),
        "scaling": {
            "with_centering": scaling.with_centering,
            "with_scaling": scaling.with_scaling,
            "quantile_range": list(scaling.quantile_range),
            "unit_variance": scaling.unit_variance,
        },
        "centers": scaler.center_.tolist() if scaling.with_centering else None,
        "scales": scaler.scale_.tolist() if scaling.with_scaling else None,
        "feature_iqr": {name: float(iqr[name]) for name in specification.features},
    }
    return PreparedFeatureSet(
        specification=specification.name,
        feature_names=specification.features,
        matrix=matrix,
        transformed_frame=transformed,
        scaler=scaler,
        metadata=metadata,
    )


def prepare_national_features(frame: pd.DataFrame, config: ReferenceConfig) -> PreparedFeatureSet:
    return prepare_feature_specification(frame, config.specification("national_14"), config)


def prepare_inbound_features(frame: pd.DataFrame, config: ReferenceConfig) -> PreparedFeatureSet:
    return prepare_feature_specification(frame, config.specification("cbt_inbound_17"), config)


def prepare_raw_outcome_features(
    frame: pd.DataFrame, config: ReferenceConfig
) -> PreparedFeatureSet:
    return prepare_feature_specification(frame, config.specification("cbt_outcome_raw_21"), config)


def prepare_ilr_outcome_features(
    frame: pd.DataFrame, config: ReferenceConfig
) -> PreparedFeatureSet:
    missing = [name for name in OUTCOME_SHARE_COLUMNS if name not in frame.columns]
    if missing:
        raise ValueError(f"Outcome source is missing compositional parts: {missing}")
    missing_coordinates = [name for name in NHS_OUTCOME_ILR_NAMES if name not in frame.columns]
    if missing_coordinates:
        raise ValueError(
            "NHS-aligned ILR coordinates must be calculated before preprocessing: "
            f"{missing_coordinates}"
        )
    return prepare_feature_specification(
        frame, config.specification("cbt_outcome_nhs_ilr_20"), config
    )
