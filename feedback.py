import logging

logger = logging.getLogger(__name__)


def handle_card_click(event_body):
    common_event = event_body.get("commonEventObject", {})
    params = common_event.get("parameters", {})
    user = event_body.get("user", {})
    if not user:
        chat = event_body.get("chat", {})
        user = chat.get("user", {})

    vote = params.get("vote", "unknown")
    message_id = params.get("message_id", "unknown")
    user_name = user.get("displayName", "unknown")

    logger.info("Feedback: vote=%s user=%s message=%s", vote, user_name, message_id)

    return {
        "actionResponse": {"type": "UPDATE_MESSAGE"},
        "cardsV2": [{
            "cardId": "progressive-card",
            "card": {
                "sections": [{
                    "widgets": [{
                        "textParagraph": {
                            "text": "フィードバックありがとうございます！"
                        }
                    }]
                }]
            }
        }],
    }
