import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "gpap2_analytical_regression_script",
    ROOT / "scripts" / "build_analytical_regression_evidence.py",
)
assert SPEC and SPEC.loader
REGRESSION = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = REGRESSION
SPEC.loader.exec_module(REGRESSION)


def test_default_mode_is_non_mutating_check() -> None:
    assert REGRESSION.parse_args([]).mode == "check"
    assert REGRESSION.parse_args(["--check"]).mode == "check"
    assert REGRESSION.parse_args(["--write-canonical"]).mode == "write-canonical"


def test_check_mode_recomputes_to_work_and_preserves_tracked_files() -> None:
    before = REGRESSION.tracked_hashes()
    REGRESSION.run_check()
    after = REGRESSION.tracked_hashes()
    assert after == before
    report = json.loads(REGRESSION.CHECK_REPORT.read_text(encoding="utf-8"))
    assert report["passed"] is True
    assert report["tracked_files_unchanged"] is True
    assert report["temporary_output_root"].startswith("work/")
    assert report["expected_assignment_checksums"] == report["observed_assignment_checksums"]


def test_manifest_comparison_allows_only_output_serialisation_hash_differences(
    tmp_path: Path,
) -> None:
    expected = {
        "contract_version": "1.1",
        "inbound_aligned_assignment_sha256": "LOCKED",
        "outputs": {"example.csv": "CANONICAL"},
    }
    observed = {
        "contract_version": "1.1",
        "inbound_aligned_assignment_sha256": "LOCKED",
        "outputs": {"example.csv": "PORTABLE"},
    }
    expected_path = tmp_path / "expected.json"
    observed_path = tmp_path / "outputs" / "validation" / "observed.json"
    observed_path.parent.mkdir(parents=True)
    expected_path.write_text(json.dumps(expected), encoding="utf-8")
    observed_path.write_text(json.dumps(observed), encoding="utf-8")

    original_expected_paths = REGRESSION.expected_paths
    original_sha256 = REGRESSION.sha256
    canonical = tmp_path / "example.csv"
    canonical.write_text("value\n1\n", encoding="utf-8")
    candidate = tmp_path / "outputs" / "tables" / "example.csv"
    candidate.parent.mkdir()
    candidate.write_text("value\n1.0\n", encoding="utf-8")
    expected["outputs"]["example.csv"] = "CANONICAL"
    observed["outputs"]["example.csv"] = "PORTABLE"
    expected_path.write_text(json.dumps(expected), encoding="utf-8")
    observed_path.write_text(json.dumps(observed), encoding="utf-8")
    REGRESSION.expected_paths = lambda: {"example.csv": canonical}
    REGRESSION.sha256 = lambda path: "CANONICAL" if path == canonical else "PORTABLE"
    try:
        assert REGRESSION.compare_manifest(expected_path, observed_path) == []
        observed["inbound_aligned_assignment_sha256"] = "CHANGED"
        observed_path.write_text(json.dumps(observed), encoding="utf-8")
        assert "stable JSON contract differs" in REGRESSION.compare_manifest(
            expected_path, observed_path
        )[0]
    finally:
        REGRESSION.expected_paths = original_expected_paths
        REGRESSION.sha256 = original_sha256
