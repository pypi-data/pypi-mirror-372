from django.apps import AppConfig


class DiscordnotifyConfig(AppConfig):
    name = "discordnotify"
    label = "discordnotify"
    verbose_name = "discordnotify"

    def ready(self):
        from . import signals  # noqa F401
