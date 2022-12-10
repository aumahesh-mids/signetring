from pydantic import BaseModel
from datetime import datetime
from trustedauthority.app.model.enums import SourceAppType


class SourceAppRequest(BaseModel):
    name: str
    kind: SourceAppType
    one_time_key: str


class SourceAppUpdate(BaseModel):
    id: str
    name: str
    kind: SourceAppType


class SourceAppResponse(BaseModel):
    id: str
    name: str
    kind: SourceAppType
    ta_public_key: str
    created_at: datetime
    updated_at: datetime

class SourceAppCreateResponse(BaseModel):
    id: str
    name: str
    kind: SourceAppType
    ta_private_key: str
    ta_public_key: str
    created_at: datetime
    updated_at: datetime


class SourceAppStats(BaseModel):
    id: str
    num_objects: int


class SourceApp(BaseModel):
    id: str
    name: str
    kind: SourceAppType
    cert: str
    ta_private_key: str
    ta_public_key: str
    created_at: datetime
    updated_at: datetime
    last_object_registered_at: datetime
    num_objects: int
