"""Input and cross-cohort contract validation with precise failure evidence."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from .config import ReferenceConfig
from .contracts import FORBIDDEN_HISTORICAL_FEATURES, REQUIRED_BOOKING_FEATURES
from .io import read_contract_csv, sha256


@dataclass(frozen=True)
class ValidationResult:
    filename: str
    expected_rows: int
    observed_rows: int
    expected_columns: int
    observed_columns: int
    expected_numeric_features: int
    observed_numeric_features: int
    identifier: str
    identifier_present: bool
    exact_column_order: bool
    unique_practices: int
    blank_practices: int
    duplicate_practices: int
    missing_numeric_values: int
    non_numeric_values: int
    non_finite_numeric_values: int
    negative_values: int
    out_of_range_share_values: int
    required_booking_features_present: bool
    forbidden_historical_features_absent: bool
    checksum_matches: bool
    size_matches: bool
    dimensions_match: bool
    provenance_matches: bool
    passed: bool
    failure_reasons: str


def _expected_columns(contract: pd.Series) -> list[str]:
    return str(contract["columns_pipe"]).split("|")


def validate_matrix(
    path: Path,
    contract: pd.Series,
    config: ReferenceConfig | None = None,
) -> ValidationResult:
    frame = read_contract_csv(path)
    expected_columns = _expected_columns(contract)
    identifier = str(contract["identifier"])
    identifier_present = identifier in frame.columns
    exact_column_order = frame.columns.tolist() == expected_columns

    if identifier_present:
        identifier_values = frame[identifier].astype("string")
        blank_practices = int(
            (identifier_values.isna() | identifier_values.fillna("").str.strip().eq("")).sum()
        )
        duplicate_practices = int(identifier_values.duplicated().sum())
        unique_practices = int(identifier_values.nunique(dropna=True))
        numeric_source = frame.drop(columns=[identifier])
    else:
        blank_practices = len(frame)
        duplicate_practices = 0
        unique_practices = 0
        numeric_source = frame

    blank_numeric = numeric_source.isna() | numeric_source.astype("string").apply(
        lambda column: column.str.strip().eq("")
    )
    numeric = numeric_source.apply(pd.to_numeric, errors="coerce")
    non_numeric = int((numeric.isna() & ~blank_numeric).sum().sum())
    missing = int(blank_numeric.sum().sum())
    numeric_array = numeric.to_numpy(dtype=float)
    non_finite = int((~np.isfinite(numeric_array) & ~np.isnan(numeric_array)).sum())
    negative = int((numeric < 0).sum().sum())
    share_columns = [name for name in numeric.columns if name.endswith("_share")]
    out_of_range_shares = int(
        sum(((numeric[name] < 0) | (numeric[name] > 1)).sum() for name in share_columns)
    )

    required_booking = all(name in frame.columns for name in REQUIRED_BOOKING_FEATURES)
    forbidden_absent = all(name not in frame.columns for name in FORBIDDEN_HISTORICAL_FEATURES)
    checksum_matches = sha256(path) == str(contract["sha256"]).upper()
    size_matches = path.stat().st_size == int(contract["size_bytes"])
    dimensions_match = frame.shape == (int(contract["rows"]), int(contract["columns"]))
    numeric_features_match = numeric_source.shape[1] == int(contract["numeric_features"])

    provenance_matches = all(
        str(contract[field]).strip()
        for field in ("source_repository", "source_commit", "source_tag", "download_url")
    )
    if config is not None:
        provenance_matches = provenance_matches and all(
            [
                str(contract["source_repository"]) == config.pcadi.repository,
                str(contract["source_commit"]) == config.pcadi.commit_sha,
                str(contract["source_tag"]) == config.pcadi.tag,
                identifier == config.identifier,
            ]
        )

    checks = {
        "identifier column is present": identifier_present,
        "columns and order match": exact_column_order,
        "dimensions match": dimensions_match,
        "numeric feature count matches": numeric_features_match,
        "identifiers are nonblank": blank_practices == 0,
        "identifiers are unique": duplicate_practices == 0,
        "numeric values are not missing": missing == 0,
        "all feature values are numeric": non_numeric == 0,
        "numeric values are finite": non_finite == 0,
        "numeric values are non-negative": negative == 0,
        "share values are within zero and one": out_of_range_shares == 0,
        "separate one-day and two-to-seven-day features are present": required_booking,
        "obsolete one-to-seven-day feature is absent": forbidden_absent,
        "SHA-256 matches": checksum_matches,
        "byte size matches": size_matches,
        "PCADI provenance matches configuration": provenance_matches,
    }
    failures = [name for name, passed in checks.items() if not passed]
    return ValidationResult(
        filename=path.name,
        expected_rows=int(contract["rows"]),
        observed_rows=len(frame),
        expected_columns=int(contract["columns"]),
        observed_columns=len(frame.columns),
        expected_numeric_features=int(contract["numeric_features"]),
        observed_numeric_features=numeric_source.shape[1],
        identifier=identifier,
        identifier_present=identifier_present,
        exact_column_order=exact_column_order,
        unique_practices=unique_practices,
        blank_practices=blank_practices,
        duplicate_practices=duplicate_practices,
        missing_numeric_values=missing,
        non_numeric_values=non_numeric,
        non_finite_numeric_values=non_finite,
        negative_values=negative,
        out_of_range_share_values=out_of_range_shares,
        required_booking_features_present=required_booking,
        forbidden_historical_features_absent=forbidden_absent,
        checksum_matches=checksum_matches,
        size_matches=size_matches,
        dimensions_match=dimensions_match,
        provenance_matches=provenance_matches,
        passed=not failures,
        failure_reasons="; ".join(failures),
    )


def validate_contract_directory(
    data_dir: Path,
    contracts_path: Path,
    config: ReferenceConfig | None = None,
) -> pd.DataFrame:
    contracts = pd.read_csv(contracts_path)
    results = []
    for _, contract in contracts.iterrows():
        path = data_dir / contract["filename"]
        if not path.exists():
            raise FileNotFoundError(f"Required PCADI input is absent: {path}")
        results.append(asdict(validate_matrix(path, contract, config)))
    return pd.DataFrame(results)


def validate_cohort_relationships(data_dir: Path, config: ReferenceConfig) -> pd.DataFrame:
    national = read_contract_csv(data_dir / config.specification("national_14").source_file)
    inbound = read_contract_csv(data_dir / config.specification("cbt_inbound_17").source_file)
    outcomes = read_contract_csv(data_dir / config.specification("cbt_outcome_raw_21").source_file)
    identifier = config.identifier
    national_features = list(config.specification("national_14").features)
    rows = []
    for child_name, child, parent_name, parent in [
        ("CBT inbound", inbound, "national", national),
        ("CBT outcome-complete", outcomes, "CBT inbound", inbound),
    ]:
        missing_ids = set(child[identifier]) - set(parent[identifier])
        rows.append(
            {
                "test": f"{child_name} practices are nested in {parent_name}",
                "expected": 0,
                "observed": len(missing_ids),
                "passed": len(missing_ids) == 0,
            }
        )
    for child_name, child in [("CBT inbound", inbound), ("CBT outcome-complete", outcomes)]:
        merged = child[[identifier, *national_features]].merge(
            national[[identifier, *national_features]],
            on=identifier,
            suffixes=("_child", "_national"),
            validate="one_to_one",
        )
        unequal = sum(
            int(
                (
                    ~np.isclose(
                        merged[f"{feature}_child"], merged[f"{feature}_national"], rtol=0, atol=0
                    )
                ).sum()
            )
            for feature in national_features
        )
        rows.append(
            {
                "test": f"{child_name} inherits all national feature values exactly",
                "expected": 0,
                "observed": unequal,
                "passed": unequal == 0,
            }
        )
    return pd.DataFrame(rows)
