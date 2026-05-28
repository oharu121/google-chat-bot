# Plan: Progressive card UX with step tracking and feedback

**Status:** Completed
**Date:** 2026-05-28

## Context

The Google Chat bot originally used a simple create-then-patch card pattern: a static "Thinking..." card replaced by a final result card. This gave users no visibility into pipeline progress during the several seconds of processing. Additionally, there was no mechanism for users to provide feedback on responses. Cold starts were taking ~2 minutes due to the Chat API discovery document being downloaded over the network on each function cold start, and Cloud Functions Gen 2 CPU throttling was silently freezing background threads after the HTTP response returned.

## Approach

We built a progressive card that updates in real-time as the pipeline advances through discrete steps. Each step transition patches the card via the Chat API, with a rate-limit-aware throttler ensuring we stay within the 1 write/second/space quota. The card uses a collapsible accordion to show step history without cluttering the UI, and adds feedback buttons (thumbs up/down) on completion.

To solve the cold start problem, we bundled a static copy of the Chat API v1 discovery document (`chat_discovery.json`) and use `build_from_document()` instead of the network-dependent `build("chat", "v1")`. This eliminates the ~2 minute network download entirely.

CPU throttling was resolved by deploying with `--cpu=1` and `--no-cpu-throttling`, which keeps the CPU allocated to background threads after the HTTP response returns.

## Changes

### 1. Pipeline Data Model (`models.py` — new)
Added `StepStatus` and `PipelineStatus` enums, `Step` and `PipelineState` dataclasses, and icon/color mapping dicts. Pure data layer with no I/O dependencies.

### 2. Progressive Card Builder (`cards.py` — modified)
Added `build_progressive_card(state, message_name)` with helper functions:
- `_build_status_steps_section()` — combined collapsible section with status text as the uncollapsible widget and step history below
- `_build_content_section()` — response paragraphs as separate `textParagraph` widgets
- `_build_feedback_section()` — thumbs up/down `buttonList` with `onClick.action.function: "feedback"`

### 3. Rate-Limit Throttler (`throttle.py` — new)
`ThrottledPatcher` enforces minimum 1-second intervals between API writes. Uses a "latest-wins" buffer strategy — during rapid step transitions, only the most recent state is sent. Supports `force=True` for the final patch and `flush()` for cleanup.

### 4. Feedback Handler (`feedback.py` — new)
Handles `CARD_CLICKED` events routed by `commonEventObject.invokedFunction`. Logs vote/user/message metadata and returns an `updateMessageAction` response replacing the card with an acknowledgment. Uses `hostAppDataAction.chatDataAction.updateMessageAction` format (not `renderActions`, which is for dialogs only).

### 5. Worker Pipeline (`worker.py` — modified)
Restructured `process_message` to use `PipelineState` + `ThrottledPatcher`. Pipeline progresses through 4 Japanese-labeled steps: query analysis, query building, KB search, answer generation. Each step transition patches the card. Final card includes all content paragraphs and feedback buttons.

### 6. Event Routing (`main.py` — modified)
Added `CARD_CLICKED` event routing before the existing message handler. Routes `commonEventObject.invokedFunction == "feedback"` to `feedback.handle_card_click()`.

### 7. Static Discovery Document (`chat_api.py` — modified, `chat_discovery.json` — new)
Replaced `build("chat", "v1")` with `build_from_document()` using a bundled 410KB discovery document. Uses double-checked locking for thread-safe singleton initialization. Removed warmup thread and `is_warm()` helper.

### 8. Deployment Configuration (`CLAUDE.md` — modified)
Updated deploy command to two steps: `gcloud functions deploy` with `--cpu=1 --memory=512Mi`, then `gcloud run services update --no-cpu-throttling`.

## Files Modified

| File | Change |
|------|--------|
| [models.py](models.py) | New — pipeline data model with enums, dataclasses, icon/color mappings |
| [cards.py](cards.py) | Added progressive card builder with collapsible steps section |
| [throttle.py](throttle.py) | New — rate-limit-aware patcher with latest-wins buffer |
| [feedback.py](feedback.py) | New — CARD_CLICKED event handler with updateMessageAction response |
| [worker.py](worker.py) | Restructured pipeline with 4 Japanese steps and ThrottledPatcher |
| [main.py](main.py) | Added CARD_CLICKED event routing |
| [chat_api.py](chat_api.py) | Static discovery doc, removed warmup thread |
| [chat_discovery.json](chat_discovery.json) | New — bundled Chat API v1 discovery document |
| [CLAUDE.md](CLAUDE.md) | Updated deploy command with CPU/throttling settings |
| [tests/test_models.py](tests/test_models.py) | New — 12 tests for data model |
| [tests/test_progressive_card.py](tests/test_progressive_card.py) | New — 21 tests for progressive card |
| [tests/test_throttle.py](tests/test_throttle.py) | New — 9 tests for throttler |
| [tests/test_feedback.py](tests/test_feedback.py) | Updated — 5 tests for feedback handler |
| [tests/test_worker.py](tests/test_worker.py) | Rewritten — 11 tests for new pipeline |
| [tests/test_main.py](tests/test_main.py) | Updated — 10 tests including card click routing |
| [tests/test_chat_api.py](tests/test_chat_api.py) | Updated — 8 tests including discovery doc validation |

## Guard Rails

| Scenario | Behavior |
|----------|----------|
| Google Chat API rate limit exceeded (>1 write/sec/space) | ThrottledPatcher buffers and delays patches to stay within quota |
| Initial card creation fails | Pipeline logs error and returns early — no crash, no orphaned patches |
| Patch fails mid-pipeline | Exception caught, logged, pipeline continues to flush |
| Unknown `invokedFunction` in CARD_CLICKED event | Returns empty `{}` — no error, no crash |
| Missing feedback parameters | Defaults to "unknown" for vote/message_id/user_name |
| CPU throttled after HTTP response | Prevented by `--no-cpu-throttling` deploy flag |
| Cold start with no network | Static discovery doc eliminates network dependency |

## Verification

1. `uv run pytest -v` — all 86 tests pass
2. Deploy with two-step command from CLAUDE.md
3. Send message in Google Chat — card appears immediately with step progress
4. Card updates through 4 steps with collapsible accordion
5. Final card shows response paragraphs + feedback buttons
6. Click feedback button — card replaced with acknowledgment text

## Breaking Changes

- Card IDs changed from "thinking-card"/"result-card" to "progressive-card"
- `is_warm()` removed from `chat_api.py` (was only used internally)
- Deploy command now requires two steps (functions deploy + run services update)
