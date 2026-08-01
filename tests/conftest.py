from pathlib import Path

import pytest

from gpap2.config import ReferenceConfig, load_config


@pytest.fixture(scope="session")
def repository_root() -> Path:
    return Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def reference_config(repository_root: Path) -> ReferenceConfig:
    return load_config(repository_root / "configs" / "reference_apr2025_mar2026.json")
