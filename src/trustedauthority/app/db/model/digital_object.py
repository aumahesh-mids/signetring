import logging
from typing import TYPE_CHECKING
from sqlalchemy import String, Integer, Boolean, Column, DateTime, Enum, BLOB

from trustedauthority.app.db.model.base import Base
from sqlalchemy.orm import relationship

from trustedauthority.app.model.digital_object import DigitalObjectResponse, DigitalObjectStats
from trustedauthority.app.model.enums import DigitalObjectType

if TYPE_CHECKING:
    from trustedauthority.app.db.model.user import User

logger = logging.getLogger(__name__)


class DigitalObject(Base):
    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    kind = Column(Enum(DigitalObjectType))
    source_app_id = Column(String, nullable=False)
    owner_id = Column(String, nullable=False)
    parent_id = Column(String, nullable=True)
    parent_ta_cert = Column(String, nullable=True)
    ta_cert = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    payload = Column(String, nullable=False)
    num_publications = Column(Integer, default=0)

    # creator_id = relationship("User", back_populates="objects")

    def __repr__(self):
        x = self.id + ' ' + self.name + ' ' + str(self.kind)
        return x

    def digital_object_response(self):
        logger.info(f'db obj {self}')
        obj = DigitalObjectResponse(id=self.id,
                                    name=self.name,
                                    kind=self.kind,
                                    source_app_id=self.source_app_id,
                                    owner_id=self.owner_id,
                                    parent_id=self.parent_id,
                                    parent_ta_cert=self.parent_ta_cert,
                                    ta_cert=self.ta_cert,
                                    created_at=self.created_at,
                                    updated_at=self.updated_at)
        logger.info(f'response obj {obj}')
        return obj

    def digital_object_stats_response(self):
        logger.info(f'db obj {self}')
        obj = DigitalObjectStats(id=self.id,
                                 num_verifications=self.num_verifications)
        logger.info(f'response obj {obj}')
        return obj