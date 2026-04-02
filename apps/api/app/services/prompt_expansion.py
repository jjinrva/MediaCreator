from __future__ import annotations

import hashlib
import json
import os
import re
import uuid
from pathlib import Path
from typing import Mapping, cast
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.models.asset import Asset
from app.models.history_event import HistoryEvent
from app.models.models_registry import ModelRegistry
from app.models.storage_object import StorageObject
from app.services.characters import get_character_payload
from app.services.generation_provider import get_generation_capability
from app.services.jobs import get_system_actor_id
from app.services.lora_dataset import get_character_lora_dataset_payload
from app.services.storage_service import resolve_storage_layout

REPO_ROOT = Path(__file__).resolve().parents[4]
TEXT_TO_IMAGE_WORKFLOW_PATH = REPO_ROOT / "workflows" / "comfyui" / "text_to_image_v1.json"
TEXT_TO_VIDEO_WORKFLOW_PATH = REPO_ROOT / "workflows" / "comfyui" / "text_to_video_v1.json"
CIVITAI_DEFAULT_BASE_URL = "https://civitai.com/api/v1"
HANDLE_PATTERN = re.compile(r"@[a-z0-9_][a-z0-9_-]*", re.IGNORECASE)


def _asset_query() -> Select[tuple[Asset]]:
    return select(Asset).order_by(Asset.created_at.desc())


def _history_query() -> Select[tuple[HistoryEvent]]:
    return select(HistoryEvent).order_by(HistoryEvent.created_at.asc())


def _registry_query() -> Select[tuple[ModelRegistry]]:
    return select(ModelRegistry).order_by(ModelRegistry.created_at.desc())


def _storage_object_query() -> Select[tuple[StorageObject]]:
    return select(StorageObject).order_by(StorageObject.created_at.desc())


def _slugify(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return normalized or "model"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _record_history_event(
    session: Session,
    actor_id: uuid.UUID,
    *,
    asset_id: uuid.UUID,
    details: dict[str, object],
    event_type: str,
) -> None:
    session.add(
        HistoryEvent(
            actor_id=actor_id,
            asset_id=asset_id,
            details=details,
            event_type=event_type,
        )
    )


def _character_prompt_recipes(session: Session) -> list[dict[str, object]]:
    character_assets = list(
        session.scalars(_asset_query().where(Asset.asset_type == "character")).all()
    )
    payloads: list[dict[str, object]] = []
    for character_asset in reversed(character_assets):
        dataset_payload = get_character_lora_dataset_payload(
            session,
            character_asset.public_id,
            api_base_url="",
        )
        if dataset_payload is None:
            continue

        character_payload = get_character_payload(
            session,
            character_asset.public_id,
            api_base_url="",
        )
        label = None
        if character_payload is not None:
            label_value = character_payload.get("label")
            if isinstance(label_value, str):
                label = label_value

        dataset = cast(dict[str, object], dataset_payload["dataset"])
        prompt_handle = dataset.get("prompt_handle")
        prompt_expansion = dataset.get("prompt_expansion")
        visible_tags = dataset.get("visible_tags")
        dataset_status = dataset.get("status")
        if (
            not isinstance(prompt_handle, str)
            or not isinstance(prompt_expansion, str)
            or not isinstance(visible_tags, list)
            or not isinstance(dataset_status, str)
        ):
            continue

        payloads.append(
            {
                "label": label or f"Character {str(character_asset.public_id)[:8]}",
                "prompt_expansion": prompt_expansion,
                "prompt_handle": prompt_handle,
                "public_id": character_asset.public_id,
                "status": character_asset.status,
                "training_prompt_status": dataset_status,
                "visible_tags": [str(tag) for tag in visible_tags],
            }
        )
    return payloads


def expand_prompt_text(session: Session, prompt_text: str) -> dict[str, object]:
    expanded_prompt = prompt_text
    matched_handles: list[str] = []
    handle_map = {
        cast(str, recipe["prompt_handle"]): cast(str, recipe["prompt_expansion"])
        for recipe in _character_prompt_recipes(session)
    }
    for handle in sorted(handle_map.keys(), key=len, reverse=True):
        pattern = re.compile(rf"(?<!\w){re.escape(handle)}(?!\w)")
        if pattern.search(expanded_prompt):
            matched_handles.append(handle)
            expanded_prompt = pattern.sub(handle_map[handle], expanded_prompt)

    unresolved_handles = [
        handle
        for handle in HANDLE_PATTERN.findall(prompt_text)
        if handle not in matched_handles
    ]
    return {
        "expanded_prompt": expanded_prompt,
        "matched_handles": matched_handles,
        "unresolved_handles": unresolved_handles,
    }


def _character_label(session: Session, character_asset_id: uuid.UUID) -> str:
    character_asset = session.get(Asset, character_asset_id)
    if character_asset is None:
        return f"Character {str(character_asset_id)[:8]}"

    payload = get_character_payload(session, character_asset.public_id, api_base_url="")
    if payload is None:
        return f"Character {str(character_asset.public_id)[:8]}"

    label = payload.get("label")
    return (
        label
        if isinstance(label, str) and label
        else f"Character {str(character_asset.public_id)[:8]}"
    )


def _registry_payload(
    session: Session,
    registry_entry: ModelRegistry,
    *,
    source: str,
) -> dict[str, object]:
    asset = session.get(Asset, registry_entry.character_asset_id)
    storage_object = (
        session.get(StorageObject, registry_entry.storage_object_id)
        if registry_entry.storage_object_id is not None
        else None
    )
    owner_label = (
        _character_label(session, registry_entry.character_asset_id)
        if asset is not None and asset.asset_type == "character"
        else "Imported external LoRA"
    )

    return {
        "character_public_id": str(asset.public_id) if asset is not None else None,
        "model_name": registry_entry.model_name,
        "owner_label": owner_label,
        "prompt_handle": registry_entry.prompt_handle,
        "registry_public_id": str(registry_entry.public_id),
        "source": source,
        "status": registry_entry.status,
        "storage_path": storage_object.storage_path if storage_object is not None else None,
        "toolkit_name": registry_entry.toolkit_name,
    }


def _registry_storage_has_artifact(session: Session, registry_entry: ModelRegistry) -> bool:
    if registry_entry.storage_object_id is None:
        return False
    storage_object = session.get(StorageObject, registry_entry.storage_object_id)
    if storage_object is None:
        return False
    return Path(storage_object.storage_path).exists()


def list_local_lora_options(session: Session) -> list[dict[str, object]]:
    payloads: list[dict[str, object]] = []
    registry_entries = list(
        session.scalars(
            _registry_query().where(
                ModelRegistry.model_type == "lora",
                ModelRegistry.status == "current",
            )
        ).all()
    )
    for entry in registry_entries:
        if not _registry_storage_has_artifact(session, entry):
            continue
        asset = session.get(Asset, entry.character_asset_id)
        if asset is None or asset.asset_type != "character":
            continue
        payloads.append(_registry_payload(session, entry, source="local"))
    return payloads


def list_external_lora_options(session: Session) -> list[dict[str, object]]:
    payloads: list[dict[str, object]] = []
    registry_entries = list(
        session.scalars(
            _registry_query().where(
                ModelRegistry.model_type == "lora",
                ModelRegistry.toolkit_name == "civitai",
                ModelRegistry.status == "available",
            )
        ).all()
    )
    for entry in registry_entries:
        asset = session.get(Asset, entry.character_asset_id)
        if asset is None or asset.asset_type != "external-lora":
            continue
        payloads.append(_registry_payload(session, entry, source="external"))
    return payloads


def get_civitai_import_capability(env: Mapping[str, str] | None = None) -> dict[str, object]:
    resolved_env = env if env is not None else os.environ
    storage_layout = resolve_storage_layout(resolved_env)
    enabled = resolved_env.get("MEDIACREATOR_ENABLE_CIVITAI_IMPORT") == "1"
    base_url = resolved_env.get("MEDIACREATOR_CIVITAI_API_BASE_URL", CIVITAI_DEFAULT_BASE_URL)
    missing_requirements: list[str] = []

    if not enabled:
        missing_requirements.append("civitai_import_disabled")
    if not storage_layout.nas_available:
        missing_requirements.append("nas_storage_missing")

    status = "enabled" if not missing_requirements else "disabled"
    detail = (
        (
            "Civitai discovery/import is enabled and imported models will be written "
            "into the internal registry."
        )
        if status == "enabled"
        else (
            "Civitai discovery/import is disabled until the opt-in flag and NAS-backed "
            "storage are both ready."
        )
    )
    return {
        "base_url": base_url,
        "detail": detail,
        "missing_requirements": missing_requirements,
        "status": status,
    }


def search_external_loras(
    query: str,
    *,
    env: Mapping[str, str] | None = None,
) -> list[dict[str, object]]:
    capability = get_civitai_import_capability(env)
    if capability["status"] != "enabled":
        raise RuntimeError(str(capability["detail"]))
    if not query.strip():
        return []

    search_url = (
        f"{capability['base_url']}/models?"
        + urlencode({"limit": "5", "query": query, "types": "LORA"})
    )
    request = Request(search_url, headers={"accept": "application/json"}, method="GET")
    try:
        with urlopen(request, timeout=5.0) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError) as exc:
        raise RuntimeError(f"Unable to query Civitai: {exc}") from exc

    results: list[dict[str, object]] = []
    items = payload.get("items", [])
    if not isinstance(items, list):
        return results

    for item in items:
        if not isinstance(item, dict):
            continue
        model_name = item.get("name")
        versions = item.get("modelVersions")
        if not isinstance(model_name, str) or not isinstance(versions, list) or not versions:
            continue

        version = versions[0]
        if not isinstance(version, dict):
            continue
        files = version.get("files")
        if not isinstance(files, list) or not files:
            continue

        download_url = None
        for file_payload in files:
            if not isinstance(file_payload, dict):
                continue
            candidate = file_payload.get("downloadUrl")
            if isinstance(candidate, str):
                download_url = candidate
                break
        if download_url is None:
            continue

        version_name = version.get("name")
        results.append(
            {
                "download_url": download_url,
                "model_name": model_name,
                "prompt_handle": f"@external_{_slugify(model_name)}",
                "version_name": version_name if isinstance(version_name, str) else "latest",
            }
        )
    return results


def _write_external_model(
    download_url: str,
    *,
    env: Mapping[str, str] | None = None,
    model_name: str,
) -> Path:
    storage_layout = resolve_storage_layout(env)
    if not storage_layout.nas_available:
        raise RuntimeError("External LoRA import requires NAS-backed storage.")

    import_root = storage_layout.loras_root / "imports" / "civitai"
    import_root.mkdir(parents=True, exist_ok=True)
    suffix = Path(download_url).suffix or ".safetensors"
    target_path = import_root / f"{_slugify(model_name)}{suffix}"
    request = Request(download_url, headers={"accept": "*/*"}, method="GET")
    try:
        with urlopen(request, timeout=20.0) as response:
            target_path.write_bytes(response.read())
    except (HTTPError, URLError, TimeoutError) as exc:
        raise RuntimeError(f"Unable to download external LoRA: {exc}") from exc
    return target_path


def import_external_lora(
    session: Session,
    *,
    download_url: str,
    env: Mapping[str, str] | None = None,
    model_name: str,
    prompt_handle: str,
) -> ModelRegistry:
    capability = get_civitai_import_capability(env)
    if capability["status"] != "enabled":
        raise RuntimeError(str(capability["detail"]))

    actor_id = get_system_actor_id(session)
    model_path = _write_external_model(download_url, env=env, model_name=model_name)
    external_asset = Asset(
        asset_type="external-lora",
        status="available",
        created_by_actor_id=actor_id,
        current_owner_actor_id=actor_id,
    )
    session.add(external_asset)
    session.flush()

    storage_object = StorageObject(
        storage_path=str(model_path),
        root_class="nas",
        object_type="external-lora-model",
        media_type="application/octet-stream",
        byte_size=model_path.stat().st_size,
        sha256=_sha256(model_path),
        created_by_actor_id=actor_id,
        current_owner_actor_id=actor_id,
        source_asset_id=external_asset.id,
    )
    session.add(storage_object)
    session.flush()

    registry_entry = ModelRegistry(
        character_asset_id=external_asset.id,
        model_type="lora",
        model_name=model_name,
        status="available",
        prompt_handle=prompt_handle if prompt_handle.startswith("@") else f"@{prompt_handle}",
        toolkit_name="civitai",
        storage_object_id=storage_object.id,
        details={"download_url": download_url, "source": "civitai"},
    )
    session.add(registry_entry)
    session.flush()
    _record_history_event(
        session,
        actor_id,
        asset_id=external_asset.id,
        details={
            "download_url": download_url,
            "model_name": model_name,
            "model_registry_public_id": str(registry_entry.public_id),
            "prompt_handle": registry_entry.prompt_handle,
            "storage_object_public_id": str(storage_object.public_id),
        },
        event_type="generation.external_lora_imported",
    )
    return registry_entry


def _registry_entry_by_public_id(
    session: Session,
    registry_public_id: uuid.UUID | None,
) -> ModelRegistry | None:
    if registry_public_id is None:
        return None
    return session.execute(
        _registry_query().where(ModelRegistry.public_id == registry_public_id)
    ).scalar_one_or_none()


def _validate_local_lora_entry(
    session: Session,
    registry_public_id: uuid.UUID | None,
) -> dict[str, object] | None:
    entry = _registry_entry_by_public_id(session, registry_public_id)
    if entry is None:
        return None
    asset = session.get(Asset, entry.character_asset_id)
    if asset is None or asset.asset_type != "character":
        raise LookupError("Local LoRA registry entry not found.")
    return _registry_payload(session, entry, source="local")


def _validate_external_lora_entry(
    session: Session,
    registry_public_id: uuid.UUID | None,
) -> dict[str, object] | None:
    entry = _registry_entry_by_public_id(session, registry_public_id)
    if entry is None:
        return None
    asset = session.get(Asset, entry.character_asset_id)
    if asset is None or asset.asset_type != "external-lora":
        raise LookupError("External LoRA registry entry not found.")
    return _registry_payload(session, entry, source="external")


def _request_workflow(target_kind: str) -> tuple[str, Path]:
    if target_kind == "video":
        return "text_to_video_v1", TEXT_TO_VIDEO_WORKFLOW_PATH
    return "text_to_image_v1", TEXT_TO_IMAGE_WORKFLOW_PATH


def _request_history_details(session: Session, request_asset_id: uuid.UUID) -> dict[str, object]:
    history_events = session.scalars(
        _history_query().where(HistoryEvent.asset_id == request_asset_id)
    ).all()
    for event in history_events:
        if event.event_type == "generation.requested":
            return event.details
    raise LookupError("Generation request history is missing.")


def _generation_request_payload(session: Session, request_asset: Asset) -> dict[str, object]:
    details = _request_history_details(session, request_asset.id)
    raw_prompt = details.get("raw_prompt")
    expanded_prompt = details.get("expanded_prompt")
    target_kind = details.get("target_kind")
    workflow_id = details.get("workflow_id")
    workflow_path = details.get("workflow_path")
    provider_status = details.get("provider_status")
    matched_handles = details.get("matched_handles")
    if (
        not isinstance(raw_prompt, str)
        or not isinstance(expanded_prompt, str)
        or not isinstance(target_kind, str)
        or not isinstance(workflow_id, str)
        or not isinstance(workflow_path, str)
        or not isinstance(provider_status, str)
        or not isinstance(matched_handles, list)
    ):
        raise LookupError("Generation request details are incomplete.")

    local_lora = details.get("local_lora")
    external_lora = details.get("external_lora")
    return {
        "created_at": request_asset.created_at,
        "expanded_prompt": expanded_prompt,
        "external_lora": external_lora if isinstance(external_lora, dict) else None,
        "local_lora": local_lora if isinstance(local_lora, dict) else None,
        "matched_handles": [str(handle) for handle in matched_handles],
        "provider_status": provider_status,
        "public_id": request_asset.public_id,
        "raw_prompt": raw_prompt,
        "status": request_asset.status,
        "target_kind": target_kind,
        "workflow_id": workflow_id,
        "workflow_path": workflow_path,
    }


def create_generation_request(
    session: Session,
    *,
    external_lora_registry_public_id: uuid.UUID | None,
    local_lora_registry_public_id: uuid.UUID | None,
    prompt_text: str,
    target_kind: str,
) -> dict[str, object]:
    expansion = expand_prompt_text(session, prompt_text)
    local_lora = _validate_local_lora_entry(session, local_lora_registry_public_id)
    external_lora = _validate_external_lora_entry(session, external_lora_registry_public_id)
    capability = get_generation_capability()
    actor_id = get_system_actor_id(session)
    workflow_id, workflow_path = _request_workflow(target_kind)
    request_asset = Asset(
        asset_type="generation-request",
        status="prepared" if capability.status == "ready" else "staged",
        created_by_actor_id=actor_id,
        current_owner_actor_id=actor_id,
    )
    session.add(request_asset)
    session.flush()

    _record_history_event(
        session,
        actor_id,
        asset_id=request_asset.id,
        details={
            "expanded_prompt": expansion["expanded_prompt"],
            "external_lora": external_lora,
            "local_lora": local_lora,
            "matched_handles": cast(list[str], expansion["matched_handles"]),
            "provider_status": capability.status,
            "raw_prompt": prompt_text,
            "target_kind": target_kind,
            "workflow_id": workflow_id,
            "workflow_path": str(workflow_path),
        },
        event_type="generation.requested",
    )
    session.flush()
    return _generation_request_payload(session, request_asset)


def recent_generation_requests(session: Session) -> list[dict[str, object]]:
    request_assets = list(
        session.scalars(_asset_query().where(Asset.asset_type == "generation-request")).all()
    )
    return [_generation_request_payload(session, asset) for asset in request_assets]


def get_generation_workspace_payload(session: Session) -> dict[str, object]:
    capability = get_generation_capability()
    return {
        "characters": _character_prompt_recipes(session),
        "civitai_import": get_civitai_import_capability(),
        "external_loras": list_external_lora_options(session),
        "generation_capability": {
            "detail": (
                "ComfyUI is ready for generation requests."
                if capability.status == "ready"
                else (
                    "Generation requests are stored truthfully, but media output is not "
                    "claimed until ComfyUI capability is ready."
                )
            ),
            "missing_requirements": capability.missing_requirements,
            "status": capability.status,
        },
        "local_loras": list_local_lora_options(session),
        "recent_requests": recent_generation_requests(session),
        "workflow_contracts": [
            {
                "path": str(TEXT_TO_IMAGE_WORKFLOW_PATH),
                "target_kind": "image",
                "workflow_id": "text_to_image_v1",
            },
            {
                "path": str(TEXT_TO_VIDEO_WORKFLOW_PATH),
                "target_kind": "video",
                "workflow_id": "text_to_video_v1",
            },
        ],
    }
