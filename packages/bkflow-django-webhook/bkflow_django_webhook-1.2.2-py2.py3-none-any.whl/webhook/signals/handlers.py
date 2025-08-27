# -*- coding: utf-8 -*-
from typing import List, Tuple, Union

from django.dispatch import receiver

from webhook.api import event_broadcast
from webhook.base_models import Event, Scope
from webhook.signals import event_broadcast_signal


@receiver(event_broadcast_signal)
def handle_event_broadcast(
    sender: Union[Event, str], scopes: List[Union[Scope, Tuple[str, str]]], extra_info: dict = None, **kwargs
):
    event_broadcast(event=sender, scopes=scopes, extra_info=extra_info)
