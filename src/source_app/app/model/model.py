from datetime import datetime

from pydantic import BaseModel

from trustedauthority.app.model.enums import SourceAppType


class InitAppRequest(BaseModel):
    name: str
    kind: SourceAppType


class InitAppResponse(BaseModel):
    ta_id: str
    name: str
    kind: SourceAppType
    ta_public_key: str
    created_at: datetime
    updated_at: datetime


class ClickRequest(BaseModel):
    user_id: str
    user_private_key: str
    parent_obj_id: str
    parent_ta_cert: str

