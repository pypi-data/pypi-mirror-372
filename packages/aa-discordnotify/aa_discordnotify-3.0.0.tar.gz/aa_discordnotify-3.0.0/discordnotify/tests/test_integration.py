from unittest.mock import patch

import grpc
from celery.exceptions import Retry
from discordproxy.exceptions import DiscordProxyException, DiscordProxyTimeoutError

from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse

from allianceauth.notifications import notify
from allianceauth.notifications.models import Notification
from allianceauth.services.modules.discord.models import DiscordUser
from app_utils.testing import create_fake_user

from discordnotify import views
from discordnotify.signals import forward_new_notifications
from discordnotify.tasks import task_forward_notification_to_discord

CORE_PATH = "discordnotify.core"
SIGNALS_PATH = "discordnotify.signals"
VIEWS_PATH = "discordnotify.views"
TASKS_PATH = "discordnotify.tasks"


@patch(CORE_PATH + ".DiscordClient.create_direct_message", spec=True)
@override_settings(CELERY_ALWAYS_EAGER=True)
class TestIntegration(TestCase):
    def setUp(self) -> None:
        self.user = create_fake_user(1001, "Bruce Wayne")

    @patch(SIGNALS_PATH + ".DISCORDNOTIFY_ENABLED", True)
    @patch(SIGNALS_PATH + ".DISCORDNOTIFY_SUPERUSER_ONLY", False)
    def test_should_forward_when_new_notification_is_created(
        self, mock_create_direct_message
    ):
        # given
        DiscordUser.objects.create(user=self.user, uid=123)
        # when
        notify(self.user, title="title", message="message")
        # then
        self.assertTrue(mock_create_direct_message.called)
        _, kwargs = mock_create_direct_message.call_args
        self.assertEqual(kwargs["user_id"], 123)
        self.assertEqual(kwargs["embed"].description, "message")
        self.assertEqual(kwargs["embed"].title, "title")

    @patch(SIGNALS_PATH + ".DISCORDNOTIFY_ENABLED", True)
    @patch(SIGNALS_PATH + ".DISCORDNOTIFY_SUPERUSER_ONLY", False)
    def test_should_split_messages_that_are_too_long(self, mock_create_direct_message):
        # given
        DiscordUser.objects.create(user=self.user, uid=123)
        # when
        notify(self.user, title="title", message="x" * 3000)
        # then
        self.assertTrue(mock_create_direct_message.called)
        _, kwargs = mock_create_direct_message.call_args
        self.assertEqual(len(kwargs["embed"].description), 2048)

    @patch(SIGNALS_PATH + ".DISCORDNOTIFY_SUPERUSER_ONLY", False)
    def test_should_not_forward_when_app_is_disabled(self, mock_create_direct_message):
        # given
        DiscordUser.objects.create(user=self.user, uid=123)
        # when
        with patch(SIGNALS_PATH + ".DISCORDNOTIFY_ENABLED", False):
            notify(self.user, "hi")
        # then
        self.assertFalse(mock_create_direct_message.called)

    @patch(SIGNALS_PATH + ".DISCORDNOTIFY_ENABLED", True)
    @patch(SIGNALS_PATH + ".DISCORDNOTIFY_SUPERUSER_ONLY", False)
    def test_should_not_forward_when_notification_is_updated(
        self, mock_create_direct_message
    ):
        # given
        DiscordUser.objects.create(user=self.user, uid=123)
        post_save.disconnect(forward_new_notifications, sender=Notification)
        notify(self.user, "hi")
        post_save.connect(forward_new_notifications, sender=Notification)
        # when
        notif = Notification.objects.filter(user=self.user).first()
        notif.mark_viewed()
        # then
        self.assertFalse(mock_create_direct_message.called)

    @patch(SIGNALS_PATH + ".DISCORDNOTIFY_ENABLED", True)
    @patch(SIGNALS_PATH + ".DISCORDNOTIFY_SUPERUSER_ONLY", False)
    def test_should_not_forward_when_user_has_no_account(
        self, mock_create_direct_message
    ):
        # when
        notify(self.user, "hi")
        # then
        self.assertFalse(mock_create_direct_message.called)

    @patch(SIGNALS_PATH + ".DISCORDNOTIFY_ENABLED", True)
    @patch(SIGNALS_PATH + ".DISCORDNOTIFY_SUPERUSER_ONLY", True)
    def test_should_forward_to_superusers_only_1(self, mock_create_direct_message):
        # given
        DiscordUser.objects.create(user=self.user, uid=123)
        # when
        notify(self.user, "hi")
        # then
        self.assertFalse(mock_create_direct_message.called)

    @patch(SIGNALS_PATH + ".DISCORDNOTIFY_ENABLED", True)
    @patch(SIGNALS_PATH + ".DISCORDNOTIFY_SUPERUSER_ONLY", True)
    def test_should_forward_to_superusers_only_2(self, mock_create_direct_message):
        # given
        user = User.objects.create_superuser("Clark Kent")
        DiscordUser.objects.create(user=user, uid=987)
        # when
        notify(user, "hi")
        # then
        self.assertTrue(mock_create_direct_message.called)

    @patch(SIGNALS_PATH + ".DISCORDNOTIFY_ENABLED", True)
    @patch(SIGNALS_PATH + ".DISCORDNOTIFY_SUPERUSER_ONLY", True)
    def test_should_forward_to_superusers_only_3(self, mock_create_direct_message):
        # given
        user = User.objects.create_superuser("Clark Kent")
        DiscordUser.objects.create(user=user, uid=987)
        post_save.disconnect(forward_new_notifications, sender=Notification)
        notify(user, "hi")
        post_save.connect(forward_new_notifications, sender=Notification)
        # when
        notif = Notification.objects.filter(user=user).first()
        notif.mark_viewed()
        # then
        self.assertFalse(mock_create_direct_message.called)

    @patch(CORE_PATH + ".DISCORDNOTIFY_MARK_AS_VIEWED", True)
    @patch(SIGNALS_PATH + ".DISCORDNOTIFY_ENABLED", True)
    @patch(SIGNALS_PATH + ".DISCORDNOTIFY_SUPERUSER_ONLY", False)
    def test_should_mark_notification_as_viewed_once_submitted(
        self, mock_create_direct_message
    ):
        # given
        DiscordUser.objects.create(user=self.user, uid=123)
        # when
        obj = Notification.objects.notify_user(user=self.user, title="hi")
        # then
        obj.refresh_from_db()
        self.assertTrue(obj.viewed)

    @patch(CORE_PATH + ".DISCORDNOTIFY_MARK_AS_VIEWED", False)
    @patch(SIGNALS_PATH + ".DISCORDNOTIFY_ENABLED", True)
    @patch(SIGNALS_PATH + ".DISCORDNOTIFY_SUPERUSER_ONLY", False)
    def test_should_not_mark_notification_as_viewed_once_submitted(
        self, mock_create_direct_message
    ):
        # given
        DiscordUser.objects.create(user=self.user, uid=123)
        # when
        obj = Notification.objects.notify_user(user=self.user, title="hi")
        # then
        obj.refresh_from_db()
        self.assertFalse(obj.viewed)

    @patch(CORE_PATH + ".DISCORDNOTIFY_MARK_AS_VIEWED", False)
    @patch(SIGNALS_PATH + ".DISCORDNOTIFY_ENABLED", True)
    @patch(SIGNALS_PATH + ".DISCORDNOTIFY_SUPERUSER_ONLY", False)
    def test_should_not_mark_notification_as_viewed_when_failed(
        self, mock_create_direct_message
    ):
        # given
        mock_create_direct_message.side_effect = DiscordProxyException
        DiscordUser.objects.create(user=self.user, uid=123)
        # when
        obj = Notification.objects.notify_user(user=self.user, title="hi")
        # then
        obj.refresh_from_db()
        self.assertFalse(obj.viewed)


class TestViews(TestCase):
    @patch(VIEWS_PATH + ".notify", wraps=notify)
    @patch(VIEWS_PATH + ".messages")
    def test_should_create_notification_and_send_message(
        self, spy_messages_plus, spy_notify
    ):
        # given
        user = User.objects.create_user("Bruce Wayne")
        factory = RequestFactory()
        request = factory.get(reverse("discordnotify:send_test_notification"))
        request.user = user
        # when
        response = views.send_test_notification(request)
        # then
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("authentication:dashboard"))
        self.assertTrue(spy_notify.called)
        self.assertTrue(spy_messages_plus.success.called)


@patch(TASKS_PATH + ".logger", spec=True)
@patch(TASKS_PATH + ".forward_notification_to_discord", spec=True)
class TestTasks(TestCase):
    def test_should_send_notification(
        self, mock_forward_notification_to_discord, mock_logger
    ):
        # when
        task_forward_notification_to_discord(
            notification_id=1,
            discord_uid=2,
            title="title",
            message="message",
            level="INFO",
            timestamp="abc",
        )
        # then
        self.assertTrue(mock_forward_notification_to_discord.called)
        self.assertTrue(mock_logger.info.called)

    def test_should_retry_when_timeout_reached(
        self, mock_forward_notification_to_discord, mock_logger
    ):
        # given
        timeout_exception = DiscordProxyTimeoutError(
            status=grpc.StatusCode.DEADLINE_EXCEEDED, details="Timeout"
        )
        mock_forward_notification_to_discord.side_effect = timeout_exception
        # when
        with self.assertRaises(Retry):
            task_forward_notification_to_discord(
                notification_id=1,
                discord_uid=2,
                title="title",
                message="message",
                level="INFO",
                timestamp="abc",
            )
        self.assertTrue(mock_forward_notification_to_discord.called)
        self.assertTrue(mock_logger.warning.called)
