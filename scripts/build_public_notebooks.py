"""Build the seven analytical notebooks from executable source cells."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS = ROOT / "notebooks"


def markdown(text: str) -> dict:
    return {
        "cell_type": "markdown",
        "id": hashlib.sha1(("markdown:" + text).encode()).hexdigest()[:12],
        "metadata": {},
        "source": text.splitlines(keepends=True),
    }


def code(text: str) -> dict:
    return {
        "cell_type": "code",
        "id": hashlib.sha1(("code:" + text).encode()).hexdigest()[:12],
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": text.splitlines(keepends=True),
    }


SETUP = """from pathlib import Path
import sys

ROOT = Path.cwd()
if ROOT.name == 'notebooks':
    ROOT = ROOT.parent
sys.path.insert(0, str(ROOT / 'src'))
CONFIG_PATH = ROOT / 'configs' / 'reference_apr2025_mar2026.json'
from gpap2.config import load_config
REFERENCE_CONFIG = load_config(CONFIG_PATH)
AUTHORITY_MANIFEST = REFERENCE_CONFIG.resolve(REFERENCE_CONFIG.authority_checksum_file)
import pandas as pd
pd.set_option('display.max_columns', 50)
pd.set_option('display.width', 120)
pd.set_option('display.precision', 6)
"""


def write(name: str, cells: list[dict]) -> None:
    notebook = {
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3.13.14"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    (NOTEBOOKS / name).write_text(
        json.dumps(notebook, indent=1),
        encoding="utf-8",
        newline="\n",
    )


def main() -> None:
    write(
        "01_validate_the_access_profile_inputs.ipynb",
        [
            markdown("""# Validate the access-profile inputs

**Data and method:** the three immutable matrices published by the pinned PCADI reference release.

**Purpose:** confirm that the modelling inputs satisfy their complete contracts before any model is fitted.

The gate checks the exact columns and order, identifier integrity, dimensions, feature domains, checksums, byte sizes, separate one-day and two-to-seven-day booking features, cohort nesting, inherited national values and the pinned PCADI source commit."""),
            code(SETUP),
            markdown("""## Method contract

This stage inherits the three PCADI matrices and checks their identity, provenance, dimensions, feature order, value domains and cohort relationships. The tables below are generated from the loaded [reference configuration](../configs/reference_apr2025_mar2026.json), [PCADI input contracts](../data/contracts/pcadi_input_contracts.csv), [validation implementation](../src/gpap2/validation.py) and [notebook reporting helpers](../src/gpap2/notebook_reporting.py). They do not reproduce PCADI's source-integration pipeline."""),
            code("""from gpap2.config import load_config
from gpap2.io import read_contract_csv
from gpap2.notebook_reporting import (
    build_input_contract_table,
    build_output_contract_table,
    build_quality_gate_table,
)
from gpap2.validation import validate_cohort_relationships, validate_contract_directory

config = load_config(CONFIG_PATH)
contracts = read_contract_csv(config.resolve(config.contracts_file))
matrix_checks = validate_contract_directory(
    config.resolve(config.input_directory),
    config.resolve(config.contracts_file),
    config,
)
cohort_checks = validate_cohort_relationships(config.resolve(config.input_directory), config)
input_contract = build_input_contract_table(config, contracts, matrix_checks)
input_contract"""),
            code("""quality_gates = build_quality_gate_table(matrix_checks, cohort_checks)
quality_gates"""),
            code("""assert matrix_checks['passed'].all(), matrix_checks.loc[~matrix_checks['passed'], ['filename', 'failure_reasons']]
assert cohort_checks['passed'].all(), cohort_checks.loc[~cohort_checks['passed']]
assert quality_gates['passed'].all(), quality_gates.loc[~quality_gates['passed']]
output_contract = build_output_contract_table({
    'validated matrices': int(matrix_checks['passed'].sum()),
    'validated cohort relationships': int(cohort_checks['passed'].sum()),
    'failed gates': int((~quality_gates['passed']).sum()),
    'next evidence': 'fixed national matrix and feature contract',
})
output_contract"""),
            markdown("""## Decision

The checksum-controlled PCADI outputs can enter GPAP² without recalculation or imputation. The practice identifier is retained for traceability and excluded from every numerical model."""),
            markdown(
                """**What this establishes:** The validated matrix and feature contract form the fixed input to national profile modelling."""
            ),
        ],
    )

    write(
        "02_select_national_access_pressure_profiles.ipynb",
        [
            markdown("""# Reproduce and justify the selected national access-pressure model

**Data and method:** the validated 6,067-practice national matrix, fourteen-feature specification and locked preprocessing controls.

**Purpose:** show why the fourteen-feature K-Means model with three profiles is the national benchmark, then reproduce its frozen partition under one configuration-controlled contract.

Four activity and change features receive `log1p`; all fourteen features receive robust median/IQR scaling. K-Means uses three clusters, 100 initialisations, a maximum of 500 iterations, seed 2026 and the Lloyd algorithm."""),
            code(SETUP),
            markdown("""## Method contract

This stage inherits the validated national matrix. It exposes the ordered feature and transformation contract, fitted robust-scaling metadata, model controls, retained selection evidence and reproduced outputs. Values come from the [reference configuration](../configs/reference_apr2025_mar2026.json), [preprocessing implementation](../src/gpap2/preprocessing.py), [model implementation](../src/gpap2/models.py), [analysis implementation](../src/gpap2/analysis.py) and [reporting helpers](../src/gpap2/notebook_reporting.py)."""),
            code("""from gpap2.io import read_contract_csv, validate_authority_file

selection_paths = {
    'model roles': ROOT / 'outputs' / 'tables' / 'model_role_register.csv',
    'robustness': ROOT / 'outputs' / 'tables' / 'robustness_summary.csv',
    'national quality': ROOT / 'outputs' / 'tables' / 'national_profile_quality.csv',
}
for path in selection_paths.values():
    validate_authority_file(path, AUTHORITY_MANIFEST)

model_roles = read_contract_csv(selection_paths['model roles'])
robustness = read_contract_csv(selection_paths['robustness'])
national_quality = read_contract_csv(selection_paths['national quality'])
model_roles"""),
            code("""selection_evidence = robustness.loc[
    robustness['robustness_domain'].isin(
        ['Algorithmic alignment', 'Assignment uncertainty', 'Feature sensitivity']
    )
]
selection_evidence"""),
            code("""import json
import numpy as np
import pandas as pd
from sklearn.metrics import adjusted_rand_score, silhouette_score
from gpap2.config import load_config
from gpap2.io import read_contract_csv, sha256
from gpap2.models import align_labels, fit_primary_kmeans
from gpap2.notebook_reporting import (
    build_feature_contract_table,
    build_model_contract_table,
    build_output_contract_table,
    build_transformation_contract_table,
)
from gpap2.preprocessing import prepare_national_features

config = load_config(CONFIG_PATH)
source = config.resolve(config.input_directory) / config.specification('national_14').source_file
matrix = read_contract_csv(source)
reference_path = config.resolve(config.frozen_assignment_file)
reference = read_contract_csv(reference_path)
prepared = prepare_national_features(matrix, config)
model = fit_primary_kmeans(prepared.matrix, config.model)
final_profiles = align_labels(reference['kmeans_cluster'].to_numpy(), model.labels_)

summary = pd.DataFrame({
    'profile': np.sort(np.unique(final_profiles)),
    'practice_count': pd.Series(final_profiles).value_counts().sort_index().to_numpy(),
})
summary"""),
            code("""feature_contract = build_feature_contract_table(config, 'national_14')
feature_contract"""),
            code("""transformation_contract = build_transformation_contract_table(prepared)
transformation_contract"""),
            code("""model_contract = build_model_contract_table(config, prepared)
model_contract"""),
            code("""exact_agreement = float(np.mean(final_profiles == reference['kmeans_cluster'].to_numpy()))
ari = float(adjusted_rand_score(reference['kmeans_cluster'], final_profiles))
silhouette = float(silhouette_score(prepared.matrix, final_profiles))
assignment_sha256 = sha256(reference_path)
run_manifest = {
    'source_sha256': sha256(source),
    'frozen_assignment_sha256': sha256(reference_path),
    'rows': len(matrix),
    'features': list(prepared.feature_names),
    'exact_agreement': exact_agreement,
    'adjusted_rand_index': ari,
    'silhouette': silhouette,
    'random_seed': config.model.random_seed,
    'n_init': config.model.n_init,
    'max_iter': config.model.max_iter,
    'algorithm': config.model.algorithm,
}
runtime_manifest = ROOT / 'work' / 'notebooks' / 'national_profile_run_manifest.json'
runtime_manifest.parent.mkdir(parents=True, exist_ok=True)
runtime_manifest.write_text(json.dumps(run_manifest, indent=2) + '\\n', encoding='utf-8')
output_contract = build_output_contract_table({
    'practices': len(matrix),
    'numeric features': len(prepared.feature_names),
    'profile sizes': ' | '.join(str(value) for value in summary['practice_count']),
    'silhouette': silhouette,
    'agreement with frozen assignment': exact_agreement,
    'ARI with frozen assignment': ari,
    'canonical aligned assignment SHA-256': assignment_sha256,
    'assignment output': reference_path.relative_to(ROOT).as_posix(),
    'runtime manifest': runtime_manifest.relative_to(ROOT).as_posix(),
})
output_contract"""),
            code("""assert matrix[config.identifier].equals(reference[config.identifier])
assert exact_agreement == 1.0 and ari == 1.0
expected_sizes = national_quality.set_index('cluster')['practice_count'].to_dict()
assert summary.set_index('profile')['practice_count'].to_dict() == expected_sizes
assert transformation_contract['iqr_gate_passed'].all()
print('Every frozen national profile assignment was reproduced exactly.')"""),
            markdown("""## Decision

The configuration-controlled implementation exactly reproduces all 6,067 registered assignments. The output uses profile labels 1 to 3; no zero-based label is presented as the analytical result."""),
            markdown(
                """**What this establishes:** The selected national profiles provide the reference partition for restricted-cohort, representation, temporal, contextual and geographic comparisons."""
            ),
        ],
    )

    write(
        "03_test_telephone_inbound_evidence.ipynb",
        [
            markdown("""# Test what telephone inbound evidence adds

**Data and method:** the reproduced national benchmark and the nested 3,020-practice CBT inbound cohort.

**Purpose:** calculate the matched comparison between the 14-feature control and 17-feature CBT inbound model on the same 3,020 practices.

The additional variables are inbound calls per 1,000 registered patient-months, mean absolute monthly call-rate change and call-rate range. The full-data comparison is recomputed here. Closed resampling evidence is inspected only after its authority checksum is validated."""),
            code(SETUP),
            markdown("""## Method contract

This stage inherits the fixed national feature values for the nested CBT-observed cohort. It fits the shared 14-feature baseline and 17-feature inbound specification under identical preprocessing and K-Means controls. The displayed values come from the [reference configuration](../configs/reference_apr2025_mar2026.json), [comparison implementation](../src/gpap2/analysis.py), [preprocessing implementation](../src/gpap2/preprocessing.py) and [reporting helpers](../src/gpap2/notebook_reporting.py)."""),
            code("""from gpap2.analysis import compare_inbound_models
from gpap2.config import load_config
from gpap2.io import read_contract_csv, validate_authority_file
from gpap2.notebook_reporting import (
    build_comparison_contract_table,
    build_feature_contract_table,
    build_model_contract_table,
    build_transformation_contract_table,
)
from gpap2.validation import validate_cohort_relationships

config = load_config(CONFIG_PATH)
source = config.resolve(config.input_directory) / config.specification('cbt_inbound_17').source_file
inbound = read_contract_csv(source)
comparison = compare_inbound_models(inbound, config)
cohort_checks = validate_cohort_relationships(config.resolve(config.input_directory), config)
cohort_checks.loc[cohort_checks['test'].str.startswith('CBT inbound')]"""),
            code("""feature_contract = build_feature_contract_table(config, 'cbt_inbound_17')
feature_contract"""),
            code("""transformation_contract = build_transformation_contract_table(
    comparison.prepared['cbt_inbound_17']
)
transformation_contract"""),
            code("""build_model_contract_table(config, comparison.prepared['cbt_inbound_17'])"""),
            code("""stability_path = ROOT / 'outputs' / 'tables' / 'robustness_summary.csv'
validate_authority_file(stability_path, AUTHORITY_MANIFEST)
stability = read_contract_csv(stability_path)
stability.loc[stability['robustness_domain'].eq('CBT inbound sensitivity')]"""),
            code("""import numpy as np
from gpap2.analysis import canonical_assignment_sha256

row = comparison.comparisons.iloc[0]
assignment_hash = canonical_assignment_sha256(
    comparison.assignments,
    config.identifier,
    'cbt_inbound_17_aligned_to_national_14',
)
authority_path = ROOT / 'outputs' / 'validation' / 'analytical_regression_results.csv'
validate_authority_file(authority_path, AUTHORITY_MANIFEST)
authority = read_contract_csv(authority_path)
expected = authority.loc[
    authority['reference'].eq(row['reference']) & authority['candidate'].eq(row['candidate'])
].iloc[0]
for metric in ['adjusted_rand_index', 'normalised_mutual_information', 'aligned_agreement']:
    assert np.isclose(row[metric], expected[metric], atol=1e-12, rtol=0)
assert int(row['reassigned_practices']) == int(expected['reassigned_practices'])
assert assignment_hash == expected['canonical_aligned_assignment_sha256']
comparison_contract = build_comparison_contract_table(
    comparison.comparisons,
    comparison.diagnostics,
    {'cbt_inbound_17': assignment_hash},
)
comparison_contract"""),
            markdown("""## Decision

Inbound telephone activity is an informative restricted-cohort sensitivity. It changes a material set of assignments but does not replace the national OCS-GPAD profile model or imply national CBT coverage."""),
            markdown(
                """**What this establishes:** The inbound result is a restricted evidence-availability sensitivity and defines the baseline for testing whether telephone-outcome representation changes that sensitivity. It does not replace or rerun the national model."""
            ),
        ],
    )

    write(
        "04_test_telephone_outcome_composition.ipynb",
        [
            markdown("""# Test telephone outcome composition without repeated weighting

**Data and method:** the national benchmark, inbound sensitivity and the nested 1,456-practice outcome-complete cohort.

**Purpose:** calculate the authoritative NHS-aligned three-coordinate representation of four CBT outcome shares and compare 17-feature, raw 21-feature and ILR 20-feature models on the same 1,456 practices.

The reference outcome parts are strictly positive. Each row is closed to one and no pseudocount is added. Coordinate names and the orthonormal basis encode dealt-versus-missed, answered-versus-IVR/callback and IVR-versus-callback balances."""),
            code(SETUP),
            markdown("""## Method contract

This stage inherits the 1,456-practice outcome-complete cohort and compares the inbound 17-feature baseline, raw 21-feature outcome representation and NHS-aligned 20-feature ILR representation under identical model controls. Composition, transformation and output tables are generated through the tested [composition implementation](../src/gpap2/composition.py), [analysis implementation](../src/gpap2/analysis.py), [preprocessing implementation](../src/gpap2/preprocessing.py) and [reporting helpers](../src/gpap2/notebook_reporting.py)."""),
            code("""import numpy as np
import pandas as pd
from gpap2.analysis import add_nhs_outcome_coordinates, compare_outcome_models
from gpap2.composition import NHS_OUTCOME_ILR_BASIS, inverse_nhs_outcome_ilr, validate_orthonormal_basis
from gpap2.config import load_config
from gpap2.contracts import NHS_OUTCOME_ILR_NAMES, OUTCOME_SHARE_COLUMNS
from gpap2.io import read_contract_csv, validate_authority_file
from gpap2.notebook_reporting import (
    build_comparison_contract_table,
    build_composition_contract_table,
    build_feature_contract_table,
    build_model_contract_table,
)

config = load_config(CONFIG_PATH)
source = config.resolve(config.input_directory) / config.specification('cbt_outcome_raw_21').source_file
outcomes = read_contract_csv(source)
shares = outcomes.loc[:, OUTCOME_SHARE_COLUMNS].to_numpy(dtype=float)
working, closed = add_nhs_outcome_coordinates(outcomes)
coordinates = working.loc[:, NHS_OUTCOME_ILR_NAMES].to_numpy(dtype=float)
validate_orthonormal_basis(NHS_OUTCOME_ILR_BASIS)
reconstruction_error = float(np.max(np.abs(inverse_nhs_outcome_ilr(coordinates) - closed)))
pseudocount_used = False

composition_audit = build_composition_contract_table(
    shares,
    closed,
    NHS_OUTCOME_ILR_BASIS,
    OUTCOME_SHARE_COLUMNS,
    NHS_OUTCOME_ILR_NAMES,
    reconstruction_error,
    pseudocount_used=pseudocount_used,
)
composition_audit"""),
            code("""basis_table = pd.DataFrame(
    NHS_OUTCOME_ILR_BASIS,
    index=NHS_OUTCOME_ILR_NAMES,
    columns=OUTCOME_SHARE_COLUMNS,
)
basis_table"""),
            code("""comparison = compare_outcome_models(outcomes, config)
specification_rows = []
for specification in ['cbt_inbound_17', 'cbt_outcome_raw_21', 'cbt_outcome_nhs_ilr_20']:
    feature_table = build_feature_contract_table(config, specification)
    specification_rows.append({
        'specification': specification,
        'features': len(feature_table),
        'log1p features': ' | '.join(feature_table.loc[feature_table['transformation'].eq('log1p'), 'feature']),
        'unchanged features': ' | '.join(feature_table.loc[feature_table['transformation'].eq('unchanged'), 'feature']),
    })
pd.DataFrame(specification_rows)"""),
            code("""build_model_contract_table(
    config,
    comparison.prepared['cbt_outcome_nhs_ilr_20'],
)"""),
            code("""authority_path = ROOT / 'outputs' / 'validation' / 'analytical_regression_results.csv'
validate_authority_file(authority_path, AUTHORITY_MANIFEST)
authority = pd.read_csv(authority_path)
observed = comparison.comparisons.merge(authority, on=['reference', 'candidate'], suffixes=('_recomputed', '_authority'))
for field in ['adjusted_rand_index', 'normalised_mutual_information', 'aligned_agreement']:
    assert np.allclose(observed[f'{field}_recomputed'], observed[f'{field}_authority'], atol=1e-12, rtol=0)
assert (observed['reassigned_practices_recomputed'] == observed['reassigned_practices_authority']).all()
observed[['reference', 'candidate', 'adjusted_rand_index_recomputed', 'normalised_mutual_information_recomputed', 'aligned_agreement_recomputed', 'reassigned_practices_recomputed']]"""),
            code("""nhs_row = comparison.comparisons.loc[comparison.comparisons['candidate'].eq('cbt_outcome_nhs_ilr_20') & comparison.comparisons['reference'].eq('cbt_inbound_17')].iloc[0]
raw_row = comparison.comparisons.loc[comparison.comparisons['candidate'].eq('cbt_outcome_raw_21') & comparison.comparisons['reference'].eq('cbt_inbound_17')].iloc[0]
assert (shares > 0).all() and pseudocount_used is False
assert reconstruction_error < 1e-12
from gpap2.analysis import canonical_assignment_sha256
assignment_hash = canonical_assignment_sha256(
    comparison.assignments,
    config.identifier,
    'cbt_outcome_nhs_ilr_20_aligned_to_inbound_17',
)
expected_nhs = authority.loc[
    authority['reference'].eq(nhs_row['reference']) & authority['candidate'].eq(nhs_row['candidate'])
].iloc[0]
expected_raw = authority.loc[
    authority['reference'].eq(raw_row['reference']) & authority['candidate'].eq(raw_row['candidate'])
].iloc[0]
for observed_row, expected_row in [(nhs_row, expected_nhs), (raw_row, expected_raw)]:
    for metric in ['adjusted_rand_index', 'normalised_mutual_information', 'aligned_agreement']:
        assert np.isclose(observed_row[metric], expected_row[metric], atol=1e-12, rtol=0)
    assert int(observed_row['reassigned_practices']) == int(expected_row['reassigned_practices'])
assert assignment_hash == expected_nhs['canonical_aligned_assignment_sha256']
comparison_contract = build_comparison_contract_table(
    comparison.comparisons,
    comparison.diagnostics,
    {'cbt_outcome_nhs_ilr_20': assignment_hash},
)
comparison_contract"""),
            markdown("""## Decision

The NHS-aligned 20-feature ILR model is the preferred outcome-representation sensitivity. The raw 21-feature model remains a representation comparator. Neither restricted-cohort model replaces the national model."""),
            markdown(
                """**What this establishes:** The outcome-representation result contributes to the robustness evidence alongside inbound, algorithmic, feature and temporal comparisons."""
            ),
        ],
    )

    write(
        "05_assess_temporal_persistence.ipynb",
        [
            markdown("""# Assess whether profiles persist over time

**Data and method:** the national benchmark and its algorithm, feature and telephone sensitivity boundaries. The temporal calculation is parallel to the telephone calculations, not computationally downstream from them.

**Purpose:** inspect checksum-verified half-year and quarterly authority tables and decide whether shorter windows support or replace the annual model.

This notebook validates included authority tables. It does not claim to reconstruct the full monthly national feature pipeline included in the dissertation analysis."""),
            code(SETUP),
            code("""import pandas as pd
from gpap2.io import validate_authority_file

canonical_path = ROOT / 'outputs' / 'tables' / 'temporal_canonical_period_metrics.csv'
structural_path = ROOT / 'outputs' / 'tables' / 'temporal_structural_period_metrics.csv'
validate_authority_file(canonical_path, AUTHORITY_MANIFEST)
validate_authority_file(structural_path, AUTHORITY_MANIFEST)
canonical = pd.read_csv(canonical_path)
structural = pd.read_csv(structural_path)
canonical[['period_type', 'period_name', 'practices', 'annual_agreement_share', 'adjusted_rand_index_vs_annual', 'silhouette_score']]"""),
            code("""summary = canonical.groupby('period_type').agg(
    periods=('period_name', 'count'),
    minimum_practices=('practices', 'min'),
    median_annual_agreement=('annual_agreement_share', 'median'),
    median_ari_vs_annual=('adjusted_rand_index_vs_annual', 'median'),
).reset_index()
assert set(summary['period_type']) == {'half_year', 'quarter'}
assert len(structural) == len(canonical) == 6
summary"""),
            markdown("""## Decision

Half-year and quarterly partitions retain related structure but show genuine within-year reassignment. The April 2025 to March 2026 annual model remains the reference; temporal results are sensitivity evidence rather than replacement profiles."""),
            markdown(
                """**What this establishes:** the robustness evidence bounds the external-context interpretation of the fixed national profiles."""
            ),
        ],
    )

    write(
        "06_interpret_profiles_with_external_context.ipynb",
        [
            markdown("""# Inspect external context for the frozen profiles

**Data and method:** the fixed national profiles, their uncertainty signals and the completed robustness evidence.

**Purpose:** inspect selected population, workforce, place and patient-experience authorities without allowing contextual variables to redefine the frozen activity profiles.

This notebook validates and displays included machine-readable evidence. Upstream source acquisition and derivation are documented separately and are not presented as being rebuilt here."""),
            code(SETUP),
            code("""import pandas as pd
from gpap2.io import validate_authority_file

paths = {
    'profile_summary': ROOT / 'outputs' / 'tables' / 'numeric_profile_descriptive_summary.csv',
    'gpps': ROOT / 'outputs' / 'tables' / 'gpps_precision_profile_summary.csv',
    'marginal_effects': ROOT / 'outputs' / 'tables' / 'context_multinomial_average_marginal_effects.csv',
    'narratives': ROOT / 'outputs' / 'tables' / 'neutral_profile_narratives.csv',
}
for path in paths.values():
    validate_authority_file(path, AUTHORITY_MANIFEST)
tables = {name: pd.read_csv(path) for name, path in paths.items()}
pd.DataFrame({'table': list(tables), 'rows': [len(frame) for frame in tables.values()]})"""),
            code("""from gpap2.profile_labels import PROFILE_SHORT_LABELS

observed_labels = tables['narratives'].set_index('frozen_profile_number')['approved_descriptive_label']
for profile, label in PROFILE_SHORT_LABELS.items():
    assert observed_labels.loc[profile].casefold() == label.casefold()
tables['narratives'][['frozen_profile_number', 'approved_descriptive_label', 'national_n', 'permitted_interpretation', 'interpretation_boundary']]"""),
            markdown("""## Interpretation contract

Patient experience, workforce, population, deprivation, rurality and geography are practice-level external evidence. Denominators differ by measure. Associations can describe context and test coherence; they cannot establish patient-level mechanisms, performance rankings or causal effects."""),
            markdown(
                """**What this establishes:** contextual findings inform the geographic account and the claim-to-evidence synthesis."""
            ),
        ],
    )

    write(
        "07_translate_profiles_into_evidence_readiness.ipynb",
        [
            markdown("""# Translate the analysis into evidence-ready claims

**Data and method:** the validated benchmark, profile definitions, robustness evidence, external context and documented geography evidence.

**Purpose:** inspect checksum-verified writing authorities that connect each proposed conclusion to its empirical source, cohort and language boundary.

This is an evidence-inspection notebook. It does not rerun upstream external-source extraction or adjusted models."""),
            code(SETUP),
            code("""import pandas as pd
from gpap2.io import validate_authority_file

claims_path = ROOT / 'outputs' / 'tables' / 'claim_to_evidence_matrix.csv'
availability_path = ROOT / 'outputs' / 'tables' / 'evidence_availability_summary.csv'
validate_authority_file(claims_path, AUTHORITY_MANIFEST)
validate_authority_file(availability_path, AUTHORITY_MANIFEST)
claims = pd.read_csv(claims_path)
availability = pd.read_csv(availability_path)
pd.DataFrame({
    'authority': ['claim-to-evidence matrix', 'evidence-availability summary'],
    'rows': [len(claims), len(availability)],
})"""),
            code("""required_scientific_fields = {
    'claim_id',
    'primary_claim_domain',
    'exact_construct_observed',
    'support_category',
    'linked_table_figure',
    'source_lineage',
    'construct_evidence_link',
    'permitted_wording',
    'prohibited_wording',
}
assert required_scientific_fields.issubset(claims.columns)
assert len(claims) == 42 and claims['claim_id'].is_unique
claims[['claim_id', 'primary_claim_domain', 'proposed_claim', 'support_category', 'permitted_wording', 'prohibited_wording']].head(10)"""),
            markdown("""## Decision

The evidence supports descriptive practice-level activity profiles, bounded robustness results and contextual associations. Linked pathway, outcome, safety, cost and implementation evidence is required before extending those results to causal or patient-level claims."""),
            markdown(
                """**What this establishes:** the 42-claim authority defines the evidence that may be reported and the interpretations that require additional data."""
            ),
        ],
    )

    print("built seven analytical notebooks")


if __name__ == "__main__":
    main()
