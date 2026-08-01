# Analytical roadmap

GPAP² follows one cumulative route from checksum-verified annual practice matrices to bounded interpretation. Every stage inherits the decisions and contracts established earlier.

## Validate the modelling interface

PCADI supplies one national OCS-GPAD matrix and two nested CBT matrices. GPAP² checks exact filenames, byte sizes, SHA-256 checksums, dimensions, feature order, numeric validity, unique practice codes, booking-feature semantics, cohort nesting and inherited national values.

## Justify and reproduce the national profile model

The model-role register makes the fourteen-feature K-Means model the national benchmark; alternative algorithms and feature specifications remain robustness evidence. Four high-skew activity and change measures receive `log1p`. All fourteen features are scaled by their medians and interquartile ranges. K-Means uses three clusters, 100 initialisations, a maximum of 500 iterations, seed 2026 and the Lloyd algorithm. Labels are aligned to the frozen public profile numbers and must reproduce all 6,067 assignments exactly.

## Define profiles and assignment uncertainty

The three profiles receive neutral recorded-activity descriptions. Practice-level silhouette values, GMM posterior evidence, retention and algorithm disagreement remain attached so the hard partition is not mistaken for uniform certainty.

## Test the robustness envelope

Retained-specification, algorithm and assignment-uncertainty evidence establish the general robustness boundary. Telephone and temporal analyses add parallel sensitivity evidence within that boundary.

### CBT inbound and outcome evidence

CBT reporting creates nested evidence-availability cohorts. A 3,020-practice comparison tests three inbound-call features. A 1,456-practice comparison tests complete recorded telephone outcomes. The preferred outcome sensitivity uses three NHS-aligned ILR coordinates for the four positive outcome shares. The raw 21-feature model remains a representation comparator.

### Temporal persistence within the year

Checksum-verified half-year and quarterly authorities show how shorter windows relate to the annual model. The annual model remains the reference because shorter windows reduce the calculable cohort and introduce assignment variability.

## Inspect external context

Frozen profile assignments are linked to selected practice-level public evidence for patient experience, workforce, registered population, deprivation, rurality and March 2026 organisational geography. Associations are descriptive and preserve measure-specific denominators.

## Examine geography and system distribution

The portable QGIS project shows within-ICB profile composition and assignment-caution shares across 42 March 2026 ICB organisations. It uses April 2023 ONS boundaries and preserves the distinction between practice composition, patient prevalence and system performance.

## Translate evidence readiness

Claims are linked to their empirical sources, cohorts, limitations and prohibited interpretations. This prevents a profile label from being treated as a patient pathway, performance ranking or causal mechanism.
