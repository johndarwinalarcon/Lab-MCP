from __future__ import annotations

import os


os.environ.setdefault(
    "JWT_SECRET_KEY",
    "test-secret-key-for-pytest-that-is-at-least-32-bytes",
)
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("JWT_EXPIRATION_MINUTES", "30")
os.environ.setdefault("FRANKFURTER_BASE_URL", "https://api.frankfurter.dev/v1")
os.environ.setdefault("FRANKFURTER_TIMEOUT_SECONDS", "10.0")
os.environ.setdefault("APP_NAME", "CurrencyMCPServer")
