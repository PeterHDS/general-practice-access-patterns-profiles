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
SOURCE = ROOT / "data" / "icb_profile_mapping_layer_publication_safe.geojson"
EXPECTED_SOURCE_SHA256 = "FD501EB2A2DE54F9BC2C17A34DF53A8CF40D4BDD6DC28706E759524E42D4BFE1"
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

    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    features = data.get("features", [])
    if len(features) != 42:
        raise SystemExit("Portable GeoJSON must contain exactly 42 ICB features")
    expected_metadata = {
        "analysis_period": "2025-04-01 to 2026-03-31",
        "boundary_vintage": "2023-04",
        "organisation_reference_date": "2026-03-31",
    }
    for feature in features:
        properties = feature.get("properties", {})
        if "reference_period" in properties:
            raise SystemExit("Legacy conflated reference_period remains in GeoJSON")
        for field, expected in expected_metadata.items():
            if properties.get(field) != expected:
                raise SystemExit(f"Unexpected {field}: {properties.get(field)!r}")
        if not properties.get("geography_note"):
            raise SystemExit("GeoJSON feature is missing geography_note")

    with zipfile.ZipFile(PROJECT) as archive:
        qgs_names = [name for name in archive.namelist() if name.lower().endswith(".qgs")]
        if len(qgs_names) != 1:
            raise SystemExit("QGZ must contain exactly one QGS project document")
        project_xml = archive.read(qgs_names[0]).decode("utf-8")

    private_path_pattern = "(?:[A-Za-z]:" + r"\\\\|C:/" + "Users/|/home/|/" + "Users/)"
    if re.search(private_path_pattern, project_xml):
        raise SystemExit("QGIS project contains a private absolute path")
    if "./data/icb_profile_mapping_layer_publication_safe.geojson" not in project_xml:
        raise SystemExit("QGIS project does not use the expected relative GeoJSON path")
    for name in EXPECTED_LAYERS | EXPECTED_LAYOUTS:
        if name not in project_xml:
            raise SystemExit(f"QGIS project is missing: {name}")
    for marker in (
        "gpap2_analysis_period",
        "gpap2_boundary_vintage",
        "gpap2_organisation_reference_date",
        "gpap2_geography_note",
        "gpap2_ons_attribution",
        "gpap2_os_attribution",
    ):
        if marker not in project_xml:
            raise SystemExit(f"QGIS project is missing metadata marker: {marker}")
    for attribution in (ONS_ATTRIBUTION, OS_ATTRIBUTION):
        if project_xml.count(attribution) < 2:
            raise SystemExit(f"QGIS layouts do not both contain attribution: {attribution}")
    if "ds7010" in project_xml.lower():
        raise SystemExit("QGIS project retains a DS7010-era custom-property name")

    print(
        "QGIS package validation passed: 42 ICBs, 4 layers, 2 layouts, "
        "relative source and separated reference metadata"
    )


if __name__ == "__main__":
    main()
