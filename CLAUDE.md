# Project: Google Chat Bot

## GCP Setup
- GCP account, project ID, and ADC are all configured via `gcloud` CLI
- Default compute service account: `1048379142203-compute@developer.gserviceaccount.com`

## Deployment
- Cloud Functions 2nd gen (Cloud Run-based), region `asia-northeast1`
- Cloud Run is uv-native: always deploy directly from `pyproject.toml` + `uv.lock`. Never export or generate `requirements.txt`
- Always deploy with `--no-allow-unauthenticated`
- Deploy command (two steps):
  ```
  gcloud functions deploy google-chat-bot --gen2 --runtime=python314 --region=asia-northeast1 --source=. --entry-point=handle_chat --trigger-http --no-allow-unauthenticated --memory=512Mi --cpu=1
  gcloud run services update google-chat-bot --region=asia-northeast1 --no-cpu-throttling
  ```
- `--no-cpu-throttling` is required because the bot uses background threads for progressive card updates. CPU throttling freezes threads after the HTTP response returns.
- `--cpu=1` is the minimum required for `--no-cpu-throttling`.

## Chat API
- `chat_discovery.json` is a bundled static discovery document for the Chat API v1. This avoids a ~2 min network download on cold start. Re-download periodically if Google updates the API:
  ```
  curl -o chat_discovery.json 'https://chat.googleapis.com/$discovery/rest?version=v1'
  ```

## Package Management
- Use `uv` for all Python package management (not pip)
- Use `uv run` to execute commands in the project venv

## Research Before Assuming
- GCP services evolve fast. Always WebSearch or use context7 to verify current capabilities before making claims about supported runtimes, API features, deployment options, or service limitations.
- Past mistakes from stale knowledge: assumed Cloud Run requires `requirements.txt` (it natively supports uv), assumed Cloud Functions only supports up to python313 (python314 is GA).
- When in doubt, search first — don't trust training data for GCP specifics.
