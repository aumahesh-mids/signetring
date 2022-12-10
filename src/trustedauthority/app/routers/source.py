from typing import List, Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from crypto.crypt import decrypt, sym_encrypt
from trustedauthority.app.config.settings import settings
from trustedauthority.app.db.handler.source_app_db import source_app as source_app_db
from trustedauthority.app.db.handler.digital_object_db import digital_object as digital_object_db
from trustedauthority.app.model.digital_object import DigitalObjectResponse

from trustedauthority.app.model.source import SourceAppResponse, SourceAppRequest, SourceAppStats, \
    SourceAppCreateResponse
from trustedauthority.app.routers import deps

router = APIRouter()


@router.get('/', response_model=List[SourceAppResponse])
async def read_source_apps(db: Session = Depends(deps.get_db)) -> Any:
    apps = source_app_db.get_multi(db)
    app_objs = []
    for a in apps:
        app_objs.append(a.source_app_response())
    return app_objs


@router.get('/{app_id}', response_model=SourceAppResponse)
async def read_source_app(*, db: Session = Depends(deps.get_db), app_id: str) -> Any:
    return source_app_db.get(db=db, id=app_id).source_app_response()


@router.get('/{app_id}/stats', response_model=SourceAppStats)
async def read_source_app_stats(*, db: Session = Depends(deps.get_db), app_id: str) -> Any:
    return source_app_db.get(db=db, id=app_id).source_app_stats_response()

@router.get('/{app_id}/objects', response_model=List[DigitalObjectResponse])
async def read_source_app_objects(*, db: Session = Depends(deps.get_db), app_id: str) -> Any:
    source_app = source_app_db.get(db=db, id=app_id)
    objs = digital_object_db.get_app_objects(db, source_app.id)
    owned_objs = []
    for obj in objs:
        owned_objs.append(obj.digital_object_response())
    return owned_objs


@router.post('/', response_model=SourceAppCreateResponse)
async def create_source_app(*, db: Session = Depends(deps.get_db), source_app_object: SourceAppRequest) -> Any:
    resp = source_app_db.create(db=db, obj_in=source_app_object).source_app_create_response()
    one_time_key = decrypt(source_app_object.one_time_key, settings.TA_PRIVATE_KEY_FILE)
    ta_public_key = resp.ta_public_key
    ta_private_key = resp.ta_private_key
    resp.ta_public_key = sym_encrypt(ta_public_key, bytes(one_time_key, 'utf-8'))
    resp.ta_private_key = sym_encrypt(ta_private_key, bytes(one_time_key, 'utf-8'))
    return resp
