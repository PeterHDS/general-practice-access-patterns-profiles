from pathlib import Path

import pandas as pd

from gpap2.io import sha256
from gpap2.validation import validate_cohort_relationships, validate_matrix


def make_contract(path: Path, columns: list[str], identifier: str) -> pd.Series:
    return pd.Series(
        {
            "filename": path.name,
            "rows": 2,
            "columns": len(columns),
            "numeric_features": len(columns) - 1,
            "size_bytes": path.stat().st_size,
            "identifier": identifier,
            "columns_pipe": "|".join(columns),
            "sha256": sha256(path),
            "source_repository": "example/repository",
            "source_commit": "a" * 40,
            "source_tag": "reference",
            "download_url": "https://example.invalid/matrix.csv",
        }
    )


def test_validate_matrix_accepts_exact_contract(tmp_path: Path) -> None:
    identifier = "practice_code_standardised"
    path = tmp_path / "matrix.csv"
    columns = [identifier, "gpad_1_day_share", "gpad_2_to_7_days_share"]
    pd.DataFrame(
        {
            identifier: ["A00001", "A00002"],
            "gpad_1_day_share": [0.1, 0.2],
            "gpad_2_to_7_days_share": [0.3, 0.4],
        }
    ).to_csv(path, index=False)
    result = validate_matrix(path, make_contract(path, columns, identifier))
    assert result.passed
    assert result.unique_practices == 2


def test_validate_matrix_rejects_malformed_identifier(tmp_path: Path) -> None:
    identifier = "practice_code_standardised"
    path = tmp_path / "matrix.csv"
    columns = [identifier, "gpad_1_day_share", "gpad_2_to_7_days_share"]
    pd.DataFrame(
        {
            identifier: ["", "A00002"],
            "gpad_1_day_share": [0.1, 0.2],
            "gpad_2_to_7_days_share": [0.3, 0.4],
        }
    ).to_csv(path, index=False)
    result = validate_matrix(path, make_contract(path, columns, identifier))
    assert not result.passed
    assert "identifiers are nonblank" in result.failure_reasons


def test_validate_matrix_rejects_forbidden_booking_feature(tmp_path: Path) -> None:
    identifier = "practice_code_standardised"
    path = tmp_path / "matrix.csv"
    columns = [identifier, "gpad_1_day_share", "gpad_2_to_7_days_share", "gpad_1_to_7_days_share"]
    pd.DataFrame(
        {
            identifier: ["A00001", "A00002"],
            "gpad_1_day_share": [0.1, 0.2],
            "gpad_2_to_7_days_share": [0.3, 0.4],
            "gpad_1_to_7_days_share": [0.4, 0.6],
        }
    ).to_csv(path, index=False)
    result = validate_matrix(path, make_contract(path, columns, identifier))
    assert not result.passed
    assert "obsolete one-to-seven-day feature is absent" in result.failure_reasons


def test_reference_cohort_relationships(repository_root, reference_config) -> None:
    results = validate_cohort_relationships(repository_root / "data/reference", reference_config)
    assert results["passed"].all()
