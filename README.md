# GPAP²: General Practice Access Patterns and Profiles

**Turning fragmented primary-care data into tested evidence about how access is organised across general practice.**

[![Python 3.11 to 3.13](https://img.shields.io/badge/python-3.11%20to%203.13-blue)](pyproject.toml) [![Version 1.0.0](https://img.shields.io/badge/version-1.0.0-0072B2)](CHANGELOG.md) [![Code licence: MIT](https://img.shields.io/badge/code%20licence-MIT-009E73)](LICENSE)

People reach general practice through online requests, appointments and telephone services, but the public data describing those routes are published separately. GPAP² brings these signals together to identify recurring practice-level access patterns across England, test how stable those patterns are, examine who the available evidence represents, and connect the profiles to patient experience, workforce, population and geography.

## What the analysis found

The national analysis covers **6,067 practices** observed from **1 April 2025 to 31 March 2026**. Fourteen OCS and GPAD features describe practice-size-normalised activity, activity composition and month-to-month variation. The selected descriptive model applies the registered transformations and robust scaling before fitting three K-Means profiles.

| Profile | Practices | Neutral description |
|---|---:|---|
| 1 | 1,753 | Lower recorded activity, higher DNA and shorter-delay shares |
| 2 | 2,312 | Higher face-to-face share, longer delay and lower OCS activity |
| 3 | 2,002 | Higher recorded activity, higher same-day share and greater variation |

![Relative profile characteristics and practice-level assignment uncertainty for the three-profile national model](outputs/figures/national_profile_characteristics_and_uncertainty.png)

The model reproduces all 6,067 registered assignments using seed 2026, 100 initialisations, a maximum of 500 iterations and the Lloyd algorithm. K-Means was selected as the stable descriptive partition, not because k=3 was uniquely proved. Ward clustering, a spherical Gaussian mixture model and a 12-feature comparator provide complementary structural, uncertainty and construct-sensitivity evidence. [See the model-selection evidence](docs/model-selection-and-uncertainty.md).

## Who the evidence represents

Evidence availability creates three nested populations:

| Analysis | Parent | Retained | Not carried forward | Direct scope |
|---|---:|---:|---:|---|
| National profiles | 6,130 | 6,067 | 63 | Practices meeting the twelve-month OCS and GPAD contract |
| CBT inbound sensitivity | 6,067 | 3,020 | 3,047 | Practices with matched and complete inbound telephony evidence |
| CBT outcome sensitivity | 3,020 | 1,456 | 1,564 | Practices with complete valid call-outcome composition |

The population audit measures whether retained and non-retained practices differ in observed practice size, deprivation, rurality, region and ICB composition. It defines the population to which each result directly applies; it does not treat missing telephony evidence as zero activity.

![Nested populations and measured composition differences at each evidence boundary](outputs/figures/population_selection_and_generalisability.png)

[Read the population and generalisability account](docs/population-and-generalisability.md) or download the [population scope register](outputs/tables/population_scope_register.csv).

## What can be concluded

The **GPAP² Evidence Map** translates 42 research claims across access, patient experience, workload, equity, safety and value into four evidence states. Each claim records the construct, represented population, evidence source, uncertainty, permitted wording, prohibited wording and additional evidence required.

[Explore the evidence map](docs/evidence-map/index.html) | [Read the text version](docs/evidence-map.md) | [Download the canonical 42-claim authority](outputs/tables/claim_to_evidence_matrix.csv)

![Evidence readiness by research domain and support category](outputs/figures/evidence_readiness_overview.png)

The profiles describe configurations of **recorded practice activity**. They are not performance tiers and do not measure total demand, unmet need, workload, resolution, safety or causal impact.

## Follow the analytical sequence

| Analytical component | Question answered | Main evidence |
|---|---|---|
| Input and population contracts | Are the matrices valid, unique and correctly nested? | [Input validation notebook](notebooks/01_validate_the_access_profile_inputs.ipynb), [population audit](docs/population-and-generalisability.md) |
| National model selection | Which descriptive partition is stable and interpretable? | [National model notebook](notebooks/02_select_national_access_pressure_profiles.ipynb), [model-selection summary](outputs/tables/national_model_selection_summary.csv) |
| Profiles and uncertainty | What characterises each profile, and which assignments are uncertain? | [Profile interpretation](docs/profile-interpretation.md), [uncertainty summary](outputs/tables/national_uncertainty_summary.csv) |
| Robustness and sensitivity | Do algorithms, features, telephony evidence or time windows alter the pattern? | [CBT inbound](notebooks/03_test_telephone_inbound_evidence.ipynb), [CBT outcomes](notebooks/04_test_telephone_outcome_composition.ipynb), [temporal analysis](notebooks/05_assess_temporal_persistence.ipynb) |
| External interpretation | How are profiles associated with patient experience, workforce, deprivation and rurality? | [External-context notebook](notebooks/06_interpret_profiles_with_external_context.ipynb) |
| Geography | How are profiles distributed across 42 March 2026 ICB organisations? | [QGIS project](qgis/README.md), [geography guide](docs/geography-and-qgis.md) |
| Evidence readiness | Which claims are supported, qualified or require more evidence? | [Evidence-readiness notebook](notebooks/07_translate_profiles_into_evidence_readiness.ipynb), [Evidence Map](docs/evidence-map/index.html) |

![The GPAP² analytical sequence from validated inputs to bounded claims](docs/assets/gpap2-roadmap.svg)

## Reproduce the reference analysis

The three matrices are produced by the immutable PCADI tag [`reference-apr2025-mar2026`](https://github.com/PeterHDS/pcadi-data-integration/releases/tag/reference-apr2025-mar2026) at commit `1239c63356acfb824277ee6fbaee25fa8df51313`. The acquisition script downloads each file to a temporary location, verifies its filename, byte size, schema and SHA-256, then installs it atomically.

Windows PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev,notebooks,docs]"
python scripts/fetch_pcadi_inputs.py
python -m gpap2 validate
python scripts/reproduce_primary_profiles.py
python scripts/build_analytical_regression_evidence.py --check
pytest
python scripts/execute_public_notebooks.py --check
python scripts/validate_public_repository.py
python qgis/scripts/validate_qgis_project.py
```

Linux or macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev,notebooks,docs]'
python scripts/fetch_pcadi_inputs.py
python -m gpap2 validate
python scripts/reproduce_primary_profiles.py
python scripts/build_analytical_regression_evidence.py --check
pytest
python scripts/execute_public_notebooks.py --check
python scripts/validate_public_repository.py
python qgis/scripts/validate_qgis_project.py
```

The reference run used Windows 11, Python 3.13.14 and QGIS 3.44.12 LTR. The workflow in [`.github/workflows/ci.yml`](.github/workflows/ci.yml) defines Python 3.11, 3.12 and 3.13 gates with read-only permissions and actions pinned to full commit SHAs.

| Evidence layer | Execution class |
|---|---|
| Input contracts and cohort nesting | Recomputed and validated |
| National clustering and assignments | Recomputed |
| CBT inbound and outcome comparisons | Recomputed |
| Temporal and external context | Validated from frozen authority tables |
| Evidence readiness | Inspected from checksum-controlled scientific authority |
| QGIS maps | Portable project plus structural and runtime evidence |

## Documentation and repository map

- [Analytical roadmap](docs/analytical-roadmap.md)
- [Analytical model card](docs/analytical-model-card.md)
- [Population and generalisability](docs/population-and-generalisability.md)
- [Model selection and uncertainty](docs/model-selection-and-uncertainty.md)
- [Telephone evidence](docs/telephone-evidence.md)
- [Temporal robustness](docs/temporal-robustness.md)
- [External context](docs/external-context.md)
- [Geography and QGIS](docs/geography-and-qgis.md)
- [Evidence readiness](docs/evidence-readiness.md)
- [Data and lineage](docs/data-and-lineage.md)
- [Reproducibility contract](docs/reproducibility.md)
- [Reproducibility releases](docs/reproducibility-releases.md)

| Path | Purpose |
|---|---|
| [`notebooks/`](notebooks/README.md) | Seven executable notebooks following the analytical sequence |
| [`src/gpap2/`](src/gpap2) | Typed configuration, contracts, preprocessing, modelling and validation |
| [`configs/`](configs/reference_apr2025_mar2026.json) | Complete reference-period analytical contract |
| [`data/contracts/`](data/contracts/pcadi_input_contracts.csv) | Immutable PCADI file, schema and provenance contracts |
| [`outputs/`](outputs/README.md) | Selected tables, figures and machine-readable validation evidence |
| [`qgis/`](qgis/README.md) | Portable QGIS project, geographic data, previews and validation |
| [`tests/`](tests) | Unit, schema and analytical regression tests |

## Data boundary, citation and reuse

[PCADI](https://github.com/PeterHDS/pcadi-data-integration) owns NHS source acquisition guidance, SQL integration, practice-month validation and annual matrix construction. GPAP² starts at the validated modelling interface and owns preprocessing, clustering, robustness, contextual linkage, mapping and evidence-ready interpretation. The upstream integration pipeline is referenced rather than duplicated.

Use [`CITATION.cff`](CITATION.cff) for citation metadata. Code is licensed under the [MIT License](LICENSE). Documentation is available under [CC BY 4.0](DOCUMENTATION_LICENSE.md). NHS-derived data and geographic assets retain their source terms; review [data licensing](DATA_LICENSE.md) before redistribution.

GPAP² was developed and is maintained by Peter Oluwatimilehin as an open research and reproducibility resource.
