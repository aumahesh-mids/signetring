from datetime import datetime

from pydantic.main import BaseModel


class KeyRequest(BaseModel):
    user_id: str
    app_id: str


class KeyUpdate(BaseModel):
    pass


class KeyResponse(BaseModel):
    sym_key_part1: str
    sym_key_part2: str
    challenge_text: str
    expires_at: datetime


class Key(BaseModel):
    id: str
    user_id: str
    app_id: str
    key: str
    challenge_text: str
    expires_at: datetime

