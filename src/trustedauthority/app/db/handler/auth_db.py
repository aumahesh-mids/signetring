import logging
from datetime import datetime, timedelta
import uuid

from sqlalchemy.orm import Session

from trustedauthority.app.db.handler.base import BaseHandler
from trustedauthority.app.db.model.auth import Auth
from trustedauthority.app.model.auth import KeyRequest, KeyUpdate
from crypto.key import new_symmetric_key

logger = logging.getLogger(__name__)


class AuthDBHandler(BaseHandler[Auth, KeyRequest, KeyUpdate]):
    def create(self, db: Session, *, obj_in: KeyRequest) -> Auth:
        db_obj = Auth()
        db_obj.id = str(uuid.uuid1())
        logger.info(f"key create request {obj_in}")
        db_obj.user_id = obj_in.user_id
        db_obj.app_id = obj_in.app_id
        db_obj.key = new_symmetric_key().decode('utf-8')
        db_obj.challenge_text = str(uuid.uuid1())
        db_obj.expires_at = datetime.now() + timedelta(days=1)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_key(self, db: Session, *, user_id: str, app_id: str) -> Auth:
        entry = db.query(self.model) \
            .filter(self.model.user_id == user_id, self.model.app_id == app_id) \
            .first()
        return entry


auth = AuthDBHandler(Auth)
