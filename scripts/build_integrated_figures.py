"""Build the v1 synthesis figures from included frozen authority tables."""

# ruff: noqa: E501

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gpap2.visual_style import (  # noqa: E402
    INK,
    MUTED,
    SUPPORT_COLOURS,
    apply_figure_style,
    finish_axis,
)

FIGURE_DIR = ROOT / "outputs" / "figures"


def _save(figure: plt.Figure, stem: str) -> None:
    for suffix in ("png", "svg"):
        output = FIGURE_DIR / f"{stem}.{suffix}"
        figure.savefig(
            output,
            dpi=220 if suffix == "png" else None,
            bbox_inches="tight",
            facecolor="white",
        )
        if suffix == "svg":
            text = output.read_text(encoding="utf-8")
            output.write_text(
                "\n".join(line.rstrip() for line in text.splitlines()) + "\n",
                encoding="utf-8",
            )
    plt.close(figure)


def build_model_selection_figure() -> None:
    apply_figure_style()
    tables = ROOT / "outputs" / "tables"
    evidence = pd.read_csv(tables / "national_model_selection_summary.csv").set_index(
        "candidate_key"
    )
    stability = pd.read_csv(tables / "national_confirmatory_stability_summary.csv").set_index(
        "model_id"
    )
    candidates = ["km14", "ward14", "gmm14s", "km12"]
    labels = [
        "K-Means\n14 features",
        "Ward\n14 features",
        "Spherical GMM\n14 features",
        "K-Means\n12 features",
    ]
    stability_ids = [
        "km14_k3_robust",
        "ward14_k3_robust",
        "gmm14_spherical_k3_robust",
        "km12_no_ocs_k3_robust",
    ]
    colours = ["#0072B2", "#CC79A7", "#009E73", "#E69F00"]

    figure, axes = plt.subplots(1, 3, figsize=(16, 5.7), constrained_layout=True)
    panels = [
        (
            axes[0],
            evidence.loc[candidates, "exact_silhouette"].to_numpy(),
            "Full-data silhouette",
            "Mean silhouette",
        ),
        (
            axes[1],
            stability.loc[stability_ids, "reference_ari_median"].to_numpy(),
            "Repeated-sample recovery",
            "Median ARI to full-data solution",
        ),
        (
            axes[2],
            evidence.loc[candidates, "aligned_agreement_vs_primary_kmeans14"].to_numpy(),
            "Agreement with selected model",
            "Aligned practice agreement",
        ),
    ]
    for axis, values, title, ylabel in panels:
        bars = axis.bar(np.arange(4), values, color=colours)
        axis.set_xticks(np.arange(4), labels)
        axis.set_ylim(0, 1.05 if values.max() > 0.5 else max(values) * 1.28)
        axis.set_ylabel(ylabel)
        axis.set_title(title, loc="left")
        finish_axis(axis, grid_axis="y")
        for bar, value in zip(bars, values, strict=True):
            axis.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + axis.get_ylim()[1] * 0.025,
                f"{value:.3f}",
                ha="center",
                va="bottom",
                fontsize=9,
            )
    figure.suptitle("Model selection used complementary evidence", fontsize=17, color=INK)
    figure.text(
        0.01,
        -0.03,
        "K-Means k=3 is the selected descriptive partition. Ward tests hierarchical structure; "
        "the spherical GMM supplies probabilistic uncertainty; the 12-feature model tests construct sensitivity.",
        fontsize=9,
        color=MUTED,
    )
    _save(figure, "model_selection_and_uncertainty")


def build_population_selection_figure() -> None:
    apply_figure_style()
    tables = ROOT / "outputs" / "tables"
    stage = pd.read_csv(tables / "cohort_selection_stage_summary.csv")
    continuous_files = [
        "national_selection_continuous.csv",
        "cbt_inbound_selection_continuous.csv",
        "cbt_outcome_selection_continuous.csv",
    ]
    categorical_files = [
        "national_selection_categorical.csv",
        "cbt_inbound_selection_categorical.csv",
        "cbt_outcome_selection_categorical.csv",
    ]
    stage_labels = ["National", "CBT inbound", "CBT outcome-complete"]

    figure, axes = plt.subplots(1, 2, figsize=(15, 6.4), constrained_layout=True)
    y = np.arange(3)
    parent = stage["parent_n"].to_numpy()
    selected = stage["selected_n"].to_numpy()
    comparison = stage["comparison_n"].to_numpy()
    axes[0].barh(y, selected, color="#0072B2", label="Retained")
    axes[0].barh(y, comparison, left=selected, color="#B8B8B8", label="Not carried forward")
    axes[0].set_yticks(y, stage_labels)
    axes[0].invert_yaxis()
    axes[0].set_xlabel("Practices")
    axes[0].set_title("Nested analytical populations", loc="left")
    axes[0].legend(loc="lower right")
    finish_axis(axes[0], grid_axis="x")
    for index, (retained, total) in enumerate(zip(selected, parent, strict=True)):
        axes[0].text(retained / 2, index, f"{retained:,}", ha="center", va="center", color="white")
        axes[0].text(total + 65, index, f"of {total:,}", ha="left", va="center", color=MUTED)

    metrics = []
    for index, (continuous_name, categorical_name) in enumerate(
        zip(continuous_files, categorical_files, strict=True)
    ):
        continuous = pd.read_csv(tables / continuous_name).set_index("analysis_name")
        categorical = (
            pd.read_csv(tables / categorical_name)
            .drop_duplicates("analysis_name")
            .set_index("analysis_name")
        )
        metrics.extend(
            [
                (
                    index,
                    "Practice size",
                    abs(
                        float(
                            continuous.loc[
                                "registered_patients_march_2026", "standardized_mean_difference"
                            ]
                        )
                    ),
                ),
                (
                    index,
                    "Deprivation",
                    abs(
                        float(
                            continuous.loc[
                                "patient_weighted_imd2025_score", "standardized_mean_difference"
                            ]
                        )
                    ),
                ),
                (
                    index,
                    "Rurality",
                    abs(
                        float(
                            continuous.loc[
                                "registered_patients_rural_pct", "standardized_mean_difference"
                            ]
                        )
                    ),
                ),
                (index, "Region", float(categorical.loc["commissioning_region", "cramers_v"])),
                (index, "ICB", float(categorical.loc["icb", "cramers_v"])),
            ]
        )
    metric_frame = pd.DataFrame(metrics, columns=["stage", "measure", "effect"])
    measures = ["Practice size", "Deprivation", "Rurality", "Region", "ICB"]
    marker_map = {
        "Practice size": "o",
        "Deprivation": "s",
        "Rurality": "^",
        "Region": "D",
        "ICB": "P",
    }
    for measure in measures:
        subset = metric_frame.loc[metric_frame["measure"].eq(measure)]
        axes[1].plot(
            subset["stage"],
            subset["effect"],
            marker=marker_map[measure],
            linewidth=1.8,
            label=measure,
        )
    axes[1].set_xticks(range(3), stage_labels)
    axes[1].set_ylim(0, 0.8)
    axes[1].set_ylabel("Absolute SMD or Cramér's V")
    axes[1].set_title("Measured composition differences", loc="left")
    axes[1].legend(ncol=2, loc="upper left")
    finish_axis(axes[1], grid_axis="y")

    figure.suptitle("Population selection changes the scope of telephony evidence", fontsize=17)
    figure.text(
        0.01,
        -0.03,
        "Continuous differences use absolute standardised mean differences; categorical concentration uses Cramér's V. "
        "The measures describe selection, not practice quality.",
        fontsize=9,
        color=MUTED,
    )
    _save(figure, "population_selection_and_generalisability")


def build_evidence_readiness_figure() -> None:
    apply_figure_style()
    claims = pd.read_csv(ROOT / "outputs" / "tables" / "claim_to_evidence_matrix.csv")
    domains = ["ACCESS", "PATIENT_EXPERIENCE", "WORKLOAD", "EQUITY", "SAFETY", "VALUE"]
    labels = ["Access", "Patient\nexperience", "Workload", "Equity", "Safety", "Value"]
    categories = [
        "DESCRIPTIVELY_SUPPORTED",
        "ASSOCIATIVELY_EXAMINABLE",
        "PARTIALLY_SUPPORTABLE_WITH_MAJOR_QUALIFICATION",
        "NOT_SUPPORTABLE_WITH_CURRENT_PUBLIC_DATA",
    ]
    category_labels = [
        "Descriptively supported",
        "Associatively examinable",
        "Major qualification",
        "Additional evidence required",
    ]
    counts = (
        claims.groupby(["primary_claim_domain", "support_category"])
        .size()
        .unstack(fill_value=0)
        .reindex(domains, fill_value=0)
    )
    figure, axis = plt.subplots(figsize=(12.5, 6.4), constrained_layout=True)
    left = np.zeros(len(domains))
    for category, label in zip(categories, category_labels, strict=True):
        values = counts.get(category, pd.Series(0, index=domains)).to_numpy()
        bars = axis.barh(
            np.arange(len(domains)), values, left=left, color=SUPPORT_COLOURS[category], label=label
        )
        for bar, value in zip(bars, values, strict=True):
            if value:
                label_colour = (
                    INK
                    if category
                    in {
                        "ASSOCIATIVELY_EXAMINABLE",
                        "PARTIALLY_SUPPORTABLE_WITH_MAJOR_QUALIFICATION",
                    }
                    else "white"
                )
                axis.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_y() + bar.get_height() / 2,
                    str(int(value)),
                    ha="center",
                    va="center",
                    color=label_colour,
                    fontsize=9,
                )
        left += values
    axis.set_yticks(np.arange(len(domains)), labels)
    axis.invert_yaxis()
    axis.set_xlabel("Claims in the 42-claim authority")
    axis.set_title("Evidence status differs by analytical question", loc="left")
    axis.legend(ncol=2, loc="lower right")
    finish_axis(axis, grid_axis="x")
    figure.suptitle("Evidence readiness across six research domains", fontsize=17)
    figure.text(
        0.01,
        -0.03,
        "Text labels and counts accompany colour. Categories define permitted interpretation; they are not a composite score.",
        fontsize=9,
        color=MUTED,
    )
    _save(figure, "evidence_readiness_overview")


def main() -> None:
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    build_model_selection_figure()
    build_population_selection_figure()
    build_evidence_readiness_figure()


if __name__ == "__main__":
    main()
