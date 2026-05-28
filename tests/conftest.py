import pytest


class FakeRequest:
    """Mimics a Flask request object for testing."""

    def __init__(self, data):
        self._data = data

    def get_json(self, silent=False):
        return self._data


@pytest.fixture
def make_request():
    """Factory fixture that creates FakeRequest instances."""
    return FakeRequest
