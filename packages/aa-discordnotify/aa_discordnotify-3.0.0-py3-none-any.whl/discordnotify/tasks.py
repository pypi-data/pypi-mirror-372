"""Tasks for Discord Notify."""

import random

from celery import shared_task
from discordproxy.exceptions import DiscordProxyTimeoutError

from allianceauth.services.hooks import get_extension_logger
from app_utils.logging import LoggerAddTag

from . import __title__
from .core import forward_notification_to_discord

logger = LoggerAddTag(get_extension_logger(__name__), __title__)


@shared_task(bind=True)
def task_forward_notification_to_discord(
    self,
    notification_id: int,
    discord_uid: int,
    title: str,
    message: str,
    level: str,
    timestamp: str,
):
    """Forward a notification to discord as task."""
    try:
        forward_notification_to_discord(
            notification_id=notification_id,
            discord_uid=discord_uid,
            title=title,
            message=message,
            level=level,
            timestamp=timestamp,
        )
    except DiscordProxyTimeoutError as ex:
        countdown = 30 + int(random.uniform(0, 5)) * 60
        logger.warning(
            "Timeout exceeded when trying to send notification %d to Discord. "
            "Trying again in %d seconds.",
            notification_id,
            countdown,
        )
        raise self.retry(countdown=countdown) from ex

    logger.info("Forwarded notification %d to Discord", notification_id)
