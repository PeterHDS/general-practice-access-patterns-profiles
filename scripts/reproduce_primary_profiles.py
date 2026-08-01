"""Reproduce the frozen three-profile national solution under the reference contract."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import adjusted_rand_score, silhouette_samples, silhouette_score

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gpap2.config import load_config  # noqa: E402
from gpap2.io import read_contract_csv, sha256  # noqa: E402
from gpap2.models import align_labels, fit_primary_kmeans  # noqa: E402
from gpap2.preprocessing import prepare_national_features  # noqa: E402
from gpap2.validation import validate_matrix  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT / "configs" / "reference_apr2025_mar2026.json",
    )
    parser.add_argument("--input", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    config = load_config(args.config)
    specification = config.specification("national_14")
    input_path = args.input or config.resolve(config.input_directory) / specification.source_file
    output_path = args.output or config.resolve(config.output_directory) / "primary_assignments.csv"
    manifest_path = output_path.with_name(f"{output_path.stem}_run_manifest.json")

    contracts = pd.read_csv(config.resolve(config.contracts_file))
    contract = contracts.loc[contracts["filename"].eq(input_path.name)]
    if len(contract) != 1:
        raise ValueError(f"No unique input contract found for {input_path.name}")
    validation = validate_matrix(input_path, contract.iloc[0], config)
    if not validation.passed:
        raise ValueError(f"National matrix failed validation: {validation.failure_reasons}")

    frame = read_contract_csv(input_path)
    prepared = prepare_national_features(frame, config)
    model = fit_primary_kmeans(prepared.matrix, config.model)

    frozen_path = config.resolve(config.frozen_assignment_file)
    frozen = read_contract_csv(frozen_path)
    if not frame[config.identifier].equals(frozen[config.identifier]):
        raise ValueError("Frozen assignment order does not match the national input matrix")
    frozen_labels = frozen["kmeans_cluster"].to_numpy(dtype=int)
    final_labels = align_labels(frozen_labels, model.labels_)
    exact_agreement = float(np.mean(final_labels == frozen_labels))
    ari = float(adjusted_rand_score(frozen_labels, final_labels))
    if exact_agreement != 1.0 or not np.array_equal(final_labels, frozen_labels):
        raise AssertionError(
            "Frozen assignments were not reproduced exactly: "
            f"agreement={exact_agreement}, ARI={ari}"
        )

    silhouettes = silhouette_samples(prepared.matrix, final_labels)
    result = frame[[config.identifier]].copy()
    result["national_profile"] = final_labels
    result["silhouette_value"] = silhouettes
    output_path.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output_path, index=False, lineterminator="\n")

    profile_sizes = {
        str(int(profile)): int(count)
        for profile, count in pd.Series(final_labels).value_counts().sort_index().items()
    }
    manifest = {
        "contract_version": config.contract_version,
        "configuration": str(config.config_path),
        "configuration_sha256": sha256(config.config_path),
        "observation_period": [config.observation_start, config.observation_end],
        "pcadi_repository": config.pcadi.repository,
        "pcadi_commit": config.pcadi.commit_sha,
        "pcadi_tag": config.pcadi.tag,
        "input": str(input_path),
        "input_sha256": sha256(input_path),
        "frozen_assignments": str(frozen_path),
        "frozen_assignments_sha256": sha256(frozen_path),
        "output": str(output_path),
        "output_sha256": sha256(output_path),
        "rows": len(result),
        "features": len(prepared.feature_names),
        "feature_names": list(prepared.feature_names),
        "exact_agreement": exact_agreement,
        "adjusted_rand_index": ari,
        "profile_sizes": profile_sizes,
        "silhouette": float(silhouette_score(prepared.matrix, final_labels)),
        "random_seed": config.model.random_seed,
        "clusters": config.model.clusters,
        "n_init": config.model.n_init,
        "max_iter": config.model.max_iter,
        "algorithm": config.model.algorithm,
    }
    manifest_path.write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
