#
# Copyright The NOMAD Authors.
#
# This file is part of NOMAD. See https://nomad-lab.eu for further info.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import datetime
import hashlib
import hmac
import uuid
from collections.abc import Callable
from enum import Enum
from functools import wraps
from inspect import Parameter, signature
from typing import cast

import jwt
import requests
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi import Query as FastApiQuery
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

from nomad import datamodel, infrastructure, utils
from nomad.config import config
from nomad.utils import get_logger, strip

from ..common import root_path
from ..models import HTTPExceptionModel, User
from ..utils import create_responses

logger = get_logger(__name__)

router = APIRouter()


class APITag(str, Enum):
    DEFAULT = 'auth'


class Token(BaseModel):
    access_token: str
    token_type: str


class SignatureToken(BaseModel):
    signature_token: str


class AppToken(BaseModel):
    app_token: str


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f'{root_path}/auth/token', auto_error=False
)


def create_user_dependency(
    required: bool = False,
    basic_auth_allowed: bool = False,
    bearer_token_auth_allowed: bool = True,
    upload_token_auth_allowed: bool = False,
    signature_token_auth_allowed: bool = False,
) -> Callable:
    """
    Creates a dependency for getting the authenticated user. The parameters define if
    the authentication is required or not, and which authentication methods are allowed.
    """

    def user_dependency(**kwargs) -> User | None:
        user = None
        if basic_auth_allowed:
            user = _get_user_basic_auth(kwargs.get('form_data'))
        if user is None and bearer_token_auth_allowed:
            user = _get_user_bearer_token_auth(kwargs.get('bearer_token'))
        if user is None and upload_token_auth_allowed:
            user = _get_user_upload_token_auth(kwargs.get('token'))
        if user is None and signature_token_auth_allowed:
            user = _get_user_signature_token_auth(
                kwargs.get('signature_token'), kwargs.get('request')
            )

        if user is None and config.tests.assume_auth_for_username:
            user = datamodel.User.get(username=config.tests.assume_auth_for_username)

        if required and user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Authorization required.',
            )

        if config.oasis.allowed_users is not None:
            # We're an oasis, and have allowed_users set
            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail='Authentication is required for this Oasis',
                    headers={'WWW-Authenticate': 'Bearer'},
                )
            if (
                user.email not in config.oasis.allowed_users
                and user.username not in config.oasis.allowed_users
            ):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail='You are not authorized to access this Oasis',
                    headers={'WWW-Authenticate': 'Bearer'},
                )

        if user is not None:
            try:
                assert datamodel.User.get(user.user_id) is not None
            except Exception as e:
                logger = utils.get_logger(__name__)
                logger.error(
                    'API usage by unknown user. Possible misconfiguration', exc_info=e
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail='You are logged in with an unknown user',
                    headers={'WWW-Authenticate': 'Bearer'},
                ) from e

        return user

    # Create the desired function signature (as it depends on which auth options are allowed)
    new_parameters = []
    if basic_auth_allowed:
        new_parameters.append(
            Parameter(
                name='form_data',
                annotation=OAuth2PasswordRequestForm,
                default=Depends(),
                kind=Parameter.KEYWORD_ONLY,
            )
        )
    if bearer_token_auth_allowed:
        new_parameters.append(
            Parameter(
                name='bearer_token',
                annotation=str,
                default=Depends(oauth2_scheme),
                kind=Parameter.KEYWORD_ONLY,
            )
        )
    if upload_token_auth_allowed:
        new_parameters.append(
            Parameter(
                name='token',
                annotation=str,
                default=FastApiQuery(
                    None,
                    description='Token for simplified authorization for uploading.',
                ),
                kind=Parameter.KEYWORD_ONLY,
            )
        )
    if signature_token_auth_allowed:
        new_parameters.append(
            Parameter(
                name='signature_token',
                annotation=str,
                default=FastApiQuery(
                    None, description='Signature token used to sign download urls.'
                ),
                kind=Parameter.KEYWORD_ONLY,
            )
        )
        new_parameters.append(
            Parameter(name='request', annotation=Request, kind=Parameter.KEYWORD_ONLY)
        )

    # Create a wrapper around user_dependency, and set the signature on it
    @wraps(user_dependency)
    def wrapper(**kwargs) -> Callable:
        return user_dependency(**kwargs)

    sig = signature(user_dependency)
    sig = sig.replace(parameters=tuple(new_parameters))
    wrapper.__signature__ = sig  # type: ignore
    return wrapper


def _get_user_basic_auth(form_data: OAuth2PasswordRequestForm) -> User | None:
    """
    Verifies basic auth (username and password), throwing an exception
    if illegal credentials are provided.

    Returns:
        The corresponding User object if successful,
        None if no credentials provided.
    """
    if form_data and form_data.username and form_data.password:
        try:
            infrastructure.keycloak.basicauth(form_data.username, form_data.password)
            return cast(
                datamodel.User,
                infrastructure.user_management.get_user(form_data.username),
            )
        except infrastructure.KeycloakError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Incorrect username or password',
                headers={'WWW-Authenticate': 'Bearer'},
            )
    return None


def _get_user_bearer_token_auth(bearer_token: str) -> User | None:
    """
    Verifies bearer_token (throwing exception if illegal value provided).

    Returns:
        The corresponding User object,
        or None if no bearer_token provided.
    """
    if not bearer_token:
        return None

    try:
        unverified_payload = jwt.decode(
            bearer_token, options={'verify_signature': False}
        )
        if unverified_payload.keys() == {'user', 'exp'}:
            return _get_user_from_simple_token(bearer_token)
    except jwt.exceptions.DecodeError:
        pass  # token could be non-JWT, e.g. for testing

    try:
        return cast(datamodel.User, infrastructure.keycloak.tokenauth(bearer_token))
    except infrastructure.KeycloakError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={'WWW-Authenticate': 'Bearer'},
        )


def _get_user_upload_token_auth(upload_token: str) -> User | None:
    """
    Verifies the upload token (throwing exception if illegal value provided).

    Returns:
        The corresponding User object,
        or None if no upload_token provided.
    """
    if upload_token:
        try:
            payload, signature = upload_token.split('.')
            payload_bytes = utils.base64_decode(payload)
            signature_bytes = utils.base64_decode(signature)

            compare = hmac.new(
                bytes(config.services.api_secret, 'utf-8'),
                msg=payload_bytes,
                digestmod=hashlib.sha1,
            )

            if signature_bytes == compare.digest():
                user_id = str(uuid.UUID(bytes=payload_bytes))
                return cast(
                    datamodel.User, infrastructure.user_management.get_user(user_id)
                )
        except Exception:
            # Decode error, format error, user not found, etc.
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='A invalid upload token was supplied.',
            )
    return None


def _get_user_signature_token_auth(
    signature_token: str, request: Request
) -> User | None:
    """
    Verifies the signature token (throwing exception if illegal value provided).

    Returns:
        The corresponding User object,
        or None if no upload_token provided.
    """
    if signature_token:
        return _get_user_from_simple_token(signature_token)

    elif request:
        auth_cookie = request.cookies.get('Authorization')
        if auth_cookie:
            try:
                auth_cookie = requests.utils.unquote(auth_cookie)  # type: ignore
                if auth_cookie.startswith('Bearer '):
                    cookie_bearer_token = auth_cookie[7:]
                    return cast(
                        datamodel.User,
                        infrastructure.keycloak.tokenauth(cookie_bearer_token),
                    )

            except infrastructure.KeycloakError as e:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=str(e),
                    headers={'WWW-Authenticate': 'Bearer'},
                )
            except Exception:
                pass

    return None


def _get_user_from_simple_token(token) -> User | None:
    """
    Verifies a simple token (throwing exception if illegal value provided).

    Returns:
        The corresponding user object,
        or None if no token was provided.
    """
    try:
        decoded = jwt.decode(token, config.services.api_secret, algorithms=['HS256'])
        return datamodel.User.get(user_id=decoded['user'])
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Token with invalid/unexpected payload.',
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Expired token.'
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token.'
        )


_bad_credentials_response = (
    status.HTTP_401_UNAUTHORIZED,
    {
        'model': HTTPExceptionModel,
        'description': strip(
            """
        Unauthorized. The provided credentials were not recognized."""
        ),
    },
)


@router.post(
    '/token',
    tags=[APITag.DEFAULT],
    summary='Get an access token',
    responses=create_responses(_bad_credentials_response),
    response_model=Token,
)
async def get_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    This API uses OAuth as an authentication mechanism. This operation allows you to
    retrieve an *access token* by posting username and password as form data.

    This token can be used on subsequent API calls to authenticate
    you. Operations that support or require authentication will expect the *access token*
    in an HTTP Authorization header like this: `Authorization: Bearer <access token>`.

    On the OpenAPI dashboard, you can use the *Authorize* button at the top.

    You only need to provide `username` and `password` values. You can ignore the other
    parameters.
    """
    try:
        access_token = infrastructure.keycloak.basicauth(
            form_data.username, form_data.password
        )
    except infrastructure.KeycloakError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    return {'access_token': access_token, 'token_type': 'bearer'}


@router.get(
    '/token',
    tags=[APITag.DEFAULT],
    summary='Get an access token',
    responses=create_responses(_bad_credentials_response),
    response_model=Token,
    deprecated=True,
)
async def get_token_via_query(username: str, password: str):
    """
    **[DEPRECATED]** This endpoint is **no longer recommended**.
    Please use the **POST** endpoint instead.

    This was a convenience alternative to the **POST** version, allowing retrieval of
    an *access token* by providing a username and password via query parameters.

    **Why is this deprecated?**
        Query parameters expose credentials in URLs, which can be logged or cached.
    """
    try:
        access_token = infrastructure.keycloak.basicauth(username, password)
    except infrastructure.KeycloakError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    return {'access_token': access_token, 'token_type': 'bearer'}


@router.get(
    '/signature_token',
    tags=[APITag.DEFAULT],
    summary='Get a signature token',
    response_model=SignatureToken,
)
async def get_signature_token(
    user: User | None = Depends(create_user_dependency(required=True)),
):
    """
    Generates and returns a signature token for the authenticated user. Authentication
    has to be provided with another method, e.g. access token.
    """
    signature_token = generate_simple_token(user.user_id, expires_in=10)
    return {'signature_token': signature_token}


@router.get(
    '/app_token',
    tags=[APITag.DEFAULT],
    summary='Get an app token',
    response_model=AppToken,
)
async def get_app_token(
    expires_in: int = FastApiQuery(gt=0, le=config.services.app_token_max_expires_in),
    user: User = Depends(create_user_dependency(required=True)),
):
    """
    Generates and returns an app token with the requested expiration time for the
    authenticated user. Authentication has to be provided with another method,
    e.g. access token.

    This app token can be used like the access token (see `/auth/token`) on subsequent API
    calls to authenticate you using the HTTP header `Authorization: Bearer <app token>`.
    It is provided for user convenience as a shorter token with a user-defined (probably
    longer) expiration time than the access token.
    """
    app_token = generate_simple_token(user.user_id, expires_in)
    return {'app_token': app_token}


def generate_simple_token(user_id, expires_in: int):
    """
    Generates and returns JWT encoding just user_id and expiration time, signed with the
    API secret.
    """
    expires_at = datetime.datetime.utcnow() + datetime.timedelta(seconds=expires_in)
    payload = dict(user=user_id, exp=expires_at)
    return jwt.encode(payload, config.services.api_secret, 'HS256')


def generate_upload_token(user):
    """Generates and returns upload token for user."""
    payload = uuid.UUID(user.user_id).bytes
    signature = hmac.new(
        bytes(config.services.api_secret, 'utf-8'), msg=payload, digestmod=hashlib.sha1
    )

    return f'{utils.base64_encode(payload)}.{utils.base64_encode(signature.digest())}'
