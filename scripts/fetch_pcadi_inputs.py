"""Acquire the three matrices from an immutable PCADI commit and validate atomically."""

from __future__ import annotations

import argparse
import sys
import tempfile
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import unquote, urlparse

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gpap2.config import load_config  # noqa: E402
from gpap2.io import sha256  # noqa: E402
from gpap2.validation import validate_matrix  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT / "configs" / "reference_apr2025_mar2026.json",
    )
    args = parser.parse_args()
    config = load_config(args.config)
    contracts = pd.read_csv(config.resolve(config.contracts_file))
    destination = config.resolve(config.input_directory)
    destination.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, object]] = []

    for _, contract in contracts.iterrows():
        expected_filename = str(contract["filename"])
        url = str(contract["download_url"])
        advertised_filename = Path(unquote(urlparse(url).path)).name
        if advertised_filename != expected_filename:
            raise RuntimeError(
                "PCADI URL filename does not match its contract: "
                f"{advertised_filename!r} != {expected_filename!r}"
            )
        target = destination / expected_filename
        existing_valid = False
        if target.exists():
            existing_valid = validate_matrix(target, contract, config).passed

        if not existing_valid:
            with tempfile.NamedTemporaryFile(
                prefix=f".{target.name}.", suffix=".download", dir=destination, delete=False
            ) as temporary:
                temporary_path = Path(temporary.name)
            try:
                urllib.request.urlretrieve(url, temporary_path)
                result = validate_matrix(temporary_path, contract, config)
                if not result.passed:
                    raise RuntimeError(
                        f"Downloaded {target.name} failed validation: {result.failure_reasons}"
                    )
                temporary_path.replace(target)
                acquisition = "downloaded_and_atomically_installed"
            finally:
                temporary_path.unlink(missing_ok=True)
        else:
            acquisition = "existing_file_validated"

        records.append(
            {
                "acquired_utc": datetime.now(UTC).isoformat(),
                "source_repository": config.pcadi.repository,
                "source_commit": config.pcadi.commit_sha,
                "source_tag": config.pcadi.tag,
                "download_url": contract["download_url"],
                "source_filename": contract["filename"],
                "destination": str(target),
                "size_bytes": target.stat().st_size,
                "sha256": sha256(target),
                "acquisition": acquisition,
            }
        )
        print(f"verified {target.name}: {sha256(target)}")

    manifest_path = config.resolve(config.output_directory) / "pcadi_acquisition_manifest.csv"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(records).to_csv(manifest_path, index=False, lineterminator="\n")
    print(f"wrote acquisition manifest: {manifest_path}")


if __name__ == "__main__":
    main()
