"""Static, link, archive-allow-list and portable-path validation."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
import zipfile
from pathlib import Path
from urllib.parse import unquote

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
    ".yml",
    ".yaml",
}
PRIVATE_PATTERNS = [
    "C:" + r"\\Users\\",
    "/" + "Users/",
    "/" + r"home/[A-Za-z0-9._-]+/",
]
FORBIDDEN_RELEASE_PARTS = {
    ".git",
    ".ipynb_checkpoints",
    ".pytest_cache",
    ".ruff_cache",
    "__pycache__",
    "build",
    "dist",
    "work",
}
FORBIDDEN_RELEASE_SUFFIXES = {".db", ".pyc", ".sqlite", ".sqlite3"}


def tracked_release_files() -> set[str]:
    result = subprocess.run(
        ["git", "ls-files", "--cached"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        return {line.replace("\\", "/") for line in result.stdout.splitlines() if line}

    # A release archive intentionally has no .git directory. In that setting,
    # the checksum-controlled public manifest is the authoritative file list.
    manifest = ROOT / "outputs" / "validation" / "public_file_manifest.csv"
    if not manifest.is_file():
        raise SystemExit(
            "Neither Git metadata nor outputs/validation/public_file_manifest.csv is available"
        )
    with manifest.open("r", encoding="utf-8", newline="") as stream:
        paths = {row["path"] for row in csv.DictReader(stream)}
    return paths | {"outputs/validation/public_file_manifest.csv"}


def manifest_set_failures(release_files: set[str], manifest_files: list[str]) -> list[str]:
    failures: list[str] = []
    duplicates = sorted({path for path in manifest_files if manifest_files.count(path) > 1})
    if duplicates:
        failures.append(f"duplicate manifest entries: {', '.join(duplicates)}")
    expected = release_files - {"outputs/validation/public_file_manifest.csv"}
    observed = set(manifest_files)
    missing = sorted(expected - observed)
    unregistered = sorted(observed - expected)
    if missing:
        failures.append(f"tracked release files missing from manifest: {', '.join(missing)}")
    if unregistered:
        failures.append(
            f"manifest entries not present in tracked release: {', '.join(unregistered)}"
        )
    return failures


def scan_text(relative: Path, text: str, failures: list[str]) -> None:
    for pattern in PRIVATE_PATTERNS:
        if re.search(pattern, text):
            failures.append(f"private absolute path in {relative}")
    if relative.suffix.lower() == ".md":
        for heading in re.findall(r"^#{1,6}\s+(.+)$", text, flags=re.MULTILINE):
            if re.search(r"\b(?:Scenario|Task|E0[0-9][A-Z]?)\b", heading, re.IGNORECASE):
                failures.append(f"internal stage code in heading {relative}: {heading}")
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
            target = unquote(target.split("#", 1)[0].strip("<>"))
            if not target or re.match(r"^[a-z]+://", target, re.IGNORECASE):
                continue
            resolved = (ROOT / relative.parent / target).resolve()
            if not resolved.exists():
                failures.append(f"broken local link in {relative}: {target}")


def main() -> None:
    failures: list[str] = []
    release_files = tracked_release_files()
    for relative_name in sorted(release_files):
        path = ROOT / relative_name
        if not path.is_file():
            failures.append(f"tracked release file is absent: {relative_name}")
            continue
        relative = Path(relative_name)
        suffix = path.suffix.lower()
        if suffix == ".ipynb":
            text = path.read_text(encoding="utf-8")
            json.loads(text)
            scan_text(relative, text, failures)
        elif suffix in TEXT_SUFFIXES or path.name == "CITATION.cff":
            scan_text(relative, path.read_text(encoding="utf-8", errors="strict"), failures)
        elif suffix == ".qgz":
            with zipfile.ZipFile(path) as archive:
                projects = [name for name in archive.namelist() if name.endswith(".qgs")]
                if len(projects) != 1:
                    failures.append(f"QGZ does not contain exactly one QGS file: {relative}")
                for project in projects:
                    scan_text(relative, archive.read(project).decode("utf-8"), failures)

    for workflow in (ROOT / ".github" / "workflows").glob("*.yml"):
        text = workflow.read_text(encoding="utf-8")
        for action, reference in re.findall(r"uses:\s*([^@\s]+)@([^\s#]+)", text):
            if not re.fullmatch(r"[0-9a-f]{40}", reference):
                failures.append(f"GitHub Action is not pinned to a full SHA: {action}@{reference}")

    manifest = ROOT / "outputs" / "validation" / "public_file_manifest.csv"
    if not manifest.exists():
        failures.append("public file manifest is absent")
    else:
        with manifest.open("r", encoding="utf-8", newline="") as stream:
            rows = list(csv.DictReader(stream))
            failures.extend(manifest_set_failures(release_files, [row["path"] for row in rows]))
            for row in rows:
                relative = Path(row["path"])
                if any(part in FORBIDDEN_RELEASE_PARTS for part in relative.parts):
                    failures.append(f"forbidden release path in manifest: {row['path']}")
                if relative.suffix.lower() in FORBIDDEN_RELEASE_SUFFIXES:
                    failures.append(f"forbidden release file type in manifest: {row['path']}")
                target = ROOT / relative
                if not target.exists():
                    failures.append(f"manifest target is absent: {row['path']}")
                    continue
                binary = (
                    target.suffix.lower() in {".png", ".jpg", ".jpeg", ".qgz", ".zip"}
                    or row["path"].startswith("data/reference/")
                    or row["path"].startswith("qgis/data/")
                )
                payload = target.read_bytes()
                if not binary:
                    payload = payload.replace(b"\r\n", b"\n")
                digest = hashlib.sha256(payload).hexdigest().upper()
                if digest != row["sha256"].upper():
                    failures.append(f"manifest checksum mismatch: {row['path']}")

    claims = ROOT / "outputs/tables/claim_to_evidence_matrix.csv"
    if claims.exists():
        with claims.open("r", encoding="utf-8-sig", newline="") as stream:
            claim_rows = list(csv.DictReader(stream))
        required = {
            "private_build_lineage_id",
            "public_evidence_path",
            "official_source_reference",
            "public_evidence_status",
            "public_evidence_note",
        }
        if claim_rows and not required.issubset(claim_rows[0]):
            failures.append("claim evidence matrix lacks the public/private lineage contract")
        for row in claim_rows:
            for value in row.get("public_evidence_path", "").split(";"):
                value = value.strip()
                if not value or not (ROOT / value).is_file():
                    failures.append(
                        f"claim {row.get('claim_id')} has unresolved public evidence path: {value}"
                    )
    if failures:
        raise SystemExit("\n".join(sorted(set(failures))))
    print("public repository static and release-allow-list checks passed")


if __name__ == "__main__":
    main()
