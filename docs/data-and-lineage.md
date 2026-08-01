# Data and lineage

## Repository boundary

[PCADI](https://github.com/PeterHDS/pcadi-data-integration) owns NHS source acquisition guidance, source schemas, SQL joins, practice-month integration, missingness rules, annual cohort construction and the three modelling matrices. GPAP² owns modelling-input validation, preprocessing, clustering, robustness, contextual linkage, mapping and evidence-ready interpretation.

The reference matrices are pinned to PCADI tag [`reference-apr2025-mar2026`](https://github.com/PeterHDS/pcadi-data-integration/releases/tag/reference-apr2025-mar2026) and commit `1239c63356acfb824277ee6fbaee25fa8df51313`. Moving `main` URLs are not used for analytical acquisition.

## Reference contracts

| Contract | Shape | SHA-256 |
|---|---:|---|
| National OCS-GPAD matrix | 6,067 x 15 | `C50B14AA191C54C29201DC9909E138395C1A2AEA7F596E8CF6B02F43A6DD7EBF` |
| CBT inbound matrix | 3,020 x 18 | `CCC179B870BBD3EC46DD1B75868DB38156FE23A44BBC5A8FF698505FC9B63ED5` |
| CBT outcome-complete matrix | 1,456 x 22 | `D3D2E70C1A718260DD332B59F835EB6316826677A1DF5CEB928ED563C0FC1021` |

The first column is `practice_code_standardised`. Every remaining column is numeric. The identifier stays attached to outputs for traceability and never enters a numerical model.

## National feature contract

| Family | Features |
|---|---|
| OCS volume and composition | submissions per 1,000 registered patient-months; clinical share; administrative share |
| GPAD volume and attendance | appointments per 1,000 registered patient-months; DNA share |
| GPAD mode | face-to-face share; telephone share |
| GPAD booking interval | same day; 1 day; 2 to 7 days; 8 to 14 days; over 14 days |
| Variation | mean absolute monthly rate change for OCS and GPAD |

The published one-day and two-to-seven-day booking intervals remain separate. The obsolete combined one-to-seven-day feature is rejected by the contract validator.

## Population denominators

PCADI calculates annual rates from validated monthly registered-patient counts. GPAP² inherits those rates without recalculation. Shares use documented source-family denominators rather than a combined OCS-GPAD total.

## Larger downstream masters

Two full local research masters support later analysis but are not required to execute the compact public route:

- a 6,067 x 148 organisationally enriched profile master, SHA-256 `E94F50D98E9E4AB2F6B83E8F4A136DA47DDA9516C0CB061E764A3A5FBE747596`;
- a 6,067 x 194 temporal master, SHA-256 `3271053E206E81BCC87DEFC842E0B75CB8DCAACE6F16BF1F65934F1343AAC454`.

Selected publication-safe summaries and their checksums are included. The full masters can be supplied as separately governed release assets if approved.
