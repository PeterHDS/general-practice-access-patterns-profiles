# Analytical notebook sequence

The notebooks form one dependency-led analytical sequence. Reusable calculations live in
`src/gpap2`; every notebook states its data and method contract, analytical purpose, result and the evidence it establishes.
The telephone and temporal notebooks contribute parallel evidence to the robustness envelope and
do not falsely imply a computational dependency between those analyses.

1. `01_validate_the_access_profile_inputs.ipynb`
2. `02_select_national_access_pressure_profiles.ipynb`, reproduce and justify the selected national model
3. `03_test_telephone_inbound_evidence.ipynb`
4. `04_test_telephone_outcome_composition.ipynb`
5. `05_assess_temporal_persistence.ipynb`
6. `06_interpret_profiles_with_external_context.ipynb`
7. `07_translate_profiles_into_evidence_readiness.ipynb`

Run `python scripts/fetch_pcadi_inputs.py` before the first four notebooks. The later notebooks read compact authority tables included under `outputs/tables` only after their checksums and schemas pass the authority manifest configured in `configs/reference_apr2025_mar2026.json`.

Run every notebook from a clean kernel with
`python scripts/execute_public_notebooks.py --check`. This executes disposable copies, does not
rewrite tracked notebooks and does not allow stored errors. The maintainer-only
`--write-canonical` mode requires the exact registered environment.
