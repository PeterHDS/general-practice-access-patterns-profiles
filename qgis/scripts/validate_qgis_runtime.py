"""Open the registered QGIS project and record resolved runtime evidence."""

from __future__ import annotations

import hashlib
import json
import platform
from datetime import UTC, datetime
from pathlib import Path

from qgis.core import Qgis, QgsApplication, QgsProject

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
REPOSITORY = ROOT.parent
PROJECT = ROOT / "GPAP2_Digital_GP_Access_Profiles_March_2026.qgz"
SOURCE = ROOT / "data" / "icb_profile_mapping_layer.geojson"
OUTPUT = REPOSITORY / "outputs" / "validation" / "qgis_runtime_validation.json"
EXPECTED_LAYERS = {
    "Profile 1 within-ICB share",
    "Profile 2 within-ICB share",
    "Profile 3 within-ICB share",
    "Assignment-caution share",
}
EXPECTED_LAYOUTS = {"National three-profile composition", "Assignment-caution share"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def main() -> None:
    application = QgsApplication([], False)
    application.initQgis()
    try:
        project = QgsProject.instance()
        opened = project.read(str(PROJECT))
        layers = [
            {
                "name": layer.name(),
                "feature_count": int(layer.featureCount()),
                "source": Path(layer.source().split("|", 1)[0]).name,
                "valid": bool(layer.isValid()),
            }
            for layer in project.mapLayers().values()
        ]
        layouts = [layout.name() for layout in project.layoutManager().printLayouts()]
        missing = [
            layer
            for layer in layers
            if not layer["valid"] or layer["feature_count"] != 42
        ]
        if not opened or missing:
            raise SystemExit("QGIS could not resolve every registered 42-feature layer")
        if {layer["name"] for layer in layers} != EXPECTED_LAYERS:
            raise SystemExit("QGIS layer names do not match the registered contract")
        if set(layouts) != EXPECTED_LAYOUTS:
            raise SystemExit("QGIS layout names do not match the registered contract")
        if {layer["source"] for layer in layers} != {SOURCE.name}:
            raise SystemExit("QGIS layers do not resolve the registered portable GeoJSON")

        record = {
            "qgis_version": Qgis.QGIS_VERSION,
            "operating_system": platform.platform(),
            "project_path": PROJECT.relative_to(REPOSITORY).as_posix(),
            "project_sha256": sha256(PROJECT),
            "source_path": SOURCE.relative_to(REPOSITORY).as_posix(),
            "source_sha256": sha256(SOURCE),
            "project_open_status": opened,
            "missing_layer_count": len(missing),
            "layers": layers,
            "layouts": layouts,
            "validation_timestamp_utc": datetime.now(UTC).isoformat(),
            "validation_route": "PyQGIS open, source-resolution and feature-count validation",
            "validation_status": "passed",
            "notes": (
                "All four layers resolve the package-relative GeoJSON. Required ONS and OS "
                "attribution is retained in the adjacent QGIS and geography documentation."
            ),
        }
        OUTPUT.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        print("QGIS runtime validation passed")
    finally:
        application.exitQgis()


if __name__ == "__main__":
    main()
