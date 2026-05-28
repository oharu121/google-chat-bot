import logging

from feedback import handle_card_click


def _make_click_event(function_name="feedback", vote="up", message_id="spaces/S/messages/M"):
    return {
        "commonEventObject": {
            "invokedFunction": function_name,
            "parameters": {
                "vote": vote,
                "message_id": message_id,
            },
        },
        "user": {"displayName": "Alice", "name": "users/123"},
    }


class TestHandleCardClick:
    def test_returns_update_message_action_format(self):
        result = handle_card_click(_make_click_event(vote="up"))
        action = result["hostAppDataAction"]["chatDataAction"]["updateMessageAction"]
        assert "message" in action
        assert "cardsV2" in action["message"]

    def test_logs_feedback(self, caplog):
        with caplog.at_level(logging.INFO):
            handle_card_click(_make_click_event(vote="down", message_id="spaces/S/messages/X"))
        assert any("down" in r.message for r in caplog.records)

    def test_handles_missing_parameters(self):
        event = {"commonEventObject": {}, "user": {}}
        result = handle_card_click(event)
        assert isinstance(result, dict)

    def test_acknowledged_text_in_response(self):
        result = handle_card_click(_make_click_event(vote="up"))
        response_str = str(result)
        assert "ありがとう" in response_str

    def test_extracts_user_name(self, caplog):
        with caplog.at_level(logging.INFO):
            handle_card_click(_make_click_event(vote="up"))
        assert any("Alice" in r.message for r in caplog.records)
