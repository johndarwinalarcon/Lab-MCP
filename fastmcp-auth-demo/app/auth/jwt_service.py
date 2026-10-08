from __future__ import annotations

import time
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt

from app.auth.exceptions import InvalidTokenError, TokenExpiredError
from app.config.settings import get_settings
from app.logging_config import logger


class JWTService:
    def __init__(self) -> None:
        settings = get_settings()
        self.secret_key = settings.jwt_secret_key.get_secret_value()
        self.algorithm = settings.jwt_algorithm
        self.expiration_minutes = settings.jwt_expiration_minutes

    def create_access_token(self, username: str) -> str:
        issued_at = int(time.time())
        expires_at = issued_at + (self.expiration_minutes * 60)
        payload = {
            "sub": username,
            "iat": issued_at,
            "exp": expires_at,
        }
        logger.info("JWT generated for user", extra={"username": username})
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def verify_token(self, token: str) -> dict[str, Any]:
        if not token:
            raise InvalidTokenError("JWT is required")

        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
            )
        except jwt.ExpiredSignatureError as exc:
            logger.warning("Expired JWT rejected", extra={"reason": str(exc)})
            raise TokenExpiredError("JWT has expired") from exc
        except jwt.PyJWTError as exc:
            logger.warning("Invalid JWT rejected", extra={"reason": str(exc)})
            raise InvalidTokenError("JWT is invalid") from exc

        username = payload.get("sub")
        if not username:
            raise InvalidTokenError("JWT does not contain a subject")

        logger.info("JWT validated", extra={"username": username})
        return payload

    def get_current_user(self, token: str) -> str:
        payload = self.verify_token(token)
        return str(payload["sub"])
