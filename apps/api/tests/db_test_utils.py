import uuid
from collections.abc import Iterator
from contextlib import contextmanager

from alembic.config import Config
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL, make_url

from alembic import command

TEST_BASE_DATABASE_URL = (
    "postgresql+psycopg://mediacreator:mediacreator@127.0.0.1:54329/mediacreator"
)


def temp_database_url(base_url: str, suffix: str) -> tuple[str, str]:
    database_name = f"mediacreator_{suffix}_{uuid.uuid4().hex[:8]}"
    return (
        make_url(base_url).set(database=database_name).render_as_string(hide_password=False),
        database_name,
    )


def create_database(base_url: str, database_name: str) -> None:
    url = make_url(base_url)
    admin_url = URL.create(
        drivername=url.drivername,
        username=url.username,
        password=url.password,
        host=url.host,
        port=url.port,
        database="postgres",
    )
    engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")
    try:
        with engine.connect() as connection:
            connection.execute(text(f'DROP DATABASE IF EXISTS "{database_name}" WITH (FORCE)'))
            connection.execute(text(f'CREATE DATABASE "{database_name}"'))
    finally:
        engine.dispose()


def drop_database(base_url: str, database_name: str) -> None:
    url = make_url(base_url)
    admin_url = URL.create(
        drivername=url.drivername,
        username=url.username,
        password=url.password,
        host=url.host,
        port=url.port,
        database="postgres",
    )
    engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")
    try:
        with engine.connect() as connection:
            connection.execute(text(f'DROP DATABASE IF EXISTS "{database_name}" WITH (FORCE)'))
    finally:
        engine.dispose()


def alembic_config(database_url: str) -> Config:
    config = Config("/opt/MediaCreator/apps/api/alembic.ini")
    config.set_main_option("sqlalchemy.url", database_url)
    return config


@contextmanager
def migrated_database(
    suffix: str,
    *,
    base_url: str = TEST_BASE_DATABASE_URL,
) -> Iterator[str]:
    database_url, database_name = temp_database_url(base_url, suffix)
    create_database(base_url, database_name)

    try:
        command.upgrade(alembic_config(database_url), "head")
        yield database_url
    finally:
        drop_database(base_url, database_name)
