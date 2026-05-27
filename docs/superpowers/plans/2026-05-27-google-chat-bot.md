# Google Chat Echo Bot Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deploy a minimal echo bot to Google Cloud Functions that responds to Google Chat messages.

**Architecture:** Single Python Cloud Function (2nd gen) receives HTTPS POST from Google Chat, extracts sender name and message text, returns a greeting. Managed with `uv`, deployed via `gcloud`.

**Tech Stack:** Python 3.12, functions-framework, uv, gcloud CLI, Cloud Functions 2nd gen

---

## File Structure

| File | Responsibility |
|------|---------------|
| `main.py` | Cloud Function entry point — handles incoming Chat requests |
| `pyproject.toml` | uv project config and dependencies |
| `.python-version` | Pins Python 3.12 |
| `.gitignore` | Ignores generated files (`requirements.txt`, `.venv`, etc.) |
| `tests/test_main.py` | Unit tests for the handler function |

---

### Task 1: Initialize uv project

**Files:**
- Create: `pyproject.toml`
- Create: `.python-version`
- Create: `.gitignore`

- [ ] **Step 1: Initialize project with uv**

```bash
cd /Users/lin.yuchen/Developer/work/google-chat-bot
uv init --no-readme
```

This creates `pyproject.toml`, `.python-version`, and `hello.py` (which we'll delete).

- [ ] **Step 2: Clean up generated hello.py**

```bash
rm -f /Users/lin.yuchen/Developer/work/google-chat-bot/hello.py
```

- [ ] **Step 3: Add dependencies**

```bash
cd /Users/lin.yuchen/Developer/work/google-chat-bot
uv add functions-framework
uv add --dev pytest
```

- [ ] **Step 4: Set up .gitignore**

Create `.gitignore` with:

```
.venv/
__pycache__/
*.pyc
requirements.txt
.python-version
uv.lock
```

- [ ] **Step 5: Verify uv setup**

```bash
cd /Users/lin.yuchen/Developer/work/google-chat-bot
uv run python -c "import functions_framework; print('OK')"
```

Expected: `OK`

- [ ] **Step 6: Initialize git and commit**

```bash
cd /Users/lin.yuchen/Developer/work/google-chat-bot
git init
git add pyproject.toml .gitignore
git commit -m "chore: initialize uv project with functions-framework"
```

---

### Task 2: Write failing test for handle_chat

**Files:**
- Create: `tests/__init__.py`
- Create: `tests/test_main.py`

- [ ] **Step 1: Create test directory**

```bash
mkdir -p /Users/lin.yuchen/Developer/work/google-chat-bot/tests
touch /Users/lin.yuchen/Developer/work/google-chat-bot/tests/__init__.py
```

- [ ] **Step 2: Write the test file**

Create `tests/test_main.py`:

```python
import json


class FakeRequest:
    """Mimics a Flask request object for testing."""

    def __init__(self, data):
        self._data = data

    def get_json(self, silent=False):
        return self._data


def test_echo_reply():
    from main import handle_chat

    request = FakeRequest({
        "message": {
            "text": "hello",
            "sender": {"displayName": "Alice"},
        }
    })
    response = handle_chat(request)
    assert response == {"text": "Hello Alice! You said: hello"}


def test_empty_request():
    from main import handle_chat

    request = FakeRequest(None)
    response = handle_chat(request)
    assert response == {"text": "Empty request"}


def test_missing_sender():
    from main import handle_chat

    request = FakeRequest({
        "message": {
            "text": "hi",
        }
    })
    response = handle_chat(request)
    assert response == {"text": "Hello someone! You said: hi"}
```

- [ ] **Step 3: Run tests to verify they fail**

```bash
cd /Users/lin.yuchen/Developer/work/google-chat-bot
uv run pytest tests/test_main.py -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'main'`

- [ ] **Step 4: Commit test file**

```bash
cd /Users/lin.yuchen/Developer/work/google-chat-bot
git add tests/
git commit -m "test: add failing tests for handle_chat"
```

---

### Task 3: Implement handle_chat to pass tests

**Files:**
- Create: `main.py`

- [ ] **Step 1: Write main.py**

Create `main.py`:

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

- [ ] **Step 2: Run tests to verify they pass**

```bash
cd /Users/lin.yuchen/Developer/work/google-chat-bot
uv run pytest tests/test_main.py -v
```

Expected: 3 passed

- [ ] **Step 3: Commit**

```bash
cd /Users/lin.yuchen/Developer/work/google-chat-bot
git add main.py
git commit -m "feat: implement echo bot handler"
```

---

### Task 4: Local smoke test with functions-framework

**Files:** None (manual verification)

- [ ] **Step 1: Start local server**

```bash
cd /Users/lin.yuchen/Developer/work/google-chat-bot
uv run functions-framework --target=handle_chat --port=8080
```

This starts a local HTTP server on port 8080.

- [ ] **Step 2: Send a test request (in a separate terminal)**

```bash
curl -X POST http://localhost:8080 \
  -H "Content-Type: application/json" \
  -d '{"message": {"text": "hello", "sender": {"displayName": "Test User"}}}'
```

Expected response:

```json
{"text": "Hello Test User! You said: hello"}
```

- [ ] **Step 3: Stop the local server**

Press `Ctrl+C` in the terminal running the server.

---

### Task 5: Deploy to Cloud Functions

**Files:** None (CLI commands only)

- [ ] **Step 1: Generate requirements.txt**

```bash
cd /Users/lin.yuchen/Developer/work/google-chat-bot
uv export --format requirements-txt --no-hashes > requirements.txt
```

- [ ] **Step 2: Deploy**

```bash
cd /Users/lin.yuchen/Developer/work/google-chat-bot
gcloud functions deploy google-chat-bot \
  --gen2 \
  --runtime=python312 \
  --region=asia-northeast1 \
  --source=. \
  --entry-point=handle_chat \
  --trigger-http \
  --allow-unauthenticated
```

Wait for deploy to complete (~1-2 minutes). Note the output URL.

- [ ] **Step 3: Verify deployment with curl**

```bash
curl -X POST YOUR_FUNCTION_URL \
  -H "Content-Type: application/json" \
  -d '{"message": {"text": "hello", "sender": {"displayName": "Test User"}}}'
```

Replace `YOUR_FUNCTION_URL` with the URL from the deploy output.

Expected response:

```json
{"text": "Hello Test User! You said: hello"}
```

- [ ] **Step 4: Clean up generated file and commit**

```bash
cd /Users/lin.yuchen/Developer/work/google-chat-bot
rm requirements.txt
git add -A
git commit -m "chore: deployment verified"
```

---

### Task 6: Register bot in Google Chat API (Manual)

**Files:** None (GCP Console)

- [ ] **Step 1: Open Chat API configuration**

Go to: GCP Console → APIs & Services → Google Chat API → Configuration

(Or search "Google Chat API" in the GCP Console search bar, then click "Configuration" tab)

- [ ] **Step 2: Fill in configuration**

| Field | Value |
|-------|-------|
| App name | Echo Bot |
| Avatar URL | Leave blank |
| Description | Echo bot |
| Functionality | Check "Receive 1:1 messages" |
| Connection settings | Select "HTTP endpoint URL" |
| HTTP endpoint URL | Paste your Cloud Function URL from Task 5 |
| Visibility | "Make this app available to specific people and groups" → add your email |

- [ ] **Step 3: Save and wait**

Click Save. It may take a few minutes for the bot to appear in Google Chat.

---

### Task 7: End-to-end test in Google Chat

- [ ] **Step 1: Open Google Chat**

Go to chat.google.com (or open Google Chat in Gmail sidebar).

- [ ] **Step 2: Find the bot**

Click "New chat" → search for "Echo Bot" → select it.

If the bot doesn't appear, wait a few minutes — registration can take time to propagate.

- [ ] **Step 3: Send a message**

Send: `hello`

Expected reply: `Hello YourName! You said: hello`

- [ ] **Step 4: Done!**

Bot is live. You now have a working Google Chat bot.
