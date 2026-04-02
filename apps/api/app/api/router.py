from fastapi import APIRouter

from app.api.routes.body import router as body_router
from app.api.routes.characters import router as characters_router
from app.api.routes.exports import router as exports_router
from app.api.routes.face import router as face_router
from app.api.routes.generation import router as generation_router
from app.api.routes.health import router as health_router
from app.api.routes.jobs import router as jobs_router
from app.api.routes.lora import router as lora_router
from app.api.routes.lora_datasets import router as lora_datasets_router
from app.api.routes.motion import router as motion_router
from app.api.routes.photosets import router as photosets_router
from app.api.routes.pose import router as pose_router
from app.api.routes.system import router as system_router
from app.api.routes.video import router as video_router
from app.api.routes.wardrobe import router as wardrobe_router

api_router = APIRouter()
api_router.include_router(body_router)
api_router.include_router(characters_router)
api_router.include_router(exports_router)
api_router.include_router(face_router)
api_router.include_router(generation_router)
api_router.include_router(health_router)
api_router.include_router(jobs_router)
api_router.include_router(lora_router)
api_router.include_router(lora_datasets_router)
api_router.include_router(motion_router)
api_router.include_router(photosets_router)
api_router.include_router(pose_router)
api_router.include_router(system_router)
api_router.include_router(video_router)
api_router.include_router(wardrobe_router)
