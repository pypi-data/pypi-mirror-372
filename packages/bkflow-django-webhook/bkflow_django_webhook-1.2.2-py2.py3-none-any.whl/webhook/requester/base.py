# -*- coding: utf-8 -*-
import base64
import json
import logging

import requests
from pydantic import BaseModel

logger = logging.getLogger(__name__)

JSON_CONTENT_TYPE = "application/json"
FORM_CONTENT_TYPE = "application/x-www-form-urlencoded"


class RequestConfig(BaseModel):
    url: str
    method: str = "post"
    content_type: str = JSON_CONTENT_TYPE
    params: dict = {}
    headers: dict = None
    data: dict = {}  # convert to json when content_type is JSON_CONTENT_TYPE
    verify: bool = False
    timeout: int = None
    authorization: dict = None

    @staticmethod
    def _gen_default_headers(content_type, authorization=None):
        headers = {"Content-Type": content_type}
        if not authorization:
            return headers
        auth_type = authorization.get("type", "").lower()

        if auth_type == "bearer":
            token = authorization.get("token", "")
            headers["Authorization"] = f"Bearer {token}"
        elif auth_type == "basic":
            username = authorization.get("username", "")
            password = authorization.get("password", "")
            if username and password:
                auth_str = f"{username}:{password}".encode("utf-8")
                headers["Authorization"] = "Basic " + base64.b64encode(auth_str).decode("ascii")

        return headers

    def __init__(self, **kwargs):
        kwargs["headers"] = {
            **self._gen_default_headers(
                content_type=kwargs.get("content_type", JSON_CONTENT_TYPE),
                authorization=kwargs.get("authorization")
            ),
            **self._normalize_headers(kwargs.get("headers"))
        }
        super().__init__(**kwargs)

    @staticmethod
    def _normalize_headers(headers):
        """将headers统一转换为标准字典格式"""
        if headers is None:
            return {}
        if isinstance(headers, dict):
            return headers.copy()
        if isinstance(headers, list):
            normalized = {}
            for item in headers:
                if not isinstance(item, dict) or 'key' not in item:
                    continue
                key = item['key']
                value = item.get('value')
                if isinstance(value, (dict, list)):
                    value = json.dumps(value) if value else ''
                elif not isinstance(value, str):
                    value = str(value)
                normalized[key] = value
            return normalized

        raise ValueError(f"Unsupported headers type: {type(headers)}")

    def dict(self, **kwargs):
        result = super().dict(**kwargs)
        content_type = result.pop("content_type")
        result.pop("authorization")
        if content_type == JSON_CONTENT_TYPE:
            result["json"] = result.pop("data")
        return result


class RequestResult(BaseModel):
    result: bool
    response: requests.Response = None
    exe_data: str = None

    class Config:
        arbitrary_types_allowed = True

    @property
    def ok(self):
        return self.result and self.response.ok

    @property
    def response_status_code(self):
        if self.response is None:
            return None
        return self.response.status_code

    def json_response(self):
        if self.response is None:
            return None
        try:
            return self.response.json()
        except Exception as e:
            logger.exception(f"[RequestResult.json_response error] {e}")
            return self.response.text


class Requester:
    def __init__(self, config: dict):
        self.request_config = config

    def request(self, *args, **kwargs) -> RequestResult:
        try:
            response = requests.request(**self.request_config)
        except Exception as e:
            logger.exception(f"[Requester.request error] {e}")
            return RequestResult(result=False, exe_data=str(e))
        else:
            return RequestResult(result=True, response=response)
