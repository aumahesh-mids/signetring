import logging
from datetime import datetime
import uuid

from sqlalchemy.orm import Session

from trustedauthority.app.db.handler.base import BaseHandler
from trustedauthority.app.db.model.user import User
from trustedauthority.app.model.enums import StatsType
from trustedauthority.app.model.user import UserRequest, UserUpdate
from crypto.key import new_public_private_key_pair

logger = logging.getLogger(__name__)


class UserDBHandler(BaseHandler[User, UserRequest, UserUpdate]):
    def create(self, db: Session, *, obj_in: UserRequest) -> User:
        db_obj = User()
        db_obj.id = str(uuid.uuid1())
        logger.info(f"user create request {obj_in}")
        db_obj.name = obj_in.name
        db_obj.kind = obj_in.kind
        pub, priv = new_public_private_key_pair()
        db_obj.ta_public_key = pub
        db_obj.ta_private_key = priv
        db_obj.created_at = datetime.now()
        db_obj.updated_at = db_obj.created_at
        db_obj.num_created = 0
        db_obj.num_edited = 0
        db_obj.num_published = 0
        db_obj.num_verifications = 0
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def increment_stats(self, db: Session, stat: StatsType, user_id: str, commit: bool):
        if stat == StatsType.Creations:
            values = {'num_created': self.model.num_created + 1,
                      'updated_at': datetime.now()}
        elif stat == StatsType.Edits:
            values = {'num_edited': self.model.num_edited+1,
                      'updated_at': datetime.now()}
        elif stat == StatsType.Publications:
            values = {'num_published': self.model.num_published+1,
                      'updated_at': datetime.now()}
        elif stat == StatsType.Verifications:
            values = {'num_verifications': self.model.num_verifications+1,
                      'updated_at': datetime.now()}
        else:
            return
        db.query(self.model)\
            .filter(self.model.id==user_id)\
            .update(values)
        if commit:
            db.commit()


user = UserDBHandler(User)
