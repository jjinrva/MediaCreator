from app.schemas.health import HealthResponse
from app.services.storage_service import resolve_storage_layout


def get_health_response() -> HealthResponse:
    storage_layout = resolve_storage_layout()

    return HealthResponse(
        application="MediaCreator",
        service="api",
        status="ok",
        mode="single-user",
        phase="03",
        storage_mode=storage_layout.storage_mode,
        nas_available=storage_layout.nas_available,
    )
