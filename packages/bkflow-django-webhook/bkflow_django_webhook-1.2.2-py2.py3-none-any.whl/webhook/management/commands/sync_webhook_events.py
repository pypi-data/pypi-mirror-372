# -*- coding: utf-8 -*-
from os import path

import yaml
from django.core.management.base import BaseCommand

from webhook.models import Event


class Command(BaseCommand):
    """
    python manage.py sync_webhook_events base_path filename
    """

    def add_arguments(self, parser):
        parser.add_argument("base_path", type=str, help="base_path")
        parser.add_argument("filename", type=str, help="filename")

    def handle(self, *args, **kwargs):
        base_path = kwargs["base_path"]
        filename = kwargs["filename"]
        self.stdout.write(f"sync events and scopes with filename: {filename}")

        with open(path.join(base_path, filename), "r", encoding="utf-8") as f:
            webhook_config = yaml.load(f, Loader=yaml.FullLoader)

        # sync events
        events = webhook_config.get("events", [])
        for event in events:
            if not event.get("code"):
                self.stdout.error(f"event code is required, event: {event}")
                continue
            Event.objects.get_or_create(
                code=event["code"], name=event["name"], description=event.get("description", "")
            )
