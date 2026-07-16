import pytest

from example_claims import CLAIMS


@pytest.fixture
def claims() -> list[str]:
    return CLAIMS
