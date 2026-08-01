"""Build the complete public figure and map provenance register."""

# ruff: noqa: E501

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gpap2.io import sha256  # noqa: E402

CANONICAL_PYTHON = "Python 3.13.14 with the pinned notebook and figure dependencies"
PROFILE_AUTHORITY = "src/gpap2/profile_labels.py"

FIGURES = [
    {
        "figure_path": "outputs/figures/national_profile_characteristics_and_uncertainty.png",
        "public_role": "Primary national profile characteristics and practice-level uncertainty",
        "sources": [
            "data/reference/primary_practice_access_clustering_matrix.csv",
            "outputs/tables/national_profile_assignments.csv",
            "outputs/tables/national_profile_uncertainty_plot_data.csv",
        ],
        "generator_path": "scripts/build_selected_figures.py",
        "authority_source": "Included national matrix, frozen assignments and uncertainty authority",
        "reproducibility_class": "recomputed_from_included_matrices",
        "canonical_environment": CANONICAL_PYTHON,
        "notes": "Regenerated from the included national matrix and checksum-controlled authorities.",
    },
    {
        "figure_path": "outputs/figures/telephone_inbound_profile_comparison.png",
        "public_role": "Matched 14-feature and 17-feature CBT inbound profile comparison",
        "sources": ["data/reference/cbt_inbound_sensitivity_clustering_matrix_17_features.csv"],
        "generator_path": "scripts/build_selected_figures.py",
        "authority_source": "Included CBT inbound matrix and locked comparison implementation",
        "reproducibility_class": "recomputed_from_included_matrices",
        "canonical_environment": CANONICAL_PYTHON,
        "notes": "Regenerated with the same locked preprocessing, seed and label alignment as Notebook 3.",
    },
    {
        "figure_path": "outputs/figures/temporal_robustness_summary.png",
        "public_role": "Annual-profile agreement across half-year and quarterly windows",
        "sources": [
            "outputs/tables/temporal_canonical_period_metrics.csv",
            "outputs/tables/temporal_structural_period_metrics.csv",
        ],
        "generator_path": "scripts/build_selected_figures.py",
        "authority_source": "Checksum-controlled temporal authority tables",
        "reproducibility_class": "regenerated_from_included_authority_tables",
        "canonical_environment": CANONICAL_PYTHON,
        "notes": "The public repository regenerates this summary, not the excluded monthly upstream pipeline.",
    },
    {
        "figure_path": "outputs/maps/icb_profile_composition.png",
        "public_role": "Within-ICB composition of the three national profiles",
        "sources": ["qgis/data/icb_profile_mapping_layer_publication_safe.geojson"],
        "generator_path": "scripts/build_selected_figures.py",
        "authority_source": "Publication-safe GeoJSON with audited geography metadata",
        "reproducibility_class": "regenerated_from_included_authority_tables",
        "canonical_environment": CANONICAL_PYTHON,
        "notes": "Includes mandatory ONS and OS attribution; eight small Profile 1 cells remain suppressed.",
    },
    {
        "figure_path": "qgis/previews/national_three_profile_map_preview.png",
        "public_role": "QGIS print-layout preview of national profile composition",
        "sources": ["qgis/data/icb_profile_mapping_layer_publication_safe.geojson"],
        "generator_path": "qgis/scripts/build_qgis_project.py",
        "authority_source": "Portable QGIS project and publication-safe GeoJSON",
        "reproducibility_class": "qgis_rendered_output",
        "canonical_environment": "QGIS 3.44.12 LTR on Windows 11",
        "notes": "Runtime record proves four resolved layers, two layouts and regenerated preview checksums.",
    },
    {
        "figure_path": "qgis/previews/assignment_caution_map_preview.png",
        "public_role": "QGIS print-layout preview of assignment-caution share",
        "sources": ["qgis/data/icb_profile_mapping_layer_publication_safe.geojson"],
        "generator_path": "qgis/scripts/build_qgis_project.py",
        "authority_source": "Portable QGIS project and publication-safe GeoJSON",
        "reproducibility_class": "qgis_rendered_output",
        "canonical_environment": "QGIS 3.44.12 LTR on Windows 11",
        "notes": "Runtime record proves four resolved layers, two layouts and regenerated preview checksums.",
    },
    {
        "figure_path": "outputs/figures/external_context_effect_sizes.png",
        "public_role": "Rank-based contextual profile effect-size summary",
        "sources": ["outputs/tables/numeric_profile_descriptive_summary.csv"],
        "generator_path": "",
        "authority_source": "Closed external-profile analysis; figure checksum controlled in the release manifest",
        "reproducibility_class": "checksum_validated_frozen_authority",
        "canonical_environment": "Closed source-analysis environment; summary table included for inspection",
        "notes": "The omnibus rank-test table needed for exact regeneration is intentionally outside the compact public pipeline.",
    },
    {
        "figure_path": "outputs/figures/national_profile_stability_and_sensitivity.png",
        "public_role": "National algorithm and feature-specification stability evidence",
        "sources": ["outputs/tables/robustness_summary.csv", "outputs/tables/model_role_register.csv"],
        "generator_path": "",
        "authority_source": "Closed resampling analysis; figure checksum controlled in the release manifest",
        "reproducibility_class": "checksum_validated_frozen_authority",
        "canonical_environment": "Closed resampling environment; aggregate authority tables included",
        "notes": "The 100-run practice-level resampling arrays are intentionally excluded from the compact public repository.",
    },
    {
        "figure_path": "outputs/figures/patient_experience_by_profile.png",
        "public_role": "GP Patient Survey estimates by fixed national profile",
        "sources": [
            "outputs/tables/numeric_profile_descriptive_summary.csv",
            "outputs/tables/gpps_precision_profile_summary.csv",
        ],
        "generator_path": "",
        "authority_source": "Closed GPPS profile analysis; figure checksum controlled in the release manifest",
        "reproducibility_class": "checksum_validated_frozen_authority",
        "canonical_environment": "Closed external-source environment; aggregate authorities included",
        "notes": "Practice-level GPPS estimates are not redistributed, so the full distribution cannot be regenerated exactly.",
    },
    {
        "figure_path": "outputs/figures/telephone_outcome_representation_stability.png",
        "public_role": "Resampling stability of inbound, raw-outcome and NHS-ILR models",
        "sources": [
            "outputs/tables/telephone_outcome_model_comparison.csv",
            "outputs/tables/telephone_outcome_model_diagnostics.csv",
        ],
        "generator_path": "",
        "authority_source": "Closed outcome resampling analysis; figure checksum controlled in the release manifest",
        "reproducibility_class": "checksum_validated_frozen_authority",
        "canonical_environment": "Closed resampling environment; aggregate authority tables included",
        "notes": "The 100-run outcome resampling arrays are intentionally excluded from the compact public repository.",
    },
]


def main() -> None:
    rows: list[dict[str, str]] = []
    for record in FIGURES:
        figure = ROOT / record["figure_path"]
        if not figure.is_file():
            raise FileNotFoundError(f"Public figure is absent: {record['figure_path']}")
        source_paths = record.pop("sources")
        checksums = []
        for relative in source_paths:
            source = ROOT / relative
            if not source.is_file():
                raise FileNotFoundError(f"Figure source is absent: {relative}")
            checksums.append(f"{relative}={sha256(source)}")
        generator = record["generator_path"]
        if generator and not (ROOT / generator).is_file():
            raise FileNotFoundError(f"Figure generator is absent: {generator}")
        rows.append(
            {
                **record,
                "source_table_paths": ";".join(source_paths),
                "source_checksums": ";".join(checksums),
                "profile_label_authority": PROFILE_AUTHORITY,
            }
        )
    columns = [
        "figure_path",
        "public_role",
        "source_table_paths",
        "generator_path",
        "authority_source",
        "source_checksums",
        "reproducibility_class",
        "canonical_environment",
        "profile_label_authority",
        "notes",
    ]
    output = ROOT / "outputs" / "validation" / "figure_provenance.csv"
    pd.DataFrame(rows)[columns].sort_values("figure_path").to_csv(
        output, index=False, lineterminator="\n"
    )
    print(f"wrote provenance for {len(rows)} public figures and maps")


if __name__ == "__main__":
    main()
