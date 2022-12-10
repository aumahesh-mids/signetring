import json
import logging
from datetime import datetime
from typing import Any

import requests
from fastapi import APIRouter, status, HTTPException

from crypto.crypt import encrypt, sym_decrypt, encrypt_with_key_str
from crypto.key import new_symmetric_key
from source_app.app.model.model import ClickRequest
from trustedauthority.app.model.digital_object import DigitalObjectResponse
from trustedauthority.app.model.enums import UserType
from trustedauthority.app.model.source import SourceAppResponse
from trustedauthority.app.model.user import UserCreateResponse, UserRequest, UserResponse
from user.app.config.settings import settings
from user.app.model.user import InitUserRequest, InitUserResponse

logger = logging.getLogger(__name__)

router = APIRouter()

app_inited = False
app_user = UserCreateResponse(id='dummy',
                              name='dummy',
                              kind=UserType.Creator,
                              ta_public_key='',
                              ta_private_key='',
                              created_at=datetime.now(),
                              updated_at=datetime.now())


@router.post('/', response_model=InitUserResponse)
async def init_user(user_request: InitUserRequest) -> Any:
    global app_user, app_inited
    logger.debug(f'request {user_request}')
    user_registration_endpoint = settings.TA_API_URL + '/users/'
    one_time_key = new_symmetric_key()
    encrypted_one_time_key = encrypt(one_time_key.decode('utf-8'), settings.TA_PUBLIC_KEY)
    user_registration_object = UserRequest(name=user_request.name,
                                           kind=user_request.kind,
                                           one_time_key=encrypted_one_time_key)
    json_obj = json.dumps(user_registration_object.__dict__)
    logger.debug(f'json {json_obj}')
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    ta_response = requests.post(user_registration_endpoint, data=json_obj, headers=headers)
    logger.debug(f'user creation status code {ta_response.status_code}')
    if ta_response.status_code != status.HTTP_200_OK:
        raise Exception('user creation failed')
    logger.debug(f'user creation response {ta_response.json()}')
    j = json.loads(ta_response.content)
    x = UserCreateResponse(**j)
    public_key = x.ta_public_key
    private_key = x.ta_private_key
    app_user.ta_public_key = sym_decrypt(public_key, one_time_key)
    app_user.ta_private_key = sym_decrypt(private_key, one_time_key)
    app_user.id = x.id
    app_user.name = x.name
    app_user.kind = x.kind
    app_user.created_at = x.created_at
    app_user.updated_at = x.updated_at

    api_response = InitUserResponse(ta_id=app_user.id,
                                    name=app_user.name,
                                    kind=app_user.kind,
                                    ta_public_key=app_user.ta_public_key,
                                    created_at=app_user.created_at,
                                    updated_at=app_user.updated_at)

    app_inited = True

    return api_response


@router.get('/', response_model=UserResponse)
async def get_user() -> Any:
    if not app_inited:
        raise HTTPException(status_code=400, detail='app not initialized')
    user_response = UserResponse(id=app_user.id,
                                 name=app_user.name,
                                 kind=app_user.kind,
                                 ta_public_key=app_user.ta_public_key,
                                 created_at=app_user.created_at,
                                 updated_at=app_user.updated_at)
    return user_response


@router.post('/click', response_model=DigitalObjectResponse)
async def click() -> Any:
    # post a click request to app
    new_click = ClickRequest(user_id=app_user.id,
                             user_private_key=app_user.ta_private_key,
                             parent_obj_id='',
                             parent_ta_cert='')
    json_obj = json.dumps(new_click.__dict__)
    logger.debug(f'json {json_obj}')
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    new_click_request = settings.SOURCE_APP_API_URL + '/app/click'
    ta_response = requests.post(new_click_request, data=json_obj, headers=headers)
    logger.debug(f'click request status code {ta_response.status_code}')
    logger.debug(f'click request response {ta_response.json()}')
    j = json.loads(ta_response.content)
    resp = DigitalObjectResponse(**j)
    return resp

