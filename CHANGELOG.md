# Changelog

## v0.2.0 (2026-05-28)

### Added

- Progressive card UX: real-time step updates through 4-step pipeline with collapsible accordion
- `models.py` — pipeline data model (`StepStatus`, `PipelineStatus`, `Step`, `PipelineState`)
- `throttle.py` — rate-limit-aware patcher (1 write/sec/space, latest-wins buffer)
- `feedback.py` — CARD_CLICKED event handler with thumbs up/down buttons
- `chat_discovery.json` — bundled static Chat API v1 discovery document (eliminates ~2 min cold start)
- 58 new tests (86 total)

### Changed

- `worker.py` — restructured pipeline with `ThrottledPatcher` and 4 Japanese-labeled steps
- `cards.py` — added `build_progressive_card()` with collapsible status/steps section
- `chat_api.py` — uses `build_from_document()` with local discovery doc instead of network download
- `main.py` — routes `CARD_CLICKED` events to feedback handler
- Deploy command now requires `--cpu=1` and `--no-cpu-throttling` for background thread support

### Removed

- `is_warm()` helper from `chat_api.py` (replaced by static discovery doc)
- Warmup thread (no longer needed)

## v0.1.0 (2026-05-28)

### Added

- cardsV2 thinking-to-patch pattern: bot shows "Thinking..." card, then patches with result
- Background threading for async Chat API calls (create + patch)
- `cards.py` — pure cardsV2 builder functions (thinking, result, error)
- `chat_api.py` — Chat API wrapper with dependency injection
- `worker.py` — orchestration: thinking card → work → patch result
- 28 tests covering all modules
- `CLAUDE.md` with deployment preferences
