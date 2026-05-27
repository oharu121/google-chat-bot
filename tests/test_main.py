import json


class FakeRequest:
    """Mimics a Flask request object for testing."""

    def __init__(self, data):
        self._data = data

    def get_json(self, silent=False):
        return self._data


def test_echo_reply():
    from main import handle_chat

    request = FakeRequest({
        "message": {
            "text": "hello",
            "sender": {"displayName": "Alice"},
        }
    })
    response = handle_chat(request)
    assert response == {"text": "Hello Alice! You said: hello"}


def test_empty_request():
    from main import handle_chat

    request = FakeRequest(None)
    response = handle_chat(request)
    assert response == {"text": "Empty request"}


def test_missing_sender():
    from main import handle_chat

    request = FakeRequest({
        "message": {
            "text": "hi",
        }
    })
    response = handle_chat(request)
    assert response == {"text": "Hello someone! You said: hi"}
