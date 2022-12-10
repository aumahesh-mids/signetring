import logging
from typing import List, Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from crypto.crypt import decrypt
from trustedauthority.app.config.settings import settings
from trustedauthority.app.db.handler.user_db import user as user_db
from trustedauthority.app.db.handler.digital_object_db import digital_object as digital_object_db
from trustedauthority.app.model.digital_object import DigitalObjectResponse
from trustedauthority.app.model.user import User, UserRequest, UserResponse, UserStats, UserCreateResponse
from trustedauthority.app.routers import deps

from crypto.crypt import sym_encrypt

router = APIRouter()

logger = logging.getLogger(__name__)


@router.get('/', response_model=List[UserResponse])
async def read_users(db: Session = Depends(deps.get_db)) -> Any:
    users = user_db.get_multi(db)
    user_objs = []
    for u in users:
        user_objs.append(u.user_response())
    return user_objs


@router.get('/{user_id}', response_model=UserResponse)
async def read_user(*, db: Session = Depends(deps.get_db), user_id: str) -> Any:
    return user_db.get(db=db, id=user_id).user_response()


@router.get('/{user_id}/stats', response_model=UserStats)
async def read_user_stats(*, db: Session = Depends(deps.get_db), user_id: str) -> Any:
    return user_db.get(db=db, id=user_id).stat_response()


@router.get('/{user_id}/objects', response_model=List[DigitalObjectResponse])
async def read_user_objects(*, db: Session = Depends(deps.get_db), user_id: str) -> Any:
    user = user_db.get(db=db, id=user_id)
    objs = digital_object_db.get_owner_objects(db, user.id)
    owned_objs = []
    for obj in objs:
        owned_objs.append(obj.digital_object_response())
    return owned_objs


@router.post('/', response_model=UserCreateResponse)
async def create_user(*, db: Session = Depends(deps.get_db), user_object: UserRequest) -> Any:
    logger.debug(f'user creation request {user_object}')
    resp = user_db.create(db=db, obj_in=user_object).user_create_response()
    one_time_key = decrypt(user_object.one_time_key, settings.TA_PRIVATE_KEY_FILE)
    ta_public_key = resp.ta_public_key
    ta_private_key = resp.ta_private_key
    resp.ta_public_key = sym_encrypt(ta_public_key, bytes(one_time_key, 'utf-8'))
    resp.ta_private_key = sym_encrypt(ta_private_key, bytes(one_time_key, 'utf-8'))
    return resp
