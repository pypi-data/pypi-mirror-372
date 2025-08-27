# -*- coding: utf-8 -*-
from typing import Dict, List

from django.db import models, transaction
from django.db.models import Q

from webhook.base_models import Scope as ScopeBaseModel
from webhook.base_models import Webhook as WebhookBaseModel


class WebhookManager(models.Manager):
    def apply_scope_webhooks(self, scope: ScopeBaseModel, webhooks: List[WebhookBaseModel]):
        """
        apply the given webhooks to the specified scope
        need to guarantee the scope in webhooks is the same as the scope parameter
        """
        codes = set([webhook.code for webhook in webhooks])
        with transaction.atomic():
            Scope.objects.get_or_create(type=scope.type, code=scope.code)
            # delete ones
            self.filter(scope_type=scope.type, scope_code=scope.code).exclude(code__in=codes).delete()

            # create or update ones
            existing_webhook_info = self.filter(scope_type=scope.type, scope_code=scope.code).values("code", "id")
            existing_webhook_code2id = {info["code"]: info["id"] for info in existing_webhook_info}
            create_ones = [
                Webhook(**webhook.dict()) for webhook in webhooks if webhook.code not in existing_webhook_code2id
            ]
            self.bulk_create(create_ones)
            # update ones
            update_ones = [
                Webhook(id=existing_webhook_code2id[webhook.code], **webhook.dict())
                for webhook in webhooks
                if webhook.code in existing_webhook_code2id
            ]
            self.bulk_update(update_ones, fields=["name", "method", "endpoint", "extra_info"])


class Webhook(models.Model):
    # HTTP 请求方法选项
    METHOD_CHOICES = [
        ('GET', 'get'),
        ('POST', 'post')
    ]

    code = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    method = models.CharField("请求方法", max_length=10, choices=METHOD_CHOICES, default="POST")
    endpoint = models.URLField()
    scope_type = models.CharField(max_length=64)
    scope_code = models.CharField(max_length=64)
    extra_info = models.JSONField(null=True, blank=True)

    objects = WebhookManager()

    class Meta:
        unique_together = ("scope_type", "scope_code", "code")
        ordering = ["-id"]



class History(models.Model):
    webhook_code = models.CharField(max_length=255, db_index=True)
    event_code = models.CharField(max_length=255, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    success = models.BooleanField()
    status_code = models.IntegerField(null=True, blank=True, default=None)
    delivery_id = models.CharField(max_length=64, db_index=True)
    scope_type = models.CharField(max_length=64)
    scope_code = models.CharField(max_length=64)
    extra_info = models.JSONField(null=True, blank=True)  # request、response、time

    class Meta:
        index_together = ("scope_type", "scope_code", "webhook_code", "event_code")
        ordering = ["-id"]


class SubscriptionManager(models.Manager):
    def apply_scope_subscriptions(self, scope: ScopeBaseModel, subscription_configs: Dict[str, List[str]]):
        """
        subscription_configs: {webhook_code: [event_code]}
        """
        with transaction.atomic():
            flatten_subscription_configs = [
                (webhook_code, event_code)
                for webhook_code, event_codes in subscription_configs.items()
                for event_code in event_codes
            ]
            query_filter = Q()
            for webhook_code, event_code in flatten_subscription_configs:
                query_filter |= Q(webhook_code=webhook_code, event_code=event_code)

            # delete
            self.filter(scope_type=scope.type, scope_code=scope.code).exclude(query_filter).delete()

            # create
            existing_ones = self.filter(scope_type=scope.type, scope_code=scope.code).values_list(
                "webhook_code", "event_code"
            )
            create_configs = set(flatten_subscription_configs) - set(existing_ones)
            create_ones = [
                Subscription(
                    scope_type=scope.type, scope_code=scope.code, webhook_code=webhook_code, event_code=event_code
                )
                for webhook_code, event_code in create_configs
            ]
            self.bulk_create(create_ones)


class Subscription(models.Model):
    webhook_code = models.CharField(max_length=255, db_index=True)
    event_code = models.CharField(max_length=255, db_index=True)
    scope_type = models.CharField(max_length=64)
    scope_code = models.CharField(max_length=64)

    objects = SubscriptionManager()

    class Meta:
        index_together = ("scope_type", "scope_code", "event_code", "webhook_code")
        ordering = ["-id"]


class EventManager(models.Manager):
    def all_events(self) -> list:
        return list(self.all().values_list("code", flat=True))


class Event(models.Model):
    code = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    info = models.JSONField(null=True, blank=True)

    objects = EventManager()


class Scope(models.Model):
    type = models.CharField(max_length=64)
    code = models.CharField(max_length=64)

    class Meta:
        unique_together = ("type", "code")
