import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "validate_public_repository", ROOT / "scripts" / "validate_public_repository.py"
)
assert SPEC and SPEC.loader
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


def test_manifest_set_equality_accepts_exact_release() -> None:
    release = {"README.md", "data.csv", "outputs/validation/public_file_manifest.csv"}
    assert VALIDATOR.manifest_set_failures(release, ["README.md", "data.csv"]) == []


def test_manifest_set_equality_rejects_unregistered_file() -> None:
    release = {
        "README.md",
        "unregistered.txt",
        "outputs/validation/public_file_manifest.csv",
    }
    failures = VALIDATOR.manifest_set_failures(release, ["README.md"])
    assert any("unregistered.txt" in failure for failure in failures)


def test_manifest_set_equality_rejects_duplicates() -> None:
    release = {"README.md", "outputs/validation/public_file_manifest.csv"}
    failures = VALIDATOR.manifest_set_failures(release, ["README.md", "README.md"])
    assert any("duplicate" in failure for failure in failures)
