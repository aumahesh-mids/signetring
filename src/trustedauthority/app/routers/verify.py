from typing import List, Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from trustedauthority.app.db.handler.published_object_db import published_object as published_object_db
from trustedauthority.app.model.verify import VerifyRequest, VerifyResponse
from trustedauthority.app.routers import deps

router = APIRouter()


@router.post('/', response_model=VerifyResponse)
async def verify_object(*, db: Session = Depends(deps.get_db), verify_request: VerifyRequest) -> Any:
    return published_object_db.verify(db=db, verify_request=verify_request)