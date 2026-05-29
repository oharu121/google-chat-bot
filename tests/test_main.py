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


# --- CARD_CLICKED event routing ---

ENDPOINT_URL = "https://asia-northeast1-test.cloudfunctions.net/google-chat-bot"


def _card_click_event(action="feedback", vote="up", message_id="spaces/S/messages/M"):
    """Build a CARD_CLICKED event. invokedFunction is the endpoint URL for HTTP add-ons."""
    return {
        "commonEventObject": {
            "invokedFunction": ENDPOINT_URL,
            "parameters": {
                "action": action,
                "vote": vote,
                "message_id": message_id,
            },
        },
        "user": {"displayName": "Alice", "name": "users/123"},
    }


@patch("main.feedback")
def test_card_click_routes_to_feedback_handler(mock_feedback, make_request):
    mock_feedback.handle_card_click.return_value = {"actionResponse": {"type": "UPDATE_MESSAGE"}}
    request = make_request(_card_click_event())
    handle_chat(request)
    mock_feedback.handle_card_click.assert_called_once()


@patch("main.feedback")
def test_card_click_returns_handler_response(mock_feedback, make_request):
    expected = {"actionResponse": {"type": "UPDATE_MESSAGE"}, "cardsV2": []}
    mock_feedback.handle_card_click.return_value = expected
    request = make_request(_card_click_event())
    result = handle_chat(request)
    assert result == expected


@patch("main.feedback")
def test_unknown_action_returns_empty(mock_feedback, make_request):
    request = make_request(_card_click_event(action="unknown_action"))
    result = handle_chat(request)
    assert result == {}
    mock_feedback.handle_card_click.assert_not_called()


@patch("main.threading.Thread")
def test_card_click_does_not_spawn_thread(mock_thread_cls, make_request):
    request = make_request(_card_click_event())
    handle_chat(request)
    mock_thread_cls.assert_not_called()


@patch("main.threading.Thread")
def test_message_event_ignores_card_click_routing(mock_thread_cls, make_request):
    mock_thread_cls.return_value = MagicMock()
    request = make_request(_addons_request("hello", sender_name="Alice", space_name="spaces/S"))
    handle_chat(request)
    mock_thread_cls.assert_called_once()
