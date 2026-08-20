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
