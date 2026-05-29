import pytest


class FakeRequest:
    """Mimics a Flask request object for testing."""

    def __init__(self, data):
        self._data = data
        self.base_url = "http://localhost:8080"
        self.headers = {"Host": "localhost:8080"}

    def get_json(self, silent=False):
        return self._data


@pytest.fixture
def make_request():
    """Factory fixture that creates FakeRequest instances."""
    return FakeRequest
