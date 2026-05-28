from unittest.mock import MagicMock, patch

from throttle import ThrottledPatcher


def _make_patcher(min_interval=1.0, start_time=0.0):
    client = MagicMock()
    patcher = ThrottledPatcher(client, "spaces/S/messages/M", min_interval=min_interval)
    return patcher, client


class TestFirstPatch:
    @patch("throttle.time")
    def test_sent_immediately(self, mock_time):
        mock_time.monotonic.return_value = 0.0
        patcher, client = _make_patcher()
        patcher.patch({"cardsV2": [{"cardId": "test"}]})
        client.patch_message.assert_called_once_with(
            "spaces/S/messages/M", {"cardsV2": [{"cardId": "test"}]}, "cardsV2"
        )


class TestThrottling:
    @patch("throttle.time")
    def test_patch_within_interval_is_buffered(self, mock_time):
        mock_time.monotonic.return_value = 0.0
        patcher, client = _make_patcher()
        patcher.patch({"body": "first"})
        assert client.patch_message.call_count == 1

        mock_time.monotonic.return_value = 0.5  # only 0.5s later
        patcher.patch({"body": "second"})
        assert client.patch_message.call_count == 1  # still 1, buffered

    @patch("throttle.time")
    def test_patch_after_interval_is_sent(self, mock_time):
        mock_time.monotonic.return_value = 0.0
        patcher, client = _make_patcher()
        patcher.patch({"body": "first"})

        mock_time.monotonic.return_value = 1.5  # 1.5s later
        patcher.patch({"body": "second"})
        assert client.patch_message.call_count == 2

    @patch("throttle.time")
    def test_buffer_is_latest_wins(self, mock_time):
        mock_time.monotonic.return_value = 0.0
        patcher, client = _make_patcher()
        patcher.patch({"body": "first"})

        mock_time.monotonic.return_value = 0.3
        patcher.patch({"body": "second"})
        mock_time.monotonic.return_value = 0.6
        patcher.patch({"body": "third"})

        # flush should send "third", not "second"
        mock_time.monotonic.return_value = 1.5
        patcher.flush()
        last_call_body = client.patch_message.call_args_list[-1][0][1]
        assert last_call_body == {"body": "third"}


class TestFlush:
    @patch("throttle.time")
    def test_sends_buffered_body(self, mock_time):
        mock_time.monotonic.return_value = 0.0
        patcher, client = _make_patcher()
        patcher.patch({"body": "first"})

        mock_time.monotonic.return_value = 0.3
        patcher.patch({"body": "buffered"})

        # flush should sleep remainder then send
        mock_time.monotonic.return_value = 0.3
        patcher.flush()
        mock_time.sleep.assert_called()
        assert client.patch_message.call_count == 2
        last_body = client.patch_message.call_args_list[-1][0][1]
        assert last_body == {"body": "buffered"}

    @patch("throttle.time")
    def test_noop_when_nothing_buffered(self, mock_time):
        mock_time.monotonic.return_value = 0.0
        patcher, client = _make_patcher()
        patcher.patch({"body": "first"})

        patcher.flush()
        assert client.patch_message.call_count == 1  # no extra call


class TestForce:
    @patch("throttle.time")
    def test_force_sleeps_and_patches(self, mock_time):
        mock_time.monotonic.return_value = 0.0
        patcher, client = _make_patcher()
        patcher.patch({"body": "first"})

        mock_time.monotonic.return_value = 0.3
        patcher.patch({"body": "forced"}, force=True)
        mock_time.sleep.assert_called()
        assert client.patch_message.call_count == 2

    @patch("throttle.time")
    def test_force_immediate_when_interval_elapsed(self, mock_time):
        mock_time.monotonic.return_value = 0.0
        patcher, client = _make_patcher()
        patcher.patch({"body": "first"})

        mock_time.monotonic.return_value = 2.0
        patcher.patch({"body": "forced"}, force=True)
        mock_time.sleep.assert_not_called()
        assert client.patch_message.call_count == 2

    @patch("throttle.time")
    def test_force_sends_correct_body(self, mock_time):
        mock_time.monotonic.return_value = 0.0
        patcher, client = _make_patcher()
        patcher.patch({"body": "first"})

        mock_time.monotonic.return_value = 0.5
        patcher.patch({"body": "the-forced-body"}, force=True)
        last_body = client.patch_message.call_args_list[-1][0][1]
        assert last_body == {"body": "the-forced-body"}
