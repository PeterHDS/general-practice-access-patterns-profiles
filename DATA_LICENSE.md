# Data, figure and map reuse register

The MIT licence covers project code only. Original narrative documentation is covered by
[CC BY 4.0](DOCUMENTATION_LICENSE.md). Data-derived files retain the rights and attribution
requirements of their source material. This register identifies what is redistributed, what GPAP²
changed, and the wording that should accompany reuse.

## Required source attributions

For adapted NHS England information:

> Contains information from NHS England, licenced under the current version of the Open Government Licence.

For the ONS digital boundary geometry and every rendered map that uses it:

> Source: Office for National Statistics licensed under the Open Government Licence v.3.0
>
> Contains OS data © Crown copyright and database right 2026

## File-family register

| Public file family | Source organisation and publication | Source period | Licence or reuse terms | Project modification | Redistribution status and attribution |
|---|---|---|---|---|---|
| `data/reference/primary_practice_access_clustering_matrix.csv` | [PCADI reference release](https://github.com/PeterHDS/pcadi-data-integration/releases/tag/reference-apr2025-mar2026), derived from NHS England OCS and GPAD publications | 1 April 2025 to 31 March 2026 | NHS England content under the current [Open Government Licence](https://digital.nhs.uk/about-nhs-digital/terms-and-conditions); PCADI provenance and contract also apply | Annual practice features selected and validated upstream; unchanged in GPAP² | Included. Retain PCADI provenance and the NHS England attribution above. |
| `data/reference/cbt_inbound_sensitivity_clustering_matrix_17_features.csv` | PCADI reference release, derived from NHS England OCS, GPAD and Cloud Based Telephony publications | 1 April 2025 to 31 March 2026 | Same NHS England and PCADI terms | Restricted reporting cohort and annual features constructed upstream; unchanged in GPAP² | Included. Retain PCADI provenance and NHS England attribution. |
| `data/reference/cbt_outcomes_sensitivity_clustering_matrix_21_features.csv` | PCADI reference release, derived from NHS England OCS, GPAD and Cloud Based Telephony publications | 1 April 2025 to 31 March 2026 | Same NHS England and PCADI terms | Outcome-complete cohort and annual features constructed upstream; unchanged in GPAP² | Included. Retain PCADI provenance and NHS England attribution. |
| `outputs/tables/national_profile_assignments.csv`, telephone assignment tables and analytical summaries | Project-created analysis of the three PCADI matrices | 1 April 2025 to 31 March 2026 | Project analytical expression under CC BY 4.0; source facts remain under NHS England OGL terms | Preprocessing, clustering, label alignment, comparisons and aggregation documented in code and notebooks | Included. Cite GPAP² and retain PCADI and NHS England attribution where source measures are reproduced. |
| GP Patient Survey summaries in `outputs/tables/` and related figures | [NHS England GP Patient Survey 2026](https://www.england.nhs.uk/statistics/statistical-work-areas/patient-surveys/gp-patient-survey/), published by Ipsos on behalf of NHS England | Survey fieldwork 2 January to 13 April 2026; publication 9 July 2026 | NHS England content under the current OGL except where the source marks third-party rights | Practice estimates linked to fixed profiles and summarised; no respondent records redistributed | Derived summaries included. Use the NHS England attribution and cite the GP Patient Survey 2026. |
| Workforce summaries in `outputs/tables/` | [NHS England General Practice Workforce, 31 March 2026](https://digital.nhs.uk/data-and-information/publications/statistical/general-and-personal-medical-services/31-march-2026) | 31 March 2026 | NHS England content under the current OGL | Practice-level workforce measures standardised, linked and aggregated to profile summaries | Derived summaries included. Use the NHS England attribution. |
| Registered-population summaries in `outputs/tables/` | [NHS England Patients Registered at a GP Practice, March 2026](https://digital.nhs.uk/data-and-information/publications/statistical/patients-registered-at-a-gp-practice/march-2026) | March 2026 | NHS England content under the current OGL | Practice totals and age composition linked to fixed profiles and summarised | Derived summaries included. Use the NHS England attribution. |
| Deprivation summaries in `outputs/tables/` | [Ministry of Housing, Communities and Local Government, English Indices of Deprivation 2025](https://www.gov.uk/government/statistics/english-indices-of-deprivation-2025), corrected files published 17 November 2025 | English Indices of Deprivation 2025 | Crown copyright information under the [Open Government Licence v3.0](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/) unless otherwise stated | Corrected LSOA information aggregated to patient-weighted practice context, then summarised by profile | Derived summaries included. Attribute MHCLG and the English Indices of Deprivation 2025 under OGL v3.0. |
| Rurality summaries in `outputs/tables/` | [Office for National Statistics, 2021 Rural Urban Classification](https://www.ons.gov.uk/methodology/geography/geographicalproducts/ruralurbanclassifications/2021ruralurbanclassification) | 2021 classification; source page updated 31 March 2026 | ONS information under OGL v3.0; source-specific third-party notices remain applicable | LSOA classification aggregated to patient-weighted practice context, then summarised by profile | Derived summaries included. Use `Source: Office for National Statistics licensed under the Open Government Licence v.3.0`. |
| `qgis/data/icb_profile_mapping_layer_publication_safe.geojson` | ONS April 2023 ICB digital boundaries plus March 2026 NHS organisational reference and GPAP² profile aggregates | April 2023 boundary vintage; 31 March 2026 organisations | [ONS digital-boundary licence](https://www.ons.gov.uk/methodology/geography/licences): OGL v3.0 with mandatory OS statement | Audited organisation crosswalk, profile counts and shares added; small cells suppressed; geometry retained | Included. Both exact ONS and OS statements above are mandatory. |
| `qgis/GPAP2_Digital_GP_Access_Profiles_March_2026.qgz`, `qgis/previews/` and `outputs/maps/` | Project-created cartography using the redistributed ONS geometry and derived profile aggregates | Same as boundary and analysis metadata recorded in the project | Project layout and documentation under CC BY 4.0; embedded data retain ONS, OS and NHS England terms | Styling, layouts, legends, captions and publication-safe suppression | Included. Both exact ONS and OS statements above are mandatory on or immediately adjacent to map products. |
| Project-created code in `src/`, `scripts/`, `tests/` and `qgis/scripts/` | Peter Oluwatimilehin | 2026 | [MIT](LICENSE) | Original implementation and validation code | Included under MIT. Data obtained or produced by running the code are not automatically relicensed under MIT. |
| Project-created documentation in `README.md`, `docs/`, `notebooks/` narrative cells and `references/` | Peter Oluwatimilehin | 2026 | [CC BY 4.0](DOCUMENTATION_LICENSE.md) | Original explanatory and methodological writing | Included under CC BY 4.0, subject to retained third-party source quotations and attributions. |
| Project-created figures and non-map tables in `outputs/` | Peter Oluwatimilehin, derived from the sources listed above | Reference periods stated in each source table or figure provenance row | Project analytical expression under CC BY 4.0; underlying source rights retained | Selected aggregates, comparisons and visual encodings | Included. Cite GPAP² and retain the source-family attributions recorded in `outputs/validation/figure_provenance.csv`. |

Raw NHS publication archives, respondent-level GPPS data, the large external-context masters and
the PCADI working database are not redistributed in this repository. Source acquisition routes are
listed in [`references/official-sources.md`](references/official-sources.md), and analytical lineage is
documented in [`docs/data-and-lineage.md`](docs/data-and-lineage.md).
