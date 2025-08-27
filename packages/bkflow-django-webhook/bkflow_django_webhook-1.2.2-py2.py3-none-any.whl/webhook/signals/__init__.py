# -*- coding: utf-8 -*-

from django.dispatch import Signal

event_broadcast_signal = Signal(providing_args=["scopes", "extra_info"])

pre_event_broadcast_signal = Signal(providing_args=["event", "scope"])
post_event_broadcast_signal = Signal(providing_args=["event", "scope"])
pre_send_request_signal = Signal(providing_args=["webhook", "event"])
post_send_request_signal = Signal(providing_args=["webhook", "event"])
