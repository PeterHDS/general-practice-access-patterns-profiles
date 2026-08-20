"""Write compact machine-readable validation evidence for the reference repository."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pandas as pd
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gpap2.config import load_config  # noqa: E402
from gpap2.io import sha256  # noqa: E402
from gpap2.validation import (  # noqa: E402
    validate_cohort_relationships,
    validate_contract_directory,
)


def manifest_payload(path: Path) -> bytes:
    relative = path.relative_to(ROOT).as_posix()
    binary = (
        path.suffix.lower() in {".png", ".jpg", ".jpeg", ".qgz", ".zip"}
        or relative.startswith("data/reference/")
        or relative.startswith("qgis/data/")
    )
    payload = path.read_bytes()
    if not binary:
        payload = payload.replace(b"\r\n", b"\n")
    return payload


def manifest_sha256(path: Path) -> str:
    return hashlib.sha256(manifest_payload(path)).hexdigest().upper()


def main() -> None:
    validation = ROOT / "outputs" / "validation"
    validation.mkdir(parents=True, exist_ok=True)

    config = load_config(ROOT / "configs" / "reference_apr2025_mar2026.json")
    contracts = validate_contract_directory(
        config.resolve(config.input_directory),
        config.resolve(config.contracts_file),
        config,
    )
    contracts.to_csv(validation / "pcadi_input_validation.csv", index=False, lineterminator="\n")
    relationships = validate_cohort_relationships(config.resolve(config.input_directory), config)
    relationships.to_csv(
        validation / "cohort_relationship_validation.csv", index=False, lineterminator="\n"
    )

    notebook_rows = []
    for path in sorted((ROOT / "notebooks").glob("[0-9][0-9]_*.ipynb")):
        data = json.loads(path.read_text(encoding="utf-8"))
        cells = [cell for cell in data["cells"] if cell["cell_type"] == "code"]
        errors = sum(
            output.get("output_type") == "error"
            for cell in cells
            for output in cell.get("outputs", [])
        )
        notebook_rows.append(
            {
                "notebook": path.name,
                "code_cells": len(cells),
                "executed_code_cells": sum(
                    cell.get("execution_count") is not None for cell in cells
                ),
                "stored_errors": errors,
                "sha256": sha256(path),
                "passed": bool(
                    cells and not errors and all(c.get("execution_count") for c in cells)
                ),
            }
        )
    pd.DataFrame(notebook_rows).to_csv(
        validation / "public_notebook_execution.csv", index=False, lineterminator="\n"
    )

    rows = []
    excluded = {
        ".git",
        "work",
        ".pytest_cache",
        ".ruff_cache",
        "__pycache__",
        "build",
        "dist",
    }
    if not (ROOT / ".git").exists():
        raise SystemExit(
            "build_validation_evidence.py is a maintainer-only command and requires a Git checkout"
        )
    listing = subprocess.run(
        ["git", "ls-files", "--cached"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    for relative_name in sorted(listing):
        path = ROOT / relative_name
        relative_parts = Path(relative_name).parts
        if not path.is_file() or any(part in excluded for part in relative_parts):
            continue
        relative = path.relative_to(ROOT).as_posix()
        if relative == "outputs/validation/public_file_manifest.csv":
            continue
        row = {
            "path": relative,
            "bytes": len(manifest_payload(path)),
            "sha256": manifest_sha256(path),
            "rows": "",
            "columns": "",
            "image_width": "",
            "image_height": "",
        }
        if path.suffix.lower() == ".csv":
            with path.open("r", encoding="utf-8-sig", errors="replace", newline="") as stream:
                reader = csv.reader(stream)
                header = next(reader, [])
                row["columns"] = len(header)
                row["rows"] = sum(1 for _ in reader)
        elif path.suffix.lower() in {".png", ".jpg", ".jpeg"}:
            with Image.open(path) as image:
                row["image_width"], row["image_height"] = image.size
        rows.append(row)
    pd.DataFrame(rows).to_csv(
        validation / "public_file_manifest.csv", index=False, lineterminator="\n"
    )
    print(f"wrote validation evidence for {len(rows)} tracked public files")


if __name__ == "__main__":
    main()
