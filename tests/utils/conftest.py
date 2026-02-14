import pytest

@pytest.fixture
def get_regex_text() -> str:
    return "545 343 754"


@pytest.fixture
def get_duration_str() -> str:
    return "04:02:56.8"