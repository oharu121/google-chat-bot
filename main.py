import json
import sys

import functions_framework
from flask import jsonify


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
        return jsonify(create_message("Empty request"))

    chat = body.get("chat", {})
    message_payload = chat.get("messagePayload", {})
    message = message_payload.get("message", {})
    user_text = message.get("text", "")
    sender = message.get("sender", {}).get("displayName", "someone")

    response = create_message(f"Hello {sender}! You said: {user_text}")
    print(f"RESPONSE: {json.dumps(response, ensure_ascii=False)}", file=sys.stderr, flush=True)
    return jsonify(response)
