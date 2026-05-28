from unittest.mock import patch, MagicMock

from main import handle_chat, create_message


def _addons_request(text, sender_name=None, space_name="spaces/TEST", message_name=None):
    """Build a Workspace Add-ons format request payload."""
    message = {"text": text}
    if sender_name is not None:
        message["sender"] = {"displayName": sender_name}
    if message_name is not None:
        message["name"] = message_name
    return {
        "chat": {
            "messagePayload": {
                "message": message,
                "space": {"name": space_name},
            }
        }
    }


def test_empty_request_returns_message(make_request):
    request = make_request(None)
    response = handle_chat(request)
    assert response == create_message("Empty request")


@patch("main.threading.Thread")
def test_returns_empty_acknowledgment(mock_thread_cls, make_request):
    mock_thread_cls.return_value = MagicMock()
    request = make_request(_addons_request("hello", sender_name="Alice"))
    response = handle_chat(request)
    assert response == {}


@patch("main.threading.Thread")
def test_spawns_background_thread(mock_thread_cls, make_request):
    mock_thread = MagicMock()
    mock_thread_cls.return_value = mock_thread
    request = make_request(_addons_request("hello", sender_name="Alice", space_name="spaces/S"))
    handle_chat(request)
    mock_thread_cls.assert_called_once()
    mock_thread.start.assert_called_once()


@patch("main.threading.Thread")
def test_thread_receives_correct_args(mock_thread_cls, make_request):
    mock_thread_cls.return_value = MagicMock()
    request = make_request(_addons_request(
        "hello", sender_name="Alice", space_name="spaces/S", message_name="spaces/S/messages/U"
    ))
    handle_chat(request)
    kwargs = mock_thread_cls.call_args[1]
    assert kwargs["args"] == ("spaces/S", "hello", "Alice", "spaces/S/messages/U")


@patch("main.threading.Thread")
def test_no_thread_without_space_name(mock_thread_cls, make_request):
    payload = {"chat": {"messagePayload": {"message": {"text": "hi"}}}}
    request = make_request(payload)
    handle_chat(request)
    mock_thread_cls.assert_not_called()
