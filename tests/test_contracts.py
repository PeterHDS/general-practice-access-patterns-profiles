import json

import numpy as np
import pandas as pd

from gpap2.config import load_config
from gpap2.models import fit_primary_kmeans
from gpap2.preprocessing import prepare_national_features


def test_feature_contracts_are_explicit_and_immutable(reference_config) -> None:
    counts = {
        "national_14": 14,
        "cbt_inbound_17": 17,
        "cbt_outcome_raw_21": 21,
        "cbt_outcome_nhs_ilr_20": 20,
    }
    for name, expected in counts.items():
        specification = reference_config.specification(name)
        assert len(specification.features) == expected
        assert len(specification.features) == len(set(specification.features))
        assert "gpad_1_to_7_days_share" not in specification.features
        assert "gpad_1_day_share" in specification.features
        assert "gpad_2_to_7_days_share" in specification.features


def test_reference_model_controls_are_loaded_from_configuration(reference_config) -> None:
    assert reference_config.model.random_seed == 2026
    assert reference_config.model.clusters == 3
    assert reference_config.model.n_init == 100
    assert reference_config.model.max_iter == 500
    assert reference_config.model.algorithm == "lloyd"


def test_changed_configuration_changes_model_settings(reference_config, tmp_path) -> None:
    raw = json.loads(reference_config.config_path.read_text(encoding="utf-8"))
    raw["random_seed"] = 7
    raw["primary_n_init"] = 9
    path = tmp_path / "config.json"
    path.write_text(json.dumps(raw), encoding="utf-8")
    changed = load_config(path)
    matrix = np.vstack([np.zeros((5, 2)), np.ones((5, 2)) * 5, np.ones((5, 2)) * 10])
    model = fit_primary_kmeans(matrix, changed.model)
    assert model.random_state == 7
    assert model.n_init == 9


def test_national_preprocessing_is_deterministic(reference_config) -> None:
    features = reference_config.specification("national_14").features
    frame = pd.DataFrame({name: np.linspace(0.1, 1.0, 12) for name in features})
    first = prepare_national_features(frame, reference_config)
    second = prepare_national_features(frame, reference_config)
    assert first.feature_names == features
    np.testing.assert_allclose(first.matrix, second.matrix)


def test_feature_order_violation_is_rejected(reference_config) -> None:
    features = list(reference_config.specification("national_14").features)
    frame = pd.DataFrame({name: [0.2, 0.3] for name in reversed(features)})
    try:
        prepare_national_features(frame, reference_config)
    except ValueError as exc:
        assert "authoritative order" in str(exc)
    else:
        raise AssertionError("Reversed feature order was accepted")


def test_iqr_metadata_is_recorded_for_transformed_and_untransformed_features(
    reference_config,
) -> None:
    features = reference_config.specification("national_14").features
    frame = pd.DataFrame({name: np.linspace(0.1, 10.0, 20) for name in features})
    prepared = prepare_national_features(frame, reference_config)
    assert set(prepared.metadata["feature_iqr"]) == set(features)
    assert all(value > 0 for value in prepared.metadata["feature_iqr"].values())


def test_one_constant_feature_is_rejected_and_named(reference_config) -> None:
    features = reference_config.specification("national_14").features
    frame = pd.DataFrame({name: np.linspace(0.1, 10.0, 20) for name in features})
    frame[features[0]] = 1.0
    with np.testing.assert_raises_regex(ValueError, features[0]):
        prepare_national_features(frame, reference_config)


def test_all_constant_features_are_rejected(reference_config) -> None:
    features = reference_config.specification("national_14").features
    frame = pd.DataFrame({name: np.ones(20) for name in features})
    with np.testing.assert_raises_regex(ValueError, "invalid IQR features"):
        prepare_national_features(frame, reference_config)


def test_non_finite_feature_is_rejected_before_iqr(reference_config) -> None:
    features = reference_config.specification("national_14").features
    frame = pd.DataFrame({name: np.linspace(0.1, 10.0, 20) for name in features})
    frame.loc[0, features[-1]] = np.inf
    with np.testing.assert_raises_regex(ValueError, "missing or non-finite"):
        prepare_national_features(frame, reference_config)
