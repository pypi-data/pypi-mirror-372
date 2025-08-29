###
# #%L
# aiSSEMBLE::Open Inference Protocol::Shared
# %%
# Copyright (C) 2024 Booz Allen Hamilton Inc.
# %%
# This software package is licensed under the Booz Allen Public License. All Rights Reserved.
# #L%
###
from fastapi import HTTPException, status
from ..config.oip_config import OIPConfig
import jwt
from aissemble_open_inference_protocol_shared.auth.auth_context import (
    AuthContext,
)


def verify_jwt_token(authorization):
    """
    This method checks for the existence of a Bearer token and extracts the payload (user/subject, etc...)
    :param authorization: The FastAPI HTTPAuthorizationCredentials (scheme and credentials)
    :return: the unencrypted jwt payload
    """
    if authorization is None:
        # No Authorization header means this is an anonymous user
        payload = {"sub": "Anonymous", "name": "Anonymous"}
    else:
        if authorization.scheme != "Bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or missing Authorization header",
            )
        try:
            config = OIPConfig()
            secret_key = config.auth_secret()
            algorithm = config.auth_algorithm()
            payload = jwt.decode(
                authorization.credentials, secret_key, algorithms=[algorithm]
            )
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )
        except jwt.PyJWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unexpected error parsing token",
            )

    return payload


def authenticate_and_authorize(auth_context: AuthContext):
    """
    This method verifies the jwt is valid and then calls the authz adapter to see if the
    user can perform the requested action on the resource.
    :param auth_context: Contains the context, including token (HTTPAuthorizationCredentials),
    resource, action, user ip, request url
    :return: if the user/subject is not-authorized then a 403 error is raised.
    """
    config = OIPConfig()
    if config.auth_enabled:
        token_data = verify_jwt_token(auth_context.bearer_token)
        if not auth_context.authz_adapter.authorize(
            user=token_data.get("sub"),
            resource=auth_context.auth_resource,
            action=auth_context.auth_action,
            user_ip=auth_context.user_ip,
            request_url=auth_context.request_url,
            role=token_data.get("roles", None),
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
            )
