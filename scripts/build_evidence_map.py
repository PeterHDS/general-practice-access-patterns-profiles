"""Generate the static evidence map from the canonical 42-claim authority."""

# ruff: noqa: E501

from __future__ import annotations

import csv
import html
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLAIMS = ROOT / "outputs" / "tables" / "claim_to_evidence_matrix.csv"
POPULATION = ROOT / "outputs" / "tables" / "population_scope_register.csv"
PRESENTATION = ROOT / "outputs" / "tables" / "evidence_map_presentation.csv"
DOMAIN_SUMMARY = ROOT / "outputs" / "tables" / "evidence_domain_summary.csv"
OUTPUT_DIR = ROOT / "docs" / "evidence-map"
HTML_OUTPUT = OUTPUT_DIR / "index.html"
MARKDOWN_OUTPUT = ROOT / "docs" / "evidence-map.md"

DOMAIN_ORDER = ["ACCESS", "PATIENT_EXPERIENCE", "WORKLOAD", "EQUITY", "SAFETY", "VALUE"]
DOMAIN_LABELS = {
    "ACCESS": "Access",
    "PATIENT_EXPERIENCE": "Patient experience",
    "WORKLOAD": "Workload",
    "EQUITY": "Equity",
    "SAFETY": "Safety",
    "VALUE": "Value",
}
DOMAIN_QUESTIONS = {
    "ACCESS": "What do recorded activity patterns and their robustness show?",
    "PATIENT_EXPERIENCE": "How do fixed profiles relate to reported patient experience?",
    "WORKLOAD": "What can recorded activity and workforce context say about workload?",
    "EQUITY": "Which practice-level inequalities can be examined with available context?",
    "SAFETY": "Which safety claims require linked outcomes or pathway evidence?",
    "VALUE": "Which value claims require cost and outcome evidence?",
}
SUPPORT_ORDER = [
    "DESCRIPTIVELY_SUPPORTED",
    "ASSOCIATIVELY_EXAMINABLE",
    "PARTIALLY_SUPPORTABLE_WITH_MAJOR_QUALIFICATION",
    "NOT_SUPPORTABLE_WITH_CURRENT_PUBLIC_DATA",
]
SUPPORT_LABELS = {
    "DESCRIPTIVELY_SUPPORTED": "Descriptively supported",
    "ASSOCIATIVELY_EXAMINABLE": "Associatively examinable",
    "PARTIALLY_SUPPORTABLE_WITH_MAJOR_QUALIFICATION": "Major qualification required",
    "NOT_SUPPORTABLE_WITH_CURRENT_PUBLIC_DATA": "Additional evidence required",
}
SUPPORT_SYMBOLS = {
    "DESCRIPTIVELY_SUPPORTED": "●",
    "ASSOCIATIVELY_EXAMINABLE": "◆",
    "PARTIALLY_SUPPORTABLE_WITH_MAJOR_QUALIFICATION": "▲",
    "NOT_SUPPORTABLE_WITH_CURRENT_PUBLIC_DATA": "○",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def population_scope(row: dict[str, str]) -> tuple[str, str]:
    cohort = row["relevant_cohort"]
    if "1,456" in cohort:
        return (
            "Directly represents the 1,456-practice outcome-complete CBT cohort; selection is strongly concentrated geographically.",
            "outputs/tables/cbt_outcome_cohort_flow.csv;outputs/tables/cbt_outcome_selection_continuous.csv;outputs/tables/cbt_outcome_selection_categorical.csv",
        )
    if "3,020" in cohort:
        return (
            "Directly represents the 3,020-practice CBT inbound cohort; evidence availability is geographically concentrated.",
            "outputs/tables/cbt_inbound_cohort_flow.csv;outputs/tables/cbt_inbound_selection_continuous.csv;outputs/tables/cbt_inbound_selection_categorical.csv",
        )
    if "5,924" in cohort or "5,677" in cohort:
        return (
            "Directly represents the stated shorter-period calculable cohort; it is smaller than the 6,067-practice annual population.",
            "outputs/tables/temporal_canonical_period_metrics.csv;outputs/tables/temporal_structural_period_metrics.csv",
        )
    if "42 ICB" in cohort:
        return (
            "Represents the 6,067 national practices aggregated across 42 March 2026 ICB organisations.",
            "qgis/data/icb_profile_mapping_layer.geojson;outputs/maps/icb_profile_composition.png",
        )
    if cohort == "No valid analytical cohort for this construct":
        return (
            "No valid analytical cohort exists for this construct in the available evidence.",
            "outputs/tables/claim_to_evidence_matrix.csv",
        )
    if row["primary_claim_domain"] in {"PATIENT_EXPERIENCE", "WORKLOAD", "EQUITY"}:
        return (
            "Uses the measure-specific valid practice population recorded in the claim authority.",
            "outputs/tables/evidence_availability_summary.csv;outputs/tables/numeric_profile_descriptive_summary.csv",
        )
    return (
        "Directly represents the 6,067 practices in the national analytical cohort unless the claim records a narrower valid population.",
        "outputs/tables/national_profile_assignments.csv;outputs/tables/national_profile_quality.csv;outputs/tables/national_cohort_flow.csv",
    )


def build_presentation_rows(claims: list[dict[str, str]]) -> list[dict[str, str]]:
    rows = []
    for claim in claims:
        scope, paths = population_scope(claim)
        support = claim["support_category"]
        rows.append(
            {
                "claim_id": claim["claim_id"],
                "domain": claim["primary_claim_domain"],
                "domain_label": DOMAIN_LABELS[claim["primary_claim_domain"]],
                "support_category": support,
                "support_label": SUPPORT_LABELS[support],
                "support_symbol": SUPPORT_SYMBOLS[support],
                "population_scope_note": scope,
                "repository_evidence_paths": paths,
            }
        )
    return rows


def write_csv(path: Path, rows: list[dict[str, str]], columns: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def build_domain_summary(claims: list[dict[str, str]]) -> list[dict[str, str | int]]:
    counts: dict[str, Counter[str]] = defaultdict(Counter)
    for claim in claims:
        counts[claim["primary_claim_domain"]][claim["support_category"]] += 1
    rows = []
    for domain in DOMAIN_ORDER:
        row: dict[str, str | int] = {
            "domain": domain,
            "domain_label": DOMAIN_LABELS[domain],
            "question_addressed": DOMAIN_QUESTIONS[domain],
            "claim_count": sum(counts[domain].values()),
        }
        row.update({category.lower(): counts[domain][category] for category in SUPPORT_ORDER})
        rows.append(row)
    return rows


def evidence_links(paths: str) -> str:
    links = []
    for path in paths.split(";"):
        label = Path(path).name
        links.append(f'<a href="../../{html.escape(path)}">{html.escape(label)}</a>')
    return ", ".join(links)


def build_html(
    claims: list[dict[str, str]],
    presentation: list[dict[str, str]],
    summaries: list[dict[str, str | int]],
) -> str:
    display = {row["claim_id"]: row for row in presentation}
    summary_cards = []
    for row in summaries:
        breakdown = ", ".join(
            f"{SUPPORT_LABELS[category]}: {row[category.lower()]}"
            for category in SUPPORT_ORDER
            if row[category.lower()]
        )
        summary_cards.append(
            f'<section class="domain-summary"><h2>{html.escape(str(row["domain_label"]))}</h2>'
            f"<p>{html.escape(str(row['question_addressed']))}</p>"
            f"<p><strong>{row['claim_count']} claims.</strong> {html.escape(breakdown)}.</p></section>"
        )
    claim_cards = []
    for claim in claims:
        meta = display[claim["claim_id"]]
        searchable = " ".join(
            claim.get(field, "")
            for field in (
                "claim_id",
                "proposed_claim",
                "exact_construct_observed",
                "source_datasets",
                "relevant_cohort",
                "key_evidence_result",
                "permitted_wording",
            )
        ).casefold()
        claim_cards.append(
            f'''<article class="claim-card" data-domain="{html.escape(meta["domain"])}" data-support="{html.escape(meta["support_category"])}" data-search="{html.escape(searchable)}">
  <header><span class="claim-id">{html.escape(claim["claim_id"])}</span><span class="support support-{html.escape(meta["support_category"].lower())}">{meta["support_symbol"]} {html.escape(meta["support_label"])}</span></header>
  <h2>{html.escape(claim["proposed_claim"])}</h2>
  <p><strong>Observed construct:</strong> {html.escape(claim["exact_construct_observed"])}</p>
  <p><strong>Population:</strong> {html.escape(claim["relevant_cohort"])}</p>
  <p class="scope"><strong>Population scope:</strong> {html.escape(meta["population_scope_note"])}</p>
  <details><summary>Evidence, wording and limits</summary>
    <dl>
      <dt>Source datasets</dt><dd>{html.escape(claim["source_datasets"])}</dd>
      <dt>Method</dt><dd>{html.escape(claim["methods_actually_used"])}</dd>
      <dt>Main result</dt><dd>{html.escape(claim["key_evidence_result"])}</dd>
      <dt>Permitted wording</dt><dd>{html.escape(claim["permitted_wording"])}</dd>
      <dt>Prohibited wording</dt><dd>{html.escape(claim["prohibited_wording"])}</dd>
      <dt>Uncertainty and bias</dt><dd>{html.escape(claim["uncertainty"])} {html.escape(claim["main_bias_risks"])}</dd>
      <dt>Additional evidence</dt><dd>{html.escape(claim["additional_data_needed"])}</dd>
      <dt>Repository evidence</dt><dd>{evidence_links(meta["repository_evidence_paths"])}</dd>
    </dl>
  </details>
</article>'''
        )
    options = "".join(
        f'<option value="{domain}">{html.escape(DOMAIN_LABELS[domain])}</option>'
        for domain in DOMAIN_ORDER
    )
    support_options = "".join(
        f'<option value="{category}">{html.escape(SUPPORT_LABELS[category])}</option>'
        for category in SUPPORT_ORDER
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>GPAP² Evidence Map</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
<a class="skip-link" href="#claims">Skip to claims</a>
<main>
  <header class="page-header">
    <p class="eyebrow">GPAP² research evidence</p>
    <h1>Evidence Map</h1>
    <p>Explore 42 claims across six domains. Each entry links the proposed interpretation to its population, method, evidence status and wording boundary.</p>
    <nav aria-label="Evidence downloads"><a href="../../outputs/tables/claim_to_evidence_matrix.csv">Download the canonical claim authority</a> · <a href="../evidence-map.md">Read the text version</a> · <a href="../population-and-generalisability.md">Understand population scope</a></nav>
  </header>
  <section class="domain-grid" aria-label="Evidence domain summary">{"".join(summary_cards)}</section>
  <section class="controls" aria-label="Filter claims">
    <label for="search">Search claims<input id="search" type="search" autocomplete="off"></label>
    <label for="domain">Domain<select id="domain"><option value="">All domains</option>{options}</select></label>
    <label for="support">Evidence status<select id="support"><option value="">All statuses</option>{support_options}</select></label>
    <button id="clear" type="button">Clear filters</button>
  </section>
  <p id="count" aria-live="polite">42 claims shown</p>
  <section id="claims" class="claim-grid" aria-label="Claims">{"".join(claim_cards)}</section>
  <p id="empty" hidden>No claims match the selected filters.</p>
</main>
<script src="app.js"></script>
</body>
</html>
"""


def build_markdown(claims: list[dict[str, str]], presentation: list[dict[str, str]]) -> str:
    display = {row["claim_id"]: row for row in presentation}
    lines = [
        "# GPAP² Evidence Map",
        "",
        "This text view presents the same 42 claims as the interactive evidence map. The canonical machine-readable authority is [`claim_to_evidence_matrix.csv`](../outputs/tables/claim_to_evidence_matrix.csv).",
        "",
    ]
    for domain in DOMAIN_ORDER:
        lines.extend([f"## {DOMAIN_LABELS[domain]}", "", DOMAIN_QUESTIONS[domain], ""])
        for claim in (item for item in claims if item["primary_claim_domain"] == domain):
            meta = display[claim["claim_id"]]
            lines.extend(
                [
                    f"### {claim['claim_id']}: {claim['proposed_claim']}",
                    "",
                    f"- **Evidence status:** {meta['support_symbol']} {meta['support_label']}",
                    f"- **Observed construct:** {claim['exact_construct_observed']}",
                    f"- **Population:** {claim['relevant_cohort']}",
                    f"- **Population scope:** {meta['population_scope_note']}",
                    f"- **Method:** {claim['methods_actually_used']}",
                    f"- **Main result:** {claim['key_evidence_result']}",
                    f"- **Permitted wording:** {claim['permitted_wording']}",
                    f"- **Prohibited wording:** {claim['prohibited_wording']}",
                    f"- **Additional evidence required:** {claim['additional_data_needed']}",
                    "",
                ]
            )
    return "\n".join(lines)


def main() -> None:
    claims = read_csv(CLAIMS)
    if len(claims) != 42:
        raise ValueError(f"Expected 42 claims, found {len(claims)}")
    if set(DOMAIN_ORDER) != {row["primary_claim_domain"] for row in claims}:
        raise ValueError("The six expected primary claim domains are not present")
    if set(SUPPORT_ORDER) != {row["support_category"] for row in claims}:
        raise ValueError("Unexpected evidence support categories")
    if not POPULATION.is_file():
        raise FileNotFoundError(POPULATION)

    presentation = build_presentation_rows(claims)
    summaries = build_domain_summary(claims)
    write_csv(PRESENTATION, presentation, list(presentation[0]))
    write_csv(DOMAIN_SUMMARY, summaries, list(summaries[0]))
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    HTML_OUTPUT.write_text(build_html(claims, presentation, summaries), encoding="utf-8")
    MARKDOWN_OUTPUT.write_text(build_markdown(claims, presentation), encoding="utf-8")
    print("Built the 42-claim evidence map and machine-readable presentation layer")


if __name__ == "__main__":
    main()
