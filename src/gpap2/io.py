"""Portable file loading and checksum verification."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def read_contract_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, dtype={"practice_code_standardised": "string"})


def validate_authority_file(path: Path, manifest_path: Path) -> str:
    """Validate an included machine-readable authority file and return its checksum."""
    manifest = pd.read_csv(manifest_path)
    relative = path.resolve().relative_to(manifest_path.resolve().parents[2]).as_posix()
    match = manifest.loc[manifest["path"].eq(relative)]
    if len(match) != 1:
        raise ValueError(f"Authority manifest has no unique entry for {relative}")
    observed = sha256(path)
    expected = str(match.iloc[0]["sha256"]).upper()
    if observed != expected:
        raise ValueError(f"Authority checksum mismatch for {relative}: {observed} != {expected}")
    return observed
