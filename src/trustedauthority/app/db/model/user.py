import logging
from typing import TYPE_CHECKING

from sqlalchemy import String, Integer, Column, DateTime, Enum, BLOB
from sqlalchemy.orm import relationship
from trustedauthority.app.db.model.base import Base
from trustedauthority.app.model.enums import UserType
from trustedauthority.app.model.user import UserResponse, UserStats, UserCreateResponse

if TYPE_CHECKING:
    from trustedauthority.app.db.model.digital_object import DigitalObject

logger = logging.getLogger(__name__)


class User(Base):
    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    kind = Column(Enum(UserType))
    ta_public_key = Column(String, nullable=False)
    ta_private_key = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    num_created = Column(Integer, default=0)
    num_edited = Column(Integer, default=0)
    num_published = Column(Integer, default=0)

    # objects = relationship("DigitalObject", back_populates="creator_id")

    def __repr__(self):
        return self.id + ' ' + self.name + ' ' + str(self.kind)

    def user_response(self) -> UserResponse:
        logger.info(f'db obj {self}')
        obj = UserResponse(id=self.id,
                           name=self.name,
                           kind=self.kind,
                           ta_public_key=self.ta_public_key,
                           created_at=self.created_at,
                           updated_at=self.updated_at)
        logger.info(f'response obj {obj}')
        return obj

    def user_create_response(self) -> UserCreateResponse:
        logger.info(f'db obj {self}')
        obj = UserCreateResponse(id=self.id,
                                 name=self.name,
                                 kind=self.kind,
                                 ta_public_key=self.ta_public_key,
                                 ta_private_key=self.ta_private_key,
                                 created_at=self.created_at,
                                 updated_at=self.updated_at)
        logger.info(f'response obj {obj}')
        return obj

    def stat_response(self) -> UserStats:
        logger.info(f'db obj {self}')
        obj = UserStats(id=self.id,
                        num_created=self.num_created,
                        num_edited=self.num_edited,
                        num_published=self.num_published,
                        num_verifications=self.num_verifications)
        logger.info(f'response obj {obj}')
        return obj
