"""Command-line interfaces for validation and reference inspection."""

from __future__ import annotations

import argparse
from pathlib import Path

from .config import load_config
from .validation import validate_cohort_relationships, validate_contract_directory


def main() -> None:
    parser = argparse.ArgumentParser(prog="gpap2")
    subparsers = parser.add_subparsers(dest="command", required=True)
    validate = subparsers.add_parser("validate", help="validate PCADI modelling inputs")
    validate.add_argument(
        "--config",
        type=Path,
        default=Path("configs/reference_apr2025_mar2026.json"),
    )
    args = parser.parse_args()

    if args.command == "validate":
        config = load_config(args.config)
        data_dir = config.resolve(config.input_directory)
        contracts_path = config.resolve(config.contracts_file)
        matrix_results = validate_contract_directory(data_dir, contracts_path, config)
        cohort_results = validate_cohort_relationships(data_dir, config)
        print("PCADI MATRIX CONTRACTS")
        print(matrix_results.to_string(index=False))
        print("\nCOHORT RELATIONSHIPS")
        print(cohort_results.to_string(index=False))
        if not matrix_results["passed"].all() or not cohort_results["passed"].all():
            raise SystemExit(1)


if __name__ == "__main__":
    main()
