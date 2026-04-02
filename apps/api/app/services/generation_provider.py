import os
from collections.abc import Callable, Mapping
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from pydantic import BaseModel

from app.services.storage_service import resolve_storage_layout

REQUIRED_WORKFLOW_FILES = (
    "text_to_image_v1.json",
    "character_refine_img2img_v1.json",
)
CHECKPOINT_SUFFIXES = (".ckpt", ".safetensors")
VAE_SUFFIXES = (".pt", ".ckpt", ".safetensors")


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _workflows_root_from_env(env: Mapping[str, str]) -> Path:
    default_root = _repo_root() / "workflows" / "comfyui"
    return Path(env.get("MEDIACREATOR_COMFYUI_WORKFLOWS_ROOT", str(default_root)))


def _nas_backed(path: Path, *, nas_root: Path) -> bool:
    return path == nas_root or nas_root in path.parents


def _matching_files(root: Path, suffixes: tuple[str, ...]) -> list[str]:
    if not root.exists():
        return []

    return sorted(
        file_path.name
        for file_path in root.iterdir()
        if file_path.is_file() and file_path.suffix.lower() in suffixes
    )


def ping_comfyui_service(base_url: str, timeout_seconds: float = 1.0) -> bool:
    try:
        request = Request(base_url, method="GET")
        with urlopen(request, timeout=timeout_seconds):
            return True
    except HTTPError:
        return True
    except URLError:
        return False


class GenerationCapability(BaseModel):
    provider: str = "comfyui"
    status: str
    comfyui_base_url: str | None
    comfyui_base_url_configured: bool
    comfyui_service_reachable: bool
    workflows_root: Path
    required_workflow_files: list[str]
    discovered_workflow_files: list[str]
    missing_workflow_files: list[str]
    checkpoints_root: Path
    loras_root: Path
    embeddings_root: Path
    vaes_root: Path
    model_roots_on_nas: bool
    checkpoint_files_detected: list[str]
    vae_files_detected: list[str]
    missing_requirements: list[str]


def get_generation_capability(
    env: Mapping[str, str] | None = None,
    *,
    service_ping: Callable[[str], bool] | None = None,
) -> GenerationCapability:
    resolved_env = env if env is not None else os.environ
    storage_layout = resolve_storage_layout(resolved_env)
    workflows_root = _workflows_root_from_env(resolved_env)
    base_url = resolved_env.get("MEDIACREATOR_COMFYUI_BASE_URL")
    discovered_workflow_files = (
        sorted(
            file_path.name
            for file_path in workflows_root.glob("*.json")
            if file_path.is_file()
        )
        if workflows_root.exists()
        else []
    )
    missing_workflow_files = [
        workflow_name
        for workflow_name in REQUIRED_WORKFLOW_FILES
        if workflow_name not in discovered_workflow_files
    ]
    checkpoint_files = _matching_files(storage_layout.checkpoints_root, CHECKPOINT_SUFFIXES)
    vae_files = _matching_files(storage_layout.vaes_root, VAE_SUFFIXES)
    model_roots = (
        storage_layout.checkpoints_root,
        storage_layout.loras_root,
        storage_layout.embeddings_root,
        storage_layout.vaes_root,
    )
    model_roots_on_nas = all(
        _nas_backed(model_root, nas_root=storage_layout.nas_root) for model_root in model_roots
    )
    ping = service_ping or ping_comfyui_service
    service_reachable = False
    if base_url:
        service_reachable = ping(base_url)

    missing_requirements: list[str] = []
    if not base_url:
        missing_requirements.append("comfyui_base_url_missing")
    if base_url and not service_reachable:
        missing_requirements.append("comfyui_service_unreachable")
    if not workflows_root.exists():
        missing_requirements.append("workflows_root_missing")
    if missing_workflow_files:
        missing_requirements.append("required_workflows_missing")
    if not model_roots_on_nas:
        missing_requirements.append("model_roots_not_on_nas")
    if not checkpoint_files:
        missing_requirements.append("checkpoint_files_missing")
    if not vae_files:
        missing_requirements.append("vae_files_missing")

    if not base_url:
        status = "unavailable"
    elif missing_requirements:
        status = "partially-configured"
    else:
        status = "ready"

    return GenerationCapability(
        status=status,
        comfyui_base_url=base_url,
        comfyui_base_url_configured=bool(base_url),
        comfyui_service_reachable=service_reachable,
        workflows_root=workflows_root,
        required_workflow_files=list(REQUIRED_WORKFLOW_FILES),
        discovered_workflow_files=discovered_workflow_files,
        missing_workflow_files=missing_workflow_files,
        checkpoints_root=storage_layout.checkpoints_root,
        loras_root=storage_layout.loras_root,
        embeddings_root=storage_layout.embeddings_root,
        vaes_root=storage_layout.vaes_root,
        model_roots_on_nas=model_roots_on_nas,
        checkpoint_files_detected=checkpoint_files,
        vae_files_detected=vae_files,
        missing_requirements=missing_requirements,
    )
