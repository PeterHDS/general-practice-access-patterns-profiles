from pathlib import Path

from gpap2.profile_labels import PROFILE_LABELS, SUPERSEDED_PUBLIC_PHRASES

ROOT = Path(__file__).resolve().parents[1]


def test_profile_one_label_is_authoritative() -> None:
    assert PROFILE_LABELS[1] == "Lower recorded activity, higher DNA and shorter-delay shares"


def test_superseded_profile_phrases_are_absent_from_public_text() -> None:
    suffixes = {".cff", ".csv", ".json", ".md", ".py", ".svg", ".toml", ".txt", ".yml"}
    failures = []
    for path in ROOT.rglob("*"):
        if (
            not path.is_file()
            or path.suffix.lower() not in suffixes
            or ".git" in path.parts
            or "work" in path.parts
        ):
            continue
        text = path.read_text(encoding="utf-8", errors="strict").lower()
        for phrase in SUPERSEDED_PUBLIC_PHRASES:
            retained_scientific_authorities = {"national_uncertainty_summary.csv"}
            if (
                phrase in text
                and path.name != "profile_labels.py"
                and path.name not in retained_scientific_authorities
            ):
                failures.append(f"{path.relative_to(ROOT)}: {phrase}")
    assert not failures, failures
