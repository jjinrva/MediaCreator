from pydantic import BaseModel


class HealthResponse(BaseModel):
    application: str
    service: str
    status: str
    mode: str
    phase: str
    storage_mode: str
    nas_available: bool
