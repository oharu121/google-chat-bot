# Plan: Add cardsV2 thinking-to-patch pattern for Google Chat bot

**Status:** Completed
**Date:** 2026-05-28

## Context

The Google Chat bot originally returned synchronous text-only responses via the Workspace Add-ons format. Google Chat does not support streaming responses, so the bot had no way to show progress while processing a request. The user experience was a silent wait until the final response appeared.

Google's own AI Concepts Codelab demonstrates a pattern using the Chat API's `messages.create()` followed by `messages.patch()` to simulate progress updates — create a "Thinking..." card, then patch it with the final result. This gives users immediate visual feedback that their message was received and is being processed.

The sync HTTP response from a Workspace Add-on does not return the created message's resource name, making it impossible to patch from the sync handler. A different approach was needed.

## Approach

Return an empty `{}` acknowledgment from the sync HTTP handler and spawn a background thread that uses the Chat API directly. Cloud Functions 2nd gen (Cloud Run-based) supports background threads that outlive the HTTP response.

The architecture separates concerns into four layers:
- `cards.py` — Pure functions that build cardsV2 structures (no I/O, trivially testable)
- `chat_api.py` — Thin wrapper around the Google Chat API with dependency injection for testability
- `worker.py` — Orchestration logic: create thinking card, do work, patch with result
- `main.py` — HTTP handler that extracts request data and spawns the worker thread

This layering was chosen over a monolithic handler to enable thorough unit testing at each boundary without requiring real API credentials. The `ChatApiClient` accepts an optional `service` parameter for test injection, avoiding monkeypatching.

An emoji reaction ("read receipt") was initially planned but dropped after discovering that the `chat.bot` OAuth scope does not cover the Reactions API — reactions require user-level OAuth which Chat apps cannot use.

## Changes

### 1. Card builders (`cards.py`)
Added three pure functions: `build_thinking_card()`, `build_result_card(text, sender)`, and `build_error_card(error_message)`. Each returns a valid cardsV2 structure with a unique `cardId` for targeted patching.

### 2. Chat API client (`chat_api.py`)
Created `ChatApiClient` wrapping `spaces().messages().create()`, `.patch()`, and `.reactions().create()`. Constructor accepts optional `service` param for DI. Production default uses `google.auth.default(scopes=['https://www.googleapis.com/auth/chat.bot'])`.

### 3. Background worker (`worker.py`)
`process_message(space_name, user_text, sender, user_message_name, chat_client)` orchestrates: create thinking card → capture message name → build result → patch. Error handling ensures create failure skips patch, and patch failure logs without crashing.

### 4. Handler update (`main.py`)
`handle_chat()` now returns `{}` immediately and spawns a `threading.Thread` targeting `process_message`. Extracts `space_name`, `user_message_name`, `user_text`, and `sender` from the Workspace Add-ons request format.

### 5. Dependencies
Added `google-api-python-client` and `google-auth` to `pyproject.toml`.

### 6. Deployment config (`CLAUDE.md`)
Documented GCP deployment preferences: Cloud Functions 2nd gen, `asia-northeast1`, uv-native (no requirements.txt), `--no-allow-unauthenticated`.

## Files Modified

| File | Change |
|------|--------|
| [cards.py](cards.py) | New — cardsV2 builder functions (thinking, result, error) |
| [chat_api.py](chat_api.py) | New — Chat API wrapper with DI |
| [worker.py](worker.py) | New — Background orchestration: thinking → patch |
| [main.py](main.py) | Updated — returns `{}`, spawns thread, extracts Add-ons fields |
| [pyproject.toml](pyproject.toml) | Updated — added google-api-python-client, google-auth |
| [CLAUDE.md](CLAUDE.md) | New — deployment preferences and GCP config |
| [tests/conftest.py](tests/conftest.py) | New — shared FakeRequest fixture |
| [tests/test_cards.py](tests/test_cards.py) | New — 11 tests for card builders |
| [tests/test_chat_api.py](tests/test_chat_api.py) | New — 6 tests for API client |
| [tests/test_worker.py](tests/test_worker.py) | New — 6 tests for worker orchestration |
| [tests/test_main.py](tests/test_main.py) | Updated — 5 tests for Add-ons format |

## Guard Rails

| Scenario | Behavior |
|----------|----------|
| Chat API `create_message` fails | Worker logs error and returns early; no patch attempted |
| Chat API `patch_message` fails | Worker logs error; thinking card remains visible but doesn't crash |
| Request has no `space_name` | No thread spawned; handler returns `{}` silently |
| Empty request body | Returns Add-ons format message: "Empty request" |

## Verification

1. Run `uv run pytest -v` — all 28 tests pass
2. Deploy: `gcloud functions deploy google-chat-bot --gen2 --runtime=python312 --region=asia-northeast1 --source=. --entry-point=handle_chat --trigger-http --no-allow-unauthenticated`
3. Send a message in Google Chat — thinking card appears, then patches to result card with sender attribution

## Breaking Changes

None — this is a greenfield feature on a new bot.
