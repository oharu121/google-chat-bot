from dataclasses import dataclass, field
from enum import Enum


class StepStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class PipelineStatus(Enum):
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Step:
    id: str
    label: str
    status: StepStatus = StepStatus.PENDING
    detail: str | None = None


@dataclass
class PipelineState:
    steps: list[Step]
    content_paragraphs: list[str] = field(default_factory=list)
    sender: str | None = None
    status: PipelineStatus = PipelineStatus.PROCESSING
    current_step_description: str = ""


STEP_STATUS_ICONS: dict[StepStatus, str] = {
    StepStatus.PENDING: "⬜",
    StepStatus.IN_PROGRESS: "⏳",
    StepStatus.COMPLETED: "✅",
    StepStatus.FAILED: "❌",
}

STEP_STATUS_COLORS: dict[StepStatus, str] = {
    StepStatus.PENDING: "#9aa0a6",
    StepStatus.IN_PROGRESS: "#1a73e8",
    StepStatus.COMPLETED: "#188038",
    StepStatus.FAILED: "#d93025",
}
