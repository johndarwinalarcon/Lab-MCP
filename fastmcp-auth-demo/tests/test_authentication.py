from app.auth.auth_controller import AuthenticationService, InMemoryUserStore
from app.auth.auth_models import LoginRequest
from app.auth.exceptions import InvalidCredentialsError, InvalidTokenError
from app.auth.jwt_service import JWTService


def test_login_returns_jwt_for_valid_credentials():
    service = AuthenticationService(
        InMemoryUserStore({"admin": "Admin123*"}),
        JWTService(),
    )

    token = service.login(LoginRequest(username="admin", password="Admin123*"))

    assert token.access_token
    assert token.token_type == "bearer"


def test_login_rejects_invalid_credentials():
    service = AuthenticationService(
        InMemoryUserStore({"admin": "Admin123*"}),
        JWTService(),
    )

    try:
        service.login(LoginRequest(username="admin", password="WrongPass1"))
        assert False, "InvalidCredentialsError was not raised"
    except InvalidCredentialsError as exc:
        assert str(exc) == "Invalid username or password"


def test_valid_jwt_is_accepted():
    service = AuthenticationService(
        InMemoryUserStore({"admin": "Admin123*"}),
        JWTService(),
    )
    token = service.login(LoginRequest(username="admin", password="Admin123*"))

    current = service.get_current_user(token.access_token)

    assert current.username == "admin"


def test_invalid_jwt_is_rejected():
    service = AuthenticationService(
        InMemoryUserStore({"admin": "Admin123*"}),
        JWTService(),
    )

    try:
        service.get_current_user("not-a-valid-jwt")
        assert False, "InvalidTokenError was not raised"
    except InvalidTokenError:
        pass
