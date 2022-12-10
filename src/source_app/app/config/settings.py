import secrets
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, BaseSettings, EmailStr, HttpUrl, PostgresDsn, validator


class Settings(BaseSettings):
    API_V1_STR: str = "/app/api/v1"
    TA_API_URL: str = "http://localhost:8000/trustedauthority/api/v1"
    TA_PUBLIC_KEY: str = "/Users/aumahesh/code/mids/233-PrivacyEngineering/workdir/w233-project/src/trustedauthority/app/config/ta.pub"
    SECRET_KEY: str = "1234"
    # 60 minutes * 24 hours * 8 days = 100 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 100
    SERVER_NAME: str = "app"
    SERVER_HOST: str = "localhost"
    PROJECT_NAME: str = "app"

    class Config:
        case_sensitive = True


settings = Settings()