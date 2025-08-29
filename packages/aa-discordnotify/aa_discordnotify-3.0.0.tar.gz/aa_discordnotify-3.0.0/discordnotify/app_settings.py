"""Settings for Discord Notify."""

from django.conf import settings

DISCORDPROXY_PORT = getattr(settings, "DISCORDPROXY_PORT", 50051)
"""Port used to communicate with Discord Proxy."""

DISCORDPROXY_HOST = getattr(settings, "DISCORDPROXY_HOST", "localhost")
"""Host used to communicate with Discord Proxy."""

DISCORDNOTIFY_SUPERUSER_ONLY = getattr(settings, "DISCORDNOTIFY_SUPERUSER_ONLY", False)
"""When set to True, only superusers will be get their notifications forwarded."""

DISCORDNOTIFY_ENABLED = getattr(settings, "DISCORDNOTIFY_ENABLED", True)
"""Set to False to disable this app."""

DISCORDNOTIFY_MARK_AS_VIEWED = getattr(settings, "DISCORDNOTIFY_MARK_AS_VIEWED", True)
"""When set to True, will mark all notifications as read
that have been successfully submitted to Discord.
"""
