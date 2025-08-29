from unittest.mock import patch

from django.test import TestCase
from django.utils.timezone import now

from discordnotify.core import forward_notification_to_discord

MODULE = "discordnotify.core"


@patch(MODULE + ".DiscordClient", spec=True)
class TestForwardNotificationToDiscord(TestCase):
    def test_should_have_correct_proxy_settings(self, mock_DiscordClient):
        cases = [
            ("localhost", "50051", "localhost:50051"),
            ("127.0.0.1", "50051", "127.0.0.1:50051"),
            ("127.0.0.1", "50000", "127.0.0.1:50000"),
        ]
        for host, port, expected in cases:
            with self.subTest(f"{host}, {port} = {expected}"):
                with patch(MODULE + ".DISCORDPROXY_HOST", host), patch(
                    MODULE + ".DISCORDPROXY_PORT", port
                ):
                    forward_notification_to_discord(
                        notification_id=1,
                        discord_uid=2,
                        title="title",
                        message="message",
                        level="info",
                        timestamp=now().isoformat(),
                    )
                _, kwargs = mock_DiscordClient.call_args
                target = kwargs["target"]
                self.assertEqual(target, expected)
