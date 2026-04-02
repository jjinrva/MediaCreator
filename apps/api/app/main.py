import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router

DEFAULT_ALLOWED_ORIGIN_REGEX = (
    r"^https?://"
    r"(localhost|127\.0\.0\.1|0\.0\.0\.0|10\.\d+\.\d+\.\d+|192\.168\.\d+\.\d+|"
    r"172\.(1[6-9]|2\d|3[0-1])\.\d+\.\d+)"
    r"(:\d+)?$"
)


def _read_allowed_origins() -> list[str]:
    configured_origins = os.getenv("MEDIACREATOR_ALLOWED_ORIGINS", "")
    return [origin.strip() for origin in configured_origins.split(",") if origin.strip()]

app = FastAPI(
    title="MediaCreator API",
    version="0.1.0",
    summary="Bootstrap API surface for the MediaCreator rebuild.",
)
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_headers=["*"],
    allow_methods=["*"],
    allow_origins=_read_allowed_origins(),
    allow_origin_regex=os.getenv(
        "MEDIACREATOR_ALLOWED_ORIGIN_REGEX", DEFAULT_ALLOWED_ORIGIN_REGEX
    ),
)
app.include_router(api_router)
