from pathlib import Path

import pytest


@pytest.fixture
def samples_dir() -> Path:
    return Path(__file__).parent.parent / "samples"
