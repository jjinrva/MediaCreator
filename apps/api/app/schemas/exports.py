import uuid

from pydantic import BaseModel

from app.schemas.jobs import JobSummaryResponse


class ExportArtifactResponse(BaseModel):
    status: str
    detail: str
    storage_object_public_id: uuid.UUID | None
    url: str | None


class ReconstructionStatusResponse(BaseModel):
    detail_level: str
    detail: str
    strategy: str
    riggable_base_glb: ExportArtifactResponse
    detail_prep_artifact: ExportArtifactResponse
    reconstruction_job: JobSummaryResponse


class TextureMaterialStatusResponse(BaseModel):
    current_texture_fidelity: str
    detail: str
    base_texture_artifact: ExportArtifactResponse
    refined_texture_artifact: ExportArtifactResponse


class CharacterExportScaffoldResponse(BaseModel):
    character_public_id: uuid.UUID
    preview_glb: ExportArtifactResponse
    final_glb: ExportArtifactResponse
    export_job: JobSummaryResponse
    reconstruction: ReconstructionStatusResponse
    texture_material: TextureMaterialStatusResponse
