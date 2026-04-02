import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router

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
    allow_origins=[
        f"http://{os.environ.get('MEDIACREATOR_WEB_HOST', '127.0.0.1')}:"
        f"{os.environ.get('MEDIACREATOR_WEB_PORT', '3000')}"
    ],
)
app.include_router(api_router)
