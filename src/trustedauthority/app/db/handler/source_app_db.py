import logging
import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from trustedauthority.app.db.handler.base import BaseHandler
from trustedauthority.app.db.model.source import SourceApp
from trustedauthority.app.model.source import SourceAppRequest, SourceAppUpdate
from crypto.key import new_public_private_key_pair

logger = logging.getLogger(__name__)


class SourceAppDBHandler(BaseHandler[SourceApp, SourceAppRequest, SourceAppUpdate]):
    def create(self, db: Session, *, obj_in: SourceAppRequest) -> SourceApp:
        db_obj = SourceApp()
        db_obj.id = str(uuid.uuid1())
        logger.info(f"source app create request {obj_in}")
        db_obj.name = obj_in.name
        db_obj.kind = obj_in.kind
        db_obj.ta_cert = str(uuid.uuid5(uuid.NAMESPACE_OID, obj_in.name))
        db_obj.created_at = datetime.now()
        db_obj.updated_at = db_obj.created_at
        pub, priv = new_public_private_key_pair()
        db_obj.ta_public_key = pub
        db_obj.ta_private_key = priv
        # db_obj.last_object_registered_at = None
        db_obj.num_objects = 0
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def increment_stats(self, db: Session, app_id: str, commit: bool):
        db.query(self.model)\
            .filter(self.model.id==app_id)\
            .update({'num_objects': self.model.num_objects + 1,
                     'updated_at': datetime.now()})
        if commit:
            db.commit()


source_app = SourceAppDBHandler(SourceApp)