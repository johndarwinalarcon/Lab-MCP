from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field, SecretStr

load_dotenv(Path(__file__).resolve().parents[2] / ".env")


class Settings(BaseModel):
    jwt_secret_key: SecretStr = Field(default=SecretStr("change-this-secret"))
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 30
    frankfurter_base_url: str = "https://api.frankfurter.dev/v1"
    frankfurter_timeout_seconds: float = 10.0
    app_name: str = "CurrencyMCPServer"

    model_config = {"arbitrary_types_allowed": True}


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    from os import getenv

    return Settings(
        jwt_secret_key=SecretStr(getenv("JWT_SECRET_KEY", "change-this-secret")),
        jwt_algorithm=getenv("JWT_ALGORITHM", "HS256"),
        jwt_expiration_minutes=int(getenv("JWT_EXPIRATION_MINUTES", "30")),
        frankfurter_base_url=getenv("FRANKFURTER_BASE_URL", "https://api.frankfurter.dev/v1"),
        frankfurter_timeout_seconds=float(getenv("FRANKFURTER_TIMEOUT_SECONDS", "10.0")),
        app_name=getenv("APP_NAME", "CurrencyMCPServer"),
    )
