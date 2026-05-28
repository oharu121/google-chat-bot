# Project: Google Chat Bot

## GCP Setup
- GCP account, project ID, and ADC are all configured via `gcloud` CLI
- Default compute service account: `1048379142203-compute@developer.gserviceaccount.com`

## Deployment
- Cloud Functions 2nd gen (Cloud Run-based), region `asia-northeast1`
- Cloud Run is uv-native: always deploy directly from `pyproject.toml` + `uv.lock`. Never export or generate `requirements.txt`
- Always deploy with `--no-allow-unauthenticated`
- Deploy command:
  ```
  gcloud functions deploy google-chat-bot --gen2 --runtime=python312 --region=asia-northeast1 --source=. --entry-point=handle_chat --trigger-http --no-allow-unauthenticated
  ```

## Package Management
- Use `uv` for all Python package management (not pip)
- Use `uv run` to execute commands in the project venv
