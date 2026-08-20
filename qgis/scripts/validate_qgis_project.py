"""Validate the portable GPAP² QGIS package without requiring PyQGIS."""

from __future__ import annotations

import hashlib
import json
import re
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PROJECT = ROOT / "GPAP2_Digital_GP_Access_Profiles_March_2026.qgz"
SOURCE = ROOT / "data" / "icb_profile_mapping_layer.geojson"
EXPECTED_SOURCE_SHA256 = "79CEAF2F84B866CFABAE22F95C825523EBE3FF100584D404A83B7AFE03E71D30"
EXPECTED_PROJECT_SHA256 = "5AA8BDB3C67A5318A1B98FC8485D79F853C98C4A7995E298297EB048A3D2218C"
EXPECTED_LAYERS = {
    "Profile 1 within-ICB share",
    "Profile 2 within-ICB share",
    "Profile 3 within-ICB share",
    "Assignment-caution share",
}
EXPECTED_LAYOUTS = {"National three-profile composition", "Assignment-caution share"}
ONS_ATTRIBUTION = (
    "Source: Office for National Statistics licensed under the Open Government Licence v.3.0"
)
OS_ATTRIBUTION = "Contains OS data © Crown copyright and database right 2026"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def main() -> None:
    if not PROJECT.exists() or not SOURCE.exists():
        raise SystemExit("QGIS project or portable GeoJSON is absent")
    if sha256(SOURCE) != EXPECTED_SOURCE_SHA256:
        raise SystemExit("Portable GeoJSON checksum does not match the validated source")
    if sha256(PROJECT) != EXPECTED_PROJECT_SHA256:
        raise SystemExit("QGIS project checksum does not match the validated authority")

    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    features = data.get("features", [])
    if len(features) != 42:
        raise SystemExit("Portable GeoJSON must contain exactly 42 ICB features")
    for feature in features:
        properties = feature.get("properties", {})
        if properties.get("reference_period") != "2023-04-01 to 2026-03-31":
            raise SystemExit("Unexpected QGIS reference period")
        if properties.get("publication_layer_status") != ("PRIMARY_SMALL_CELL_SUPPRESSION_APPLIED"):
            raise SystemExit("Unexpected QGIS publication-layer status")

    suppressed = {
        field: sum(feature["properties"][field] for feature in features)
        for field in (
            "profile_1_suppression_flag",
            "profile_2_suppression_flag",
            "profile_3_suppression_flag",
        )
    }
    if suppressed != {
        "profile_1_suppression_flag": 8,
        "profile_2_suppression_flag": 0,
        "profile_3_suppression_flag": 0,
    }:
        raise SystemExit(f"Unexpected QGIS suppression counts: {suppressed}")

    with zipfile.ZipFile(PROJECT) as archive:
        qgs_names = [name for name in archive.namelist() if name.lower().endswith(".qgs")]
        if len(qgs_names) != 1:
            raise SystemExit("QGZ must contain exactly one QGS project document")
        project_xml = archive.read(qgs_names[0]).decode("utf-8")

    private_path_pattern = "(?:[A-Za-z]:" + r"\\\\|C:/" + "Users/|/home/|/" + "Users/)"
    if re.search(private_path_pattern, project_xml):
        raise SystemExit("QGIS project contains a private absolute path")
    if "./data/icb_profile_mapping_layer.geojson" not in project_xml:
        raise SystemExit("QGIS project does not use the expected relative GeoJSON path")
    for name in EXPECTED_LAYERS | EXPECTED_LAYOUTS:
        if name not in project_xml:
            raise SystemExit(f"QGIS project is missing: {name}")
    documentation = (ROOT / "README.md").read_text(encoding="utf-8")
    for attribution in (ONS_ATTRIBUTION, OS_ATTRIBUTION):
        if attribution not in documentation:
            raise SystemExit(f"QGIS guide is missing required attribution: {attribution}")

    print(
        "QGIS package validation passed: 42 ICBs, 4 layers, 2 layouts, "
        "relative source, validated suppression and registered reference metadata"
    )


if __name__ == "__main__":
    main()
