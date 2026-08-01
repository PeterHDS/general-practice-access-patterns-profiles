# Contributing

Contributions should preserve the boundary between PCADI integration and GPAP² modelling. Open an issue before proposing a new analytical branch so its question, input contract, cohort and interpretation boundary are explicit.

For code changes:

1. create a focused branch;
2. install `.[dev]`;
3. run `ruff check .`, `pytest` and
   `python scripts/build_analytical_regression_evidence.py --check`;
4. update contracts and checksums when an authoritative input changes;
5. keep notebook outputs concise and deterministic; and
6. describe any effect on cohort size, feature definition or profile interpretation.

Raw NHS downloads, private audit records and large local databases must remain outside Git.

Ordinary verification is non-mutating. The `--write-canonical` analytical-regression and notebook
modes are maintainer-only release operations and must run in the locked canonical environment.
