import logging

from cards import build_thinking_card, build_result_card
from chat_api import ChatApiClient

logger = logging.getLogger(__name__)


def process_message(space_name, user_text, sender, user_message_name=None, chat_client=None):
    if chat_client is None:
        chat_client = ChatApiClient()

    if user_message_name:
        try:
            chat_client.add_reaction(user_message_name, "👀")
        except Exception:
            logger.warning("Failed to add reaction", exc_info=True)

    try:
        thinking_body = build_thinking_card()
        message_name = chat_client.create_message(space_name, thinking_body)
    except Exception:
        logger.error("Failed to create thinking card", exc_info=True)
        return

    result_text = f"Hello {sender}! You said: {user_text}"
    result_body = build_result_card(result_text, sender=sender)

    try:
        chat_client.patch_message(message_name, result_body, "cardsV2")
    except Exception:
        logger.error("Failed to patch message with result", exc_info=True)
