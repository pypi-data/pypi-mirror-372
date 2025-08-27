# -*- coding: utf-8 -*-
from django.conf import settings

DEFAULT_SETTINGS = {
    "MODE": "SYNC",  # SYNC or ASYNC
    "ALL_EVENTS_KEY": "*",
    "EVENT": {
        "DATA_SOURCE": "DB",  # DB or SETTINGS
    },
    "REQUEST": {
        "TIMEOUT": 30,
    },
}


class WebhookSettings:
    SETTING_PREFIX = "WEBHOOK"
    NESTING_SEPARATOR = "_"

    def __init__(self, default_settings=None):
        self.project_settings = self.get_flatten_settings(getattr(settings, self.SETTING_PREFIX, {}))
        self.default_settings = self.get_flatten_settings(default_settings or DEFAULT_SETTINGS)

    def __getattr__(self, key):
        if key not in self.project_settings and key not in self.default_settings:
            raise AttributeError

        value = self.project_settings.get(key) or self.default_settings.get(key)
        if value is not None:
            setattr(self, key, value)
        return value

    def get_flatten_settings(self, inputted_settings: dict, cur_prefix: str = ""):
        def get_cur_key(cur_key):
            return f"{cur_prefix}{self.NESTING_SEPARATOR}{cur_key}" if cur_prefix else cur_key

        flatten_settings = {}
        for key, value in inputted_settings.items():
            if isinstance(value, dict):
                flatten_sub_settings = self.get_flatten_settings(value, key)
                flatten_settings.update(
                    {
                        get_cur_key(flatten_key): flatten_value
                        for flatten_key, flatten_value in flatten_sub_settings.items()
                    }
                )
            else:
                flatten_settings[get_cur_key(key)] = value
        return flatten_settings


webhook_settings = WebhookSettings(DEFAULT_SETTINGS)
