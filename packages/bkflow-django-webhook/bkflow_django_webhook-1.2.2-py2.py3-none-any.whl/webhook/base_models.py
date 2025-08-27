# -*- coding: utf-8 -*-
from typing import Optional

from pydantic import BaseModel


class Event(BaseModel):
    code: str
    name: str
    description: Optional[str] = None
    info: Optional[dict] = None

    class Config:
        orm_mode = True
        from_attributes = True


class Webhook(BaseModel):
    code: str
    name: str
    method: str = "POST"
    endpoint: str
    scope_type: str
    scope_code: str
    extra_info: Optional[dict] = None

    class Config:
        orm_mode = True
        from_attributes = True


class Scope(BaseModel):
    type: str
    code: str

    class Config:
        orm_mode = True
        from_attributes = True
