import csv
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path
from types import SimpleNamespace

from gpap2.config import load_config

VALIDATOR_SPEC = importlib.util.spec_from_file_location(
    "gpap2_public_repository_validator",
    Path(__file__).resolve().parents[1] / "scripts" / "validate_public_repository.py",
)
assert VALIDATOR_SPEC and VALIDATOR_SPEC.loader
public_validator = importlib.util.module_from_spec(VALIDATOR_SPEC)
sys.modules[VALIDATOR_SPEC.name] = public_validator
VALIDATOR_SPEC.loader.exec_module(public_validator)

ROOT = Path(__file__).resolve().parents[1]
ATTRIBUTIONS = (
    "Source: Office for National Statistics licensed under the Open Government Licence v.3.0",
    "Contains OS data © Crown copyright and database right 2026",
)
FORBIDDEN_ARCHITECTURE_PHRASES = (
    "question-led",
    "choose a question",
    "select a route",
    "independent route",
    "start wherever relevant",
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def public_narrative_text() -> str:
    paths = [ROOT / "README.md", ROOT / "CONTRIBUTING.md", ROOT / ".github/CONTRIBUTING.md"]
    paths.extend((ROOT / "docs").rglob("*.md"))
    paths.extend((ROOT / "notebooks").rglob("*.md"))
    paths.extend((ROOT / "notebooks").glob("*.ipynb"))
    return "\n".join(
        path.read_text(encoding="utf-8", errors="strict") for path in paths if path.is_file()
    ).casefold()


def test_superseded_public_architecture_language_is_absent() -> None:
    text = public_narrative_text()
    for phrase in FORBIDDEN_ARCHITECTURE_PHRASES:
        assert phrase not in text


def test_roadmap_contains_the_complete_cumulative_spine() -> None:
    text = (ROOT / "docs/assets/gpap2-roadmap.svg").read_text(encoding="utf-8")
    for stage in (
        "Inputs and population",
        "National model",
        "Profiles and uncertainty",
        "Robustness envelope",
        "External context",
        "Geography",
        "Evidence Map",
    ):
        assert stage in text
    assert text.count('marker-end="url(#arrow)"') == 1
    assert text.count("<path d=") >= 6


def test_configured_authority_manifest_exists_and_notebooks_use_it() -> None:
    config = load_config(ROOT / "configs/reference_apr2025_mar2026.json")
    configured = config.resolve(config.authority_checksum_file)
    assert configured == ROOT / "outputs/validation/notebook_authority_files.csv"
    assert configured.is_file()
    builder = (ROOT / "scripts/build_public_notebooks.py").read_text(encoding="utf-8")
    assert "REFERENCE_CONFIG.resolve(REFERENCE_CONFIG.authority_checksum_file)" in builder
    assert "authority_file_checksums.csv" not in builder


def test_figure_provenance_covers_every_public_image() -> None:
    register = ROOT / "outputs/validation/figure_provenance.csv"
    with register.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    expected = {
        path.relative_to(ROOT).as_posix()
        for directory in (ROOT / "outputs/figures", ROOT / "outputs/maps", ROOT / "qgis/previews")
        for path in directory.glob("*.png")
    }
    assert {row["figure_path"] for row in rows} == expected
    allowed = {
        "recomputed_from_included_matrices",
        "regenerated_from_included_authority_tables",
        "checksum_validated_frozen_authority",
        "qgis_rendered_output",
    }
    for row in rows:
        assert row["reproducibility_class"] in allowed
        assert (ROOT / row["figure_path"]).is_file()
        if row["generator_path"]:
            assert (ROOT / row["generator_path"]).is_file()
        sources = row["source_table_paths"].split(";")
        checksum_contracts = dict(item.split("=", 1) for item in row["source_checksums"].split(";"))
        assert set(sources) == set(checksum_contracts)
        for source in sources:
            assert (ROOT / source).is_file()
            assert digest(ROOT / source) == checksum_contracts[source]


def test_exact_ons_os_attribution_is_present_in_required_locations() -> None:
    for relative in ("DATA_LICENSE.md", "qgis/README.md", "docs/geography-and-qgis.md"):
        text = (ROOT / relative).read_text(encoding="utf-8")
        for statement in ATTRIBUTIONS:
            assert statement in text


def test_data_licence_register_covers_every_redistributed_family() -> None:
    text = (ROOT / "DATA_LICENSE.md").read_text(encoding="utf-8").casefold()
    for term in (
        "primary_practice_access_clustering_matrix.csv",
        "cbt_inbound_sensitivity",
        "cbt_outcomes_sensitivity",
        "national_profile_assignments.csv",
        "gp patient survey",
        "workforce",
        "registered-population",
        "deprivation",
        "rurality",
        "icb_profile_mapping_layer.geojson",
        "qgis",
        "project-created code",
        "project-created documentation",
        "project-created figures",
    ):
        assert term in text


def test_release_provenance_has_origin_and_upstream_contract() -> None:
    record = json.loads(
        (ROOT / "outputs/validation/release_provenance.json").read_text(encoding="utf-8")
    )
    assert record["repository_url_status"] in {"confirmed_from_git_remote", "unconfirmed"}
    if record["repository_url_status"] == "confirmed_from_git_remote":
        assert record["repository_url"]
    assert record["source_commit"]
    assert record["pcadi_commit"] == "1239c63356acfb824277ee6fbaee25fa8df51313"
    assert record["pcadi_tag"] == "reference-apr2025-mar2026"
    assert record["archive_checksum_status"] == "pending_until_git_archive_is_built"


def test_notebook_ci_and_canonical_evidence_are_distinct() -> None:
    with (ROOT / "outputs/validation/notebook_ci_summary.csv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = list(csv.DictReader(stream))
    classes = [row["evidence_class"] for row in rows]
    assert classes.count("local_environment_smoke") == 3
    assert classes.count("reference_regeneration") == 1
    assert all(row["hosted_by"] != "GitHub Actions" for row in rows)
    assert all(row["workflow_url"] == "" and row["run_id"] == "" for row in rows)


def test_qgis_runtime_claim_matches_public_evidence() -> None:
    record = json.loads(
        (ROOT / "outputs/validation/qgis_runtime_validation.json").read_text(encoding="utf-8")
    )
    assert record["qgis_version"].startswith("3.44.12-")
    assert record["project_open_status"] is True
    assert record["missing_layer_count"] == 0
    assert {item["feature_count"] for item in record["layers"]} == {42}
    assert len(record["layers"]) == 4
    assert len(record["layouts"]) == 2
    assert record["validation_status"] == "passed"


def test_citation_message_does_not_require_unavailable_dissertation() -> None:
    text = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
    message = re.search(r'^message:\s*"([^"]+)"', text, flags=re.MULTILINE)
    assert message
    assert "dissertation" not in message.group(1).casefold()
    assert "official data sources" in message.group(1).casefold()


def test_readme_execution_scope_agrees_with_authority_classes() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for evidence_class in (
        "Recomputed and validated",
        "Recomputed",
        "Validated from frozen authority tables",
        "Inspected from checksum-controlled scientific authority",
        "Portable project plus structural and runtime evidence",
    ):
        assert evidence_class in readme
    with (ROOT / "outputs/validation/figure_provenance.csv").open(
        encoding="utf-8", newline=""
    ) as stream:
        classes = {row["reproducibility_class"] for row in csv.DictReader(stream)}
    assert "checksum_validated_frozen_authority" in classes
    assert "qgis_rendered_output" in classes


def test_public_validator_uses_manifest_when_git_metadata_is_absent(
    tmp_path: Path, monkeypatch
) -> None:
    manifest = tmp_path / "outputs/validation/public_file_manifest.csv"
    manifest.parent.mkdir(parents=True)
    manifest.write_text("path,bytes,sha256\nREADME.md,1,ABC\n", encoding="utf-8")
    monkeypatch.setattr(public_validator, "ROOT", tmp_path)
    monkeypatch.setattr(
        public_validator.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(returncode=128, stdout="", stderr=""),
    )
    assert public_validator.tracked_release_files() == {
        "README.md",
        "outputs/validation/public_file_manifest.csv",
    }
