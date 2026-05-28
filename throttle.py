import time


class ThrottledPatcher:
    def __init__(self, chat_client, message_name, min_interval=1.0):
        self._client = chat_client
        self._message_name = message_name
        self._min_interval = min_interval
        self._last_patch_time = float("-inf")
        self._pending_body = None

    def _send(self, body):
        self._client.patch_message(self._message_name, body, "cardsV2")
        self._last_patch_time = time.monotonic()
        self._pending_body = None

    def _wait_for_interval(self):
        elapsed = time.monotonic() - self._last_patch_time
        remaining = self._min_interval - elapsed
        if remaining > 0:
            time.sleep(remaining)

    def patch(self, body, force=False):
        elapsed = time.monotonic() - self._last_patch_time
        if elapsed >= self._min_interval:
            self._send(body)
        elif force:
            self._wait_for_interval()
            self._send(body)
        else:
            self._pending_body = body

    def flush(self):
        if self._pending_body is not None:
            self._wait_for_interval()
            self._send(self._pending_body)
