from models import (
    StepStatus,
    PipelineStatus,
    Step,
    PipelineState,
    STEP_STATUS_ICONS,
    STEP_STATUS_COLORS,
)


class TestStepStatus:
    def test_has_all_values(self):
        assert set(StepStatus) == {
            StepStatus.PENDING,
            StepStatus.IN_PROGRESS,
            StepStatus.COMPLETED,
            StepStatus.FAILED,
        }


class TestPipelineStatus:
    def test_has_all_values(self):
        assert set(PipelineStatus) == {
            PipelineStatus.PROCESSING,
            PipelineStatus.COMPLETED,
            PipelineStatus.FAILED,
        }


class TestStep:
    def test_default_status_is_pending(self):
        step = Step(id="s1", label="Do thing")
        assert step.status == StepStatus.PENDING

    def test_detail_defaults_to_none(self):
        step = Step(id="s1", label="Do thing")
        assert step.detail is None

    def test_accepts_detail(self):
        step = Step(id="s1", label="Fetch", detail="query: hello")
        assert step.detail == "query: hello"


class TestPipelineState:
    def test_default_content_paragraphs_empty(self):
        state = PipelineState(steps=[])
        assert state.content_paragraphs == []

    def test_default_status_is_processing(self):
        state = PipelineState(steps=[])
        assert state.status == PipelineStatus.PROCESSING

    def test_default_current_step_description_empty(self):
        state = PipelineState(steps=[])
        assert state.current_step_description == ""

    def test_independent_content_paragraphs(self):
        s1 = PipelineState(steps=[])
        s2 = PipelineState(steps=[])
        s1.content_paragraphs.append("hello")
        assert s2.content_paragraphs == []


class TestMappings:
    def test_icons_cover_all_statuses(self):
        for status in StepStatus:
            assert status in STEP_STATUS_ICONS

    def test_colors_cover_all_statuses(self):
        for status in StepStatus:
            assert status in STEP_STATUS_COLORS
