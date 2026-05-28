# Changelog

## v0.1.0 (2026-05-28)

### Added

- cardsV2 thinking-to-patch pattern: bot shows "Thinking..." card, then patches with result
- Background threading for async Chat API calls (create + patch)
- `cards.py` — pure cardsV2 builder functions (thinking, result, error)
- `chat_api.py` — Chat API wrapper with dependency injection
- `worker.py` — orchestration: thinking card → work → patch result
- 28 tests covering all modules
- `CLAUDE.md` with deployment preferences
