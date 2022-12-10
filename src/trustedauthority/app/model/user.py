from pydantic import BaseModel
from datetime import datetime
from trustedauthority.app.model.enums import UserType


class UserRequest(BaseModel):
    name: str
    kind: UserType
    one_time_key: str


class UserUpdate(BaseModel):
    id: str
    name: str
    kind: UserType


class UserResponse(BaseModel):
    id: str
    name: str
    kind: UserType
    ta_public_key: str
    created_at: datetime
    updated_at: datetime

class UserCreateResponse(BaseModel):
    id: str
    name: str
    kind: UserType
    ta_private_key: str
    ta_public_key: str
    created_at: datetime
    updated_at: datetime


class UserStats(BaseModel):
    id: str
    num_created: int
    num_edited: int
    num_published: int
    num_verifications: int


class User(BaseModel):
    id: str
    name: str
    kind: UserType
    ta_private_key: str
    ta_public_key: str
    created_at: datetime
    updated_at: datetime
    num_created: int
    num_edited: int
    num_published: int
    num_verifications: int
