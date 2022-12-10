from datetime import datetime

from pydantic import BaseModel


class ChallengeRequest(BaseModel):
    secret: str
    obj_id: str
    user_id: str


class ChallengeId(BaseModel):
    challenge_id: str


class ChallengeUpdate(BaseModel):
    secret: str


class ChallengeResponse(BaseModel):
    challenge_id: str
    secret: str
    obj_id: str
    user_id: str


class ChallengeAccepted(BaseModel):
    challenge_id: str
    secret: str


class ChallengeAcceptedResponse(BaseModel):
    challenge_id: str
    passed: bool