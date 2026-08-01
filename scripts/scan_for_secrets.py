"""Fail on high-confidence secret-shaped values in release text files."""

from __future__ import annotations

import csv
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {
    ".cff",
    ".csv",
    ".geojson",
    ".json",
    ".md",
    ".py",
    ".svg",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}
PATTERNS = {
    "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "GitHub token": re.compile(r"\b(?:ghp|github_pat)_[A-Za-z0-9_]{20,}\b"),
    "AWS access key": re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
    "assigned password": re.compile(r"(?i)\bpassword\s*[:=]\s*['\"][^'\"]{8,}['\"]"),
}


def tracked_paths() -> list[Path]:
    """Return the public Git surface instead of generated dependency environments."""
    result = subprocess.run(
        ["git", "ls-files", "--cached"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        return [ROOT / line for line in result.stdout.splitlines() if line]
    manifest = ROOT / "outputs" / "validation" / "public_file_manifest.csv"
    if not manifest.is_file():
        raise SystemExit("Git metadata and the public file manifest are both unavailable")
    with manifest.open("r", encoding="utf-8-sig", newline="") as stream:
        return [ROOT / row["path"] for row in csv.DictReader(stream)]


def main() -> None:
    failures = []
    for path in tracked_paths():
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8", errors="strict")
        for label, pattern in PATTERNS.items():
            if pattern.search(text):
                failures.append(f"{label}: {path.relative_to(ROOT)}")
    if failures:
        raise SystemExit("Potential secrets detected:\n" + "\n".join(failures))
    print("secret-pattern scan passed")


if __name__ == "__main__":
    main()
