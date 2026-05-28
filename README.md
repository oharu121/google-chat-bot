# Google Chat Bot

Google Chat bot with cardsV2 thinking-to-patch pattern, running on Cloud Functions (2nd gen) with Python and uv.

When a user sends a message, the bot immediately shows a "Thinking..." card, then patches it with the final result — simulating progress updates since Google Chat doesn't support streaming.

## Stack

- Python 3.12
- Cloud Functions 2nd gen (asia-northeast1)
- uv (package manager)
- functions-framework
- google-api-python-client + google-auth

## Architecture

```
main.py          → HTTP handler (returns {}, spawns thread)
worker.py        → Orchestration: thinking card → work → patch result
cards.py         → Pure cardsV2 builder functions
chat_api.py      → Chat API wrapper with DI for testability
```

## Setup

```bash
# Install dependencies
uv sync

# Run tests
uv run pytest -v

# Run locally
uv run functions-framework --target=handle_chat --port=8080
```

## Deploy

```bash
gcloud functions deploy google-chat-bot \
  --gen2 \
  --runtime=python312 \
  --region=asia-northeast1 \
  --source=. \
  --entry-point=handle_chat \
  --trigger-http \
  --no-allow-unauthenticated
```

Then configure the bot in [Google Chat API Configuration](https://console.cloud.google.com/apis/api/chat.googleapis.com/hangouts-chat).

## Note

Google Chat HTTP endpoints now use the **Google Workspace Add-ons** format:

- Request: message is at `body["chat"]["messagePayload"]["message"]`
- Response: must be wrapped in `hostAppDataAction.chatDataAction.createMessageAction.message`

The older `{"text": "..."}` response format no longer works.
