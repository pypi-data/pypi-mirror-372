"""Routes for Discord Notify."""

from django.urls import path

from . import views

app_name = "discordnotify"

urlpatterns = [
    path("test", views.send_test_notification, name="send_test_notification"),
]
