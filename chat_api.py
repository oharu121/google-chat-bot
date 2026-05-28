import google.auth
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/chat.bot"]


class ChatApiClient:
    def __init__(self, service=None):
        if service is None:
            credentials, _ = google.auth.default(scopes=SCOPES)
            self._service = build("chat", "v1", credentials=credentials)
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
