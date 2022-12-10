import logging
from typing import TYPE_CHECKING

from fastapi import HTTPException
from sqlalchemy import String, Integer, Boolean, Column, DateTime, Enum, BLOB
from sqlalchemy.orm import Session

from trustedauthority.app.db.model.base import Base
from trustedauthority.app.model.enums import DigitalObjectType

from trustedauthority.app.model.published_object import PublishObjectResponse

if TYPE_CHECKING:
    from trustedauthority.app.db.model.user import User

logger = logging.getLogger(__name__)


class PublishedObject(Base):
    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    obj_id = Column(String, index=True)
    kind = Column(Enum(DigitalObjectType))
    owner_id = Column(String, index=False)
    publisher_id = Column(String, index=True)
    source_app_id = Column(String, nullable=False)
    ta_cert = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    payload = Column(String, nullable=False)
    num_verifications = Column(Integer, default=0)

    # creator_id = relationship("User", back_populates="objects")
