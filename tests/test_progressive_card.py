from models import PipelineState, PipelineStatus, Step, StepStatus
from cards import build_progressive_card


def _make_state(**kwargs):
    defaults = dict(
        steps=[
            Step(id="analyze", label="Analyzing user query"),
            Step(id="fetch_kb", label="Fetching knowledge base"),
            Step(id="generate", label="Generating answer"),
        ],
    )
    defaults.update(kwargs)
    return PipelineState(**defaults)


class TestCardStructure:
    def test_returns_cardsv2_structure(self):
        state = _make_state()
        result = build_progressive_card(state)
        assert "cardsV2" in result
        assert len(result["cardsV2"]) == 1

    def test_card_id_is_progressive(self):
        state = _make_state()
        result = build_progressive_card(state)
        assert result["cardsV2"][0]["cardId"] == "progressive-card"

    def test_no_header(self):
        state = _make_state()
        result = build_progressive_card(state)
        assert "header" not in result["cardsV2"][0]["card"]


class TestCombinedStatusStepsSection:
    def test_first_section_is_collapsible(self):
        state = _make_state()
        result = build_progressive_card(state)
        first_section = result["cardsV2"][0]["card"]["sections"][0]
        assert first_section.get("collapsible") is True

    def test_status_widget_is_uncollapsible(self):
        state = _make_state()
        result = build_progressive_card(state)
        first_section = result["cardsV2"][0]["card"]["sections"][0]
        assert first_section.get("uncollapsibleWidgetsCount") == 1

    def test_status_shows_current_step_description(self):
        state = _make_state(current_step_description="Fetching KB")
        result = build_progressive_card(state)
        first_section = result["cardsV2"][0]["card"]["sections"][0]
        status_widget = first_section["widgets"][0]
        assert "Fetching KB" in status_widget["decoratedText"]["text"]

    def test_status_shows_starting_when_empty(self):
        state = _make_state(current_step_description="")
        result = build_progressive_card(state)
        first_section = result["cardsV2"][0]["card"]["sections"][0]
        status_widget = first_section["widgets"][0]
        assert status_widget["decoratedText"]["text"]  # not empty

    def test_widget_count_is_status_plus_steps(self):
        state = _make_state()
        result = build_progressive_card(state)
        first_section = result["cardsV2"][0]["card"]["sections"][0]
        # 1 status widget + 3 step widgets
        assert len(first_section["widgets"]) == 4

    def test_completed_step_has_check_icon(self):
        state = _make_state()
        state.steps[0].status = StepStatus.COMPLETED
        result = build_progressive_card(state)
        first_section = result["cardsV2"][0]["card"]["sections"][0]
        # step widgets start at index 1
        step_text = first_section["widgets"][1]["decoratedText"]["text"]
        assert "✅" in step_text

    def test_in_progress_step_has_clock_icon(self):
        state = _make_state()
        state.steps[1].status = StepStatus.IN_PROGRESS
        result = build_progressive_card(state)
        first_section = result["cardsV2"][0]["card"]["sections"][0]
        step_text = first_section["widgets"][2]["decoratedText"]["text"]
        assert "⏳" in step_text

    def test_pending_step_has_grey_icon(self):
        state = _make_state()
        result = build_progressive_card(state)
        first_section = result["cardsV2"][0]["card"]["sections"][0]
        step_text = first_section["widgets"][1]["decoratedText"]["text"]
        assert "⬜" in step_text

    def test_step_with_detail_shows_detail(self):
        state = _make_state()
        state.steps[1].detail = "query: how to reset"
        result = build_progressive_card(state)
        first_section = result["cardsV2"][0]["card"]["sections"][0]
        step_text = first_section["widgets"][2]["decoratedText"]["text"]
        assert "how to reset" in step_text

    def test_step_colors_use_font_tag(self):
        state = _make_state()
        state.steps[0].status = StepStatus.COMPLETED
        result = build_progressive_card(state)
        first_section = result["cardsV2"][0]["card"]["sections"][0]
        step_text = first_section["widgets"][1]["decoratedText"]["text"]
        assert "<font color=" in step_text


class TestContentSection:
    def test_omitted_when_no_paragraphs(self):
        state = _make_state(content_paragraphs=[])
        result = build_progressive_card(state)
        sections = result["cardsV2"][0]["card"]["sections"]
        # Only the combined status+steps section
        assert len(sections) == 1

    def test_present_with_paragraphs(self):
        state = _make_state(content_paragraphs=["Hello world"])
        result = build_progressive_card(state)
        sections = result["cardsV2"][0]["card"]["sections"]
        assert len(sections) >= 2

    def test_each_paragraph_is_separate_widget(self):
        state = _make_state(content_paragraphs=["First", "Second", "Third"])
        result = build_progressive_card(state)
        content_section = result["cardsV2"][0]["card"]["sections"][1]
        assert len(content_section["widgets"]) == 3

    def test_paragraph_text_in_widgets(self):
        state = _make_state(content_paragraphs=["Hello world"])
        result = build_progressive_card(state)
        content_section = result["cardsV2"][0]["card"]["sections"][1]
        text = content_section["widgets"][0]["textParagraph"]["text"]
        assert text == "Hello world"


class TestFeedbackSection:
    def test_omitted_when_processing(self):
        state = _make_state(status=PipelineStatus.PROCESSING)
        result = build_progressive_card(state)
        assert not _has_feedback_buttons(result)

    def test_present_when_completed(self):
        state = _make_state(status=PipelineStatus.COMPLETED)
        result = build_progressive_card(state, message_name="spaces/S/messages/M")
        assert _has_feedback_buttons(result)

    def test_buttons_have_feedback_function(self):
        state = _make_state(status=PipelineStatus.COMPLETED)
        result = build_progressive_card(state, message_name="spaces/S/messages/M")
        buttons = _get_feedback_buttons(result)
        for btn in buttons:
            assert btn["onClick"]["action"]["function"] == "feedback"

    def test_buttons_have_vote_params(self):
        state = _make_state(status=PipelineStatus.COMPLETED)
        result = build_progressive_card(state, message_name="spaces/S/messages/M")
        buttons = _get_feedback_buttons(result)
        votes = set()
        for btn in buttons:
            params = btn["onClick"]["action"]["parameters"]
            for p in params:
                if p["key"] == "vote":
                    votes.add(p["value"])
        assert "up" in votes
        assert "down" in votes


# --- Test helpers ---

def _has_feedback_buttons(result):
    sections = result["cardsV2"][0]["card"]["sections"]
    for section in sections:
        for widget in section.get("widgets", []):
            if "buttonList" in widget:
                return True
    return False


def _get_feedback_buttons(result):
    sections = result["cardsV2"][0]["card"]["sections"]
    for section in sections:
        for widget in section.get("widgets", []):
            if "buttonList" in widget:
                return widget["buttonList"]["buttons"]
    return []
