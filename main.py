import json
import os
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

    # Route CARD_CLICKED events (invokedFunction is endpoint URL for HTTP add-ons)
    common_event = body.get("commonEventObject", {})
    if common_event.get("invokedFunction"):
        params = common_event.get("parameters", {})
        if params.get("action") == "feedback":
            return feedback.handle_card_click(body)
        return {}

    chat = body.get("chat", {})
    message_payload = chat.get("messagePayload", {})
    message = message_payload.get("message", {})
    space_name = message_payload.get("space", {}).get("name")
    user_message_name = message.get("name")
    user_text = message.get("text", "")
    sender = message.get("sender", {}).get("displayName", "someone")

    host = request.headers.get("X-Forwarded-Host") or request.headers.get("Host", "")
    scheme = request.headers.get("X-Forwarded-Proto", "https")
    service = os.environ.get("K_SERVICE", "")
    endpoint_url = f"{scheme}://{host}/{service}" if host else ""
    if space_name:
        thread = threading.Thread(
            target=process_message,
            args=(space_name, user_text, sender, user_message_name),
            kwargs={"endpoint_url": endpoint_url},
        )
        thread.start()

    return {}
