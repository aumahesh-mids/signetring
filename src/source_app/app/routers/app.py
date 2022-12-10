import json
import logging
import random
import string
import uuid
from datetime import datetime
from typing import Any

import names
import requests
from fastapi import APIRouter, status, HTTPException

from crypto.crypt import encrypt, sym_decrypt, decrypt, decrypt_with_key_str
from crypto.key import new_symmetric_key
from source_app.app.config.settings import settings
from source_app.app.model.model import InitAppResponse, InitAppRequest, ClickRequest
from trustedauthority.app.model.auth import KeyRequest, KeyResponse
from trustedauthority.app.model.digital_object import DigitalObjectResponse, DigitalObjectRequest
from trustedauthority.app.model.enums import SourceAppType, DigitalObjectType
from trustedauthority.app.model.source import SourceAppCreateResponse, SourceAppRequest, SourceAppResponse

router = APIRouter()

logger = logging.getLogger(__name__)

source_app_inited = False

source_app_instance = SourceAppCreateResponse(id='dummy',
                                              name='dummy',
                                              kind=SourceAppType.Camera,
                                              ta_public_key='',
                                              ta_private_key='',
                                              created_at=datetime.now(),
                                              updated_at=datetime.now())


@router.post('/', response_model=InitAppResponse)
async def init_app(user_request: InitAppRequest) -> Any:
    global source_app_instance, source_app_inited
    logger.debug(f'request {user_request}')
    user_registration_endpoint = settings.TA_API_URL + '/apps/'
    one_time_key = new_symmetric_key()
    encrypted_one_time_key = encrypt(one_time_key.decode('utf-8'), settings.TA_PUBLIC_KEY)
    app_registration_object = SourceAppRequest(name=user_request.name,
                                               kind=user_request.kind,
                                               one_time_key=encrypted_one_time_key)
    json_obj = json.dumps(app_registration_object.__dict__)
    logger.debug(f'json {json_obj}')
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    ta_response = requests.post(user_registration_endpoint, data=json_obj, headers=headers)
    logger.debug(f'app creation status code {ta_response.status_code}')
    if ta_response.status_code != status.HTTP_200_OK:
        raise Exception('user creation failed')
    logger.debug(f'app creation response {ta_response.json()}')
    j = json.loads(ta_response.content)
    x = SourceAppCreateResponse(**j)
    public_key = x.ta_public_key
    private_key = x.ta_private_key
    source_app_instance.ta_public_key = sym_decrypt(public_key, one_time_key)
    source_app_instance.ta_private_key = sym_decrypt(private_key, one_time_key)
    source_app_instance.id = x.id
    source_app_instance.name = x.name
    source_app_instance.kind = x.kind
    source_app_instance.created_at = x.created_at
    source_app_instance.updated_at = x.updated_at

    api_response = InitAppResponse(ta_id=source_app_instance.id,
                                   name=source_app_instance.name,
                                   kind=source_app_instance.kind,
                                   ta_public_key=source_app_instance.ta_public_key,
                                   created_at=source_app_instance.created_at,
                                   updated_at=source_app_instance.updated_at)

    source_app_inited = True

    return api_response


@router.get('/', response_model=SourceAppResponse)
async def get() -> Any:
    if not source_app_inited:
        raise HTTPException(status_code=400, detail='app not initialized')
    app = SourceAppResponse(id=source_app_instance.id,
                            name=source_app_instance.name,
                            kind=source_app_instance.kind,
                            ta_public_key=source_app_instance.ta_public_key,
                            created_at=source_app_instance.created_at,
                            updated_at=source_app_instance.updated_at)
    return app


@router.post('/click', response_model=DigitalObjectResponse)
async def click(click_request: ClickRequest) -> Any:
    # Authenticate and create a sym key with TA
    endpoint = settings.TA_API_URL + '/auth/'
    auth_request = KeyRequest(user_id=click_request.user_id,
                              app_id=source_app_instance.id, )
    json_obj = json.dumps(auth_request.__dict__)
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    auth_response = requests.post(endpoint, data=json_obj, headers=headers)
    logger.debug(f'app creation status code {auth_response.status_code}')
    logger.debug(f'app creation response {auth_response.content}')
    j = json.loads(auth_response.content)
    resp = KeyResponse(**j)

    # decrypt challenge text
    user_private_key = click_request.user_private_key
    enc_challenge_text1 = resp.challenge_text
    sym_key_part1 = decrypt_with_key_str(resp.sym_key_part1, user_private_key)
    sym_key_part2 = decrypt_with_key_str(resp.sym_key_part2, source_app_instance.ta_private_key)
    sym_key = sym_key_part1 + sym_key_part2
    challenge_text = sym_decrypt(enc_challenge_text1, bytes(sym_key, 'utf-8'))
    enc_challenge_text2 = encrypt(challenge_text, settings.TA_PUBLIC_KEY)

    # create a pic
    name = names.get_first_name()
    letters = string.ascii_lowercase
    payload = ''.join(random.choice(letters) for i in range(100))
    encrypted_payload = encrypt(payload, settings.TA_PUBLIC_KEY)
    request = DigitalObjectRequest(name=name,
                                   kind=DigitalObjectType.Photo,
                                   source_app_id=source_app_instance.id,
                                   owner_id=click_request.user_id,
                                   challenge=enc_challenge_text2,
                                   payload=encrypted_payload,
                                   parent_id=click_request.parent_obj_id,
                                   parent_ta_cert=click_request.parent_ta_cert
                                   )
    json_obj = json.dumps(request.__dict__)
    logger.debug(f'json {json_obj}')
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    digital_object_registration_endpoint = settings.TA_API_URL + '/objects/'
    ta_response = requests.post(digital_object_registration_endpoint, data=json_obj, headers=headers)
    logger.debug(f'object creation status code {ta_response.status_code}')
    logger.debug(f'object creation response {ta_response.content}')
    j = json.loads(ta_response.content)
    resp = DigitalObjectResponse(**j)
    return resp
