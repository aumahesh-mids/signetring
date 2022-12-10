import json
import logging
import random
import string
from typing import Any

import names
import requests
from fastapi import APIRouter, HTTPException, status
from starlette.responses import Response
from starlette.status import HTTP_200_OK

from crypto.crypt import encrypt, encrypt_with_key_str, decrypt_with_key_str
from trustedauthority.app.model.enums import UserType
from trustedauthority.app.model.publish import ChallengeId, ChallengeRequest, ChallengeResponse, ChallengeUpdate
from trustedauthority.app.model.published_object import PublishObjectRequest, PublishObjectResponse, VerifyChallenge
from trustedauthority.app.model.user import UserResponse
from user.app.config.settings import settings
from user.app.model.user import ChallengeAcceptedByUser
from user.app.routers.user import app_user

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post('/{challenge_id}/verify', response_model=VerifyChallenge)
async def challenge_verify(challenge_id: str) -> Any:
    # get challenge from TA
    ta_challenge_endpoint = settings.TA_API_URL + f'/challenge/{challenge_id}'
    headers = {'Accept': 'application/json'}
    ta_response = requests.get(ta_challenge_endpoint, headers=headers)
    logger.debug(f'challenge get status code {ta_response.status_code}')
    if ta_response.status_code != status.HTTP_200_OK:
        raise HTTPException(status_code=401, detail='challenge fetch failed')
    logger.debug(f'challenge fetch response {ta_response.json()}')
    j = json.loads(ta_response.content)
    challenge = ChallengeResponse(**j)

    # decrypt secret
    encrypted_secret = challenge.secret
    secret = decrypt_with_key_str(encrypted_secret, app_user.ta_private_key)

    # get user public key from TA
    ta_user_endpoint = settings.TA_API_URL + f'/users/{challenge.user_id}'
    ta_response = requests.get(ta_user_endpoint, headers=headers)
    logger.debug(f'user fetch status code {ta_response.status_code}')
    if ta_response.status_code != status.HTTP_200_OK:
        raise HTTPException(status_code=401, detail='user fetch failed')
    logger.debug(f'user fetch response {ta_response.json()}')
    j = json.loads(ta_response.content)
    user_object = UserResponse(**j)

    # update challenge
    letters = string.ascii_lowercase
    payload = secret + ';' + ''.join(random.choice(letters) for i in range(50))
    secret = encrypt_with_key_str(payload, user_object.ta_public_key)
    ta_challenge_update_endpoint = settings.TA_API_URL + f"/challenge/{challenge_id}"
    challenge_update_object = ChallengeUpdate(secret=secret)
    json_obj = json.dumps(challenge_update_object.__dict__)
    logger.debug(f'json {json_obj}')
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    ta_response = requests.put(ta_challenge_update_endpoint, data=json_obj, headers=headers)
    logger.debug(f'challenge update status code {ta_response.status_code}')
    if ta_response.status_code != status.HTTP_200_OK:
        raise HTTPException(status_code=401, detail='challenge update failed')
    pub_secret = encrypt_with_key_str(payload, app_user.ta_public_key)
    vc = VerifyChallenge(challenge_id=challenge_id,
                         opaque=pub_secret)
    return vc


@router.post('/{challenge_id}/accept', response_model=PublishObjectResponse)
async def publish(challenge_id: str, user_acceptance: ChallengeAcceptedByUser) -> Any:
    # get challenge from TA
    ta_challenge_endpoint = settings.TA_API_URL + f'/challenge/{challenge_id}'
    headers = {'Accept': 'application/json'}
    ta_response = requests.get(ta_challenge_endpoint, headers=headers)
    logger.debug(f'challenge get status code {ta_response.status_code}')
    if ta_response.status_code != status.HTTP_200_OK:
        raise HTTPException(status_code=401, detail='challenge fetch failed')
    logger.debug(f'challenge fetch response {ta_response.json()}')
    j = json.loads(ta_response.content)
    challenge = ChallengeResponse(**j)

    # decrypt secret
    secret = decrypt_with_key_str(user_acceptance.opaque, app_user.ta_private_key)
    s1, s2 = secret.split(';')

    if s1 != user_acceptance.user_secret or s2 != user_acceptance.publisher_secret:
        raise HTTPException(status_code=401, detail='cannot verify user')

    # post publication to TA
    publish_request = PublishObjectRequest(obj_id=user_acceptance.obj_id,
                                           owner_id=user_acceptance.user_id,
                                           publisher_id=app_user.id)
    ta_publish_endpoint = settings.TA_API_URL + f'/objects/{user_acceptance.obj_id}/publish'
    json_obj = json.dumps(publish_request.__dict__)
    logger.debug(f'json {json_obj}')
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    ta_response = requests.post(ta_publish_endpoint, data=json_obj, headers=headers)
    logger.debug(f'publish request status code {ta_response.status_code}')
    if ta_response.status_code != status.HTTP_200_OK:
        raise HTTPException(status_code=401, detail='publish request failed')
    logger.debug(f'publish response {ta_response.json()}')
    j = json.loads(ta_response.content)
    publish_response = PublishObjectResponse(**j)
    return publish_response