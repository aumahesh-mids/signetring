from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from crypto.crypt import encrypt, sym_encrypt, encrypt_with_key_str
from trustedauthority.app.model.auth import KeyResponse, KeyRequest
from trustedauthority.app.routers import deps
from trustedauthority.app.db.handler.user_db import user as user_db
from trustedauthority.app.db.handler.source_app_db import source_app as app_db
from trustedauthority.app.db.handler.auth_db import auth as auth_db

router = APIRouter()


@router.post('/', response_model=KeyResponse)
async def auth_request(*, db: Session = Depends(deps.get_db), req: KeyRequest) -> Any:
    new_key = auth_db.create(db=db, obj_in=req).key_response()
    user = user_db.get(db, id=req.user_id)
    app = app_db.get(db, id=req.app_id)
    key_part1 = new_key.sym_key_part1
    key_part2 = new_key.sym_key_part2
    encrypted_part1 = encrypt_with_key_str(key_part1, user.ta_public_key)
    encrypted_part2 = encrypt_with_key_str(key_part2, app.ta_public_key)
    challenge_text = new_key.challenge_text
    key = key_part1 + key_part2
    encrypted_challenge_text = sym_encrypt(challenge_text, bytes(key, 'utf-8'))
    new_key.challenge_text = encrypted_challenge_text
    new_key.sym_key_part1 = encrypted_part1
    new_key.sym_key_part2 = encrypted_part2
    return new_key

