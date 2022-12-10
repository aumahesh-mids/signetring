from datetime import datetime

from pydantic import BaseModel

from trustedauthority.app.model.enums import DigitalObjectType


class VerifyRequest(BaseModel):
    name: str
    kind: DigitalObjectType
    owner_public_key: str
    publisher_public_key: str
    payload: str
    ta_cert: str


class VerifyResponse(BaseModel):
    name: str
    kind: DigitalObjectType
    valid: bool
    parent_name: str
    parent_ta_cert: str
    created_at: datetime
    updated_at: datetime
    published_at: datetime