"""Build selected figures from included public authority data and label contracts."""

from __future__ import annotations

import json
import sys
import textwrap
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.collections import PolyCollection

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gpap2.analysis import compare_inbound_models  # noqa: E402
from gpap2.config import load_config  # noqa: E402
from gpap2.io import read_contract_csv  # noqa: E402
from gpap2.preprocessing import prepare_national_features  # noqa: E402
from gpap2.profile_labels import PROFILE_SHORT_LABELS  # noqa: E402
from gpap2.visual_style import PROFILE_COLOURS, apply_figure_style  # noqa: E402


def _feature_label(name: str) -> str:
    replacements = {
        "gpad_": "GPAD ",
        "ocs_": "OCS ",
        "per_1000_patient_months": "per 1,000 patient-months",
        "mean_absolute_monthly_rate_change": "mean absolute monthly rate change",
        "2_to_7_days": "2-7 day",
        "8_to_14_days": "8-14 day",
        "over_14_days": "over-14-day",
        "1_day": "next-day",
        "same_day": "same-day",
    }
    result = name
    for source, target in replacements.items():
        result = result.replace(source, target)
    return result.replace("_", " ").strip()


def build_national_profile_figure() -> None:
    apply_figure_style()
    config = load_config(ROOT / "configs" / "reference_apr2025_mar2026.json")
    matrix = read_contract_csv(
        config.resolve(config.input_directory) / config.specification("national_14").source_file
    )
    assignments = read_contract_csv(ROOT / "outputs/tables/national_profile_assignments.csv")
    uncertainty = read_contract_csv(
        ROOT / "outputs/tables/national_profile_uncertainty_plot_data.csv"
    )
    if not matrix[config.identifier].equals(assignments[config.identifier]):
        raise ValueError("National matrix and frozen assignments are not in identical order")
    if set(uncertainty[config.identifier]) != set(assignments[config.identifier]):
        raise ValueError("Uncertainty plot data do not cover the frozen national cohort")

    prepared = prepare_national_features(matrix, config)
    scaled = pd.DataFrame(prepared.matrix, columns=prepared.feature_names)
    scaled["profile"] = assignments["kmeans_cluster"].to_numpy()
    medians = scaled.groupby("profile").median().loc[[1, 2, 3]]
    medians = medians.clip(-1, 1)

    fig = plt.figure(figsize=(20, 14.4))
    grid = fig.add_gridspec(2, 2, height_ratios=[1.15, 1], hspace=0.42, wspace=0.22)
    heat = fig.add_subplot(grid[0, :])
    image = heat.imshow(medians, cmap="coolwarm", vmin=-1, vmax=1, aspect="auto")
    for row in range(3):
        for column in range(len(medians.columns)):
            heat.text(
                column,
                row,
                f"{medians.iloc[row, column]:.2f}",
                ha="center",
                va="center",
                color="white" if abs(medians.iloc[row, column]) > 0.5 else "#222222",
                fontsize=8,
            )
    heat.set_yticks(range(3), [textwrap.fill(PROFILE_SHORT_LABELS[i], 34) for i in (1, 2, 3)])
    heat.set_xticks(
        range(len(medians.columns)),
        [_feature_label(name) for name in medians.columns],
        rotation=38,
        ha="right",
        fontsize=8,
    )
    heat.set_title("Relative median access-activity profiles")
    colour_bar = fig.colorbar(image, ax=heat, fraction=0.025, pad=0.025)
    colour_bar.set_label("Median robust-scaled value")

    bars = fig.add_subplot(grid[1, 0])
    summary = (
        uncertainty.groupby("profile")
        .agg(
            negative_silhouette=("kmeans_silhouette", lambda values: (values < 0).mean()),
            gmm_posterior_below_060=(
                "gmm_maximum_posterior",
                lambda values: (values < 0.60).mean(),
            ),
            gmm_retention_below_080=("gmm_retention_share", lambda values: (values < 0.80).mean()),
            kmeans_gmm_disagreement=("kmeans_gmm_disagreement", "mean"),
        )
        .loc[[1, 2, 3]]
    )
    x = np.arange(3)
    width = 0.19
    colours = ["#d16a6a", "#df963f", "#9b7896", "#5c82a8"]
    for offset, (column, colour) in enumerate(zip(summary.columns, colours, strict=True)):
        bars.bar(
            x + (offset - 1.5) * width,
            summary[column],
            width,
            label=column.replace("_", " "),
            color=colour,
        )
    bars.set_xticks(x, [f"Profile {value}" for value in (1, 2, 3)])
    bars.set_ylim(0, 1)
    bars.set_ylabel("Share of practices within profile")
    bars.set_title("Descriptive uncertainty and method-sensitivity signals")
    bars.legend(frameon=False, fontsize=8)
    bars.spines[["top", "right"]].set_visible(False)

    scatter = fig.add_subplot(grid[1, 1])
    for profile in (1, 2, 3):
        subset = uncertainty.loc[uncertainty["profile"].eq(profile)]
        scatter.scatter(
            subset["kmeans_silhouette"],
            subset["gmm_maximum_posterior"],
            s=8,
            alpha=0.28,
            color=PROFILE_COLOURS[profile],
            label=PROFILE_SHORT_LABELS[profile],
        )
    scatter.axvline(0, color="#d44", linestyle="--", linewidth=0.8)
    scatter.axhline(0.60, color="#d44", linestyle="--", linewidth=0.8)
    scatter.set_xlabel("K-Means practice-level silhouette")
    scatter.set_ylabel("Spherical-GMM maximum posterior")
    scatter.set_title("K-Means boundary strength versus GMM membership certainty")
    scatter.legend(frameon=False, fontsize=7, loc="lower right")
    scatter.spines[["top", "right"]].set_visible(False)

    fig.suptitle("Primary 14-feature K-Means profiles and practice-level uncertainty", fontsize=18)
    fig.text(
        0.5,
        0.01,
        "Labels describe relative recorded activity, not care quality, patient need, causal "
        "mechanisms or outcomes. "
        "Thresholds are descriptive audit conventions; no practice is removed or reassigned.",
        ha="center",
        fontsize=9,
    )
    destination = ROOT / "outputs/figures/national_profile_characteristics_and_uncertainty.png"
    fig.savefig(destination, dpi=220, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(destination)


def _polygon_rings(geometry: dict[str, object]) -> list[list[list[float]]]:
    if geometry["type"] == "Polygon":
        return [geometry["coordinates"][0]]
    return [polygon[0] for polygon in geometry["coordinates"]]


def build_icb_composition_map() -> None:
    apply_figure_style()
    source = ROOT / "qgis/data/icb_profile_mapping_layer.geojson"
    features = json.loads(source.read_text(encoding="utf-8"))["features"]
    fig, axes = plt.subplots(1, 3, figsize=(18, 9))
    for profile, axis in zip((1, 2, 3), axes, strict=True):
        polygons: list[list[list[float]]] = []
        values: list[float] = []
        for feature in features:
            value = feature["properties"].get(f"profile_{profile}_pct")
            for ring in _polygon_rings(feature["geometry"]):
                polygons.append(ring)
                values.append(np.nan if value is None else float(value))
        collection = PolyCollection(
            polygons,
            array=np.asarray(values),
            cmap="viridis",
            clim=(0, 70),
            edgecolors="white",
            linewidths=0.35,
        )
        axis.add_collection(collection)
        axis.autoscale_view()
        axis.set_aspect("equal")
        axis.axis("off")
        axis.set_title(textwrap.fill(PROFILE_SHORT_LABELS[profile], 34), fontsize=11)
        colour_bar = fig.colorbar(collection, ax=axis, fraction=0.034, pad=0.01)
        colour_bar.set_label("Share of practices within ICB (%)", fontsize=8)
    fig.suptitle("Composition of national access-activity profiles by ICB", fontsize=17)
    fig.text(
        0.5,
        0.035,
        "March 2026 reference geography. Eight small Profile 1 cells are suppressed. "
        "The maps show practice composition, not patient prevalence or performance.",
        ha="center",
        fontsize=9,
    )
    fig.text(
        0.5,
        0.008,
        "Source: Office for National Statistics licensed under the Open Government Licence v.3.0\n"
        "Contains OS data © Crown copyright and database right 2026",
        ha="center",
        fontsize=7.5,
    )
    destination = ROOT / "outputs/maps/icb_profile_composition.png"
    fig.savefig(destination, dpi=220, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(destination)


def build_temporal_summary() -> None:
    apply_figure_style()
    tables = ROOT / "outputs" / "tables"
    canonical = pd.read_csv(tables / "temporal_canonical_period_metrics.csv")
    structural = pd.read_csv(tables / "temporal_structural_period_metrics.csv")
    labels = {
        "H1_Apr_Sep_2025": "H1 Apr-Sep 2025",
        "H2_Oct_2025_Mar_2026": "H2 Oct 2025-Mar 2026",
        "Q1_Apr_Jun_2025": "Q1 Apr-Jun 2025",
        "Q2_Jul_Sep_2025": "Q2 Jul-Sep 2025",
        "Q3_Oct_Dec_2025": "Q3 Oct-Dec 2025",
        "Q4_Jan_Mar_2026": "Q4 Jan-Mar 2026",
    }
    order = list(labels)
    canonical = canonical.set_index("period_name").loc[order]
    structural = structural.set_index("period_name").loc[order]
    x = np.arange(len(order))
    width = 0.38
    fig, axis = plt.subplots(figsize=(13, 7))
    axis.bar(
        x - width / 2,
        canonical["annual_agreement_share"],
        width,
        label="Canonical persistence vs annual",
        color="#20639b",
    )
    axis.bar(
        x + width / 2,
        structural["agreement_with_annual_share"],
        width,
        label="Structural recurrence vs annual",
        color="#ed9f44",
    )
    axis.set_ylim(0, 1.05)
    axis.set_xticks(x, [labels[value] for value in order], rotation=28, ha="right")
    axis.set_ylabel("Agreement with annual profile")
    axis.set_title("Temporal robustness of the annual access-pressure profiles")
    axis.legend(frameon=False)
    axis.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    destination = ROOT / "outputs/figures/temporal_robustness_summary.png"
    fig.savefig(destination, dpi=220, bbox_inches="tight")
    plt.close(fig)
    print(destination)


def build_inbound_profile_comparison() -> None:
    """Regenerate the matched 14- versus 17-feature profile heatmap from included matrices."""
    apply_figure_style()
    config = load_config(ROOT / "configs" / "reference_apr2025_mar2026.json")
    source = (
        config.resolve(config.input_directory) / config.specification("cbt_inbound_17").source_file
    )
    frame = read_contract_csv(source)
    comparison = compare_inbound_models(frame, config)
    assignments = comparison.assignments
    panels = [
        (
            "national_14",
            "national_14_raw",
            "14-feature matched control",
        ),
        (
            "cbt_inbound_17",
            "cbt_inbound_17_aligned_to_national_14",
            "17-feature CBT inbound sensitivity",
        ),
    ]
    figure, axes = plt.subplots(1, 2, figsize=(18, 12), constrained_layout=True)
    image = None
    for axis, (specification, label_column, title) in zip(axes, panels, strict=True):
        prepared = comparison.prepared[specification]
        values = pd.DataFrame(prepared.matrix, columns=prepared.feature_names)
        values["profile"] = assignments[label_column].to_numpy()
        medians = values.groupby("profile").median().reindex([1, 2, 3]).T
        image = axis.imshow(medians, cmap="coolwarm", vmin=-1, vmax=1, aspect="auto")
        for row in range(len(medians)):
            for column in range(3):
                value = medians.iloc[row, column]
                axis.text(
                    column,
                    row,
                    f"{value:.2f}",
                    ha="center",
                    va="center",
                    color="white" if abs(value) > 0.45 else "#222222",
                    fontsize=8,
                )
        axis.set_xticks(range(3), [f"Profile {value}" for value in (1, 2, 3)])
        axis.set_yticks(
            range(len(medians)),
            [_feature_label(name) for name in medians.index],
            fontsize=8,
        )
        axis.set_title(title)
    assert image is not None
    colour_bar = figure.colorbar(image, ax=axes, fraction=0.025, pad=0.025)
    colour_bar.set_label("Median robust-scaled value")
    figure.suptitle("Matched access-activity profiles before and after CBT inbound evidence")
    destination = ROOT / "outputs/figures/telephone_inbound_profile_comparison.png"
    figure.savefig(destination, dpi=220, bbox_inches="tight", facecolor="white")
    plt.close(figure)
    print(destination)


def main() -> None:
    build_national_profile_figure()
    build_icb_composition_map()
    build_temporal_summary()
    build_inbound_profile_comparison()


if __name__ == "__main__":
    main()
