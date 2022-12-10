
# https://github.com/tiangolo/full-stack-fastapi-postgresql
from pydantic.networks import PostgresDsn
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, drop_database, create_database

from trustedauthority.app.config.settings import settings
from trustedauthority.app.db.model.base import Base
from trustedauthority.app.db.model.auth import Auth
from trustedauthority.app.db.model.user import User
from trustedauthority.app.db.model.digital_object import DigitalObject
from trustedauthority.app.db.model.published_object import PublishedObject
from trustedauthority.app.db.model.source import SourceApp
from trustedauthority.app.db.model.challenge import Challenge


def init_db() -> None:
    engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)
    if database_exists(engine.url):
        drop_database(engine.url)
    create_database(engine.url)
    Base.metadata.create_all(bind=engine)

