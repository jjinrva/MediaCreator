import importlib
import json
import os
import uuid
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import cast
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.services.storage_service import resolve_storage_layout

REQUIRED_WORKFLOW_FILES = (
    "text_to_image_v1.json",
    "character_refine_img2img_v1.json",
)
REQUIRED_WORKFLOW_NODE_TYPES = {
    "text_to_image_v1.json": frozenset(
        {
            "CheckpointLoaderSimple",
            "CLIPTextEncode",
            "KSampler",
            "VAEDecode",
            "SaveImage",
        }
    ),
    "character_refine_img2img_v1.json": frozenset(
        {
            "LoadImage",
            "KSampler",
            "VAEDecode",
            "SaveImage",
        }
    ),
}
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


class LoraActivationResolution(BaseModel):
    loader: str = "comfyui-lora-loader"
    model_name: str
    prompt_handle: str
    storage_object_public_id: uuid.UUID
    storage_path: str


class WorkflowContract(BaseModel):
    workflow_id: str
    version: int | None = None
    provider: str | None = None
    target_kind: str | None = None
    purpose: str | None = None
    nodes: list[dict[str, object]]
    prompt_api: dict[str, object] | None = None


def _workflow_path(workflows_root: Path, workflow_name: str) -> Path:
    return workflows_root / workflow_name


def _load_workflow_payload(workflow_path: Path) -> dict[str, object]:
    loaded = json.loads(workflow_path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError(f"Workflow '{workflow_path.name}' did not decode to an object.")
    return cast(dict[str, object], loaded)


def load_workflow_contract(workflow_path: Path) -> WorkflowContract:
    return WorkflowContract.model_validate(_load_workflow_payload(workflow_path))


def workflow_validation_errors(workflow_path: Path) -> list[str]:
    try:
        contract = load_workflow_contract(workflow_path)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return [f"invalid-json:{exc}"]
    except Exception as exc:
        return [f"invalid-contract:{exc}"]

    if not contract.nodes:
        return ["placeholder-nodes-empty"]

    node_types = {
        class_type
        for node in contract.nodes
        if isinstance(node, dict)
        for class_type in [node.get("class_type")]
        if isinstance(class_type, str)
    }
    if not node_types:
        return ["workflow-node-types-missing"]

    required_node_types = REQUIRED_WORKFLOW_NODE_TYPES.get(workflow_path.name, frozenset())
    missing_node_types = sorted(required_node_types.difference(node_types))
    errors = [f"missing-node-type:{node_type}" for node_type in missing_node_types]

    if contract.prompt_api is None or not contract.prompt_api:
        errors.append("prompt-api-missing")
    if contract.provider != "comfyui":
        errors.append("provider-not-comfyui")
    if contract.workflow_id != workflow_path.stem:
        errors.append("workflow-id-mismatch")
    return errors


def proof_image_execution_path_available() -> bool:
    try:
        module = importlib.import_module("app.services.generation_execution")
    except Exception:
        return False
    return hasattr(module, "execute_generation_proof_image_job") and hasattr(
        module, "queue_generation_proof_image"
    )


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
    invalid_workflow_files = {
        workflow_name: workflow_validation_errors(_workflow_path(workflows_root, workflow_name))
        for workflow_name in REQUIRED_WORKFLOW_FILES
        if workflow_name in discovered_workflow_files
    }
    invalid_workflow_files = {
        workflow_name: errors
        for workflow_name, errors in invalid_workflow_files.items()
        if errors
    }
    validated_workflow_files = sorted(
        workflow_name
        for workflow_name in REQUIRED_WORKFLOW_FILES
        if workflow_name in discovered_workflow_files
        and workflow_name not in invalid_workflow_files
    )
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
    if invalid_workflow_files:
        missing_requirements.append("workflow_validation_failed")
    if not model_roots_on_nas:
        missing_requirements.append("model_roots_not_on_nas")
    if not checkpoint_files:
        missing_requirements.append("checkpoint_files_missing")
    if not vae_files:
        missing_requirements.append("vae_files_missing")
    if not proof_image_execution_path_available():
        missing_requirements.append("proof_image_execution_path_missing")

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
        validated_workflow_files=validated_workflow_files,
        invalid_workflow_files=invalid_workflow_files,
        checkpoints_root=storage_layout.checkpoints_root,
        loras_root=storage_layout.loras_root,
        embeddings_root=storage_layout.embeddings_root,
        vaes_root=storage_layout.vaes_root,
        model_roots_on_nas=model_roots_on_nas,
        checkpoint_files_detected=checkpoint_files,
        vae_files_detected=vae_files,
        proof_image_execution_path_available=proof_image_execution_path_available(),
        missing_requirements=missing_requirements,
    )


def resolve_generation_lora_activation(
    session: Session,
    character_public_id: uuid.UUID,
) -> LoraActivationResolution | None:
    from app.services.lora_training import resolve_active_lora_artifact

    active_artifact = resolve_active_lora_artifact(session, character_public_id)
    if active_artifact is None:
        return None

    return LoraActivationResolution(
        model_name=str(active_artifact["model_name"]),
        prompt_handle=str(active_artifact["prompt_handle"]),
        storage_object_public_id=uuid.UUID(str(active_artifact["storage_object_public_id"])),
        storage_path=str(active_artifact["storage_path"]),
    )
