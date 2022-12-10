from typing import Optional

from pydantic import BaseModel
from datetime import datetime
from trustedauthority.app.model.enums import DigitalObjectType


class DigitalObjectRequest(BaseModel):
    name: str
    kind: DigitalObjectType
    source_app_id: str
    owner_id: str
    challenge: str
    payload: str
    parent_id: str
    parent_ta_cert: str


class DigitalObjectUpdate(BaseModel):
    pass


class DigitalObjectResponse(BaseModel):
    id: str
    name: str
    kind: DigitalObjectType
    source_app_id: str
    owner_id: str
    parent_id: Optional[str] = ''
    parent_ta_cert: Optional[str] = ''
    ta_cert: str
    created_at: datetime
    updated_at: datetime


class DigitalObjectStats(BaseModel):
    id: str
    num_verifications: int


class DigitalObject(BaseModel):
    id: str
    name: str
    kind: DigitalObjectType
    source_app_id: str
    owner_id: str
    parent_id: Optional[str] = ''
    parent_ta_cert: Optional[str] = ''
    ta_cert: str
    created_at: datetime
    updated_at: datetime
    payload: str
    num_publications: int


