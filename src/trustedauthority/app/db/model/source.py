import logging
from typing import TYPE_CHECKING
from sqlalchemy import String, Integer, Column, DateTime, Enum, BLOB
from sqlalchemy.orm import relationship

from trustedauthority.app.db.model.base import Base
from trustedauthority.app.model.enums import SourceAppType
from trustedauthority.app.model.source import SourceAppResponse, SourceAppStats, SourceAppCreateResponse

if TYPE_CHECKING:
    from digital_object import DigitalObject

logger = logging.getLogger(__name__)


class SourceApp(Base):
    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    kind = Column(Enum(SourceAppType))
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    last_object_registered_at = Column(DateTime, nullable=True)
    num_objects = Column(Integer, default=0)
    ta_public_key = Column(String, nullable=False)
    ta_private_key = Column(String, nullable=False)

    # objects = relationship("DigitalObject", back_populates="source_app_id")

    def __repr__(self):
        x = self.id + ' ' + self.name + ' ' + str(self.kind)
        return x

    def source_app_response(self) -> SourceAppResponse:
        logger.info(f'db obj {self}')
        obj = SourceAppResponse(id=self.id,
                                name=self.name,
                                kind=self.kind,
                                ta_public_key=self.ta_public_key,
                                created_at=self.created_at,
                                updated_at=self.updated_at)
        logger.info(f'response obj {obj}')
        return obj

    def source_app_create_response(self) -> SourceAppCreateResponse:
        logger.info(f'db obj {self}')
        obj = SourceAppCreateResponse(id=self.id,
                                      name=self.name,
                                      kind=self.kind,
                                      created_at=self.created_at,
                                      updated_at=self.updated_at,
                                      ta_public_key=self.ta_public_key,
                                      ta_private_key=self.ta_private_key)
        logger.info(f'response obj {obj}')
        return obj

    def source_app_stats_response(self) -> SourceAppStats:
        logger.info(f'db obj {self}')
        obj = SourceAppStats(id=self.id,
                             num_objects=self.num_objects)
        logger.info(f'response obj {obj}')
        return obj
