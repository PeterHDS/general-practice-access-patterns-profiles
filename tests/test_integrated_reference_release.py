import csv
import hashlib
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def sha256(relative: str) -> str:
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest().upper()


def test_bundle_scientific_authorities_are_exact() -> None:
    expected = {
        "outputs/tables/claim_to_evidence_matrix.csv": (
            "72E046D5804019F152FA773C4FC9A429F394814A6BBB157CDE9634E231828F7D"
        ),
        "qgis/data/icb_profile_mapping_layer.geojson": (
            "79CEAF2F84B866CFABAE22F95C825523EBE3FF100584D404A83B7AFE03E71D30"
        ),
        "qgis/GPAP2_Digital_GP_Access_Profiles_March_2026.qgz": (
            "5AA8BDB3C67A5318A1B98FC8485D79F853C98C4A7995E298297EB048A3D2218C"
        ),
    }
    for relative, digest in expected.items():
        assert sha256(relative) == digest


def test_claim_authority_and_presentation_layer_are_complete() -> None:
    claims = pd.read_csv(ROOT / "outputs/tables/claim_to_evidence_matrix.csv")
    assert claims.shape == (42, 30)
    assert claims["claim_id"].is_unique
    assert set(claims["primary_claim_domain"]) == {
        "ACCESS",
        "PATIENT_EXPERIENCE",
        "WORKLOAD",
        "EQUITY",
        "SAFETY",
        "VALUE",
    }
    presentation = pd.read_csv(ROOT / "outputs/tables/evidence_map_presentation.csv")
    assert presentation["claim_id"].tolist() == claims["claim_id"].tolist()
    for paths in presentation["repository_evidence_paths"]:
        assert all((ROOT / value).is_file() for value in paths.split(";"))


def test_population_scope_and_cohort_flows_are_exact() -> None:
    register = pd.read_csv(ROOT / "outputs/tables/population_scope_register.csv")
    assert register[
        ["parent_population", "retained_population", "not_retained_population"]
    ].values.tolist() == [
        [6130, 6067, 63],
        [6067, 3020, 3047],
        [3020, 1456, 1564],
    ]
    stages = pd.read_csv(ROOT / "outputs/tables/cohort_selection_stage_summary.csv")
    assert stages[["parent_n", "selected_n", "comparison_n"]].values.tolist() == [
        [6130, 6067, 63],
        [6067, 3020, 3047],
        [3020, 1456, 1564],
    ]
    national = pd.read_csv(ROOT / "outputs/tables/national_cohort_flow.csv").set_index("stage")
    inbound = pd.read_csv(ROOT / "outputs/tables/cbt_inbound_cohort_flow.csv").set_index("stage")
    outcome = pd.read_csv(ROOT / "outputs/tables/cbt_outcome_cohort_flow.csv").set_index("stage")
    assert national.loc["COMPLETE_SOURCE_PARENT", "practices"] == 6130
    assert national.loc["NATIONAL_ANALYTICAL_COHORT", "practices"] == 6067
    assert inbound.loc["CBT_INBOUND_ELIGIBLE", "practices"] == 3020
    assert outcome.loc["CBT_OUTCOME_COMPLETE", "practices"] == 1456


def test_qgis_geography_contract() -> None:
    data = json.loads(
        (ROOT / "qgis/data/icb_profile_mapping_layer.geojson").read_text(encoding="utf-8")
    )
    features = data["features"]
    assert len(features) == 42
    assert len({feature["properties"]["icb_code"] for feature in features}) == 42
    assert sum(feature["properties"]["profile_1_suppression_flag"] for feature in features) == 8
    assert sum(feature["properties"]["profile_2_suppression_flag"] for feature in features) == 0
    assert sum(feature["properties"]["profile_3_suppression_flag"] for feature in features) == 0


def test_evidence_map_has_text_and_static_html_routes() -> None:
    html = (ROOT / "docs/evidence-map/index.html").read_text(encoding="utf-8")
    assert "GPAP² Evidence Map" in html
    assert html.count('class="claim-card"') == 42
    assert (ROOT / "docs/evidence-map.md").is_file()
    with (ROOT / "outputs/tables/evidence_domain_summary.csv").open(
        encoding="utf-8", newline=""
    ) as stream:
        assert len(list(csv.DictReader(stream))) == 6
    for target in ("style.css", "app.js"):
        assert (ROOT / "docs/evidence-map" / target).is_file()
        assert target in html
    script = (ROOT / "docs/evidence-map/app.js").read_text(encoding="utf-8")
    assert "addEventListener('input', update)" in script
    assert "clear.addEventListener('click'" in script
    assert "search.focus()" in script


def test_evidence_map_mixed_population_scope_and_grammar() -> None:
    presentation = pd.read_csv(
        ROOT / "outputs/tables/evidence_map_presentation.csv"
    ).set_index("claim_id")
    b03 = presentation.loc["B03", "population_scope_note"]
    assert "3,020 practices" in b03
    assert "1,456-practice outcome-complete subset" in b03
    c01 = presentation.loc["C01", "population_scope_note"]
    assert "descriptive practice population" in c01
    assert "smaller complete-case contextual model" in c01
    html = (ROOT / "docs/evidence-map/index.html").read_text(encoding="utf-8")
    assert "1 claims" not in html
    assert "1 claim." in html


def _relative_luminance(colour: str) -> float:
    channels = [int(colour[index : index + 2], 16) / 255 for index in (1, 3, 5)]
    linear = [
        value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4
        for value in channels
    ]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def _contrast(first: str, second: str) -> float:
    light, dark = sorted((_relative_luminance(first), _relative_luminance(second)), reverse=True)
    return (light + 0.05) / (dark + 0.05)


def test_evidence_map_status_colours_meet_normal_text_contrast() -> None:
    light = {"#006da8", "#006b4f", "#8a5900", "#666666"}
    dark = {"#70c7ff", "#67ddb8", "#ffc65c", "#c7c7c7"}
    assert all(_contrast(colour, "#ffffff") >= 4.5 for colour in light)
    assert all(_contrast(colour, "#14171a") >= 4.5 for colour in dark)
    assert _contrast("#ffffff", "#0072b2") >= 4.5
    assert _contrast("#202124", "#009e73") >= 4.5
    assert _contrast("#202124", "#e69f00") >= 4.5
    assert _contrast("#ffffff", "#767676") >= 4.5


def test_active_qgis_builder_and_reader_surfaces_exclude_development_terms() -> None:
    builder = (ROOT / "qgis/scripts/build_qgis_project.py").read_text(encoding="utf-8")
    assert "publication-safe" not in builder.casefold()
    forbidden = (
        "closure_repair",
        "preanalysis_repair",
        "prestart_repair",
        "_corrected",
        "e07b",
        "e08a",
        "e08b",
    )
    reader_paths = [ROOT / "README.md"]
    reader_paths.extend((ROOT / "docs").rglob("*.md"))
    reader_paths.extend(
        path
        for path in (ROOT / "outputs/tables").glob("*.csv")
        if path.name != "claim_to_evidence_matrix.csv"
    )
    text = "\n".join(path.read_text(encoding="utf-8", errors="strict") for path in reader_paths)
    assert all(term not in text.casefold() for term in forbidden)


def test_social_preview_and_full_reference_workflow_use_v1_contract() -> None:
    preview_builder = (ROOT / "scripts/build_social_preview.py").read_text(encoding="utf-8")
    assert "General Practice Access Patterns and Profiles" in preview_builder
    assert "Profiles · robustness · population scope · evidence map" in preview_builder
    assert "companion" not in preview_builder.casefold()
    workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    assert "github.event_name == 'workflow_dispatch'" in workflow
    assert "github.event_name == 'pull_request' && github.base_ref == 'main'" in workflow
