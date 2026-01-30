"""Shared test fixtures."""

from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def hamqsl_xml() -> bytes:
    return (FIXTURES / "hamqsl_sample.xml").read_bytes()


@pytest.fixture
def swpc_kindex_json() -> bytes:
    return (FIXTURES / "swpc_kindex.json").read_bytes()


@pytest.fixture
def swpc_flux_json() -> bytes:
    return (FIXTURES / "swpc_flux.json").read_bytes()
