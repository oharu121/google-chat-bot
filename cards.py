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
