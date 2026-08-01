"""Summarise canonical notebook execution separately from local multi-version smoke tests."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
VALIDATION = ROOT / "outputs" / "validation"
SMOKE_REPORTS = (
    VALIDATION / "notebook_smoke_python311.json",
    VALIDATION / "notebook_smoke_python312.json",
    VALIDATION / "notebook_smoke_python313.json",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main() -> None:
    rows: list[dict[str, object]] = []
    for path in SMOKE_REPORTS:
        if not path.is_file():
            raise FileNotFoundError(f"Notebook smoke report is absent: {path}")
        report = json.loads(path.read_text(encoding="utf-8"))
        notebooks = report["notebooks"]
        passed = sum(item["status"] == "passed" for item in notebooks)
        rows.append(
            {
                "evidence_object": "seven-notebook disposable smoke execution",
                "evidence_class": "local_prepublication_smoke",
                "hosted_by": "local Windows final-gate environment",
                "workflow_url": "",
                "run_id": "",
                "source_commit": "prepublication_worktree",
                "python_version": report["environment"]["python"],
                "notebooks_expected": len(notebooks),
                "notebooks_passed": passed,
                "status": "passed" if passed == len(notebooks) else "failed",
                "execution_date_utc": max(item["finished_utc"] for item in notebooks),
                "artifact_path": path.relative_to(ROOT).as_posix(),
                "artifact_sha256": sha256(path),
                "notes": "Local evidence only; this is not a GitHub Actions run.",
            }
        )

    canonical_path = VALIDATION / "public_notebook_execution.csv"
    canonical = pd.read_csv(canonical_path)
    rows.append(
        {
            "evidence_object": "canonical seven-notebook regeneration",
            "evidence_class": "canonical_regeneration",
            "hosted_by": "locked local publication environment",
            "workflow_url": "",
            "run_id": "",
            "source_commit": "prepublication_worktree",
            "python_version": "3.13.14",
            "notebooks_expected": len(canonical),
            "notebooks_passed": int(canonical["passed"].sum()),
            "status": "passed" if canonical["passed"].all() else "failed",
            "execution_date_utc": "recorded by the publication build",
            "artifact_path": canonical_path.relative_to(ROOT).as_posix(),
            "artifact_sha256": sha256(canonical_path),
            "notes": "Canonical stored-output evidence; distinct from disposable smoke execution.",
        }
    )
    output = VALIDATION / "notebook_ci_summary.csv"
    pd.DataFrame(rows).to_csv(output, index=False, lineterminator="\n")
    print(f"wrote {len(rows)} distinct notebook evidence rows")


if __name__ == "__main__":
    main()
