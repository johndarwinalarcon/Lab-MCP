class AuthenticationError(Exception):
    """Base authentication exception."""


class InvalidCredentialsError(AuthenticationError):
    """Raised when the supplied username or password is invalid."""


class InvalidTokenError(AuthenticationError):
    """Raised when a JWT is missing, expired, malformed, or invalid."""


class TokenExpiredError(InvalidTokenError):
    """Raised when a JWT has expired."""


class FrankfurterApiError(RuntimeError):
    """Raised when the Frankfurter API request fails."""
