# Selected analytical evidence

This directory contains the smallest set of publication-safe objects needed to inspect the public analytical story.

- `tables/` holds profile summaries, robustness results, evidence availability and claim authority.
- `figures/` holds selected national, telephone, temporal and contextual figures.
- `maps/` holds selected rendered geographic previews.
- `validation/` records checksums and public-build gates.

`validation/figure_provenance.csv` classifies every public image as matrix-recomputed,
authority-table regenerated, checksum-validated frozen authority, or QGIS-rendered output. A blank
generator is intentional only where exact regeneration would require excluded practice-level or
resampling data; the included checksum and aggregate source tables remain the inspection route.

Full raw NHS downloads, large assignment manifests, resampling manifests and private development notebooks remain outside Git.
