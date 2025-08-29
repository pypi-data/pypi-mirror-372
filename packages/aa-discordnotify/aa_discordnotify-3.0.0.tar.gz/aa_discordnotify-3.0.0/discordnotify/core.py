"""Core logic for Discord Notify."""

from typing import Any

from discordproxy.client import DiscordClient
from discordproxy.discord_api_pb2 import Embed  # pylint: disable=E0611

from allianceauth.notifications.models import Notification
from app_utils.urls import reverse_absolute, static_file_absolute_url

from . import __title__
from .app_settings import (
    DISCORDNOTIFY_MARK_AS_VIEWED,
    DISCORDPROXY_HOST,
    DISCORDPROXY_PORT,
)

# embed colors
COLOR_INFO = 0x5BC0DE
COLOR_SUCCESS = 0x5CB85C
COLOR_WARNING = 0xF0AD4E
COLOR_DANGER = 0xD9534F

COLOR_MAP = {
    "info": COLOR_INFO,
    "success": COLOR_SUCCESS,
    "warning": COLOR_WARNING,
    "danger": COLOR_DANGER,
}

# limits
MAX_LENGTH_TITLE = 256
MAX_LENGTH_DESCRIPTION = 2048
DISCORD_PROXY_TIMEOUT = 300  # in seconds


def forward_notification_to_discord(
    notification_id: int,
    discord_uid: int,
    title: str,
    message: str,
    level: str,
    timestamp: str,
):
    """Forward a new notification to Discord."""
    embed = _build_embed(
        notification_id=notification_id,
        title=title,
        message=message,
        level=level,
        timestamp=timestamp,
    )
    target = f"{DISCORDPROXY_HOST}:{DISCORDPROXY_PORT}"
    client = DiscordClient(target=target, timeout=DISCORD_PROXY_TIMEOUT)
    client.create_direct_message(user_id=discord_uid, embed=embed)
    _mark_as_viewed(notification_id)


def _build_embed(
    notification_id: int, title: str, message: str, level: str, timestamp: str
) -> Any:
    description = message.strip()
    if len(description) > MAX_LENGTH_DESCRIPTION:
        description = description[: (MAX_LENGTH_DESCRIPTION - 6)] + " [...]"
    author = Embed.Author(
        name="Alliance Auth Notification",
        icon_url=static_file_absolute_url("allianceauth/icons/apple-touch-icon.png"),
    )
    footer = Embed.Footer(
        text=__title__,
        icon_url=static_file_absolute_url("discordnotify/discordnotify_logo.png"),
    )
    return Embed(
        author=author,
        title=title.strip()[:MAX_LENGTH_TITLE],
        url=reverse_absolute("notifications:view", args=[notification_id]),
        description=description,
        color=COLOR_MAP.get(level, None),
        timestamp=timestamp,
        footer=footer,
    )


def _mark_as_viewed(notification_id):
    if DISCORDNOTIFY_MARK_AS_VIEWED:
        try:
            notif = Notification.objects.get(id=notification_id)
        except Notification.DoesNotExist:
            return
        notif.mark_viewed()
