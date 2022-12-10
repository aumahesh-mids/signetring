from typing import List, Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from trustedauthority.app.db.handler.challenge_db import challenge as challenge_db
from trustedauthority.app.model.publish import ChallengeRequest, ChallengeId, ChallengeUpdate, ChallengeResponse
from trustedauthority.app.model.verify import VerifyRequest, VerifyResponse
from trustedauthority.app.routers import deps

router = APIRouter()


@router.post('/', response_model=ChallengeId)
async def init_challenge(*, db: Session = Depends(deps.get_db), challenge_request: ChallengeRequest) -> Any:
    challenge = challenge_db.create(db=db, obj_in=challenge_request)
    c = ChallengeId(challenge_id=challenge.id)
    return c


@router.put('/{challenge_id}', response_model=None)
async def update_challenge(*, db: Session = Depends(deps.get_db), challenge_id: str, challenge_update: ChallengeUpdate) -> Any:
    challenge_db.update_challenge(db=db, id=challenge_id, obj_in=challenge_update)
    return


@router.get('/{challenge_id}', response_model=ChallengeResponse)
async def fetch_challenge(*, db: Session = Depends(deps.get_db), challenge_id: str) -> Any:
    challenge = challenge_db.get_challenge(db=db, challenge_id=challenge_id)
    if challenge is None:
        raise HTTPException(status_code=401, detail='challenge not found')
    return challenge.get_challenge_response()
