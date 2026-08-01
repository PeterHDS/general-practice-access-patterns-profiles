import numpy as np
import pandas as pd
import pytest
from sklearn.metrics import adjusted_rand_score

from gpap2.analysis import (
    canonical_assignment_sha256,
    compare_inbound_models,
    compare_outcome_models,
)
from gpap2.io import read_contract_csv, sha256
from gpap2.models import align_labels, fit_primary_kmeans
from gpap2.preprocessing import prepare_national_features


@pytest.fixture(scope="module")
def outcome_comparison(repository_root, reference_config):
    path = (
        repository_root
        / "data/reference/cbt_outcomes_sensitivity_clustering_matrix_21_features.csv"
    )
    frame = read_contract_csv(path)
    return compare_outcome_models(frame, reference_config)


@pytest.fixture(scope="module")
def inbound_comparison(repository_root, reference_config):
    frame = read_contract_csv(
        repository_root / "data/reference/cbt_inbound_sensitivity_clustering_matrix_17_features.csv"
    )
    return compare_inbound_models(frame, reference_config)


def test_inbound_regression_targets(inbound_comparison) -> None:
    row = inbound_comparison.comparisons.iloc[0]
    np.testing.assert_allclose(
        [
            row["adjusted_rand_index"],
            row["normalised_mutual_information"],
            row["aligned_agreement"],
        ],
        [0.5236133527826328, 0.46895509677416825, 0.8109271523178808],
        atol=1e-12,
        rtol=0,
    )
    assert int(row["reassigned_practices"]) == 571
    assert (
        canonical_assignment_sha256(
            inbound_comparison.assignments,
            "practice_code_standardised",
            "cbt_inbound_17_aligned_to_national_14",
        )
        == "892AFAF3EC4CEB9D6B1D7DC659580CE3E11C8809ED7D792A87AA7DC8BA67FDD3"
    )


def test_outcome_regression_targets(outcome_comparison) -> None:
    targets = {
        ("cbt_inbound_17", "cbt_outcome_nhs_ilr_20"): (
            0.894915323255533,
            0.8381597876460138,
            52,
            0.9642857142857143,
        ),
        ("cbt_inbound_17", "cbt_outcome_raw_21"): (
            0.24868476416596344,
            0.2876967008718118,
            729,
            0.4993131868131868,
        ),
    }
    for (reference, candidate), expected in targets.items():
        row = outcome_comparison.comparisons.loc[
            outcome_comparison.comparisons["reference"].eq(reference)
            & outcome_comparison.comparisons["candidate"].eq(candidate)
        ].iloc[0]
        np.testing.assert_allclose(
            [
                row["adjusted_rand_index"],
                row["normalised_mutual_information"],
                row["aligned_agreement"],
            ],
            [expected[0], expected[1], expected[3]],
            atol=1e-12,
            rtol=0,
        )
        assert int(row["reassigned_practices"]) == expected[2]


def test_authoritative_ilr_aligned_assignment_checksum(outcome_comparison) -> None:
    assert (
        canonical_assignment_sha256(
            outcome_comparison.assignments,
            "practice_code_standardised",
            "cbt_outcome_nhs_ilr_20_aligned_to_inbound_17",
        )
        == "8E2B9618DE15BB363EA28F2946F7DDBD530845AC413507265D7450EFA137376C"
    )


def test_canonical_hash_is_invariant_to_raw_label_permutation() -> None:
    reference = np.array([0, 0, 1, 1, 2, 2])
    candidate = np.array([2, 2, 0, 0, 1, 1])
    frame = pd.DataFrame(
        {
            "practice_code_standardised": [f"A{i:05d}" for i in range(6)],
            "aligned": align_labels(reference, candidate) + 1,
            "reference": reference + 1,
        }
    )
    assert canonical_assignment_sha256(
        frame, "practice_code_standardised", "aligned"
    ) == canonical_assignment_sha256(frame, "practice_code_standardised", "reference")


def test_reference_national_partition_and_contract(repository_root, reference_config) -> None:
    matrix = read_contract_csv(
        repository_root / "data/reference/primary_practice_access_clustering_matrix.csv"
    )
    reference_path = repository_root / "outputs/tables/national_profile_assignments.csv"
    reference = read_contract_csv(reference_path)
    prepared = prepare_national_features(matrix, reference_config)
    model = fit_primary_kmeans(prepared.matrix, reference_config.model)
    aligned = align_labels(reference["kmeans_cluster"].to_numpy(), model.labels_)
    assert adjusted_rand_score(reference["kmeans_cluster"], aligned) == 1.0
    np.testing.assert_array_equal(aligned, reference["kmeans_cluster"].to_numpy())
    assert pd.Series(aligned).value_counts().sort_index().to_dict() == {1: 1753, 2: 2312, 3: 2002}
    assert (
        sha256(reference_path) == "C8DA5EF5A270799FFDC5184D8A6ED127CA16982C5C4713F7D12738F010FDC457"
    )
