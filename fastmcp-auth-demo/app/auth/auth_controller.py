from dataclasses import dataclass

from app.auth.auth_models import AuthenticatedUser, LoginRequest, TokenResponse
from app.auth.exceptions import InvalidCredentialsError
from app.auth.jwt_service import JWTService
from app.logging_config import logger


@dataclass(frozen=True)
class InMemoryUserStore:
    users: dict[str, str]

    def authenticate(self, username: str, password: str) -> bool:
        stored_password = self.users.get(username)
        return bool(stored_password) and stored_password == password


class AuthenticationService:
    def __init__(self, user_store: InMemoryUserStore, jwt_service: JWTService) -> None:
        self.user_store = user_store
        self.jwt_service = jwt_service

    def login(self, request: LoginRequest) -> TokenResponse:
        if not self.user_store.authenticate(request.username, request.password):
            logger.warning(
                "Login failed",
                extra={"username": request.username},
            )
            raise InvalidCredentialsError("Invalid username or password")

        token = self.jwt_service.create_access_token(request.username)
        logger.info("Login succeeded", extra={"username": request.username})
        return TokenResponse(access_token=token)

    def get_current_user(self, token: str) -> AuthenticatedUser:
        username = self.jwt_service.get_current_user(token)
        return AuthenticatedUser(username=username)


DEFAULT_USERS = InMemoryUserStore({"admin": "Admin123*"})

def create_authentication_service() -> AuthenticationService:
    return AuthenticationService(DEFAULT_USERS, JWTService())
