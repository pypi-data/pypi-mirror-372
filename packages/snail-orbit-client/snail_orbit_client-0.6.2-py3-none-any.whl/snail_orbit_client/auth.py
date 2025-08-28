"""Authentication handling for Snail Orbit API."""

from __future__ import annotations

import time
from datetime import datetime
from hashlib import sha256
from typing import Any

import jwt
from pydantic import Field

from .constants import SERVICE_TOKEN_EXP_DELTA, SERVICE_TOKEN_IAT_DELTA
from .models.base import BaseModel


class TokenInfo(BaseModel):
    """Information about an authentication token."""

    token: str = Field(description='The authentication token')
    expires_at: datetime | None = Field(
        default=None, description='Token expiration time'
    )
    is_jwt: bool = Field(description='Whether this is a JWT token')


class AuthHandler:
    """Handles authentication for API requests."""

    def __init__(self, token: str | tuple[str, str, str]) -> None:
        """Initialize auth handler.

        Args:
            token: Either a bearer token string or tuple of (kid, secret, user) for JWT signing
        """
        self._token = token
        self._is_jwt = isinstance(token, tuple)

    def get_auth_header(
        self, method: str, path: str, params: dict[str, Any] | None = None
    ) -> str:
        """Get authorization header for a request.

        Args:
            method: HTTP method (GET, POST, etc.)
            path: Request path
            params: Query parameters that will be sent with the request

        Returns:
            Authorization header value
        """
        if isinstance(self._token, str):
            return f'Bearer {self._token}'

        # JWT signing
        kid, secret, user = self._token

        sorted_params = sorted(params.items()) if params else []

        hash_input = method + path + ''.join(f'{k}={v}' for k, v in sorted_params)
        req_hash = sha256(hash_input.encode('utf-8')).hexdigest()

        now = time.time()
        payload = {
            'sub': user,
            'iat': now - SERVICE_TOKEN_IAT_DELTA,
            'exp': now + SERVICE_TOKEN_EXP_DELTA,
            'req_hash': req_hash,
        }

        token = jwt.encode(payload, secret, algorithm='HS256', headers={'kid': kid})

        return f'Bearer {token}'

    def get_token_info(self) -> TokenInfo:
        """Get information about the current token.

        Returns:
            Token information
        """
        if isinstance(self._token, str):
            # Try to decode as JWT to get expiration
            try:
                decoded = jwt.decode(
                    self._token,
                    options={'verify_signature': False, 'verify_exp': False},
                )
                exp = decoded.get('exp')
                expires_at = datetime.fromtimestamp(exp) if exp else None
                return TokenInfo(token=self._token, expires_at=expires_at, is_jwt=True)
            except jwt.InvalidTokenError:
                # Not a JWT, probably a bearer token
                return TokenInfo(token=self._token, expires_at=None, is_jwt=False)
        else:
            # JWT signing credentials
            return TokenInfo(
                token='<JWT signing credentials>', expires_at=None, is_jwt=True
            )
