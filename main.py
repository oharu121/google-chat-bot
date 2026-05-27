import functions_framework


@functions_framework.http
def handle_chat(request):
    """Google Chat bot entry point."""
    body = request.get_json(silent=True)

    if not body:
        return {"text": "Empty request"}

    message = body.get("message", {})
    user_text = message.get("text", "")
    sender = message.get("sender", {}).get("displayName", "someone")

    return {"text": f"Hello {sender}! You said: {user_text}"}
