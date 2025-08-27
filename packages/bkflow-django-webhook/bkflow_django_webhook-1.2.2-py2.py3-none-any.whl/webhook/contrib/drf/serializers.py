# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from webhook.config import webhook_settings
from webhook.models import Event


class WebhookSerializer(serializers.Serializer):
    code = serializers.CharField(help_text=_("webhook编码"), max_length=255, required=True)
    name = serializers.CharField(help_text=_("webhook名称"), max_length=255, required=True)
    endpoint = serializers.URLField(help_text=_("webhook endpoint"), max_length=255, required=True)
    method = serializers.CharField(help_text=_("webhook method"), max_length=255, required=False)
    extra_info = serializers.JSONField(help_text=_("额外扩展信息"), required=False)


class WebhookConfigsSerializer(serializers.Serializer):
    webhooks = serializers.ListField(help_text=_("webhook列表"), child=WebhookSerializer(), required=True)


class WebhookWithEventsSerializer(WebhookSerializer):
    events = serializers.ListField(help_text=_("webhook事件列表"), required=True)

    def validate_events(self, events: list):
        not_support_events = set(events) - set(Event.objects.all_events() + [webhook_settings.ALL_EVENTS_KEY])
        if not_support_events:
            raise serializers.ValidationError(_(f"校验失败，events中包含不支持的事件类型, 不支持事件类型: {not_support_events}"))
        return events


class WebhookConfigsWithEventsSerializer(serializers.Serializer):
    webhooks = serializers.ListField(help_text=_("webhook列表"), child=WebhookWithEventsSerializer(), required=True)
