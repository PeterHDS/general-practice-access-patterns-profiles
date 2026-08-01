# Data interface

GPAP² consumes three annual practice matrices produced and validated by PCADI. Run `python scripts/fetch_pcadi_inputs.py` to obtain the reference copies from the public PCADI repository and verify their contracts.

| Matrix | Practices | Numeric features | Role |
|---|---:|---:|---|
| `primary_practice_access_clustering_matrix.csv` | 6,067 | 14 | National primary analysis |
| `cbt_inbound_sensitivity_clustering_matrix_17_features.csv` | 3,020 | 17 | Inbound telephone sensitivity |
| `cbt_outcomes_sensitivity_clustering_matrix_21_features.csv` | 1,456 | 21 | Outcome-complete source representation used to derive the preferred 20-feature ILR sensitivity |

The practice identifier is retained for traceability and excluded from numerical modelling. Raw NHS files and the PCADI SQLite database are outside GPAP².

