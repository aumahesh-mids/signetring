import logging
import uuid
from datetime import datetime
from typing import List

from fastapi import HTTPException
from sqlalchemy import update
from sqlalchemy.orm import Session

from crypto.crypt import decrypt, encrypt
from crypto.util import load_key
from trustedauthority.app.config.settings import settings
from trustedauthority.app.db.handler.user_db import user as user_db
from trustedauthority.app.db.handler.auth_db import auth as auth_db
from trustedauthority.app.db.handler.source_app_db import source_app as source_app_db
from trustedauthority.app.db.handler.digital_object_db import digital_object as digital_object_db

from trustedauthority.app.db.handler.base import BaseHandler
from trustedauthority.app.db.model.digital_object import DigitalObject
from trustedauthority.app.db.model.published_object import PublishedObject
from trustedauthority.app.model.published_object import PublishObjectRequest, PublishObjectUpdate
from trustedauthority.app.model.enums import StatsType, UserType
from trustedauthority.app.model.verify import VerifyRequest, VerifyResponse

logger = logging.getLogger(__name__)


class PublishedObjectDBHandler(BaseHandler[PublishedObject, PublishObjectRequest, PublishObjectUpdate]):

    def create(self, db: Session, *, obj_in: PublishObjectRequest) -> PublishedObject:
        dobject = digital_object_db.get(db=db, id=obj_in.obj_id)
        uobject = user_db.get(db=db, id=obj_in.owner_id)
        if dobject is None:
            raise HTTPException(status_code=401, detail='object not found')

        logger.info(f"publish object request {obj_in}")
        db_obj = PublishedObject()
        db_obj.name = dobject.name
        db_obj.id = str(uuid.uuid1())
        db_obj.obj_id = obj_in.obj_id
        db_obj.kind = dobject.kind
        db_obj.owner_id = obj_in.owner_id
        db_obj.publisher_id = obj_in.publisher_id
        db_obj.source_app_id = dobject.source_app_id
        key = encrypt(uobject.ta_public_key[:100], settings.TA_PUBLIC_KEY_FILE)
        db_obj.ta_cert = key
        db_obj.created_at = datetime.now()
        db_obj.updated_at = db_obj.created_at
        payload = dobject.payload
        db_obj.payload = payload
        db_obj.num_verifications = 0
        stats_type = StatsType.Publications
        db.add(db_obj)
        digital_object_db.increment_stats(db, dobject, False)
        user_db.increment_stats(db, stats_type, obj_in.owner_id, False)
        source_app_db.increment_stats(db, dobject.source_app_id, False)
        db.commit()
        return db_obj

    def verify(self, db: Session, *, verify_request: VerifyRequest) -> VerifyResponse:
        pub_objects = published_object.get_by_name(db=db, name=verify_request.name)
        for pub_object in pub_objects:
            if pub_object.payload == verify_request.payload:
                user_obj = user_db.get(db=db, id=pub_object.owner_id)
                if user_obj is None:
                    continue
                if user_obj.ta_public_key != verify_request.owner_public_key:
                    continue
                publisher_obj = user_db.get(db=db, id=pub_object.publisher_id)
                if publisher_obj is None:
                    continue
                if publisher_obj.ta_public_key != verify_request.publisher_public_key:
                    continue
                dobject = digital_object_db.get(db=db, id=pub_object.obj_id)
                if dobject is None:
                    continue
                req_ta_cert = decrypt(verify_request.ta_cert, settings.TA_PRIVATE_KEY_FILE)
                if dobject.parent_id is not None and dobject.parent_id != '':
                    parent_obj = digital_object_db.get(db=db, id=dobject.parent_id)
                    parent_name = parent_obj.name
                    parent_ta_cert = encrypt(parent_obj.ta_cert, settings.TA_PUBLIC_KEY_FILE)
                else:
                    parent_name = ''
                    parent_ta_cert = ''
                if user_obj.ta_public_key[:100] == req_ta_cert:
                    vr = VerifyResponse(name=pub_object.name,
                                        kind=pub_object.kind,
                                        valid=True,
                                        parent_name=parent_name,
                                        parent_ta_cert=parent_ta_cert,
                                        created_at=dobject.created_at,
                                        updated_at=dobject.updated_at,
                                        published_at=pub_object.created_at)
                    published_object.increment_stats(db=db, obj_in=pub_object)
                    return vr
        raise HTTPException(status_code=401, detail='not found')

    def get_by_name(self, db: Session, *, name: str):
        objs = db.query(self.model) \
            .filter(self.model.name == name) \
            .all()
        return objs

    def increment_stats(self, db: Session, obj_in: PublishedObject):
        db.query(self.model) \
            .filter(self.model.id == obj_in.id) \
            .update({'num_verifications': self.model.num_verifications + 1,
                     'updated_at': datetime.now()})
        db.commit()


published_object = PublishedObjectDBHandler(PublishedObject)
