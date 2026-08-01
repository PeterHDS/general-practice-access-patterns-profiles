"""Typed loading and validation of the GPAP² reference configuration."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class FeatureSpecification:
    name: str
    source_file: str
    features: tuple[str, ...]
    log1p_features: tuple[str, ...]
    allow_negative_features: tuple[str, ...]


@dataclass(frozen=True)
class ScalingConfig:
    with_centering: bool
    with_scaling: bool
    quantile_range: tuple[float, float]
    unit_variance: bool


@dataclass(frozen=True)
class KMeansConfig:
    random_seed: int
    clusters: int
    n_init: int
    max_iter: int
    algorithm: str


@dataclass(frozen=True)
class PCADIProvenance:
    repository: str
    commit_sha: str
    tag: str
    release_url: str


@dataclass(frozen=True)
class ReferenceConfig:
    config_path: Path
    contract_version: str
    observation_start: str
    observation_end: str
    identifier: str
    input_directory: Path
    output_directory: Path
    contracts_file: Path
    frozen_assignment_file: Path
    authority_checksum_file: Path
    model: KMeansConfig
    scaling: ScalingConfig
    pcadi: PCADIProvenance
    feature_specifications: dict[str, FeatureSpecification]

    @property
    def repository_root(self) -> Path:
        return self.config_path.parent.parent

    def resolve(self, relative_path: Path) -> Path:
        return self.repository_root / relative_path

    def specification(self, name: str) -> FeatureSpecification:
        try:
            return self.feature_specifications[name]
        except KeyError as exc:
            available = ", ".join(sorted(self.feature_specifications))
            raise KeyError(
                f"Unknown feature specification {name!r}; choose from {available}"
            ) from exc


def _tuple_of_unique_strings(values: object, field: str) -> tuple[str, ...]:
    if not isinstance(values, list) or not values or not all(isinstance(x, str) for x in values):
        raise ValueError(f"{field} must be a non-empty list of strings")
    result = tuple(values)
    if len(result) != len(set(result)):
        raise ValueError(f"{field} contains duplicate values")
    return result


def load_config(path: Path) -> ReferenceConfig:
    path = path.resolve()
    raw = json.loads(path.read_text(encoding="utf-8"))

    scaling_raw = raw["scaling"]
    quantiles = tuple(float(value) for value in scaling_raw["quantile_range"])
    if len(quantiles) != 2 or not 0 <= quantiles[0] < quantiles[1] <= 100:
        raise ValueError("scaling.quantile_range must be two increasing percentages")
    scaling = ScalingConfig(
        with_centering=bool(scaling_raw["with_centering"]),
        with_scaling=bool(scaling_raw["with_scaling"]),
        quantile_range=(quantiles[0], quantiles[1]),
        unit_variance=bool(scaling_raw["unit_variance"]),
    )

    model = KMeansConfig(
        random_seed=int(raw["random_seed"]),
        clusters=int(raw["primary_clusters"]),
        n_init=int(raw["primary_n_init"]),
        max_iter=int(raw["primary_max_iter"]),
        algorithm=str(raw["primary_algorithm"]),
    )
    if model.clusters < 2 or model.n_init < 1 or model.max_iter < 1:
        raise ValueError("K-Means configuration contains a non-positive control")
    if model.algorithm not in {"lloyd", "elkan"}:
        raise ValueError("primary_algorithm must be 'lloyd' or 'elkan'")

    specifications: dict[str, FeatureSpecification] = {}
    for name, item in raw["feature_specifications"].items():
        features = _tuple_of_unique_strings(item["features"], f"{name}.features")
        log1p = tuple(item["log1p_features"])
        allow_negative = tuple(item["allow_negative_features"])
        if not set(log1p).issubset(features):
            raise ValueError(f"{name}.log1p_features must be a subset of features")
        if not set(allow_negative).issubset(features):
            raise ValueError(f"{name}.allow_negative_features must be a subset of features")
        specifications[name] = FeatureSpecification(
            name=name,
            source_file=str(item["source_file"]),
            features=features,
            log1p_features=log1p,
            allow_negative_features=allow_negative,
        )

    required_specs = {
        "national_14": 14,
        "cbt_inbound_17": 17,
        "cbt_outcome_raw_21": 21,
        "cbt_outcome_nhs_ilr_20": 20,
    }
    for name, expected_count in required_specs.items():
        if name not in specifications or len(specifications[name].features) != expected_count:
            raise ValueError(f"{name} must define exactly {expected_count} features")

    pcadi_raw = raw["pcadi"]
    pcadi = PCADIProvenance(
        repository=str(pcadi_raw["repository"]),
        commit_sha=str(pcadi_raw["commit_sha"]),
        tag=str(pcadi_raw["tag"]),
        release_url=str(pcadi_raw["release_url"]),
    )
    if len(pcadi.commit_sha) != 40 or any(c not in "0123456789abcdef" for c in pcadi.commit_sha):
        raise ValueError("pcadi.commit_sha must be a 40-character lowercase Git commit SHA")

    return ReferenceConfig(
        config_path=path,
        contract_version=str(raw["contract_version"]),
        observation_start=str(raw["observation_start"]),
        observation_end=str(raw["observation_end"]),
        identifier=str(raw["identifier"]),
        input_directory=Path(raw["input_directory"]),
        output_directory=Path(raw["output_directory"]),
        contracts_file=Path(raw["contracts_file"]),
        frozen_assignment_file=Path(raw["frozen_assignment_file"]),
        authority_checksum_file=Path(raw["authority_checksum_file"]),
        model=model,
        scaling=scaling,
        pcadi=pcadi,
        feature_specifications=specifications,
    )
