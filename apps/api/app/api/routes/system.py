from fastapi import APIRouter

from app.schemas.system import GenerationCapabilityResponse, SystemStatusResponse
from app.services.generation_provider import get_generation_capability
from app.services.storage_service import resolve_storage_layout

router = APIRouter(prefix="/api/v1/system", tags=["system"])


@router.get("/status", response_model=SystemStatusResponse)
def read_system_status() -> SystemStatusResponse:
    storage_layout = resolve_storage_layout()
    generation_capability = get_generation_capability()

    return SystemStatusResponse(
        application="MediaCreator",
        service="api",
        mode="single-user",
        storage_mode=storage_layout.storage_mode,
        nas_available=storage_layout.nas_available,
        generation=GenerationCapabilityResponse.model_validate(generation_capability),
    )
