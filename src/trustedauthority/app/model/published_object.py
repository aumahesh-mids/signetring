from typing import Optional

from pydantic import BaseModel
from datetime import datetime
from trustedauthority.app.model.enums import DigitalObjectType


class VerifyChallenge(BaseModel):
    challenge_id: str
    opaque: str


class PublishObjectRequest(BaseModel):
    obj_id: str
    owner_id: str
    publisher_id: str


class PublishObjectUpdate(BaseModel):
    pass


class PublishObjectResponse(BaseModel):
    name: str
    kind: DigitalObjectType
    owner_public_key: str
    publisher_public_key: str
    payload: str
    ta_cert: str


class PublishedObject(BaseModel):
    id: str
    obj_id: str
    kind: DigitalObjectType
    owner_id: str
    publisher_id: str
    source_app_id: str
    ta_cert: str
    created_at: datetime
    updated_at: datetime
    payload: str
    num_verifications: int