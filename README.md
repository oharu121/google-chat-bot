# Google Chat Bot

Google Chat bot with progressive cardsV2 updates, running on Cloud Functions (2nd gen) with Python and uv.

When a user sends a message, the bot shows a progressive card that updates in real-time through pipeline steps (analyze, build query, search KB, generate answer), with a collapsible step accordion and feedback buttons on completion.

## Stack

- Python 3.14
- Cloud Functions 2nd gen (asia-northeast1, `--no-cpu-throttling`)
- uv (package manager)
- functions-framework
- google-api-python-client + google-auth

## Architecture

```
main.py              → HTTP handler (returns {}, spawns thread, routes CARD_CLICKED)
worker.py            → Pipeline orchestration with step tracking
cards.py             → cardsV2 builders (progressive card, thinking, result, error)
models.py            → Pipeline data model (StepStatus, PipelineState)
throttle.py          → Rate-limit-aware patcher (1 write/sec/space)
feedback.py          → CARD_CLICKED event handler (thumbs up/down)
chat_api.py          → Chat API wrapper with static discovery doc
chat_discovery.json  → Bundled Chat API v1 discovery document
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
# Step 1: Deploy function
gcloud functions deploy google-chat-bot \
  --gen2 \
  --runtime=python314 \
  --region=asia-northeast1 \
  --source=. \
  --entry-point=handle_chat \
  --trigger-http \
  --no-allow-unauthenticated \
  --memory=512Mi \
  --cpu=1

# Step 2: Disable CPU throttling (required for background threads)
gcloud run services update google-chat-bot \
  --region=asia-northeast1 \
  --no-cpu-throttling
```

Then configure the bot in [Google Chat API Configuration](https://console.cloud.google.com/apis/api/chat.googleapis.com/hangouts-chat).

## Note

Google Chat HTTP endpoints now use the **Google Workspace Add-ons** format:

- Request: message is at `body["chat"]["messagePayload"]["message"]`
- Response: must be wrapped in `hostAppDataAction.chatDataAction.createMessageAction.message`
- Button clicks: CARD_CLICKED responses use `actionResponse: {type: "UPDATE_MESSAGE"}` with top-level `cardsV2` (not `renderActions` or `updateMessageAction`)
- Button `action.function` must be the full endpoint HTTPS URL (not a function name)

The older `{"text": "..."}` response format no longer works.
