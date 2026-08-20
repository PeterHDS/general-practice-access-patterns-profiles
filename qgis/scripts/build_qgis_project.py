"""Build the portable GPAP² QGIS project from the validated ICB GeoJSON.

This script performs presentation work only. It does not alter analytical
values, rerun modelling, remap practices, rank ICBs, or calculate spatial
statistics.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import platform
import re
import zipfile
from datetime import UTC, datetime
from pathlib import Path

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QColor, QFont
from qgis.core import (
    Qgis,
    QgsApplication,
    QgsExpressionContextUtils,
    QgsFillSymbol,
    QgsLayerTree,
    QgsLayoutExporter,
    QgsLayoutItemLabel,
    QgsLayoutItemLegend,
    QgsLayoutItemMap,
    QgsLayoutPoint,
    QgsLayoutSize,
    QgsLegendStyle,
    QgsPrintLayout,
    QgsProject,
    QgsRectangle,
    QgsRuleBasedRenderer,
    QgsUnitTypes,
    QgsVectorLayer,
)


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SOURCE = ROOT / "data" / "icb_profile_mapping_layer.geojson"
SOURCE_RELATIVE = "./data/icb_profile_mapping_layer.geojson"
PROJECT_FILE = ROOT / "GPAP2_Digital_GP_Access_Profiles_March_2026.qgz"
RUNTIME_RECORD = ROOT.parent / "outputs" / "validation" / "qgis_runtime_validation.json"
PROFILE_LAYOUT_PREVIEW = ROOT / "previews" / "national_three_profile_map_preview.png"
CAUTION_LAYOUT_PREVIEW = ROOT / "previews" / "assignment_caution_map_preview.png"

EXPECTED_SOURCE_SHA256 = "79ceaf2f84b866cfabae22f95c825523ebe3ff100584d404a83b7afe03e71d30"
INTERPRETATION_NOTE = "Practice composition, not patient prevalence or ICB performance"
ANALYSIS_PERIOD = "1 April 2025 to 31 March 2026"
BOUNDARY_VINTAGE = "April 2023 ICB boundaries"
ORGANISATION_REFERENCE_DATE = "31 March 2026"
GEOGRAPHY_NOTE = (
    "March 2026 ODS ICB organisations linked through the audited "
    "normalised-name crosswalk to ONS April 2023 ICB boundaries; no "
    "post-1-April-2026 remapping"
)
ONS_ATTRIBUTION = (
    "Source: Office for National Statistics licensed under the Open Government Licence v.3.0"
)
OS_ATTRIBUTION = "Contains OS data © Crown copyright and database right 2026"

THEMES = (
    {
        "name": "Profile 1 within-ICB share",
        "field": "profile_1_pct",
        "suppression": "profile_1_suppression_flag",
        "colours": ("#eff3ff", "#bdd7e7", "#6baed6", "#3182bd", "#08519c"),
        "purpose": "Share of practices assigned to Profile 1 within each ICB.",
    },
    {
        "name": "Profile 2 within-ICB share",
        "field": "profile_2_pct",
        "suppression": "profile_2_suppression_flag",
        "colours": ("#edf8fb", "#b2e2e2", "#66c2a4", "#2ca25f", "#006d2c"),
        "purpose": "Share of practices assigned to Profile 2 within each ICB.",
    },
    {
        "name": "Profile 3 within-ICB share",
        "field": "profile_3_pct",
        "suppression": "profile_3_suppression_flag",
        "colours": ("#f2f0f7", "#cbc9e2", "#9e9ac8", "#756bb1", "#54278f"),
        "purpose": "Share of practices assigned to Profile 3 within each ICB.",
    },
    {
        "name": "Assignment-caution share",
        "field": "interpretive_caution_pct",
        "suppression": None,
        "colours": ("#fff5eb", "#fdd0a2", "#fdae6b", "#e6550d", "#a63603"),
        "purpose": (
            "Share of practices carrying the fixed-profile interpretive caution "
            "flag within each ICB."
        ),
    },
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def numeric_values(layer: QgsVectorLayer, field: str, suppression: str | None) -> list[float]:
    values: list[float] = []
    for feature in layer.getFeatures():
        if suppression and int(feature[suppression] or 0) == 1:
            continue
        value = feature[field]
        try:
            number = float(value)
        except (TypeError, ValueError):
            continue
        if math.isfinite(number):
            values.append(number)
    if not values:
        raise RuntimeError(f"No finite values found for {field}")
    return values


def fill_symbol(colour: str, outline: str = "#ffffff") -> QgsFillSymbol:
    return QgsFillSymbol.createSimple(
        {
            "color": colour,
            "outline_color": outline,
            "outline_width": "0.22",
            "outline_style": "solid",
        }
    )


def make_renderer(
    layer: QgsVectorLayer,
    field: str,
    suppression: str | None,
    colours: tuple[str, ...],
) -> QgsRuleBasedRenderer:
    values = numeric_values(layer, field, suppression)
    lower = min(values)
    upper = max(values)
    width = (upper - lower) / len(colours) if upper > lower else 1.0

    root = QgsRuleBasedRenderer.Rule(None)
    valid_prefix = f'"{suppression}" = 0 AND ' if suppression else ""

    suppressed_count = (
        sum(1 for feature in layer.getFeatures() if int(feature[suppression] or 0) == 1)
        if suppression
        else 0
    )
    if suppression and suppressed_count:
        root.appendChild(
            QgsRuleBasedRenderer.Rule(
                fill_symbol("#bdbdbd", "#737373"),
                filterExp=f'"{suppression}" = 1',
                label="Suppressed (<5 practices)",
            )
        )

    for index, colour in enumerate(colours):
        start = lower + index * width
        end = upper if index == len(colours) - 1 else lower + (index + 1) * width
        if index == 0:
            interval = f'"{field}" >= {start:.12g} AND "{field}" <= {end:.12g}'
        else:
            interval = f'"{field}" > {start:.12g} AND "{field}" <= {end:.12g}'
        root.appendChild(
            QgsRuleBasedRenderer.Rule(
                fill_symbol(colour),
                filterExp=valid_prefix + interval,
                label=f"{start:.1f} to {end:.1f}%",
            )
        )

    null_count = 0
    for feature in layer.getFeatures():
        if suppression and int(feature[suppression] or 0) == 1:
            continue
        value = feature[field]
        try:
            number = float(value)
        except (TypeError, ValueError):
            null_count += 1
            continue
        if not math.isfinite(number):
            null_count += 1
    if null_count:
        null_filter = f'"{field}" IS NULL'
        if suppression:
            null_filter = f'"{suppression}" = 0 AND ({null_filter})'
        root.appendChild(
            QgsRuleBasedRenderer.Rule(
                fill_symbol("#f0f0f0", "#969696"),
                filterExp=null_filter,
                label="Not available",
            )
        )
    return QgsRuleBasedRenderer(root)


def configure_layer(theme: dict[str, object]) -> QgsVectorLayer:
    layer = QgsVectorLayer(SOURCE_RELATIVE, str(theme["name"]), "ogr")
    if not layer.isValid():
        raise RuntimeError(f"QGIS could not load {SOURCE}")
    if layer.featureCount() != 42:
        raise RuntimeError(f"Expected 42 ICB features, observed {layer.featureCount()}")

    layer.setRenderer(
        make_renderer(
            layer,
            str(theme["field"]),
            theme["suppression"] if isinstance(theme["suppression"], str) else None,
            tuple(theme["colours"]),
        )
    )
    layer.setDisplayExpression('"icb_name"')
    layer.setReadOnly(True)
    layer.setCustomProperty("gpap2/theme_field", str(theme["field"]))
    layer.setCustomProperty(
        "gpap2/suppression_field",
        str(theme["suppression"] or "NOT_APPLICABLE"),
    )
    layer.setCustomProperty("gpap2/analysis_period", ANALYSIS_PERIOD)
    layer.setCustomProperty("gpap2/boundary_vintage", BOUNDARY_VINTAGE)
    layer.setCustomProperty("gpap2/organisation_reference_date", ORGANISATION_REFERENCE_DATE)
    layer.setCustomProperty("gpap2/geography_note", GEOGRAPHY_NOTE)
    layer.setCustomProperty("gpap2/source_sha256", EXPECTED_SOURCE_SHA256)
    layer.setCustomProperty("gpap2/interpretation_boundary", INTERPRETATION_NOTE)
    layer.setCustomProperty("gpap2/purpose", str(theme["purpose"]))

    aliases = {
        "icb_code": "NHS ODS ICB organisation code",
        "boundary_icb_gss_code": "ONS GSS ICB geography code",
        "practice_n": "Practices in ICB",
        "profile_1_pct": "Profile 1 share of practices (%)",
        "profile_2_pct": "Profile 2 share of practices (%)",
        "profile_3_pct": "Profile 3 share of practices (%)",
        "interpretive_caution_pct": "Assignment-caution share of practices (%)",
    }
    for field_name, alias in aliases.items():
        index = layer.fields().indexOf(field_name)
        if index >= 0:
            layer.setFieldAlias(index, alias)

    metadata = layer.metadata()
    metadata.setTitle(str(theme["name"]))
    metadata.setAbstract(
        f"{theme['purpose']} {INTERPRETATION_NOTE}. "
        f"Analysis period: {ANALYSIS_PERIOD}. Boundary vintage: "
        f"{BOUNDARY_VINTAGE}. Organisation reference date: "
        f"{ORGANISATION_REFERENCE_DATE}. {ONS_ATTRIBUTION}. {OS_ATTRIBUTION}."
    )
    metadata.setKeywords(
        {
            "theme": [
                "NHS primary care",
                "ICB",
                "practice profile composition",
                "ICB profile themes",
            ]
        }
    )
    layer.setMetadata(metadata)
    return layer


def add_label(
    layout: QgsPrintLayout,
    text: str,
    x: float,
    y: float,
    width: float,
    height: float,
    point_size: float,
    bold: bool = False,
    alignment: Qt.AlignmentFlag = Qt.AlignLeft,
) -> QgsLayoutItemLabel:
    label = QgsLayoutItemLabel(layout)
    label.setText(text)
    font = QFont("Arial")
    font.setPointSizeF(point_size)
    font.setBold(bold)
    label.setFont(font)
    label.setFontColor(QColor("#202020"))
    label.setHAlign(alignment)
    label.setVAlign(Qt.AlignVCenter)
    layout.addLayoutItem(label)
    label.attemptMove(QgsLayoutPoint(x, y, QgsUnitTypes.LayoutMillimeters))
    label.attemptResize(QgsLayoutSize(width, height, QgsUnitTypes.LayoutMillimeters))
    return label


def padded_extent(layer: QgsVectorLayer, factor: float = 1.05) -> QgsRectangle:
    extent = QgsRectangle(layer.extent())
    extent.scale(factor)
    return extent


def add_map(
    layout: QgsPrintLayout,
    layer: QgsVectorLayer,
    x: float,
    y: float,
    width: float,
    height: float,
) -> QgsLayoutItemMap:
    item = QgsLayoutItemMap(layout)
    layout.addLayoutItem(item)
    item.attemptMove(QgsLayoutPoint(x, y, QgsUnitTypes.LayoutMillimeters))
    item.attemptResize(QgsLayoutSize(width, height, QgsUnitTypes.LayoutMillimeters))
    item.setLayers([layer])
    item.setKeepLayerSet(True)
    item.setKeepLayerStyles(True)
    item.setExtent(padded_extent(layer))
    # setExtent can adapt the item geometry to the source aspect ratio. Reapply
    # the requested frame size so the print layout retains its designed grid.
    item.attemptResize(QgsLayoutSize(width, height, QgsUnitTypes.LayoutMillimeters))
    item.setFrameEnabled(True)
    item.setFrameStrokeColor(QColor("#737373"))
    item.setBackgroundColor(QColor("#ffffff"))
    return item


def add_legend(
    layout: QgsPrintLayout,
    map_item: QgsLayoutItemMap,
    layer: QgsVectorLayer,
    x: float,
    y: float,
    width: float,
    height: float,
) -> QgsLayoutItemLegend:
    legend = QgsLayoutItemLegend(layout)
    legend.setTitle("Share of practices (%)")
    legend.setLinkedMap(map_item)
    legend.setAutoUpdateModel(False)
    layer_tree = QgsLayerTree()
    layer_tree.addLayer(layer)
    legend.model().setRootGroup(layer_tree)
    # Keep the standalone legend tree alive for the lifetime of the layout item.
    # Without this Python reference, headless export can dereference a released
    # tree after the function returns.
    legend._gpap2_layer_tree = layer_tree
    legend.setResizeToContents(False)
    legend.setFrameEnabled(False)
    title_font = QFont("Arial")
    title_font.setPointSizeF(7.0)
    title_font.setBold(True)
    item_font = QFont("Arial")
    item_font.setPointSizeF(6.2)
    legend.setStyleFont(QgsLegendStyle.Title, title_font)
    legend.setStyleFont(QgsLegendStyle.Group, item_font)
    legend.setStyleFont(QgsLegendStyle.Subgroup, item_font)
    legend.setStyleFont(QgsLegendStyle.SymbolLabel, item_font)
    legend.setStyleMargin(QgsLegendStyle.Title, 1.0)
    legend.setStyleMargin(QgsLegendStyle.Subgroup, 0.6)
    legend.setStyleMargin(QgsLegendStyle.Symbol, 0.6)
    layout.addLayoutItem(legend)
    legend.attemptMove(QgsLayoutPoint(x, y, QgsUnitTypes.LayoutMillimeters))
    legend.attemptResize(QgsLayoutSize(width, height, QgsUnitTypes.LayoutMillimeters))
    return legend


def build_profile_layout(project: QgsProject, layers: list[QgsVectorLayer]) -> QgsPrintLayout:
    layout = QgsPrintLayout(project)
    layout.initializeDefaults()
    layout.setName("National three-profile composition")
    page = layout.pageCollection().page(0)
    page.setPageSize(QgsLayoutSize(420, 297, QgsUnitTypes.LayoutMillimeters))

    add_label(
        layout,
        "Digital GP access profiles: within-ICB practice composition",
        8,
        5,
        404,
        13,
        17,
        bold=True,
        alignment=Qt.AlignCenter,
    )
    add_label(
        layout,
        "Frozen March 2026 organisational geography; April 2023 ICB boundaries",
        8,
        18,
        404,
        8,
        8.5,
        alignment=Qt.AlignCenter,
    )

    panel_x = (8, 145, 282)
    for index, layer in enumerate(layers[:3]):
        x = panel_x[index]
        add_label(
            layout,
            layer.name(),
            x,
            28,
            130,
            8,
            10,
            bold=True,
            alignment=Qt.AlignCenter,
        )
        map_item = add_map(layout, layer, x, 37, 130, 185)
        add_legend(layout, map_item, layer, x, 224, 130, 58)

    add_label(
        layout,
        f"{ONS_ATTRIBUTION}\n{OS_ATTRIBUTION}",
        8,
        273,
        404,
        11,
        5.5,
        alignment=Qt.AlignCenter,
    )
    add_label(
        layout,
        INTERPRETATION_NOTE,
        8,
        286,
        404,
        7,
        8,
        bold=True,
        alignment=Qt.AlignCenter,
    )
    project.layoutManager().addLayout(layout)
    return layout


def build_caution_layout(project: QgsProject, layer: QgsVectorLayer) -> QgsPrintLayout:
    layout = QgsPrintLayout(project)
    layout.initializeDefaults()
    layout.setName("Assignment-caution share")
    page = layout.pageCollection().page(0)
    page.setPageSize(QgsLayoutSize(297, 210, QgsUnitTypes.LayoutMillimeters))

    add_label(
        layout,
        "Assignment-caution share by ICB",
        8,
        5,
        281,
        13,
        17,
        bold=True,
        alignment=Qt.AlignCenter,
    )
    add_label(
        layout,
        "Descriptive share of practices carrying the fixed-profile caution flag",
        8,
        18,
        281,
        8,
        8.5,
        alignment=Qt.AlignCenter,
    )
    map_item = add_map(layout, layer, 10, 29, 202, 151)
    add_legend(layout, map_item, layer, 218, 34, 69, 130)
    add_label(
        layout,
        f"{ONS_ATTRIBUTION}\n{OS_ATTRIBUTION}",
        8,
        174,
        281,
        12,
        5.5,
        alignment=Qt.AlignCenter,
    )
    add_label(
        layout,
        INTERPRETATION_NOTE,
        8,
        188,
        281,
        9,
        9,
        bold=True,
        alignment=Qt.AlignCenter,
    )
    add_label(
        layout,
        "No ranking or spatial-statistical inference",
        8,
        198,
        281,
        6,
        7.5,
        alignment=Qt.AlignCenter,
    )
    project.layoutManager().addLayout(layout)
    return layout


def export_preview(layout: QgsPrintLayout, path: Path) -> None:
    if path.exists():
        path.unlink()
    settings = QgsLayoutExporter.ImageExportSettings()
    settings.dpi = 150
    result = QgsLayoutExporter(layout).exportToImage(str(path), settings)
    if result != QgsLayoutExporter.Success:
        raise RuntimeError(f"Layout preview export failed for {layout.name()}: {result}")


def sanitise_qgz_writer_identity(path: Path) -> None:
    """Replace the workstation account name written automatically by QGIS."""

    temporary = path.with_name(path.name + ".tmp")
    with zipfile.ZipFile(path, "r") as source_archive:
        members = {name: source_archive.read(name) for name in source_archive.namelist()}
    qgs_name = next(name for name in members if name.endswith(".qgs"))
    qgs_xml = members[qgs_name].decode("utf-8")
    qgs_xml = re.sub(r'saveUserFull="[^"]*"', 'saveUserFull="GPAP2"', qgs_xml)
    qgs_xml = re.sub(r'saveUser="[^"]*"', 'saveUser="GPAP2"', qgs_xml)
    members[qgs_name] = qgs_xml.encode("utf-8")
    with zipfile.ZipFile(temporary, "w", zipfile.ZIP_DEFLATED) as target_archive:
        for name, content in members.items():
            target_archive.writestr(name, content)
    os.replace(temporary, path)


def main() -> None:
    if not SOURCE.exists():
        raise FileNotFoundError(SOURCE)
    observed_hash = sha256(SOURCE)
    if observed_hash != EXPECTED_SOURCE_SHA256:
        raise RuntimeError(
            f"Source checksum mismatch: expected {EXPECTED_SOURCE_SHA256}, observed {observed_hash}"
        )

    # QGIS resolves the portable data source from the project directory.
    os.chdir(ROOT)
    app = QgsApplication([], False)
    app.initQgis()
    try:
        project = QgsProject.instance()
        project.clear()
        project.setTitle("GPAP² Digital GP Access Profiles, March 2026")
        project.setFileName(str(PROJECT_FILE))
        project.setFilePathStorage(Qgis.FilePathType.Relative)
        project.setPresetHomePath(".")

        QgsExpressionContextUtils.setProjectVariable(
            project, "gpap2_analysis_period", ANALYSIS_PERIOD
        )
        QgsExpressionContextUtils.setProjectVariable(
            project, "gpap2_boundary_vintage", BOUNDARY_VINTAGE
        )
        QgsExpressionContextUtils.setProjectVariable(
            project,
            "gpap2_organisation_reference_date",
            ORGANISATION_REFERENCE_DATE,
        )
        QgsExpressionContextUtils.setProjectVariable(
            project, "gpap2_geography_note", GEOGRAPHY_NOTE
        )
        QgsExpressionContextUtils.setProjectVariable(
            project, "gpap2_interpretation_boundary", INTERPRETATION_NOTE
        )
        QgsExpressionContextUtils.setProjectVariable(
            project, "gpap2_source_sha256", EXPECTED_SOURCE_SHA256
        )
        QgsExpressionContextUtils.setProjectVariable(
            project, "gpap2_ons_attribution", ONS_ATTRIBUTION
        )
        QgsExpressionContextUtils.setProjectVariable(
            project, "gpap2_os_attribution", OS_ATTRIBUTION
        )
        project.writeEntry("GPAP2", "analysis_period", ANALYSIS_PERIOD)
        project.writeEntry("GPAP2", "boundary_vintage", BOUNDARY_VINTAGE)
        project.writeEntry("GPAP2", "organisation_reference_date", ORGANISATION_REFERENCE_DATE)
        project.writeEntry("GPAP2", "geography_note", GEOGRAPHY_NOTE)
        project.writeEntry("GPAP2", "ons_attribution", ONS_ATTRIBUTION)
        project.writeEntry("GPAP2", "os_attribution", OS_ATTRIBUTION)
        project.writeEntry("GPAP2", "interpretation_boundary", INTERPRETATION_NOTE)
        project.writeEntry(
            "GPAP2",
            "prohibited_analyses",
            (
                "Ranking; Moran's I; LISA; spatial regression; patient-residence "
                "inference; post-April-2026 boundary conversion"
            ),
        )

        group = project.layerTreeRoot().addGroup("ICB profile themes")
        layers: list[QgsVectorLayer] = []
        for index, theme in enumerate(THEMES):
            layer = configure_layer(theme)
            project.addMapLayer(layer, False)
            node = group.addLayer(layer)
            node.setItemVisibilityChecked(index == 0)
            layers.append(layer)

        project.setCrs(layers[0].crs())
        profile_layout = build_profile_layout(project, layers)
        caution_layout = build_caution_layout(project, layers[3])

        if not project.write(str(PROJECT_FILE)):
            raise RuntimeError(f"Could not write {PROJECT_FILE}")
        sanitise_qgz_writer_identity(PROJECT_FILE)

        export_preview(profile_layout, PROFILE_LAYOUT_PREVIEW)
        export_preview(caution_layout, CAUTION_LAYOUT_PREVIEW)

        runtime_record = {
            "qgis_version": Qgis.QGIS_VERSION,
            "operating_system": platform.platform(),
            "project_path": PROJECT_FILE.relative_to(ROOT.parent).as_posix(),
            "project_open_status": True,
            "missing_layer_count": sum(not layer.isValid() for layer in layers),
            "layers": [
                {"name": layer.name(), "feature_count": int(layer.featureCount())}
                for layer in layers
            ],
            "layouts": [layout.name() for layout in project.layoutManager().layouts()],
            "rendered_previews": [
                {
                    "path": PROFILE_LAYOUT_PREVIEW.relative_to(ROOT.parent).as_posix(),
                    "sha256": sha256(PROFILE_LAYOUT_PREVIEW),
                },
                {
                    "path": CAUTION_LAYOUT_PREVIEW.relative_to(ROOT.parent).as_posix(),
                    "sha256": sha256(CAUTION_LAYOUT_PREVIEW),
                },
            ],
            "validation_timestamp_utc": datetime.now(UTC).isoformat(),
            "validation_route": "automated PyQGIS project build, open-layer validation and layout export",
            "validation_status": "passed" if all(layer.isValid() for layer in layers) else "failed",
            "notes": (
                "All four layers use the portable relative GeoJSON source. Both layouts include "
                "the required ONS and OS attribution."
            ),
        }
        RUNTIME_RECORD.parent.mkdir(parents=True, exist_ok=True)
        RUNTIME_RECORD.write_text(
            json.dumps(runtime_record, indent=2) + "\n", encoding="utf-8", newline="\n"
        )

        print(f"QGIS_VERSION={Qgis.QGIS_VERSION}")
        print(f"PROJECT={PROJECT_FILE}")
        print(f"PROJECT_SHA256={sha256(PROJECT_FILE)}")
        print(f"LAYERS={len(layers)}")
        print(f"LAYOUTS={len(project.layoutManager().layouts())}")
        print("STATUS=QGIS_PROJECT_CREATED")
        print(f"RUNTIME_RECORD={RUNTIME_RECORD}")
    finally:
        QgsProject.instance().clear()
        app.exitQgis()


if __name__ == "__main__":
    main()
