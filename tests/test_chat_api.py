from unittest.mock import MagicMock

import pytest

from chat_api import ChatApiClient


@pytest.fixture
def mock_service():
    return MagicMock()


@pytest.fixture
def client(mock_service):
    return ChatApiClient(service=mock_service)


class TestCreateMessage:
    def test_returns_message_name(self, client, mock_service):
        mock_service.spaces().messages().create().execute.return_value = {
            "name": "spaces/S/messages/M"
        }
        name = client.create_message("spaces/S", {"text": "hi"})
        assert name == "spaces/S/messages/M"

    def test_calls_api_with_correct_args(self, client, mock_service):
        mock_service.spaces().messages().create().execute.return_value = {
            "name": "spaces/S/messages/M"
        }
        body = {"text": "hello"}
        client.create_message("spaces/S", body)
        mock_service.spaces().messages().create.assert_called_with(
            parent="spaces/S", body=body
        )


class TestPatchMessage:
    def test_calls_api_with_correct_args(self, client, mock_service):
        mock_service.spaces().messages().patch().execute.return_value = {}
        body = {"cardsV2": []}
        client.patch_message("spaces/S/messages/M", body, "cardsV2")
        mock_service.spaces().messages().patch.assert_called_with(
            name="spaces/S/messages/M", updateMask="cardsV2", body=body
        )

    def test_returns_response(self, client, mock_service):
        expected = {"name": "spaces/S/messages/M", "text": "updated"}
        mock_service.spaces().messages().patch().execute.return_value = expected
        result = client.patch_message("spaces/S/messages/M", {}, "text")
        assert result == expected


class TestAddReaction:
    def test_calls_api_with_correct_args(self, client, mock_service):
        mock_service.spaces().messages().reactions().create().execute.return_value = {}
        client.add_reaction("spaces/S/messages/M", "👀")
        mock_service.spaces().messages().reactions().create.assert_called_with(
            parent="spaces/S/messages/M",
            body={"emoji": {"unicode": "👀"}},
        )

    def test_returns_response(self, client, mock_service):
        expected = {"name": "spaces/S/messages/M/reactions/R", "emoji": {"unicode": "👀"}}
        mock_service.spaces().messages().reactions().create().execute.return_value = expected
        result = client.add_reaction("spaces/S/messages/M", "👀")
        assert result == expected
