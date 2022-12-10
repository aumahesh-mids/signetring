import logging
from datetime import datetime, timedelta
import uuid

from fastapi import HTTPException
from sqlalchemy.orm import Session

from trustedauthority.app.db.handler.base import BaseHandler
from trustedauthority.app.db.model.challenge import Challenge
from trustedauthority.app.model.publish import ChallengeRequest, ChallengeUpdate
from crypto.key import new_symmetric_key

logger = logging.getLogger(__name__)


class ChallengeDBHandler(BaseHandler[Challenge, ChallengeRequest, ChallengeUpdate]):
    def create(self, db: Session, *, obj_in: ChallengeRequest) -> Challenge:
        db_obj = Challenge()
        db_obj.id = str(uuid.uuid1())
        logger.info(f"challenge create request {obj_in}")
        db_obj.obj_id = obj_in.obj_id
        db_obj.user_id = obj_in.user_id
        db_obj.secret = obj_in.secret
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update_challenge(self, db: Session, *, id: str, obj_in: ChallengeUpdate) -> Challenge:
        entry = challenge.get_challenge(db=db, challenge_id=id)
        if entry is None:
            raise HTTPException(status_code=401, detail='missing challenge')
        db.query(self.model) \
            .filter(self.model.id == id) \
            .update({'secret': obj_in.secret})
        db.commit()
        return challenge.get_challenge(db=db, challenge_id=id)

    def get_challenge(self, db: Session, *, challenge_id: str) -> Challenge:
        entry = db.query(self.model) \
            .filter(self.model.id == challenge_id) \
            .first()
        return entry


challenge = ChallengeDBHandler(Challenge)
