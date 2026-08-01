"""Build release provenance and optionally finalise an external archive sidecar.

The tracked JSON is deliberately a pre-archive record. An archive cannot contain its own
SHA-256 without changing that SHA-256, and the release manifest cannot contain its own hash.
After ``git archive``, pass ``--archive`` and ``--output`` to create the exact sidecar.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import tomllib
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "outputs" / "validation" / "release_provenance.json"
CONFIG_PATH = ROOT / "configs" / "reference_apr2025_mar2026.json"
MANIFEST_PATH = ROOT / "outputs" / "validation" / "public_file_manifest.csv"
NOTEBOOK_CI_PATH = ROOT / "outputs" / "validation" / "notebook_ci_summary.csv"
QGIS_RUNTIME_PATH = ROOT / "outputs" / "validation" / "qgis_runtime_validation.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()


def repository_url() -> str | None:
    result = subprocess.run(
        ["git", "remote", "get-url", "origin"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode:
        return None
    value = result.stdout.strip()
    if value.startswith("git@github.com:"):
        value = "https://github.com/" + value.removeprefix("git@github.com:")
    if value.endswith(".git"):
        value = value[:-4]
    return value


def build_payload(archive: Path | None, test_summary: str) -> dict[str, object]:
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    qgis = (
        json.loads(QGIS_RUNTIME_PATH.read_text(encoding="utf-8"))
        if QGIS_RUNTIME_PATH.is_file()
        else {}
    )
    notebook_ci = pd.read_csv(NOTEBOOK_CI_PATH) if NOTEBOOK_CI_PATH.is_file() else pd.DataFrame()
    archive_finalised = archive is not None
    archive_name = archive.name if archive else "gpap2-publication-candidate.zip"
    return {
        "schema_version": "1.0",
        "repository_url": repository_url(),
        "repository_url_status": "confirmed_from_git_remote" if repository_url() else "unconfirmed",
        "source_commit": (
            git("rev-parse", "HEAD") if archive_finalised else "finalised_in_external_sidecar"
        ),
        "source_commit_status": (
            "exact" if archive_finalised else "pending_until_git_archive_is_built"
        ),
        "source_branch_or_tag": git("branch", "--show-current") or "detached HEAD",
        "release_version": project["version"],
        "build_timestamp_utc": datetime.now(UTC).isoformat(),
        "archive_filename": archive_name,
        "archive_sha256": sha256(archive) if archive else None,
        "archive_checksum_status": (
            "finalised_in_external_sidecar"
            if archive_finalised
            else "pending_until_git_archive_is_built"
        ),
        "public_file_manifest_path": MANIFEST_PATH.relative_to(ROOT).as_posix(),
        "public_file_manifest_sha256": sha256(MANIFEST_PATH) if archive_finalised else None,
        "manifest_checksum_status": (
            "finalised_in_external_sidecar"
            if archive_finalised
            else "pending_to_avoid_manifest_self-reference"
        ),
        "canonical_python_version": config["canonical_notebook_environment"]["python"],
        "dependency_lock_path": "pyproject.toml",
        "dependency_lock_checksum": sha256(ROOT / "pyproject.toml"),
        "operating_system": platform.platform(),
        "pcadi_repository": config["pcadi"]["repository"],
        "pcadi_commit": config["pcadi"]["commit_sha"],
        "pcadi_tag": config["pcadi"]["tag"],
        "notebook_canonical_regeneration_status": (
            "passed"
            if not notebook_ci.empty
            and (
                notebook_ci.loc[
                    notebook_ci["evidence_class"].eq("canonical_regeneration"), "status"
                ]
                == "passed"
            ).all()
            else "not_recorded"
        ),
        "test_summary": test_summary,
        "ci_runs": (
            notebook_ci.loc[
                notebook_ci["evidence_class"].eq("github_actions"),
                ["workflow_url", "run_id", "python_version", "status"],
            ].to_dict(orient="records")
            if not notebook_ci.empty
            else []
        ),
        "qgis_version": qgis.get("qgis_version", "not recorded"),
        "qgis_validation_status": qgis.get("validation_status", "not recorded"),
        "provenance_note": (
            "The tracked record is the stable pre-archive contract. The exact source commit, "
            "archive SHA-256 and manifest SHA-256 are written to the external post-archive "
            "sidecar because embedding an object's own final hash would change that object."
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--test-summary",
        default=os.environ.get("GPAP2_TEST_SUMMARY", "not recorded"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    archive = args.archive.resolve() if args.archive else None
    if archive and not archive.is_file():
        raise FileNotFoundError(archive)
    output = args.output.resolve()
    if archive and output == DEFAULT_OUTPUT.resolve():
        raise SystemExit("Final archive provenance must be written to an external sidecar path")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(build_payload(archive, args.test_summary), indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(output)


if __name__ == "__main__":
    main()
