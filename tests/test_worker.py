from unittest.mock import MagicMock, patch

import pytest

from worker import process_message


@pytest.fixture
def mock_client():
    client = MagicMock()
    client.create_message.return_value = "spaces/S/messages/M"
    return client


class TestProcessMessage:
    @patch("worker.ThrottledPatcher")
    def test_creates_progressive_card(self, MockPatcher, mock_client):
        process_message("spaces/S", "hello", "Alice", chat_client=mock_client)
        mock_client.create_message.assert_called_once()
        args = mock_client.create_message.call_args
        assert args[0][0] == "spaces/S"
        body = args[0][1]
        assert "cardsV2" in body
        assert body["cardsV2"][0]["cardId"] == "progressive-card"

    @patch("worker.ThrottledPatcher")
    def test_patches_with_completed_card(self, MockPatcher, mock_client):
        patcher_instance = MockPatcher.return_value
        process_message("spaces/S", "hello", "Alice", chat_client=mock_client)
        force_calls = [c for c in patcher_instance.patch.call_args_list if c[1].get("force")]
        assert len(force_calls) >= 1
        final_body = force_calls[-1][0][0]
        assert "cardsV2" in final_body
        assert final_body["cardsV2"][0]["cardId"] == "progressive-card"

    @patch("worker.ThrottledPatcher")
    def test_result_contains_multiple_paragraphs(self, MockPatcher, mock_client):
        patcher_instance = MockPatcher.return_value
        process_message("spaces/S", "hello", "Alice", chat_client=mock_client)
        force_calls = [c for c in patcher_instance.patch.call_args_list if c[1].get("force")]
        final_body = force_calls[-1][0][0]
        sections = final_body["cardsV2"][0]["card"]["sections"]
        # Content section is after the combined status+steps section
        content_section = sections[1]
        paragraphs = [w["textParagraph"]["text"] for w in content_section["widgets"]]
        assert len(paragraphs) >= 3

    @patch("worker.ThrottledPatcher")
    def test_create_failure_skips_patch(self, MockPatcher, mock_client):
        mock_client.create_message.side_effect = Exception("API error")
        process_message("spaces/S", "hello", "Alice", chat_client=mock_client)
        MockPatcher.assert_not_called()

    @patch("worker.ThrottledPatcher")
    def test_patch_failure_does_not_crash(self, MockPatcher, mock_client):
        patcher_instance = MockPatcher.return_value
        patcher_instance.patch.side_effect = Exception("Patch failed")
        process_message("spaces/S", "hello", "Alice", chat_client=mock_client)

    @patch("worker.ThrottledPatcher")
    def test_flush_called_at_end(self, MockPatcher, mock_client):
        patcher_instance = MockPatcher.return_value
        process_message("spaces/S", "hello", "Alice", chat_client=mock_client)
        patcher_instance.flush.assert_called_once()

    @patch("worker.ThrottledPatcher")
    def test_four_steps_all_completed(self, MockPatcher, mock_client):
        patcher_instance = MockPatcher.return_value
        process_message("spaces/S", "hello", "Alice", chat_client=mock_client)
        force_calls = [c for c in patcher_instance.patch.call_args_list if c[1].get("force")]
        final_body = force_calls[-1][0][0]
        sections = final_body["cardsV2"][0]["card"]["sections"]
        combined_section = sections[0]
        # widgets[0] is status, widgets[1:] are steps
        step_widgets = combined_section["widgets"][1:]
        assert len(step_widgets) == 4
        for widget in step_widgets:
            assert "✅" in widget["decoratedText"]["text"]

    @patch("worker.ThrottledPatcher")
    def test_final_status_shows_steps_completed(self, MockPatcher, mock_client):
        patcher_instance = MockPatcher.return_value
        process_message("spaces/S", "hello", "Alice", chat_client=mock_client)
        force_calls = [c for c in patcher_instance.patch.call_args_list if c[1].get("force")]
        final_body = force_calls[-1][0][0]
        sections = final_body["cardsV2"][0]["card"]["sections"]
        status_text = sections[0]["widgets"][0]["decoratedText"]["text"]
        assert "4" in status_text
        assert "ステップ完了" in status_text

    @patch("worker.ThrottledPatcher")
    def test_japanese_step_labels(self, MockPatcher, mock_client):
        patcher_instance = MockPatcher.return_value
        process_message("spaces/S", "hello", "Alice", chat_client=mock_client)
        force_calls = [c for c in patcher_instance.patch.call_args_list if c[1].get("force")]
        final_body = force_calls[-1][0][0]
        sections = final_body["cardsV2"][0]["card"]["sections"]
        step_widgets = sections[0]["widgets"][1:]
        step_texts = [w["decoratedText"]["text"] for w in step_widgets]
        combined = " ".join(step_texts)
        assert "問い合わせを解析中" in combined
        assert "検索クエリを作成中" in combined
        assert "ナレッジベースを検索中" in combined
        assert "回答を生成中" in combined

    @patch("worker.ThrottledPatcher")
    def test_feedback_buttons_in_final_card(self, MockPatcher, mock_client):
        patcher_instance = MockPatcher.return_value
        process_message("spaces/S", "hello", "Alice", chat_client=mock_client)
        force_calls = [c for c in patcher_instance.patch.call_args_list if c[1].get("force")]
        final_body = force_calls[-1][0][0]
        sections = final_body["cardsV2"][0]["card"]["sections"]
        has_buttons = any(
            "buttonList" in w
            for s in sections
            for w in s.get("widgets", [])
        )
        assert has_buttons

    @patch("worker.ThrottledPatcher")
    def test_patcher_constructed_with_message_name(self, MockPatcher, mock_client):
        process_message("spaces/S", "hello", "Alice", chat_client=mock_client)
        MockPatcher.assert_called_once_with(mock_client, "spaces/S/messages/M")

