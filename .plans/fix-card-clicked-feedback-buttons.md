# Plan: Fix CARD_CLICKED feedback buttons with correct URL and response format

**Status:** Completed
**Date:** 2026-05-29

## Context

After implementing progressive cardsV2 with feedback buttons (v0.2.0), clicking "Helpful" or "Not helpful" produced the error "lin-yuchen-test-bot ではリクエストを処理できません" in Google Chat. No logs appeared on the server — the CARD_CLICKED event never reached the endpoint.

Investigation revealed three independent issues stacked on top of each other. Fixing one exposed the next, making this a particularly frustrating debugging session.

## Approach

Systematic debugging from the outside in: first ensure the event reaches the endpoint (罠1 + 罠2), then ensure the response format is correct (罠3). Each fix was deployed and tested independently.

Additionally, upgraded the Cloud Functions runtime from python312 to python314 after discovering it was GA (previously assumed only python313 was supported — a training-data staleness issue).

## Changes

### 1. `action.function` must be full endpoint URL (罠1)

HTTP-based Workspace Add-ons require `action.function` to be the complete HTTPS endpoint URL, not a function name like `"feedback"`. Google Chat POSTs the CARD_CLICKED event to this URL. Changed `cards._build_feedback_section()` to accept `endpoint_url` parameter and use it as the function value. Routing now uses `commonEventObject.parameters.action` instead of matching `invokedFunction`.

### 2. Endpoint URL construction via `K_SERVICE` (罠2)

Behind Cloud Functions Gen 2 proxy, `request.base_url` returns `http://localhost:8080/` and `request.path` returns `/` (the function name prefix is stripped). Used `X-Forwarded-Host` + `X-Forwarded-Proto` headers for host/scheme, and `K_SERVICE` environment variable (auto-set by Cloud Run) for the function name path segment.

### 3. Response format: `actionResponse` (罠3)

CARD_CLICKED responses must use `{"actionResponse": {"type": "UPDATE_MESSAGE"}, "cardsV2": [...]}`, not `hostAppDataAction.chatDataAction.updateMessageAction` (which is for synchronous message responses) or `renderActions` (which is for dialogs).

### 4. Runtime upgrade to python314

Cloud Functions now supports python314 (GA), which also uses uv as the default package manager. Updated deploy commands in CLAUDE.md and the article.

## Files Modified

| File | Change |
|------|--------|
| main.py | Route CARD_CLICKED by `parameters.action` not `invokedFunction`; construct endpoint URL via `K_SERVICE` env var; pass `endpoint_url` to worker; remove debug logging |
| cards.py | `build_progressive_card()` and `_build_feedback_section()` accept `endpoint_url`; buttons use full URL as `action.function` |
| feedback.py | Response format changed to `actionResponse: {type: "UPDATE_MESSAGE"}` with top-level `cardsV2` |
| worker.py | `process_message()` accepts and forwards `endpoint_url` to final card build |
| tests/conftest.py | `FakeRequest` updated with `headers` dict; removed unused `path` attribute |
| tests/test_main.py | Updated CARD_CLICKED test helpers for URL-based routing |
| tests/test_progressive_card.py | Tests for `endpoint_url` in feedback buttons |
| tests/test_feedback.py | Tests for `actionResponse` format |
| CLAUDE.md | Deploy command updated to `python314`; added "Research Before Assuming" section |

## Guard Rails

| Scenario | Behavior |
|----------|----------|
| `K_SERVICE` env var missing (local dev) | `endpoint_url` becomes empty string; buttons render with empty function (non-functional but doesn't crash) |
| Unknown `action` parameter in CARD_CLICKED | Returns `{}` — no-op |
| `X-Forwarded-Host` header missing | Falls back to `Host` header |

## Verification

1. `uv run pytest -v` — 87 tests pass
2. Deploy: `gcloud functions deploy ... --runtime=python314`
3. Send message in Google Chat — progressive card appears with feedback buttons
4. Click "Helpful" — card updates to "フィードバックありがとうございます！"
5. Check logs: `ENDPOINT_URL` shows full path, CARD_CLICKED event received with correct parameters

## Breaking Changes

None
