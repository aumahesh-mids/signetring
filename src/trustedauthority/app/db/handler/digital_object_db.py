import logging
import uuid
from datetime import datetime
from typing import List

from fastapi import HTTPException
from sqlalchemy import update
from sqlalchemy.orm import Session

from crypto.crypt import decrypt, sym_decrypt
from trustedauthority.app.config.settings import settings
from trustedauthority.app.db.handler.user_db import user as user_db
from trustedauthority.app.db.handler.auth_db import auth as auth_db
from trustedauthority.app.db.handler.source_app_db import source_app as source_app_db

from trustedauthority.app.db.handler.base import BaseHandler
from trustedauthority.app.db.model.digital_object import DigitalObject
from trustedauthority.app.model.digital_object import DigitalObjectRequest, DigitalObjectUpdate
from trustedauthority.app.model.enums import StatsType, UserType
from trustedauthority.app.model.verify import VerifyRequest, VerifyResponse

logger = logging.getLogger(__name__)


def verify_parent_object(db: Session, parent_id: str, parent_ta_cert: str, obj_in: DigitalObjectRequest):
    if parent_id == '':
        return
    parent_object = digital_object.get(db, parent_id)
    if parent_object is None or parent_object.ta_cert != parent_ta_cert:
        raise HTTPException(status_code=403, detail='parent object ta cert mismatch')
    if parent_object.kind != obj_in.kind:
        raise HTTPException(status_code=401, detail='parent object kind is not consistent with the object')
    return True


def verify(db: Session, obj_in: DigitalObjectRequest):
    enc_challenge = obj_in.challenge
    auth_key = auth_db.get_key(db=db, user_id=obj_in.owner_id, app_id=obj_in.source_app_id)
    expiry = auth_key.expires_at
    current = datetime.now()
    if current > expiry:
        raise HTTPException(status_code=401, detail='challenge key expired')
    challenge_text = decrypt(enc_challenge, settings.TA_PRIVATE_KEY_FILE)
    if challenge_text != auth_key.challenge_text:
        raise HTTPException(status_code=401, detail='challenge failed')
    return True


class DigitalObjectDBHandler(BaseHandler[DigitalObject, DigitalObjectRequest, DigitalObjectUpdate]):

    def create(self, db: Session, *, obj_in: DigitalObjectRequest) -> DigitalObject:
        logger.info(f"digital object create request {obj_in}")
        verify(db, obj_in)
        verify_parent_object(db, obj_in.parent_id, obj_in.parent_ta_cert, obj_in)
        db_obj = DigitalObject()
        db_obj.id = str(uuid.uuid1())
        db_obj.name = obj_in.name
        db_obj.kind = obj_in.kind
        db_obj.source_app_id = obj_in.source_app_id
        db_obj.owner_id = obj_in.owner_id
        db_obj.parent_id = obj_in.parent_id
        db_obj.ta_cert = str(uuid.uuid5(uuid.NAMESPACE_OID, obj_in.name))
        db_obj.created_at = datetime.now()
        db_obj.updated_at = db_obj.created_at
        enc_payload = obj_in.payload
        payload = decrypt(enc_payload, settings.TA_PRIVATE_KEY_FILE)
        db_obj.payload = payload
        # db_obj.last_object_registered_at = None
        db_obj.num_publications = 0
        stats_type = StatsType.Creations
        if obj_in.parent_id != '':
            stats_rype = StatsType.Edits
        db.add(db_obj)
        user_db.increment_stats(db, stats_type, obj_in.owner_id, False)
        source_app_db.increment_stats(db, obj_in.source_app_id, False)
        db.commit()
        return db_obj

    def get_children(self, db: Session, object_id: str):
        children = db.query(self.model).filter(self.model.parent_id == object_id).all()
        children_ids = []
        for child in children:
            children_ids.append(child.id)
        return children_ids

    def get_parent(self, db: Session, object_id: str):
        object = digital_object.get(db, object_id)
        parent_id = object.parent_id
        return parent_id

    def get_owner_objects(self, db: Session, user_id: str):
        objs = db.query(self.model).filter(self.model.owner_id == user_id).all()
        return objs

    def get_app_objects(self, db: Session, app_id: str):
        objs = db.query(self.model).filter(self.model.source_app_id == app_id).all()
        return objs

    def increment_stats(self, db: Session, obj_in: DigitalObject, commit: bool):
        db.query(self.model) \
            .filter(self.model.id == obj_in.id) \
            .update({'num_publications': self.model.num_publications + 1,
                     'updated_at': datetime.now()})
        if commit:
            db.commit()


digital_object = DigitalObjectDBHandler(DigitalObject)
