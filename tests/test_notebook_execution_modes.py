import importlib.util
import json
from pathlib import Path

import nbformat
import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "execute_public_notebooks", ROOT / "scripts" / "execute_public_notebooks.py"
)
assert SPEC and SPEC.loader
RUNNER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUNNER)


def test_execution_mode_is_mandatory_and_mutually_exclusive() -> None:
    with pytest.raises(SystemExit):
        RUNNER.parse_args([])
    with pytest.raises(SystemExit):
        RUNNER.parse_args(["--check", "--write-canonical"])


def test_check_mode_targets_an_ignored_machine_report() -> None:
    assert "work" in RUNNER.REPORT.parts
    assert RUNNER.REPORT.name == "notebook_execution_report.json"


def test_canonical_environment_is_fully_locked() -> None:
    contract = RUNNER.canonical_contract()
    assert contract["python"] == "3.13.14"
    assert contract["dependencies"] == {
        "numpy": "2.5.1",
        "pandas": "3.0.3",
        "scikit-learn": "1.9.0",
        "scipy": "1.18.0",
        "ipykernel": "7.1.0",
        "jupyterlab": "4.4.10",
        "matplotlib": "3.11.1",
        "nbclient": "0.11.0",
        "nbformat": "5.10.4",
    }


def test_check_mode_executes_a_copy_and_preserves_source_hash(tmp_path, monkeypatch) -> None:
    source = tmp_path / "01_smoke.ipynb"
    notebook = nbformat.v4.new_notebook(cells=[nbformat.v4.new_code_cell("value = 1")])
    nbformat.write(notebook, source)
    original = RUNNER.sha256(source)
    report = tmp_path / "execution-report.json"
    monkeypatch.setattr(RUNNER, "notebook_paths", lambda: [source])
    monkeypatch.setattr(RUNNER, "REPORT", report)
    RUNNER.run_check()
    assert RUNNER.sha256(source) == original
    payload = json.loads(report.read_text(encoding="utf-8"))
    assert payload["tracked_notebooks_unchanged"] is True
    assert payload["notebooks"][0]["status"] == "passed"
    assert payload["notebooks"][0]["execution_error"] == ""


def test_check_mode_records_execution_error_and_preserves_source(tmp_path, monkeypatch) -> None:
    source = tmp_path / "01_failure.ipynb"
    notebook = nbformat.v4.new_notebook(
        cells=[nbformat.v4.new_code_cell("raise RuntimeError('expected smoke failure')")]
    )
    nbformat.write(notebook, source)
    original = RUNNER.sha256(source)
    report = tmp_path / "execution-report.json"
    monkeypatch.setattr(RUNNER, "notebook_paths", lambda: [source])
    monkeypatch.setattr(RUNNER, "REPORT", report)
    with pytest.raises(SystemExit, match="1 notebook execution"):
        RUNNER.run_check()
    assert RUNNER.sha256(source) == original
    payload = json.loads(report.read_text(encoding="utf-8"))
    assert payload["notebooks"][0]["status"] == "failed"
    assert "RuntimeError" in payload["notebooks"][0]["execution_error"]
