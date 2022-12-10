import logging
from typing import TYPE_CHECKING

from sqlalchemy import String, Integer, Column, DateTime, Enum, BLOB
from sqlalchemy.orm import relationship
from trustedauthority.app.db.model.base import Base
from trustedauthority.app.model.auth import KeyResponse
from trustedauthority.app.model.enums import UserType
from trustedauthority.app.model.user import UserResponse, UserStats, UserCreateResponse

if TYPE_CHECKING:
    from trustedauthority.app.db.model.digital_object import DigitalObject

logger = logging.getLogger(__name__)


class Auth(Base):
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, index=True)
    app_id = Column(String, index=True)
    key = Column(String, nullable=False)
    challenge_text = Column(String, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    name = Column(String, index=True)

    def key_response(self) -> KeyResponse:
        logger.info(f'db obj {self}')
        s = len(self.key)
        obj = KeyResponse(sym_key_part1=self.key[:s],
                          sym_key_part2=self.key[s:],
                          challenge_text=self.challenge_text,
                          expires_at=self.expires_at)
        logger.info(f'response obj {obj}')
        return obj
