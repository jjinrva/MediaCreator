import uuid

from pydantic import BaseModel


class ExportArtifactResponse(BaseModel):
    status: str
    detail: str
    storage_object_public_id: uuid.UUID | None
    url: str | None


class ExportJobResponse(BaseModel):
    status: str
    detail: str


class CharacterExportScaffoldResponse(BaseModel):
    character_public_id: uuid.UUID
    preview_glb: ExportArtifactResponse
    final_glb: ExportArtifactResponse
    export_job: ExportJobResponse
