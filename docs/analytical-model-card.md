# GPAP² analytical model card

## Purpose

GPAP² identifies recurring configurations of recorded online-consultation and appointment activity across general practices in England. It then tests assignment robustness, examines restricted telephone evidence, studies shorter-period recurrence and links fixed profiles to independent contextual evidence.

## Intended analytical use

- describe national practice-level activity configurations;
- compare profile characteristics in original measurement units;
- quantify model, specification and assignment uncertainty;
- test how telephone evidence changes assignments within eligible reporting cohorts;
- examine temporal persistence and recurrence;
- support bounded ecological interpretation using patient experience, workforce, population, deprivation, rurality and geography.

The profiles describe recorded activity configurations. They do not rank care quality or measure total demand, unmet need, workload, resolution, safety or causal effect.

## Population and period

- Geography: general practices in England.
- Observation period: 1 April 2025 to 31 March 2026.
- National analytical population: 6,067 practices from a 6,130-practice complete-source parent.
- CBT inbound sensitivity: 3,020 nationally profiled practices.
- CBT outcome-complete sensitivity: 1,456 inbound-eligible practices.

The [population audit](population-and-generalisability.md) defines the measured selection boundaries.

## National inputs and preprocessing

The national matrix contains one ODS practice identifier and 14 numerical OCS–GPAD features. Four high-skew activity and change measures receive `log1p`; all 14 features are scaled by their median and interquartile range. The identifier remains attached for traceability and is excluded from the numerical model.

## Selected model

- Algorithm: K-Means.
- Clusters: 3.
- Random seed: 2026.
- Initialisations: 100.
- Maximum iterations: 500.
- Algorithm implementation: Lloyd.
- Profile sizes: 1,753; 2,312; 2,002.

## Alternatives and selection evidence

Ward agglomerative clustering, spherical Gaussian mixture models, k alternatives and a 12-feature sensitivity were compared with the selected K-Means model. K-Means k=3 provides the national hard partition; the alternatives remain structural, probabilistic and construct-validity evidence. See [model selection and uncertainty](model-selection-and-uncertainty.md).

## Evaluation and uncertainty

The selected model exactly reproduces the frozen 6,067 assignments. Across 100 common-sample runs, median ARI to the reference is 0.9599, the fifth percentile is 0.9165 and minimum cluster retention is 0.9295. Practice-level silhouette, GMM posterior, retention and cross-algorithm disagreement measures identify less certain assignments without changing them.

## Telephone extensions

The 3,020-practice inbound model adds three call-activity features. It changes 571 assignments relative to its matched 14-feature control (ARI 0.5236; aligned agreement 81.09%).

The 1,456-practice outcome analysis compares a raw 21-feature representation with a preferred 20-feature ILR representation. Four strictly positive outcome shares are represented by three orthonormal balances with no pseudocount. ILR20 changes 52 assignments relative to the outcome-complete 17-feature baseline (ARI 0.8949; aligned agreement 96.43%); raw21 changes 729.

## Temporal evidence

Half-year and quarterly analyses compare shorter-period structures with the annual reference. Direct full-period H1–H2 comparison and repeated common-sample H1–H2 resampling are reported separately. The annual model remains the descriptive anchor.

## External interpretation and geography

Fixed assignments are linked after clustering to independent context. Contextual models and QGIS outputs describe associations and composition; they do not redefine profiles. Geographic maps show the within-ICB composition of practices and assignment-caution shares across 42 March 2026 ICB organisations.

## Evidence readiness

The canonical 42-claim authority classifies the support available for access, patient experience, workload, equity, safety and value claims. The [Evidence Map](evidence-map/index.html) links each claim to its observed construct, population, method, wording boundary and additional evidence requirement. No composite readiness score is produced.

## Reproducibility and version

Version 1.0.0 integrates the closed scientific authorities registered in [reproducibility releases](reproducibility-releases.md). PCADI supplies the validated annual matrices; GPAP² owns modelling-input validation, clustering, robustness and interpretation.
