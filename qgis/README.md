# Portable QGIS project

Open `GPAP2_Digital_GP_Access_Profiles_March_2026.qgz` in QGIS 3.44 LTR or a compatible later version. The project reads `data/icb_profile_mapping_layer_publication_safe.geojson` through a relative path.

The package contains four styled layers and two print layouts. It maps within-ICB practice-profile composition and assignment-caution share across 42 March 2026 ICB organisations. The analysis covers 1 April 2025 to 31 March 2026 and uses April 2023 ICB boundaries. Small Profile 1 counts below five are suppressed.

The GeoJSON records the analysis period, boundary vintage and organisation reference date separately. Its geography note documents the audited crosswalk and confirms that no post-1-April-2026 remapping was applied.

Boundary attribution:

> Source: Office for National Statistics licensed under the Open Government Licence v.3.0
>
> Contains OS data © Crown copyright and database right 2026

Run `python scripts/validate_qgis_project.py` from this directory to repeat the compact structural validation. The separate runtime record documents the QGIS application used to open the project, resolve its layers and regenerate both previews. See [`docs/geography-and-qgis.md`](../docs/geography-and-qgis.md) for interpretation.
