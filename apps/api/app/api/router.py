from fastapi import APIRouter

from app.api.routes.body import router as body_router
from app.api.routes.characters import router as characters_router
from app.api.routes.exports import router as exports_router
from app.api.routes.face import router as face_router
from app.api.routes.health import router as health_router
from app.api.routes.jobs import router as jobs_router
from app.api.routes.photosets import router as photosets_router
from app.api.routes.pose import router as pose_router
from app.api.routes.system import router as system_router

api_router = APIRouter()
api_router.include_router(body_router)
api_router.include_router(characters_router)
api_router.include_router(exports_router)
api_router.include_router(face_router)
api_router.include_router(health_router)
api_router.include_router(jobs_router)
api_router.include_router(photosets_router)
api_router.include_router(pose_router)
api_router.include_router(system_router)
