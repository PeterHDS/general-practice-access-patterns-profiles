# Temporal robustness

The national profiles summarise twelve complete months from April 2025 to March 2026. Temporal tests ask whether similar structures recur when the period is shortened.

## Half-year comparison

The common half-year cohort contains 5,924 practices. Canonically aligned H1 and H2 solutions agree for 80.32% of practices, with adjusted Rand index 0.4964. Seeded resampling is strong within each window: median reference agreement is 0.9602 for April to September and 0.9680 for October to March.

## Quarterly comparison

The common quarterly cohort contains 5,677 practices. All-quarter assignment persistence is 54.92% under canonical alignment and 63.91% under structural alignment. The April-to-June window is the clearest diagnostic exception and is sensitive to the treatment of variation features.

![Agreement of half-year and quarterly profiles with the annual national model](../outputs/figures/temporal_robustness_summary.png)

## Decision

Shorter windows contain useful movement information but add assignment variability and reduce calculable cohort size. The twelve-month model remains the national descriptive anchor. Temporal results are robustness evidence, not replacement cluster labels.
