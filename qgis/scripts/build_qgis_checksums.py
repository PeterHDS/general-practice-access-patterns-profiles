"""Regenerate checksums for every public QGIS package component."""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "qgis_project_checksums.csv"
FILES = (
    ROOT / "GPAP2_Digital_GP_Access_Profiles_March_2026.qgz",
    ROOT / "data" / "icb_profile_mapping_layer.geojson",
    ROOT / "scripts" / "build_qgis_project.py",
    ROOT / "scripts" / "validate_qgis_project.py",
    ROOT / "scripts" / "validate_qgis_runtime.py",
    ROOT / "scripts" / "build_qgis_checksums.py",
    ROOT / "qgis_project_layer_inventory.csv",
    ROOT / "previews" / "national_three_profile_map_preview.png",
    ROOT / "previews" / "assignment_caution_map_preview.png",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    rows = [
        {
            "file": path.relative_to(ROOT).as_posix(),
            "size_bytes": path.stat().st_size,
            "sha256": sha256(path),
        }
        for path in FILES
    ]
    with OUTPUT.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=("file", "size_bytes", "sha256"),
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} QGIS checksums to {OUTPUT}")


if __name__ == "__main__":
    main()
