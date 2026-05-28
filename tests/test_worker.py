from unittest.mock import MagicMock, call

import pytest

from worker import process_message


@pytest.fixture
def mock_client():
    client = MagicMock()
    client.create_message.return_value = "spaces/S/messages/M"
    return client


class TestProcessMessage:
    def test_creates_thinking_card(self, mock_client):
        process_message("spaces/S", "hello", "Alice", chat_client=mock_client)
        mock_client.create_message.assert_called_once()
        args = mock_client.create_message.call_args
        assert args[0][0] == "spaces/S"
        body = args[0][1]
        assert "cardsV2" in body
        assert body["cardsV2"][0]["cardId"] == "thinking-card"

    def test_patches_with_result_card(self, mock_client):
        process_message("spaces/S", "hello", "Alice", chat_client=mock_client)
        mock_client.patch_message.assert_called_once()
        args = mock_client.patch_message.call_args
        assert args[0][0] == "spaces/S/messages/M"
        body = args[0][1]
        assert "cardsV2" in body
        assert body["cardsV2"][0]["cardId"] == "result-card"
        assert args[0][2] == "cardsV2"

    def test_result_contains_echo_text(self, mock_client):
        process_message("spaces/S", "hello", "Alice", chat_client=mock_client)
        body = mock_client.patch_message.call_args[0][1]
        text = body["cardsV2"][0]["card"]["sections"][0]["widgets"][0]["textParagraph"]["text"]
        assert "Alice" in text
        assert "hello" in text

    def test_create_failure_skips_patch(self, mock_client):
        mock_client.create_message.side_effect = Exception("API error")
        process_message("spaces/S", "hello", "Alice", chat_client=mock_client)
        mock_client.patch_message.assert_not_called()

    def test_patch_failure_does_not_crash(self, mock_client):
        mock_client.patch_message.side_effect = Exception("Patch failed")
        process_message("spaces/S", "hello", "Alice", chat_client=mock_client)

    def test_call_order_create_then_patch(self, mock_client):
        process_message("spaces/S", "hi", "Bob", chat_client=mock_client)
        expected_order = [
            call.create_message("spaces/S", mock_client.create_message.call_args[0][1]),
            call.patch_message("spaces/S/messages/M", mock_client.patch_message.call_args[0][1], "cardsV2"),
        ]
        mock_client.assert_has_calls(expected_order)
