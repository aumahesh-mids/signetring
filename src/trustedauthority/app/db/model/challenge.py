import logging
from typing import TYPE_CHECKING

from sqlalchemy import String, Integer, Column, DateTime, Enum, BLOB
from trustedauthority.app.db.model.base import Base
from trustedauthority.app.model.publish import ChallengeResponse

logger = logging.getLogger(__name__)


class Challenge(Base):
    id = Column(String, primary_key=True, index=True)
    obj_id = Column(String, index=True)
    secret = Column(String, nullable=False)
    user_id = Column(String, index=True)

    def get_challenge_response(self) -> ChallengeResponse:
        c = ChallengeResponse(challenge_id=self.id,
                              obj_id=self.obj_id,
                              secret=self.secret,
                              user_id=self.user_id)
        return c
