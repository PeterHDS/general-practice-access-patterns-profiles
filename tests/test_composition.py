import numpy as np
import pytest

from gpap2.composition import (
    NHS_OUTCOME_ILR_BASIS,
    close_positive_composition,
    inverse_nhs_outcome_ilr,
    multiplicative_zero_replacement_for_nonreference_data,
    nhs_outcome_ilr,
    validate_orthonormal_basis,
)
from gpap2.contracts import NHS_OUTCOME_ILR_NAMES, OUTCOME_SHARE_COLUMNS


def test_authoritative_basis_values_names_and_order() -> None:
    expected = np.array(
        [
            [1 / np.sqrt(12), -3 / np.sqrt(12), 1 / np.sqrt(12), 1 / np.sqrt(12)],
            [2 / np.sqrt(6), 0, -1 / np.sqrt(6), -1 / np.sqrt(6)],
            [0, 0, 1 / np.sqrt(2), -1 / np.sqrt(2)],
        ]
    )
    np.testing.assert_allclose(NHS_OUTCOME_ILR_BASIS, expected, atol=0, rtol=0)
    assert OUTCOME_SHARE_COLUMNS == (
        "cbt_answered_share_cbt003",
        "cbt_missed_share",
        "cbt_ivr_share",
        "cbt_callback_request_share",
    )
    assert NHS_OUTCOME_ILR_NAMES == (
        "ilr_dealt_vs_missed",
        "ilr_answered_vs_ivr_callback",
        "ilr_ivr_vs_callback",
    )


def test_authoritative_basis_is_orthonormal() -> None:
    validate_orthonormal_basis(NHS_OUTCOME_ILR_BASIS)
    np.testing.assert_allclose(NHS_OUTCOME_ILR_BASIS.sum(axis=1), 0.0, atol=1e-12)
    np.testing.assert_allclose(
        NHS_OUTCOME_ILR_BASIS @ NHS_OUTCOME_ILR_BASIS.T,
        np.eye(3),
        atol=1e-12,
    )


def test_positive_closure_and_inverse_reconstruction() -> None:
    values = np.array([[0.6, 0.2, 0.1, 0.1], [3.0, 2.0, 4.0, 1.0]])
    closed = close_positive_composition(values)
    coordinates = nhs_outcome_ilr(values)
    reconstructed = inverse_nhs_outcome_ilr(coordinates)
    np.testing.assert_allclose(closed.sum(axis=1), 1.0, atol=1e-12)
    np.testing.assert_allclose(reconstructed, closed, atol=1e-12)


def test_reference_route_rejects_zero_and_never_adds_pseudocount() -> None:
    with pytest.raises(ValueError, match="no pseudocount"):
        nhs_outcome_ilr(np.array([[0.7, 0.2, 0.1, 0.0]]))


def test_nonreference_zero_replacement_is_separate_and_closed() -> None:
    values = np.array([[0.7, 0.2, 0.1, 0.0], [0.4, 0.3, 0.2, 0.1]])
    replaced = multiplicative_zero_replacement_for_nonreference_data(values, delta=1e-6)
    assert np.all(replaced > 0)
    np.testing.assert_allclose(replaced.sum(axis=1), 1.0, atol=1e-12)


@pytest.mark.parametrize("delta", [0.0, -1.0, 1.0, np.inf, np.nan])
def test_nonreference_zero_replacement_rejects_invalid_delta(delta: float) -> None:
    with pytest.raises(ValueError, match="delta"):
        multiplicative_zero_replacement_for_nonreference_data(
            np.array([[0.5, 0.5, 0.0]]), delta=delta
        )


def test_nonreference_zero_replacement_rejects_all_zero_row() -> None:
    with pytest.raises(ValueError, match="All-zero"):
        multiplicative_zero_replacement_for_nonreference_data(np.zeros((1, 4)))
