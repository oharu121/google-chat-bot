import json
import sys
import threading

import functions_framework

import feedback
from worker import process_message


def create_message(text):
    """Wrap text in the Google Workspace Add-ons response format."""
    return {
        "hostAppDataAction": {
            "chatDataAction": {
                "createMessageAction": {
                    "message": {
                        "text": text,
                    }
                }
            }
        }
    }


@functions_framework.http
def handle_chat(request):
    """Google Chat bot entry point."""
    body = request.get_json(silent=True)
    print(f"REQUEST BODY: {json.dumps(body, ensure_ascii=False) if body else 'None'}", file=sys.stderr, flush=True)

    if not body:
        return create_message("Empty request")

    # Route CARD_CLICKED events
    common_event = body.get("commonEventObject", {})
    invoked_function = common_event.get("invokedFunction")
    if invoked_function:
        if invoked_function == "feedback":
            return feedback.handle_card_click(body)
        return {}

    chat = body.get("chat", {})
    message_payload = chat.get("messagePayload", {})
    message = message_payload.get("message", {})
    space_name = message_payload.get("space", {}).get("name")
    user_message_name = message.get("name")
    user_text = message.get("text", "")
    sender = message.get("sender", {}).get("displayName", "someone")

    if space_name:
        thread = threading.Thread(
            target=process_message,
            args=(space_name, user_text, sender, user_message_name),
        )
        thread.start()

    return {}
