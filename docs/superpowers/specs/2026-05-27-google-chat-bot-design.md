# Google Chat Echo Bot — Design Spec

## Overview

Minimum viable Google Chat bot deployed as a Cloud Function (2nd gen) in GCP. Receives messages via HTTPS, replies with an echo greeting.

## Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Runtime | Cloud Functions 2nd gen | Simplest serverless option, zero infra management |
| Language | Python 3.12 | User preference |
| Trigger | HTTPS endpoint | Direct, no extra services (vs Pub/Sub) |
| Region | asia-northeast1 (Tokyo) | User location |
| Package manager | uv | User preference; `requirements.txt` generated via `uv export` for deploy |
| IaC | None (gcloud CLI) | Minimal viable setup, Terraform is overkill at this stage |

## Prerequisites

### 1. Install gcloud CLI

```bash
brew install --cask google-cloud-sdk
```

### 2. Authenticate

```bash
# CLI auth (opens browser)
gcloud auth login

# Application Default Credentials (for local code testing)
gcloud auth application-default login

# Link quota to your project
gcloud auth application-default set-quota-project YOUR_PROJECT_ID
```

### 3. GCP project setup

```bash
# Create project (use your own globally unique ID)
gcloud projects create YOUR_PROJECT_ID --name="Google Chat Bot"
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable cloudfunctions.googleapis.com \
  cloudbuild.googleapis.com \
  chat.googleapis.com \
  run.googleapis.com
```

Billing must be linked to the project via GCP Console.

## Project Structure

```
google-chat-bot/
├── main.py              # Cloud Function entry point
├── pyproject.toml       # uv-managed dependencies
├── uv.lock              # uv lockfile (auto-generated)
├── .python-version      # Python version pin
└── .gitignore           # Ignore generated files
```

`requirements.txt` is generated at deploy time via `uv export` and should be in `.gitignore`.

## Bot Code

### main.py

```python
import functions_framework

@functions_framework.http
def handle_chat(request):
    """Google Chat bot entry point."""
    body = request.get_json(silent=True)

    if not body:
        return {"text": "Empty request"}

    message = body.get("message", {})
    user_text = message.get("text", "")
    sender = message.get("sender", {}).get("displayName", "someone")

    return {"text": f"Hello {sender}! You said: {user_text}"}
```

### pyproject.toml

Managed by `uv`. Single dependency: `functions-framework`.

## Deployment

```bash
# Generate requirements.txt from uv
uv export --format requirements-txt --no-hashes > requirements.txt

# Deploy to Cloud Functions
gcloud functions deploy google-chat-bot \
  --gen2 \
  --runtime=python312 \
  --region=asia-northeast1 \
  --source=. \
  --entry-point=handle_chat \
  --trigger-http \
  --allow-unauthenticated
```

Output URL: `https://asia-northeast1-YOUR_PROJECT_ID.cloudfunctions.net/google-chat-bot`

## Google Chat API Registration (Manual)

1. Go to GCP Console → APIs & Services → Google Chat API → Configuration
2. Fill in:
   - **App name:** Echo Bot
   - **Description:** Echo bot
   - **Functionality:** Check "Receive 1:1 messages"
   - **Connection settings:** HTTP endpoint URL → paste Cloud Function URL
   - **Visibility:** Specific people/groups → add yourself
3. Save

## Testing

1. Open Google Chat (chat.google.com)
2. Start a DM → search for "Echo Bot"
3. Send "hello"
4. Expected reply: "Hello YourName! You said: hello"

## Security Notes

- `--allow-unauthenticated` is used for simplicity. For production, verify incoming requests are from Google Chat using bearer token validation.
- No secrets or API keys are needed for this echo bot.

## Future Improvements (Out of Scope)

- Request authentication (verify Google Chat bearer tokens)
- Slash commands
- Card-based responses
- CI/CD pipeline
- Terraform for infrastructure
