from cards import build_thinking_card, build_result_card, build_error_card


class TestBuildThinkingCard:
    def test_returns_cardsv2_structure(self):
        card = build_thinking_card()
        assert "cardsV2" in card
        assert len(card["cardsV2"]) == 1

    def test_has_card_id(self):
        card = build_thinking_card()
        assert card["cardsV2"][0]["cardId"] == "thinking-card"

    def test_header_title(self):
        card = build_thinking_card()
        header = card["cardsV2"][0]["card"]["header"]
        assert header["title"] == "Thinking..."

    def test_has_status_text_in_section(self):
        card = build_thinking_card()
        sections = card["cardsV2"][0]["card"]["sections"]
        assert len(sections) >= 1
        widgets = sections[0]["widgets"]
        assert any("textParagraph" in w for w in widgets)


class TestBuildResultCard:
    def test_contains_result_text(self):
        card = build_result_card("Hello world")
        widgets = card["cardsV2"][0]["card"]["sections"][0]["widgets"]
        texts = [w["textParagraph"]["text"] for w in widgets if "textParagraph" in w]
        assert any("Hello world" in t for t in texts)

    def test_header_indicates_completion(self):
        card = build_result_card("done")
        header = card["cardsV2"][0]["card"]["header"]
        assert "title" in header

    def test_has_card_id(self):
        card = build_result_card("test")
        assert card["cardsV2"][0]["cardId"] == "result-card"

    def test_sender_attribution(self):
        card = build_result_card("hi", sender="Alice")
        header = card["cardsV2"][0]["card"]["header"]
        assert "Alice" in header.get("subtitle", "")


class TestBuildErrorCard:
    def test_contains_error_message(self):
        card = build_error_card("Something broke")
        widgets = card["cardsV2"][0]["card"]["sections"][0]["widgets"]
        texts = [w["textParagraph"]["text"] for w in widgets if "textParagraph" in w]
        assert any("Something broke" in t for t in texts)

    def test_header_indicates_error(self):
        card = build_error_card("fail")
        header = card["cardsV2"][0]["card"]["header"]
        assert "Error" in header["title"] or "error" in header["title"].lower()

    def test_has_card_id(self):
        card = build_error_card("fail")
        assert card["cardsV2"][0]["cardId"] == "error-card"
