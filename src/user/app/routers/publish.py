import json
import logging
import random
import string
from typing import Any

import names
import requests
from fastapi import APIRouter, HTTPException, status

from crypto.crypt import encrypt_with_key_str, decrypt_with_key_str
from trustedauthority.app.model.enums import UserType
from trustedauthority.app.model.publish import ChallengeId, ChallengeRequest, ChallengeResponse
from trustedauthority.app.model.published_object import PublishObjectResponse, VerifyChallenge
from trustedauthority.app.model.user import UserResponse
from user.app.config.settings import settings
from user.app.model.user import ChallengeAcceptedByUser
from user.app.routers.user import app_user

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post('/{obj_id}', response_model=PublishObjectResponse)
async def publish(obj_id: str) -> Any:
    if app_user.kind != UserType.Creator:
        raise HTTPException(status_code=401, detail="only creator can initiate publication")

    logger.debug(f"app_user {app_user}")

    # get publisher's info
    publisher_endpoint = settings.PUBLISHER_API_URL + "/user/"
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    ta_response = requests.get(publisher_endpoint, headers=headers)
    logger.debug(f'publisher get status code {ta_response.status_code}')
    if ta_response.status_code != status.HTTP_200_OK:
        raise HTTPException(status_code=401, detail='publisher get failed')
    logger.debug(f'publisher get response {ta_response.json()}')
    j = json.loads(ta_response.content)
    publisher = UserResponse(**j)

    # create challenge
    name = names.get_first_name()
    letters = string.ascii_lowercase
    payload = ''.join(random.choice(letters) for i in range(50))
    secret = encrypt_with_key_str(payload, publisher.ta_public_key)
    ta_challenge_endpoint = settings.TA_API_URL + "/challenge/"
    challenge_object = ChallengeRequest(secret=secret,
                                        obj_id=obj_id,
                                        user_id=app_user.id)
    json_obj = json.dumps(challenge_object.__dict__)
    logger.debug(f'json {json_obj}')
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    ta_response = requests.post(ta_challenge_endpoint, data=json_obj, headers=headers)
    logger.debug(f'challenge creation status code {ta_response.status_code}')
    if ta_response.status_code != status.HTTP_200_OK:
        raise HTTPException(status_code=401, detail='challenge creation failed')
    logger.debug(f'challenge creation response {ta_response.json()}')
    j = json.loads(ta_response.content)
    challenge_id = ChallengeId(**j)

    # send challenge to publisher
    publisher_endpoint = settings.PUBLISHER_API_URL + f'/challenge/{challenge_id.challenge_id}/verify'
    headers = {'Accept': 'application/json'}
    publisher_response = requests.post(publisher_endpoint, headers=headers)
    logger.debug(f'publisher challenge verification status code {publisher_response.status_code}')
    if publisher_response.status_code != status.HTTP_200_OK:
        raise HTTPException(status_code=401, detail='publisher challenge verification failed')
    logger.debug(f'challenge verification response {publisher_response.json()}')
    j = json.loads(publisher_response.content)
    verify_challenge_message = VerifyChallenge(**j)

    # verify challenge
    # get challenge from TA
    ta_challenge_endpoint = settings.TA_API_URL + f'/challenge/{challenge_id.challenge_id}'
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
    s1, s2 = secret.split(';')

    if s1 != payload:
        raise HTTPException(status_code=401, detail='cannot verify publisher')

    # accept the challenge or reject the challenge

    user_accepted_challenge = ChallengeAcceptedByUser(id=challenge_id.challenge_id,
                                                      obj_id=obj_id,
                                                      user_id=app_user.id,
                                                      user_secret=s1,
                                                      publisher_secret=s2,
                                                      opaque=verify_challenge_message.opaque)
    publisher_challenge_endpoint = settings.PUBLISHER_API_URL + f"/challenge/{challenge_id.challenge_id}/accept"
    json_obj = json.dumps(user_accepted_challenge.__dict__)
    logger.debug(f'json {json_obj}')
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    publisher_response = requests.post(publisher_challenge_endpoint, data=json_obj, headers=headers)
    logger.debug(f'publisher acceptance status code {ta_response.status_code}')
    if ta_response.status_code != status.HTTP_200_OK:
        raise HTTPException(status_code=401, detail='publisher rejected the challenge')
    logger.debug(f'publisher accepted challenge')
    j = json.loads(publisher_response.content)
    publish_response = PublishObjectResponse(**j)
    return publish_response
