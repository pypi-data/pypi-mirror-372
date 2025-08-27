# -*- coding: utf-8 -*-
import abc
import uuid
from typing import Iterable, List

from django.db.models import Q
from celery import shared_task

from webhook.base_models import Event, Scope, Webhook
from webhook.config import webhook_settings
from webhook.models import History, Subscription
from webhook.models import Webhook as WebHookModel
from webhook.requester import RequestConfig, Requester, RequestResult
from webhook.signals import (
    post_event_broadcast_signal,
    post_send_request_signal,
    pre_event_broadcast_signal,
    pre_send_request_signal,
)


class HandlerInterface(abc.ABC):
    @abc.abstractmethod
    def handle(self, *args, **kwargs):
        pass


class EventHandler(HandlerInterface):
    def __init__(self, event: Event):
        self.event = event

    def handle(self, scopes: List[Scope], *args, **kwargs) -> None:
        self._broadcast(scopes)

    def _broadcast(self, scopes: List[Scope], *args, **kwargs):
        pre_event_broadcast_signal.send(sender=self.__class__, event=self.event, scopes=scopes)

        subscription_query = Q()
        for scope in scopes:
            subscription_query |= Q(
                scope_type=scope.type,
                scope_code=scope.code,
                event_code__in=[self.event.code, webhook_settings.ALL_EVENTS_KEY],
            )
        subscriptions = (
            list(
                Subscription.objects.filter(subscription_query).values_list("webhook_code", "scope_type", "scope_code")
            )
            if scopes
            else []
        )
        webhook_query = Q()
        for webhook_code, scope_type, scope_code in subscriptions:
            webhook_query |= Q(code=webhook_code, scope_type=scope_type, scope_code=scope_code)
        webhooks = (
            [Webhook.from_orm(webhook) for webhook in WebHookModel.objects.filter(webhook_query)]
            if subscriptions
            else []
        )

        # TODO: 优化支持异步实现
        self._sync_webhooker_handle(webhooks=webhooks)

        post_event_broadcast_signal.send(sender=self.__class__, event=self.event, scopes=scopes)

    def _sync_webhooker_handle(self, webhooks: Iterable[Webhook], *args, **kwargs):
        for webhook in webhooks:
            webhooker = Webhooker(webhook)
            webhooker.handle(event=self.event, *args, **kwargs)


class Webhooker(HandlerInterface):
    def __init__(self, webhook: Webhook):
        self.webhook = webhook

    def handle(self, event: Event, *args, **kwargs):
        self._request(event=event, *args, **kwargs)

    def _request(self, event: Event, *args, **kwargs):
        pre_send_request_signal.send(sender=self.__class__, webhook=self.webhook, event=event)
        delivery_id = kwargs.pop("delivery_id", uuid.uuid4().hex)
        extra_info = self.webhook.extra_info or {}
        request_config = RequestConfig(url=self.webhook.endpoint, method=self.webhook.method, **extra_info)
        request_config.data.update({"event": event.dict(), "delivery_id": delivery_id})

        self.send_webhook_task.apply_async(
            kwargs={
                "request_config": request_config.dict(),
                "event_code": event.code,
                "delivery_id": delivery_id,
                "webhook_data": {
                    'code': self.webhook.code,
                    'scope_type': self.webhook.scope_type,
                    'scope_code': self.webhook.scope_code,
                    "retry_times": extra_info.get("retry_times", 2),
                    "interval": extra_info.get("interval", 2),
                },
                **kwargs
            }
        )
        post_send_request_signal.send(sender=self.__class__, webhook=self.webhook, event=event)

    @staticmethod
    @shared_task(bind=True)
    def send_webhook_task(self, request_config, event_code, delivery_id, webhook_data, **kwargs):
        request_result = Requester(config=request_config).request()

        history_extra_info = {
            "request": request_config,
            "response": request_result.json_response(),
            **kwargs.get("history_extra_info", {}),
        }
        # TODO: 可配置
        History.objects.create(
            webhook_code=webhook_data['code'],
            event_code=event_code,
            success=request_result.ok,
            status_code=request_result.response_status_code,
            delivery_id=delivery_id,
            scope_type=webhook_data['scope_type'],
            scope_code=webhook_data['scope_code'],
            extra_info=history_extra_info,
        )

        if not request_result.ok:
            raise self.retry(
                exc=Exception("Webhook request failed"),
                countdown=webhook_data["retry_times"],
                max_retries=webhook_data["interval"]
            )
