# Google Chat Echo Bot

Minimal Google Chat bot running on Cloud Functions (2nd gen) with Python and uv.

## Stack

- Python 3.14
- Cloud Functions 2nd gen (asia-northeast1)
- uv (package manager)
- functions-framework

## Setup

```bash
# Install dependencies
uv sync

# Run locally
uv run functions-framework --target=handle_chat --port=8080

# Test locally
curl -X POST http://localhost:8080 \
  -H "Content-Type: application/json" \
  -d '{"chat": {"messagePayload": {"message": {"text": "hello", "sender": {"displayName": "Test"}}}}}'
```

## Deploy

```bash
gcloud functions deploy google-chat-bot \
  --gen2 \
  --runtime=python314 \
  --region=asia-northeast1 \
  --source=. \
  --entry-point=handle_chat \
  --trigger-http \
  --allow-unauthenticated
```

Then configure the bot in [Google Chat API Configuration](https://console.cloud.google.com/apis/api/chat.googleapis.com/hangouts-chat).

## Note

Google Chat HTTP endpoints now use the **Google Workspace Add-ons** format:

- Request: message is at `body["chat"]["messagePayload"]["message"]`
- Response: must be wrapped in `hostAppDataAction.chatDataAction.createMessageAction.message`

The older `{"text": "..."}` response format no longer works.
