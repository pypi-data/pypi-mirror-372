# -*- coding: utf-8 -*-
import logging
from typing import List, Tuple, Union, Dict

from webhook.config import webhook_settings

from webhook.base_models import Event, Scope, Webhook
from webhook.handlers import EventHandler
from webhook.models import Event as EventModel
from webhook.models import Subscription
from webhook.models import Webhook as WebhookModel
from webhook.requester import RequestConfig, Requester

logger = logging.getLogger(__name__)


def get_scope_webhooks(scope_type: str, scope_code: str) -> List[Webhook]:
    """
    get webhooks of scope
    """
    scope = Scope(scope_type=scope_type, scope_code=scope_code)
    return [
        Webhook.from_orm(webhook)
        for webhook in WebhookModel.objects.filter(scope_type=scope.type, scope_code=scope.code)
    ]


def get_scope_subscribed_events(scope_type: str, scope_code: str, parse_all_event_key: bool = False, *args, **kwargs):
    """
    get subscriptions of scope
    """
    event_codes = Subscription.objects.filter(scope_type=scope_type, scope_code=scope_code).values_list(
        "event_code", flat=True
    )

    if webhook_settings.ALL_EVENTS_KEY in event_codes:
        return EventModel.objects.all().values_list("code", flat=True)

    return event_codes


def apply_scope_webhooks(scope_type: str, scope_code: str, webhooks: List[Dict]) -> None:
    """
    update or create webhooks by given list and delete others
    """
    scope = Scope(type=scope_type, code=scope_code)
    webhooks = [Webhook(**webhook, scope_type=scope_type, scope_code=scope_code) for webhook in webhooks]
    WebhookModel.objects.apply_scope_webhooks(scope, webhooks)


def apply_scope_subscriptions(scope_type: str, scope_code: str, subscription_configs: Dict) -> None:
    scope = Scope(type=scope_type, code=scope_code)
    Subscription.objects.apply_scope_subscriptions(scope, subscription_configs)


def event_broadcast(event: Union[Event, str], scopes: List[Union[Scope, Tuple[str, str]]], *args, **kwargs):
    """
    broadcast event to make subscription webhooks send requests
    """
    logger.info(f"[event broadcasting...] event: {event}, scopes: {scopes}, args: {args}, kwargs: {kwargs}")
    if isinstance(event, str):
        event_instance = EventModel.objects.filter(code=event).first()
        if not event_instance:
            logger.error(f"event {event} not found")
            return
        event = Event.from_orm(event_instance)

        extra_info = kwargs.get("extra_info", {})
        if event.info:
            event.info.update(extra_info)
        else:
            event.info = extra_info
    if not isinstance(event, Event):
        logger.error(f"event {event} is not a Event instance")
        return

    if not all([isinstance(scope, (Scope, tuple)) for scope in scopes]):
        logger.error(f"scopes {scopes} is not a Scope or tuple instance")
        return

    scopes = [Scope(type=scope[0], code=scope[1]) if isinstance(scope, tuple) else scope for scope in scopes]

    event_handler = EventHandler(event)
    event_handler.handle(scopes=scopes)


def verify_webhook_endpoint(webhook_config):
    request_config = RequestConfig(**webhook_config)
    result = Requester(config=request_config.dict()).request()
    return result
