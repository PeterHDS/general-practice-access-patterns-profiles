"""Checksum the included authority files consumed by public evidence-inspection notebooks."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gpap2.io import sha256  # noqa: E402

AUTHORITY_FILES = [
    "outputs/tables/national_profile_assignments.csv",
    "outputs/tables/national_profile_quality.csv",
    "outputs/tables/model_role_register.csv",
    "outputs/tables/robustness_summary.csv",
    "outputs/tables/temporal_canonical_period_metrics.csv",
    "outputs/tables/temporal_structural_period_metrics.csv",
    "outputs/tables/numeric_profile_descriptive_summary.csv",
    "outputs/tables/gpps_precision_profile_summary.csv",
    "outputs/tables/context_multinomial_average_marginal_effects.csv",
    "outputs/tables/neutral_profile_narratives.csv",
    "outputs/tables/claim_to_evidence_matrix.csv",
    "outputs/tables/evidence_availability_summary.csv",
    "outputs/tables/telephone_inbound_model_comparison.csv",
    "outputs/tables/telephone_inbound_model_diagnostics.csv",
    "outputs/tables/telephone_inbound_aligned_assignments.csv",
    "outputs/tables/telephone_outcome_model_comparison.csv",
    "outputs/tables/telephone_outcome_model_diagnostics.csv",
    "outputs/tables/telephone_outcome_model_assignments.csv",
    "outputs/validation/analytical_regression_results.csv",
]


def main() -> None:
    records = []
    for relative in AUTHORITY_FILES:
        path = ROOT / relative
        if not path.is_file():
            raise FileNotFoundError(f"Notebook authority file is absent: {relative}")
        frame = pd.read_csv(path)
        records.append(
            {
                "path": relative,
                "sha256": sha256(path),
                "size_bytes": path.stat().st_size,
                "rows": len(frame),
                "columns": len(frame.columns),
            }
        )
    output = ROOT / "outputs" / "validation" / "notebook_authority_files.csv"
    pd.DataFrame(records).to_csv(output, index=False, lineterminator="\n")
    print(f"wrote {len(records)} notebook authority contracts to {output}")


if __name__ == "__main__":
    main()
