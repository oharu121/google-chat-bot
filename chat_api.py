import json
import threading
from pathlib import Path

import google.auth
from googleapiclient.discovery import build_from_document

SCOPES = ["https://www.googleapis.com/auth/chat.bot"]

_DISCOVERY_DOC_PATH = Path(__file__).parent / "chat_discovery.json"

_default_service = None
_lock = threading.Lock()


def _get_default_service():
    global _default_service
    if _default_service is None:
        with _lock:
            if _default_service is None:
                credentials, _ = google.auth.default(scopes=SCOPES)
                doc = json.loads(_DISCOVERY_DOC_PATH.read_text())
                _default_service = build_from_document(doc, credentials=credentials)
    return _default_service


class ChatApiClient:
    def __init__(self, service=None):
        if service is None:
            self._service = _get_default_service()
        else:
            self._service = service

    def create_message(self, space_name, body):
        response = (
            self._service.spaces()
            .messages()
            .create(parent=space_name, body=body)
            .execute()
        )
        return response["name"]

    def patch_message(self, message_name, body, update_mask):
        return (
            self._service.spaces()
            .messages()
            .patch(name=message_name, updateMask=update_mask, body=body)
            .execute()
        )

    def add_reaction(self, message_name, emoji):
        return (
            self._service.spaces()
            .messages()
            .reactions()
            .create(parent=message_name, body={"emoji": {"unicode": emoji}})
            .execute()
        )
