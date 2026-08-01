"""Verify or regenerate the locked analytical-regression evidence.

Ordinary execution is non-mutating and equivalent to ``--check``. Canonical
writing is an explicit maintainer operation restricted to the configured
release environment.
"""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import platform
import subprocess
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gpap2.analysis import (  # noqa: E402
    canonical_assignment_frame,
    canonical_assignment_sha256,
    compare_inbound_models,
    compare_outcome_models,
)
from gpap2.composition import NHS_OUTCOME_ILR_BASIS, inverse_nhs_outcome_ilr  # noqa: E402
from gpap2.config import ReferenceConfig, load_config  # noqa: E402
from gpap2.contracts import NHS_OUTCOME_ILR_NAMES, OUTCOME_SHARE_COLUMNS  # noqa: E402
from gpap2.io import read_contract_csv, sha256  # noqa: E402

CONFIG_PATH = ROOT / "configs" / "reference_apr2025_mar2026.json"
CHECK_ROOT = ROOT / "work" / "analytical-regression-check"
CHECK_REPORT = CHECK_ROOT / "analytical_regression_check_report.json"
CANONICAL_REPORT = ROOT / "work" / "analytical-regression-canonical-write" / "report.json"
NUMERIC_TOLERANCE = 1e-12

EXPECTED = {
    ("national_14", "cbt_inbound_17"): {
        "adjusted_rand_index": 0.5236133527826328,
        "normalised_mutual_information": 0.46895509677416825,
        "reassigned_practices": 571,
        "aligned_agreement": 0.8109271523178808,
    },
    ("cbt_inbound_17", "cbt_outcome_nhs_ilr_20"): {
        "adjusted_rand_index": 0.894915323255533,
        "normalised_mutual_information": 0.8381597876460138,
        "reassigned_practices": 52,
        "aligned_agreement": 0.9642857142857143,
    },
    ("cbt_inbound_17", "cbt_outcome_raw_21"): {
        "adjusted_rand_index": 0.24868476416596344,
        "normalised_mutual_information": 0.2876967008718118,
        "reassigned_practices": 729,
        "aligned_agreement": 0.4993131868131868,
    },
}
EXPECTED_INBOUND_ALIGNED_SHA256 = (
    "892AFAF3EC4CEB9D6B1D7DC659580CE3E11C8809ED7D792A87AA7DC8BA67FDD3"
)
EXPECTED_ILR_ALIGNED_SHA256 = (
    "8E2B9618DE15BB363EA28F2946F7DDBD530845AC413507265D7450EFA137376C"
)
EXPECTED_ILR_RAW_SHA256 = (
    "0CC2A4DC8DC64771F4F9E6251D3DC6877783D747BC720BB507BD2D75F6D2ACE0"
)


@dataclass(frozen=True)
class EvidenceBundle:
    tables: dict[str, pd.DataFrame]
    regression: pd.DataFrame
    manifest_base: dict[str, Any]
    input_checksums: dict[str, str]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--check", action="store_true", help="verify without tracked writes")
    modes.add_argument(
        "--write-canonical",
        action="store_true",
        help="maintainer-only canonical regeneration in the locked environment",
    )
    args = parser.parse_args(argv)
    args.mode = "write-canonical" if args.write_canonical else "check"
    return args


def package_versions() -> dict[str, str]:
    return {
        "python": platform.python_version(),
        "numpy": importlib.metadata.version("numpy"),
        "pandas": importlib.metadata.version("pandas"),
        "scikit-learn": importlib.metadata.version("scikit-learn"),
        "scipy": importlib.metadata.version("scipy"),
    }


def compute_evidence(config: ReferenceConfig) -> EvidenceBundle:
    data_dir = config.resolve(config.input_directory)
    inbound_path = data_dir / config.specification("cbt_inbound_17").source_file
    outcome_path = data_dir / config.specification("cbt_outcome_raw_21").source_file
    inbound_source = read_contract_csv(inbound_path)
    outcome_source = read_contract_csv(outcome_path)
    inbound = compare_inbound_models(inbound_source, config)
    outcomes = compare_outcome_models(outcome_source, config)

    comparisons = pd.concat([inbound.comparisons, outcomes.comparisons], ignore_index=True)
    for (reference, candidate), expected in EXPECTED.items():
        observed = comparisons.loc[
            comparisons["reference"].eq(reference) & comparisons["candidate"].eq(candidate)
        ]
        if len(observed) != 1:
            raise AssertionError(
                f"Missing unique regression comparison: {reference} to {candidate}"
            )
        row = observed.iloc[0]
        for field, expected_value in expected.items():
            observed_value = row[field]
            passed = (
                int(observed_value) == expected_value
                if isinstance(expected_value, int)
                else np.isclose(
                    float(observed_value), expected_value, atol=NUMERIC_TOLERANCE, rtol=0.0
                )
            )
            if not passed:
                raise AssertionError(
                    f"Regression mismatch {reference} to {candidate}, {field}: "
                    f"{observed_value} != {expected_value}"
                )

    inbound_hash = canonical_assignment_sha256(
        inbound.assignments,
        config.identifier,
        "cbt_inbound_17_aligned_to_national_14",
    )
    ilr_hash = canonical_assignment_sha256(
        outcomes.assignments,
        config.identifier,
        "cbt_outcome_nhs_ilr_20_aligned_to_inbound_17",
    )
    ilr_raw_hash = canonical_assignment_sha256(
        outcomes.assignments,
        config.identifier,
        "cbt_outcome_nhs_ilr_20_raw",
        "cluster_20_ilr_raw",
    )
    expected_hashes = {
        "inbound aligned assignment": EXPECTED_INBOUND_ALIGNED_SHA256,
        "ILR aligned assignment": EXPECTED_ILR_ALIGNED_SHA256,
        "ILR raw-label diagnostic": EXPECTED_ILR_RAW_SHA256,
    }
    observed_hashes = {
        "inbound aligned assignment": inbound_hash,
        "ILR aligned assignment": ilr_hash,
        "ILR raw-label diagnostic": ilr_raw_hash,
    }
    for label, expected in expected_hashes.items():
        if observed_hashes[label] != expected:
            raise AssertionError(f"{label} checksum changed: {observed_hashes[label]}")

    shares = outcome_source.loc[:, OUTCOME_SHARE_COLUMNS].to_numpy(dtype=float)
    coordinates = (
        outcomes.prepared["cbt_outcome_nhs_ilr_20"]
        .transformed_frame.loc[:, NHS_OUTCOME_ILR_NAMES]
        .to_numpy(dtype=float)
    )
    closed = shares / shares.sum(axis=1, keepdims=True)
    reconstruction_error = float(np.max(np.abs(inverse_nhs_outcome_ilr(coordinates) - closed)))

    tables = {
        "telephone_inbound_model_comparison.csv": inbound.comparisons,
        "telephone_inbound_model_diagnostics.csv": inbound.diagnostics,
        "telephone_inbound_aligned_assignments.csv": canonical_assignment_frame(
            inbound.assignments,
            config.identifier,
            "cbt_inbound_17_aligned_to_national_14",
        ),
        "telephone_outcome_model_comparison.csv": outcomes.comparisons,
        "telephone_outcome_model_diagnostics.csv": outcomes.diagnostics,
        "telephone_outcome_model_assignments.csv": outcomes.assignments,
    }

    regression = comparisons.copy()
    regression.insert(0, "cohort_practices", [len(inbound_source)] + [len(outcome_source)] * 3)
    regression["pseudocount_used"] = False
    regression["canonical_aligned_assignment_sha256"] = [inbound_hash, ilr_hash, "", ""]
    regression["raw_label_assignment_sha256_diagnostic"] = ["", ilr_raw_hash, "", ""]
    regression["maximum_inverse_reconstruction_error"] = reconstruction_error

    input_checksums = {
        inbound_path.relative_to(ROOT).as_posix(): sha256(inbound_path),
        outcome_path.relative_to(ROOT).as_posix(): sha256(outcome_path),
    }
    manifest_base = {
        "contract_version": config.contract_version,
        "configuration_sha256": sha256(config.config_path),
        "source_matrix": outcome_path.name,
        "source_matrix_sha256": sha256(outcome_path),
        "practices": len(outcome_source),
        "outcome_order": list(OUTCOME_SHARE_COLUMNS),
        "coordinate_order": list(NHS_OUTCOME_ILR_NAMES),
        "basis": NHS_OUTCOME_ILR_BASIS.tolist(),
        "pseudocount_used": False,
        "inverse_reconstruction_max_abs_error": reconstruction_error,
        "inbound_aligned_assignment_sha256": inbound_hash,
        "ilr_aligned_assignment_sha256": ilr_hash,
        "ilr_raw_assignment_sha256_diagnostic": ilr_raw_hash,
        "assignment_checksum_method": (
            "maximum-agreement alignment; stable practice_code_standardised ordering; "
            "UTF-8 CSV with LF line endings; SHA-256"
        ),
        "model": {
            "clusters": config.model.clusters,
            "random_seed": config.model.random_seed,
            "n_init": config.model.n_init,
            "max_iter": config.model.max_iter,
            "algorithm": config.model.algorithm,
        },
    }
    return EvidenceBundle(tables, regression, manifest_base, input_checksums)


def write_bundle(bundle: EvidenceBundle, destination_root: Path) -> dict[str, Path]:
    table_dir = destination_root / "outputs" / "tables"
    validation_dir = destination_root / "outputs" / "validation"
    table_dir.mkdir(parents=True, exist_ok=True)
    validation_dir.mkdir(parents=True, exist_ok=True)

    written: dict[str, Path] = {}
    for filename, frame in bundle.tables.items():
        path = table_dir / filename
        frame.to_csv(path, index=False, lineterminator="\n")
        written[filename] = path
    regression_path = validation_dir / "analytical_regression_results.csv"
    bundle.regression.to_csv(regression_path, index=False, lineterminator="\n")
    written[regression_path.name] = regression_path

    manifest = {
        **bundle.manifest_base,
        "outputs": {name: sha256(path) for name, path in written.items()},
    }
    manifest_path = validation_dir / "analytical_regression_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n")
    written[manifest_path.name] = manifest_path
    return written


def tracked_paths() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "--cached"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        return [ROOT / line for line in result.stdout.splitlines() if line]
    manifest = ROOT / "outputs" / "validation" / "public_file_manifest.csv"
    if not manifest.is_file():
        raise FileNotFoundError("Git metadata and the public file manifest are both unavailable")
    paths = pd.read_csv(manifest)["path"].tolist()
    return [ROOT / path for path in paths] + [manifest]


def tracked_hashes() -> dict[str, str]:
    return {
        path.relative_to(ROOT).as_posix(): sha256(path)
        for path in tracked_paths()
        if path.is_file()
    }


def compare_csv(expected: Path, observed: Path) -> list[str]:
    failures: list[str] = []
    expected_frame = pd.read_csv(expected)
    observed_frame = pd.read_csv(observed)
    if expected_frame.columns.tolist() != observed_frame.columns.tolist():
        return [f"schema differs: {expected.relative_to(ROOT)}"]
    if len(expected_frame) != len(observed_frame):
        return [f"row count differs: {expected.relative_to(ROOT)}"]
    for column in expected_frame.columns:
        left = expected_frame[column]
        right = observed_frame[column]
        if pd.api.types.is_numeric_dtype(left) and pd.api.types.is_numeric_dtype(right):
            if not np.allclose(
                left.to_numpy(dtype=float),
                right.to_numpy(dtype=float),
                atol=NUMERIC_TOLERANCE,
                rtol=0.0,
                equal_nan=True,
            ):
                failures.append(f"numerical values differ: {expected.name}:{column}")
        elif not left.fillna("").astype(str).equals(right.fillna("").astype(str)):
            failures.append(f"values differ: {expected.name}:{column}")
    return failures


def json_equal(expected: Any, observed: Any) -> bool:
    if isinstance(expected, dict) and isinstance(observed, dict):
        return expected.keys() == observed.keys() and all(
            json_equal(expected[key], observed[key]) for key in expected
        )
    if isinstance(expected, list) and isinstance(observed, list):
        return len(expected) == len(observed) and all(
            json_equal(left, right) for left, right in zip(expected, observed, strict=True)
        )
    if isinstance(expected, (int, float)) and isinstance(observed, (int, float)):
        return bool(np.isclose(expected, observed, atol=NUMERIC_TOLERANCE, rtol=0.0))
    return expected == observed


def compare_manifest(expected_path: Path, observed_path: Path) -> list[str]:
    """Compare stable contract metadata without requiring portable CSV byte identity.

    The canonical manifest records the exact hashes of the maintained release files.
    Recomputed floating-point CSV serialisation may differ across supported Python and
    dependency builds even when its schema, rows and numerical values agree. Those CSVs
    are therefore compared semantically by :func:`compare_csv`; assignment identity is
    separately protected by the canonical assignment checksums in the stable metadata.
    """
    expected = json.loads(expected_path.read_text(encoding="utf-8"))
    observed = json.loads(observed_path.read_text(encoding="utf-8"))
    expected_outputs = expected.pop("outputs", None)
    observed_outputs = observed.pop("outputs", None)
    failures: list[str] = []
    display_path = (
        expected_path.relative_to(ROOT) if expected_path.is_relative_to(ROOT) else expected_path
    )
    if not json_equal(expected, observed):
        failures.append(f"stable JSON contract differs: {display_path}")
    expected_names = set(expected_outputs or {})
    observed_names = set(observed_outputs or {})
    if expected_names != observed_names:
        failures.append(f"manifest output inventory differs: {display_path}")
    for name, expected_hash in (expected_outputs or {}).items():
        canonical_path = expected_paths().get(name)
        if canonical_path is None or not canonical_path.is_file():
            failures.append(f"manifest output is unavailable: {name}")
        elif sha256(canonical_path) != expected_hash:
            failures.append(f"canonical manifest checksum is invalid: {name}")
    for name, observed_hash in (observed_outputs or {}).items():
        candidate_path = observed_path.parent.parent / (
            Path("tables") / name
            if name != "analytical_regression_results.csv"
            else Path("validation") / name
        )
        if not candidate_path.is_file() or sha256(candidate_path) != observed_hash:
            failures.append(f"recomputed manifest checksum is invalid: {name}")
    return failures


def expected_paths() -> dict[str, Path]:
    names = [
        "telephone_inbound_model_comparison.csv",
        "telephone_inbound_model_diagnostics.csv",
        "telephone_inbound_aligned_assignments.csv",
        "telephone_outcome_model_comparison.csv",
        "telephone_outcome_model_diagnostics.csv",
        "telephone_outcome_model_assignments.csv",
    ]
    paths = {name: ROOT / "outputs" / "tables" / name for name in names}
    paths["analytical_regression_results.csv"] = (
        ROOT / "outputs" / "validation" / "analytical_regression_results.csv"
    )
    paths["analytical_regression_manifest.json"] = (
        ROOT / "outputs" / "validation" / "analytical_regression_manifest.json"
    )
    return paths


def compare_with_authority(observed: dict[str, Path]) -> list[str]:
    failures: list[str] = []
    for name, expected in expected_paths().items():
        if not expected.is_file():
            failures.append(f"required authority file is missing: {expected.relative_to(ROOT)}")
            continue
        candidate = observed[name]
        if name.endswith(".csv"):
            failures.extend(compare_csv(expected, candidate))
        else:
            failures.extend(compare_manifest(expected, candidate))
    return failures


def write_report(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")


def run_check() -> None:
    before = tracked_hashes()
    config = load_config(CONFIG_PATH)
    bundle = compute_evidence(config)
    observed = write_bundle(bundle, CHECK_ROOT)
    failures = compare_with_authority(observed)
    after = tracked_hashes()
    changed = sorted(
        path for path in before.keys() | after.keys() if before.get(path) != after.get(path)
    )
    if changed:
        failures.append(f"tracked files changed during check: {', '.join(changed)}")

    authority = pd.read_csv(ROOT / "outputs" / "validation" / "analytical_regression_results.csv")
    report = {
        "mode": "check",
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "environment": package_versions(),
        "configuration_path": CONFIG_PATH.relative_to(ROOT).as_posix(),
        "configuration_sha256": sha256(CONFIG_PATH),
        "input_checksums": bundle.input_checksums,
        "numeric_tolerance": NUMERIC_TOLERANCE,
        "expected_metrics": authority.to_dict("records"),
        "observed_metrics": bundle.regression.to_dict("records"),
        "expected_assignment_checksums": {
            "inbound": EXPECTED_INBOUND_ALIGNED_SHA256,
            "nhs_ilr": EXPECTED_ILR_ALIGNED_SHA256,
            "nhs_ilr_raw_diagnostic": EXPECTED_ILR_RAW_SHA256,
        },
        "observed_assignment_checksums": {
            "inbound": bundle.manifest_base["inbound_aligned_assignment_sha256"],
            "nhs_ilr": bundle.manifest_base["ilr_aligned_assignment_sha256"],
            "nhs_ilr_raw_diagnostic": bundle.manifest_base[
                "ilr_raw_assignment_sha256_diagnostic"
            ],
        },
        "tracked_files_unchanged": not changed,
        "failures": failures,
        "passed": not failures,
        "temporary_output_root": CHECK_ROOT.relative_to(ROOT).as_posix(),
    }
    write_report(CHECK_REPORT, report)
    if failures:
        raise SystemExit("\n".join(failures))
    print("analytical regression check passed; tracked files unchanged")
    print(f"report: {CHECK_REPORT}")


def verify_canonical_environment(config: ReferenceConfig) -> dict[str, str]:
    observed = package_versions()
    raw = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    required = raw["canonical_notebook_environment"]
    failures = []
    if observed["python"] != required["python"]:
        failures.append(f"python={observed['python']} expected {required['python']}")
    for package, expected in required["dependencies"].items():
        try:
            installed = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            failures.append(f"{package}=missing expected {expected}")
            continue
        if installed != expected:
            failures.append(f"{package}={installed} expected {expected}")

    provenance_path = ROOT / "outputs" / "validation" / "release_provenance.json"
    provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
    lock_path = ROOT / str(provenance["dependency_lock_path"])
    observed_lock = sha256(lock_path)
    if observed_lock != provenance["dependency_lock_checksum"]:
        failures.append(
            f"dependency lock checksum={observed_lock} expected "
            f"{provenance['dependency_lock_checksum']}"
        )
    if failures:
        raise SystemExit("Canonical-write environment mismatch:\n" + "\n".join(failures))
    return observed


def run_controlled_script(relative: str) -> None:
    subprocess.run([sys.executable, str(ROOT / relative)], cwd=ROOT, check=True)


def run_write_canonical() -> None:
    config = load_config(CONFIG_PATH)
    environment = verify_canonical_environment(config)
    bundle = compute_evidence(config)
    written = write_bundle(bundle, ROOT)
    run_controlled_script("scripts/build_notebook_authority_manifest.py")
    run_controlled_script("scripts/build_validation_evidence.py")
    run_controlled_script("scripts/validate_public_repository.py")
    report = {
        "mode": "write-canonical",
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "environment": environment,
        "configuration_sha256": sha256(CONFIG_PATH),
        "dependency_lock_checksum": sha256(ROOT / "pyproject.toml"),
        "input_checksums": bundle.input_checksums,
        "written_files": {
            name: {
                "path": path.relative_to(ROOT).as_posix(),
                "sha256": sha256(path),
            }
            for name, path in written.items()
        },
        "public_repository_validation": "passed",
        "passed": True,
    }
    write_report(CANONICAL_REPORT, report)
    print("canonical analytical regression evidence regenerated in the locked environment")
    print(f"report: {CANONICAL_REPORT}")


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    if args.mode == "write-canonical":
        run_write_canonical()
    else:
        run_check()


if __name__ == "__main__":
    main()
