from pathlib import Path

import pytest

from app.processor import SupportRequestProcessor


@pytest.fixture()
def handbook_text() -> str:
    path = Path(__file__).resolve().parents[2] / "data" / "support_handbook.md"
    return path.read_text(encoding="utf-8")


@pytest.fixture()
def sample_requests_text() -> str:
    path = Path(__file__).resolve().parents[2] / "data" / "sample_requests.md"
    return path.read_text(encoding="utf-8")


@pytest.fixture()
def processor() -> SupportRequestProcessor:
    return SupportRequestProcessor()
