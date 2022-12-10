import logging
from typing import List, Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from trustedauthority.app.db.handler.digital_object_db import digital_object as digital_object_db
from trustedauthority.app.db.handler.published_object_db import published_object as published_object_db
from trustedauthority.app.db.handler.user_db import user as user_db
from trustedauthority.app.db.model.published_object import PublishedObject

from trustedauthority.app.model.digital_object import DigitalObject, DigitalObjectRequest, DigitalObjectStats, \
    DigitalObjectResponse
from trustedauthority.app.model.published_object import PublishObjectRequest, PublishObjectResponse
from trustedauthority.app.routers import deps

router = APIRouter()

logger = logging.getLogger(__name__)


@router.get('/', response_model=List[DigitalObjectResponse])
async def read_digital_objects(db: Session = Depends(deps.get_db)) -> Any:
    apps = digital_object_db.get_multi(db)
    app_objs = []
    for a in apps:
        app_objs.append(a.digital_object_response())
    return app_objs


@router.get('/{object_id}', response_model=DigitalObjectResponse)
async def read_digital_object(*, db: Session = Depends(deps.get_db), object_id: str) -> Any:
    return digital_object_db.get(db=db, id=object_id).digital_object_response()


@router.get('/{object_id}/stats', response_model=DigitalObjectStats)
async def read_digital_object_stats(*, db: Session = Depends(deps.get_db), object_id: str) -> Any:
    return digital_object_db.get(db=db, id=object_id).digital_object_stats_response()


@router.get('/{object_id}/lineage', response_model=dict)
async def read_digital_object_lineage(*, db: Session = Depends(deps.get_db), object_id: str) -> Any:
    result = {}
    q = [object_id]
    while len(q) > 0:
        n = q.pop(0)
        pid = digital_object_db.get_parent(db, n)
        logger.info(f'{n} -> {pid}')
        if pid == '':
            break
        result[n] = pid
        q.append(pid)
    return result


@router.get('/{object_id}/children', response_model=dict)
async def read_digital_object_children(*, db: Session = Depends(deps.get_db), object_id: str) -> Any:
    result = {}
    q = [object_id]
    while len(q) > 0:
        n = q.pop(0)
        children = digital_object_db.get_children(db, n)
        result[n] = children
        q.extend(children)
    return result


def get_published_object_response(db: Session, published_object: PublishedObject) -> PublishObjectResponse:
    dobject = digital_object_db.get(db=db, id=published_object.obj_id)
    if dobject is None:
        raise HTTPException(status_code=401, detail='missing digital object')
    user_object = user_db.get(db=db, id=published_object.owner_id)
    if user_object is None:
        raise HTTPException(status_code=401, detail='missing owner')
    publisher_object = user_db.get(db=db, id=published_object.publisher_id)
    if publisher_object is None:
        raise HTTPException(status_code=401, detail='missing publisher')
    pr = PublishObjectResponse(name=dobject.name,
                               kind=dobject.kind,
                               owner_public_key=user_object.ta_public_key,
                               publisher_public_key=publisher_object.ta_public_key,
                               payload=dobject.payload,
                               ta_cert=published_object.ta_cert)
    return pr


@router.post('/{object_id}/publish', response_model=PublishObjectResponse)
async def publish_digital_object(*,db: Session = Depends(deps.get_db), publish_request: PublishObjectRequest) -> Any:
    pub_response = published_object_db.create(db=db, obj_in=publish_request)
    return get_published_object_response(db, pub_response)


@router.post('/', response_model=DigitalObjectResponse)
async def create_digital_object(*, db: Session = Depends(deps.get_db), source_app_object: DigitalObjectRequest) -> Any:
    return digital_object_db.create(db=db, obj_in=source_app_object).digital_object_response()


