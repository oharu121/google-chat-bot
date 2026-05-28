def build_thinking_card():
    return {
        "cardsV2": [{
            "cardId": "thinking-card",
            "card": {
                "header": {"title": "Thinking..."},
                "sections": [{
                    "widgets": [{
                        "textParagraph": {"text": "Processing your request..."}
                    }]
                }]
            }
        }]
    }


def build_result_card(text, sender=None):
    header = {"title": "Result"}
    if sender:
        header["subtitle"] = f"Response to {sender}"
    return {
        "cardsV2": [{
            "cardId": "result-card",
            "card": {
                "header": header,
                "sections": [{
                    "widgets": [{
                        "textParagraph": {"text": text}
                    }]
                }]
            }
        }]
    }


def build_error_card(error_message):
    return {
        "cardsV2": [{
            "cardId": "error-card",
            "card": {
                "header": {"title": "Error"},
                "sections": [{
                    "widgets": [{
                        "textParagraph": {"text": error_message}
                    }]
                }]
            }
        }]
    }


def build_progressive_card(state, message_name=None):
    from models import PipelineStatus

    sections = [_build_status_steps_section(state)]

    if state.content_paragraphs:
        sections.append(_build_content_section(state.content_paragraphs))

    if state.status == PipelineStatus.COMPLETED:
        sections.append(_build_feedback_section(message_name))

    return {
        "cardsV2": [{
            "cardId": "progressive-card",
            "card": {
                "sections": sections,
            }
        }]
    }


def _build_status_steps_section(state):
    from models import STEP_STATUS_ICONS, STEP_STATUS_COLORS

    status_text = state.current_step_description or "Starting..."
    widgets = [{"decoratedText": {"text": status_text}}]

    for step in state.steps:
        icon = STEP_STATUS_ICONS[step.status]
        color = STEP_STATUS_COLORS[step.status]
        label = step.label
        if step.detail:
            label = f"{label}: {step.detail}"
        text = f'<font color="{color}">{icon} {label}</font>'
        widgets.append({"decoratedText": {"text": text}})

    return {
        "collapsible": True,
        "uncollapsibleWidgetsCount": 1,
        "widgets": widgets,
    }


def _build_content_section(paragraphs):
    widgets = [{"textParagraph": {"text": p}} for p in paragraphs]
    return {"widgets": widgets}


def _build_feedback_section(message_name):
    msg_id = message_name or ""
    return {
        "widgets": [{
            "buttonList": {
                "buttons": [
                    {
                        "text": "Helpful",
                        "onClick": {
                            "action": {
                                "function": "feedback",
                                "parameters": [
                                    {"key": "vote", "value": "up"},
                                    {"key": "message_id", "value": msg_id},
                                ],
                            }
                        },
                    },
                    {
                        "text": "Not helpful",
                        "onClick": {
                            "action": {
                                "function": "feedback",
                                "parameters": [
                                    {"key": "vote", "value": "down"},
                                    {"key": "message_id", "value": msg_id},
                                ],
                            }
                        },
                    },
                ]
            }
        }]
    }
