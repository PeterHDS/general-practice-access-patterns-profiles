# Analytical evidence

This directory contains selected machine-readable objects used to inspect and reproduce the GPAP² findings.

- `tables/` contains profile assignments and summaries, model-selection evidence, cohort-selection audits, temporal and telephone comparisons, contextual results, the population scope register and the canonical 42-claim authority.
- `figures/` contains selected national, population, telephone, temporal, contextual and evidence-readiness figures.
- `maps/` contains rendered geographic summaries.
- `validation/` records checksums, lineage, figure provenance and execution checks.

`validation/figure_provenance.csv` gives every image's source table, generator where available, source checksum, analytical period, geography and alternative text. Images fall into four reproducibility classes: recomputed from included matrices, regenerated from included authority tables, checksum-validated frozen authorities, and QGIS-rendered outputs.

Raw NHS downloads, respondent-level survey records, large resampling arrays and working databases are governed by their source repositories or reproducibility releases rather than duplicated here.
