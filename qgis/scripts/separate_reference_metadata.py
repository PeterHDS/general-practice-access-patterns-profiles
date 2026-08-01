"""Separate analytical and geographic reference concepts in the public GeoJSON.

This migration changes metadata fields only. It verifies that feature order,
geometries, organisation codes and every analytical value remain identical.
"""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "icb_profile_mapping_layer_publication_safe.geojson"
OLD_REFERENCE_PERIOD = "2023-04-01 to 2026-03-31"
ANALYSIS_PERIOD = "2025-04-01 to 2026-03-31"
BOUNDARY_VINTAGE = "2023-04"
ORGANISATION_REFERENCE_DATE = "2026-03-31"
GEOGRAPHY_NOTE = (
    "March 2026 ODS ICB organisations linked through the audited "
    "normalised-name crosswalk to ONS April 2023 ICB boundaries; no "
    "post-1-April-2026 remapping."
)


def canonical_hash(value: object) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest().upper()


def main() -> None:
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    features = data.get("features", [])
    if len(features) != 42:
        raise RuntimeError(f"Expected 42 ICB features, observed {len(features)}")

    geometry_before = canonical_hash([feature["geometry"] for feature in features])
    values_before: list[dict[str, object]] = []
    for feature in features:
        properties = copy.deepcopy(feature["properties"])
        if properties.pop("reference_period", None) != OLD_REFERENCE_PERIOD:
            raise RuntimeError("Unexpected or missing legacy reference_period value")
        values_before.append(properties)

    for feature in features:
        properties = feature["properties"]
        properties.pop("reference_period")
        properties["analysis_period"] = ANALYSIS_PERIOD
        properties["boundary_vintage"] = BOUNDARY_VINTAGE
        properties["organisation_reference_date"] = ORGANISATION_REFERENCE_DATE
        properties["geography_note"] = GEOGRAPHY_NOTE

    geometry_after = canonical_hash([feature["geometry"] for feature in features])
    values_after = []
    for feature in features:
        properties = copy.deepcopy(feature["properties"])
        for name in (
            "analysis_period",
            "boundary_vintage",
            "organisation_reference_date",
            "geography_note",
        ):
            properties.pop(name)
        values_after.append(properties)

    if geometry_before != geometry_after:
        raise RuntimeError("Geometry changed during the metadata migration")
    if canonical_hash(values_before) != canonical_hash(values_after):
        raise RuntimeError("An analytical or organisation value changed")

    data["name"] = "Publication-safe ICB profile composition"
    data["description"] = (
        "April 2025 to March 2026 practice-profile composition using March "
        "2026 organisations and April 2023 ICB boundaries."
    )
    data["source_attribution"] = data["source_attribution"].replace("Â©", "©")
    SOURCE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(f"FEATURES={len(features)}")
    print(f"GEOMETRY_CANONICAL_SHA256={geometry_after}")
    print("ANALYTICAL_AND_ORGANISATION_VALUES_UNCHANGED=true")


if __name__ == "__main__":
    main()
