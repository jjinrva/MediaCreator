import os
from collections.abc import Mapping

DEFAULT_DATABASE_URL = (
    "postgresql+psycopg://mediacreator:mediacreator@127.0.0.1:54329/mediacreator"
)


def get_database_url(env: Mapping[str, str] | None = None) -> str:
    resolved_env = env if env is not None else os.environ
    return resolved_env.get("MEDIACREATOR_DATABASE_URL", DEFAULT_DATABASE_URL)
