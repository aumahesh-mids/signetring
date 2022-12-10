import secrets
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, BaseSettings, EmailStr, HttpUrl, PostgresDsn, validator


class Settings(BaseSettings):
    API_V1_STR: str = "/trustedauthority/api/v1"
    SECRET_KEY: str = "1234"
    # 60 minutes * 24 hours * 8 days = 100 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 100
    SERVER_NAME: str = "ta"
    SERVER_HOST: str = "localhost"
    PROJECT_NAME: str = "ta"

    POSTGRES_SERVER: str = "localhost:5432"
    POSTGRES_USER: str = "admin"
    POSTGRES_PASSWORD: str = "admin"
    POSTGRES_DB: str = "ta"
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    TA_PRIVATE_KEY_FILE = '/Users/aumahesh/code/mids/233-PrivacyEngineering/workdir/w233-project/src/trustedauthority' \
                          '/app/config/ta.pem'
    TA_PUBLIC_KEY_FILE = '/Users/aumahesh/code/mids/233-PrivacyEngineering/workdir/w233-project/src/trustedauthority' \
                         '/app/config/ta.pub'

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )


    class Config:
        case_sensitive = True


settings = Settings()