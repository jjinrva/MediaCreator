from datetime import datetime
from pathlib import Path

from pydantic import BaseModel, ConfigDict


class GenerationCapabilityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    provider: str
    status: str
    comfyui_base_url: str | None
    comfyui_base_url_configured: bool
    comfyui_service_reachable: bool
    workflows_root: Path
    required_workflow_files: list[str]
    discovered_workflow_files: list[str]
    missing_workflow_files: list[str]
    validated_workflow_files: list[str]
    invalid_workflow_files: dict[str, list[str]]
    checkpoints_root: Path
    loras_root: Path
    embeddings_root: Path
    vaes_root: Path
    model_roots_on_nas: bool
    checkpoint_files_detected: list[str]
    vae_files_detected: list[str]
    proof_image_execution_path_available: bool
    missing_requirements: list[str]


class BlenderCapabilityResponse(BaseModel):
    blender_bin: str
    detail: str
    status: str


class AiToolkitCapabilityResponse(BaseModel):
    ai_toolkit_bin: str | None
    detail: str
    loras_root: str
    missing_requirements: list[str]
    status: str


class StoragePathsResponse(BaseModel):
    character_assets_root: str
    checkpoints_root: str
    embeddings_root: str
    exports_root: str
    loras_root: str
    models_root: str
    nas_root: str
    prepared_images_root: str
    renders_root: str
    scratch_root: str
    uploaded_photos_root: str
    vaes_root: str
    wardrobe_root: str


class WorkerHeartbeatResponse(BaseModel):
    service_name: str
    status: str
    detail: str
    last_seen_at: datetime | None
    seconds_since_heartbeat: int | None
    stale_after_seconds: int


class SystemStatusResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    application: str
    service: str
    mode: str
    storage_mode: str
    nas_available: bool
    generation: GenerationCapabilityResponse
    blender: BlenderCapabilityResponse
    ai_toolkit: AiToolkitCapabilityResponse
    worker: WorkerHeartbeatResponse
    storage_paths: StoragePathsResponse
