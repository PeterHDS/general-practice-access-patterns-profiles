"""Execute public notebooks without making CI Python versions rewrite release evidence."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import subprocess
import sys
import tempfile
from datetime import UTC, datetime
from pathlib import Path

import nbformat
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "reference_apr2025_mar2026.json"
REPORT = ROOT / "work" / "notebook-check" / "notebook_execution_report.json"
DEPENDENCIES = (
    "numpy",
    "pandas",
    "scikit-learn",
    "scipy",
    "ipykernel",
    "jupyterlab",
    "matplotlib",
    "nbclient",
    "nbformat",
)


def notebook_paths(root: Path = ROOT) -> list[Path]:
    return sorted((root / "notebooks").glob("[0-9][0-9]_*.ipynb"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def environment_contract() -> dict[str, object]:
    return {
        "python": ".".join(map(str, sys.version_info[:3])),
        "dependencies": {name: importlib.metadata.version(name) for name in DEPENDENCIES},
    }


def canonical_contract() -> dict[str, object]:
    return json.loads(CONFIG.read_text(encoding="utf-8"))["canonical_notebook_environment"]


def require_canonical_environment() -> None:
    expected = canonical_contract()
    observed = environment_contract()
    if observed != expected:
        raise SystemExit(
            "Canonical notebook execution requires the exact locked environment.\n"
            f"Expected: {json.dumps(expected, sort_keys=True)}\n"
            f"Observed: {json.dumps(observed, sort_keys=True)}"
        )


def strip_volatile_execution_metadata(notebook: nbformat.NotebookNode) -> None:
    for cell in notebook.cells:
        cell.get("metadata", {}).pop("execution", None)


def normalise_canonical_metadata(notebook: nbformat.NotebookNode) -> None:
    contract = canonical_contract()
    notebook.metadata["kernelspec"] = {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3",
    }
    notebook.metadata.setdefault("language_info", {})["name"] = "python"
    notebook.metadata["language_info"]["version"] = contract["python"]


def execute(source: Path, destination: Path) -> dict[str, object]:
    started = datetime.now(UTC).isoformat()
    notebook = nbformat.read(source, as_version=4)
    client = NotebookClient(
        notebook,
        timeout=180,
        kernel_name="python3",
        allow_errors=False,
        resources={"metadata": {"path": str(ROOT)}},
    )
    client.execute()
    strip_volatile_execution_metadata(notebook)
    normalise_canonical_metadata(notebook)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(nbformat.writes(notebook), encoding="utf-8", newline="\n")
    outputs = json.dumps(
        [cell.get("outputs", []) for cell in notebook.cells if cell.cell_type == "code"],
        sort_keys=True,
        default=str,
    ).encode()
    return {
        "notebook": source.name,
        "status": "passed",
        "started_utc": started,
        "finished_utc": datetime.now(UTC).isoformat(),
        "output_sha256": hashlib.sha256(outputs).hexdigest().upper(),
    }


def run_check(report_path: Path | None = None) -> None:
    report_path = report_path or REPORT
    paths = notebook_paths()
    before = {path: sha256(path) for path in paths}
    records: list[dict[str, object]] = []
    environment = environment_contract()
    with tempfile.TemporaryDirectory(prefix="gpap2-notebook-check-") as temporary:
        destination_root = Path(temporary)
        for path in paths:
            started = datetime.now(UTC).isoformat()
            try:
                record = execute(path, destination_root / path.name)
                record["execution_error"] = ""
            except Exception as exc:  # noqa: BLE001 - the report must retain kernel failures
                record = {
                    "notebook": path.name,
                    "status": "failed",
                    "started_utc": started,
                    "finished_utc": datetime.now(UTC).isoformat(),
                    "execution_error": f"{type(exc).__name__}: {exc}",
                    "output_sha256": "",
                }
            record["python_version"] = environment["python"]
            record["dependency_versions"] = environment["dependencies"]
            records.append(record)
    after = {path: sha256(path) for path in paths}
    changed = [path.name for path in paths if before[path] != after[path]]
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        json.dumps(
            {
                "mode": "check",
                "environment": environment,
                "tracked_notebooks_unchanged": not changed,
                "changed_notebooks": changed,
                "notebooks": records,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    if changed:
        raise SystemExit(f"Check mode changed tracked notebooks: {', '.join(changed)}")
    failures = [record for record in records if record["status"] != "passed"]
    if failures:
        raise SystemExit(f"{len(failures)} notebook execution(s) failed; see {report_path}")
    print(f"checked {len(records)} notebooks without modifying tracked files")


def run_write_canonical() -> None:
    require_canonical_environment()
    subprocess.run(
        [sys.executable, "scripts/build_notebook_authority_manifest.py"],
        cwd=ROOT,
        check=True,
    )
    for path in notebook_paths():
        execute(path, path)
        print(f"wrote canonical {path.name}")
    subprocess.run(
        [sys.executable, "scripts/build_notebook_authority_manifest.py"],
        cwd=ROOT,
        check=True,
    )
    subprocess.run([sys.executable, "scripts/build_validation_evidence.py"], cwd=ROOT, check=True)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--check", action="store_true", help="execute disposable copies only")
    modes.add_argument(
        "--write-canonical",
        action="store_true",
        help="rewrite tracked notebooks only in the exact locked release environment",
    )
    parser.add_argument(
        "--report",
        type=Path,
        help="optional report path for check mode; relative paths resolve from the repository root",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    if args.check:
        report = args.report or REPORT
        if not report.is_absolute():
            report = ROOT / report
        run_check(report)
    else:
        run_write_canonical()


if __name__ == "__main__":
    main()
