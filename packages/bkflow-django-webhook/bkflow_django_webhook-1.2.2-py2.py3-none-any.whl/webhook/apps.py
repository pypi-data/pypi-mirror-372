from django.apps import AppConfig


class WebhookConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "webhook"

    def ready(self):
        from .signals import (  # noqa
            event_broadcast_signal,
            post_event_broadcast_signal,
            post_send_request_signal,
            pre_event_broadcast_signal,
            pre_send_request_signal,
        )
        from .signals.handlers import handle_event_broadcast  # noqa
