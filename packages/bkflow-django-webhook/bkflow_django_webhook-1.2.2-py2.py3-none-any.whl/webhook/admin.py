# -*- coding: utf-8 -*-
from django.contrib import admin

from webhook import models


@admin.register(models.Event)
class EventAdmin(admin.ModelAdmin):
    list_display = [field.name for field in models.Event._meta.fields]
    search_fields = ["code", "name"]


@admin.register(models.Webhook)
class WebhookAdmin(admin.ModelAdmin):
    list_display = [field.name for field in models.Webhook._meta.fields]
    search_fields = ["code", "name", "scope_code"]


@admin.register(models.History)
class HistoryAdmin(admin.ModelAdmin):
    list_display = [field.name for field in models.History._meta.fields]
    search_fields = ["delivery_id", "webhook_code", "event_code", "scope_code"]
    list_filter = ["success", "status_code"]


@admin.register(models.Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = [field.name for field in models.Subscription._meta.fields]
    search_fields = ["webhook_code", "event_code", "scope_code"]
    list_filter = ["event_code"]


@admin.register(models.Scope)
class ScopeAdmin(admin.ModelAdmin):
    list_display = [field.name for field in models.Scope._meta.fields]
    search_fields = ["code"]
    list_filter = ["type"]
