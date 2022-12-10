from datetime import datetime

from pydantic import BaseModel

from trustedauthority.app.model.enums import UserType

class InitUserRequest(BaseModel):
    name: str
    kind: UserType


class InitUserResponse(BaseModel):
    ta_id: str
    name: str
    kind: UserType
    ta_public_key: str
    created_at: datetime
    updated_at: datetime


class ChallengeAcceptedByUser(BaseModel):
    id: str
    obj_id: str
    user_id: str
    user_secret: str
    publisher_secret: str
    opaque: str