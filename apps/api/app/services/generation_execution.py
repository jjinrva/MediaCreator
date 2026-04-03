from __future__ import annotations

import hashlib
import json
import uuid
from collections.abc import Mapping
from pathlib import Path
from typing import cast
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.models.asset import Asset
from app.models.history_event import HistoryEvent
from app.models.job import Job
from app.models.models_registry import ModelRegistry
from app.models.storage_object import StorageObject
from app.services.characters import get_character_asset
from app.services.generation_provider import (
    WorkflowContract,
    get_generation_capability,
    load_workflow_contract,
)
from app.services.jobs import GenerationProofImageJobPayload, enqueue_job, get_system_actor_id
from app.services.storage_service import resolve_storage_layout


def _asset_query() -> Select[tuple[Asset]]:
    return select(Asset).order_by(Asset.created_at.desc())


def _history_query() -> Select[tuple[HistoryEvent]]:
    return select(HistoryEvent).order_by(HistoryEvent.created_at.asc())


def _job_query() -> Select[tuple[Job]]:
    return select(Job).order_by(Job.created_at.desc())


def _model_registry_query() -> Select[tuple[ModelRegistry]]:
    return select(ModelRegistry).order_by(ModelRegistry.created_at.desc())


def _storage_object_query() -> Select[tuple[StorageObject]]:
    return select(StorageObject).order_by(StorageObject.created_at.desc())


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


def _generation_request_asset(
    session: Session,
    request_public_id: uuid.UUID,
) -> Asset | None:
    return session.execute(
        _asset_query().where(
            Asset.public_id == request_public_id,
            Asset.asset_type == "generation-request",
        )
    ).scalar_one_or_none()


def _proof_asset_for_request_asset_id(
    session: Session,
    request_asset_id: uuid.UUID,
) -> Asset | None:
    return session.execute(
        _asset_query().where(
            Asset.asset_type == "generation-proof-image",
            Asset.source_asset_id == request_asset_id,
        )
    ).scalar_one_or_none()


def _proof_storage_object_for_asset(
    session: Session,
    proof_asset_id: uuid.UUID,
) -> StorageObject | None:
    return session.execute(
        _storage_object_query().where(
            StorageObject.source_asset_id == proof_asset_id,
            StorageObject.object_type == "generation-proof-image",
        )
    ).scalar_one_or_none()


def _proof_job_for_asset(
    session: Session,
    proof_asset_id: uuid.UUID,
) -> Job | None:
    return session.execute(
        _job_query().where(
            Job.job_type == "generation-proof-image",
            Job.output_asset_id == proof_asset_id,
        )
    ).scalar_one_or_none()


def _sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _registry_details(
    session: Session,
    registry_public_id: uuid.UUID | None,
) -> dict[str, object] | None:
    if registry_public_id is None:
        return None

    entry = session.execute(
        _model_registry_query().where(ModelRegistry.public_id == registry_public_id)
    ).scalar_one_or_none()
    if entry is None:
        return None

    storage_path: str | None = None
    if entry.storage_object_id is not None:
        storage_object = session.get(StorageObject, entry.storage_object_id)
        if storage_object is not None:
            storage_path = storage_object.storage_path

    return {
        "model_name": entry.model_name,
        "prompt_handle": entry.prompt_handle,
        "registry_public_id": str(entry.public_id),
        "status": entry.status,
        "storage_path": storage_path,
        "toolkit_name": entry.toolkit_name,
    }


def build_generation_proof_image_job_payload(
    *,
    character_public_id: uuid.UUID | None,
    expanded_prompt: str,
    external_lora_registry_public_id: uuid.UUID | None,
    local_lora_registry_public_id: uuid.UUID | None,
    request_public_id: uuid.UUID,
    workflow_id: str,
    workflow_path: Path,
) -> dict[str, object]:
    capability = get_generation_capability()
    if capability.status != "ready":
        raise RuntimeError("Generation runtime is not ready for proof-image execution.")

    storage_layout = resolve_storage_layout()
    output_path = (
        storage_layout.renders_root
        / "generation_proofs"
        / str(request_public_id)
        / "proof.png"
    )
    payload = GenerationProofImageJobPayload(
        character_public_id=character_public_id,
        expanded_prompt=expanded_prompt,
        external_lora_registry_public_id=external_lora_registry_public_id,
        generation_request_public_id=request_public_id,
        local_lora_registry_public_id=local_lora_registry_public_id,
        output_image_path=str(output_path),
        output_root_class="nas",
        workflow_id=workflow_id,
        workflow_path=str(workflow_path),
    )
    return payload.model_dump(mode="json")


def queue_generation_proof_image(
    session: Session,
    *,
    character_public_id: uuid.UUID | None,
    expanded_prompt: str,
    external_lora_registry_public_id: uuid.UUID | None,
    local_lora_registry_public_id: uuid.UUID | None,
    request_public_id: uuid.UUID,
    workflow_id: str,
    workflow_path: Path,
) -> Job:
    request_asset = _generation_request_asset(session, request_public_id)
    if request_asset is None:
        raise LookupError("Generation request not found.")

    character_asset_id: uuid.UUID | None = None
    if character_public_id is not None:
        character_asset = get_character_asset(session, character_public_id)
        if character_asset is None:
            raise LookupError("Character not found.")
        character_asset_id = character_asset.id

    actor_id = get_system_actor_id(session)
    proof_asset = Asset(
        asset_type="generation-proof-image",
        status="queued",
        parent_asset_id=character_asset_id,
        source_asset_id=request_asset.id,
        created_by_actor_id=actor_id,
        current_owner_actor_id=actor_id,
    )
    session.add(proof_asset)
    session.flush()

    payload = build_generation_proof_image_job_payload(
        character_public_id=character_public_id,
        expanded_prompt=expanded_prompt,
        external_lora_registry_public_id=external_lora_registry_public_id,
        local_lora_registry_public_id=local_lora_registry_public_id,
        request_public_id=request_public_id,
        workflow_id=workflow_id,
        workflow_path=workflow_path,
    )
    job = enqueue_job(
        session,
        actor_id,
        payload,
        output_asset_id=proof_asset.id,
    )

    request_asset.status = "queued"
    details = {
        "character_public_id": str(character_public_id) if character_public_id else None,
        "external_lora_registry_public_id": (
            str(external_lora_registry_public_id)
            if external_lora_registry_public_id is not None
            else None
        ),
        "job_public_id": str(job.public_id),
        "local_lora_registry_public_id": (
            str(local_lora_registry_public_id)
            if local_lora_registry_public_id is not None
            else None
        ),
        "proof_asset_public_id": str(proof_asset.public_id),
        "workflow_id": workflow_id,
        "workflow_path": str(workflow_path),
    }
    _record_history_event(
        session,
        actor_id,
        asset_id=request_asset.id,
        details=cast(dict[str, object], details),
        event_type="generation.proof_image_queued",
    )
    _record_history_event(
        session,
        actor_id,
        asset_id=proof_asset.id,
        details={
            **details,
            "generation_request_public_id": str(request_public_id),
        },
        event_type="generation.proof_image_asset_created",
    )
    if character_asset_id is not None:
        _record_history_event(
            session,
            actor_id,
            asset_id=character_asset_id,
            details={
                **details,
                "generation_request_public_id": str(request_public_id),
            },
            event_type="generation.proof_image_queued",
        )
    session.flush()
    return job


def _replace_templates(value: object, replacements: Mapping[str, str]) -> object:
    if isinstance(value, str):
        rendered = value
        for key, replacement in replacements.items():
            rendered = rendered.replace(f"{{{{{key}}}}}", replacement)
        return rendered
    if isinstance(value, list):
        return [_replace_templates(item, replacements) for item in value]
    if isinstance(value, dict):
        return {
            str(key): _replace_templates(item, replacements) for key, item in value.items()
        }
    return value


def _render_prompt_graph(
    contract: WorkflowContract,
    *,
    checkpoint_name: str,
    payload: GenerationProofImageJobPayload,
    vae_name: str,
) -> dict[str, object]:
    if contract.prompt_api is None:
        raise RuntimeError("Workflow contract does not include a runnable prompt graph.")

    prompt_graph = _replace_templates(
        contract.prompt_api,
        {
            "checkpoint_name": checkpoint_name,
            "external_lora_registry_public_id": (
                str(payload.external_lora_registry_public_id)
                if payload.external_lora_registry_public_id is not None
                else ""
            ),
            "filename_prefix": f"mediacreator-proof-{payload.generation_request_public_id}",
            "local_lora_registry_public_id": (
                str(payload.local_lora_registry_public_id)
                if payload.local_lora_registry_public_id is not None
                else ""
            ),
            "prompt": payload.expanded_prompt,
            "vae_name": vae_name,
        },
    )
    if not isinstance(prompt_graph, dict):
        raise RuntimeError("Workflow prompt graph must render to a dictionary.")
    return cast(dict[str, object], prompt_graph)


def _json_request(
    url: str,
    *,
    method: str,
    payload: dict[str, object] | None = None,
) -> dict[str, object]:
    encoded_payload = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {"accept": "application/json"}
    if payload is not None:
        headers["content-type"] = "application/json"

    request = Request(url, data=encoded_payload, headers=headers, method=method)
    try:
        with urlopen(request, timeout=10.0) as response:
            decoded = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError) as exc:
        raise RuntimeError(f"Unable to talk to ComfyUI at '{url}': {exc}") from exc

    if not isinstance(decoded, dict):
        raise RuntimeError(f"ComfyUI returned a non-object payload for '{url}'.")
    return cast(dict[str, object], decoded)


def _binary_request(url: str) -> bytes:
    request = Request(url, headers={"accept": "*/*"}, method="GET")
    try:
        with urlopen(request, timeout=10.0) as response:
            return cast(bytes, response.read())
    except (HTTPError, URLError, TimeoutError) as exc:
        raise RuntimeError(f"Unable to download the proof image from '{url}': {exc}") from exc


def _prompt_id_from_response(response_payload: dict[str, object]) -> str:
    prompt_id = response_payload.get("prompt_id")
    if not isinstance(prompt_id, str) or not prompt_id:
        raise RuntimeError("ComfyUI did not return a prompt_id for the proof-image request.")
    return prompt_id


def _first_image_reference(
    history_payload: dict[str, object],
    *,
    prompt_id: str,
) -> dict[str, str]:
    history_root = history_payload
    nested_prompt = history_payload.get(prompt_id)
    if isinstance(nested_prompt, dict):
        history_root = cast(dict[str, object], nested_prompt)

    outputs = history_root.get("outputs")
    if not isinstance(outputs, dict):
        raise RuntimeError("ComfyUI history payload does not include output images.")

    for output_value in outputs.values():
        if not isinstance(output_value, dict):
            continue
        images = output_value.get("images")
        if not isinstance(images, list):
            continue
        for image_payload in images:
            if not isinstance(image_payload, dict):
                continue
            filename = image_payload.get("filename")
            subfolder = image_payload.get("subfolder")
            object_type = image_payload.get("type")
            if not isinstance(filename, str) or not filename:
                continue
            return {
                "filename": filename,
                "subfolder": subfolder if isinstance(subfolder, str) else "",
                "type": object_type if isinstance(object_type, str) else "output",
            }

    raise RuntimeError("ComfyUI history did not include any proof-image outputs.")


def execute_provider_proof_image(
    session: Session,
    payload: GenerationProofImageJobPayload,
) -> tuple[bytes, dict[str, object]]:
    capability = get_generation_capability()
    if capability.status != "ready" or capability.comfyui_base_url is None:
        raise RuntimeError("Generation runtime is not ready for proof-image execution.")

    workflow_contract = load_workflow_contract(Path(payload.workflow_path))
    checkpoint_name = capability.checkpoint_files_detected[0]
    vae_name = capability.vae_files_detected[0]
    prompt_graph = _render_prompt_graph(
        workflow_contract,
        checkpoint_name=checkpoint_name,
        payload=payload,
        vae_name=vae_name,
    )
    base_url = capability.comfyui_base_url.rstrip("/")
    prompt_response = _json_request(
        f"{base_url}/prompt",
        method="POST",
        payload={"prompt": prompt_graph},
    )
    prompt_id = _prompt_id_from_response(prompt_response)
    history_response = _json_request(f"{base_url}/history/{prompt_id}", method="GET")
    image_reference = _first_image_reference(history_response, prompt_id=prompt_id)
    proof_image_url = f"{base_url}/view?{urlencode(image_reference)}"
    proof_image_bytes = _binary_request(proof_image_url)
    if not proof_image_bytes:
        raise RuntimeError("ComfyUI returned an empty proof-image artifact.")

    return proof_image_bytes, {
        "character_public_id": str(payload.character_public_id)
        if payload.character_public_id is not None
        else None,
        "checkpoint_name": checkpoint_name,
        "comfyui_base_url": base_url,
        "external_lora": _registry_details(session, payload.external_lora_registry_public_id),
        "image_reference": image_reference,
        "local_lora": _registry_details(session, payload.local_lora_registry_public_id),
        "prompt_id": prompt_id,
        "provider_status": capability.status,
        "requested_prompt": payload.expanded_prompt,
        "vae_name": vae_name,
        "workflow_id": payload.workflow_id,
        "workflow_path": payload.workflow_path,
    }


def _write_proof_image(output_path: Path, proof_image_bytes: bytes) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(proof_image_bytes)
    if not output_path.exists():
        raise FileNotFoundError(f"Expected proof image at '{output_path}' was not written.")


def _sync_proof_storage_object(
    session: Session,
    *,
    output_asset: Asset,
    output_path: Path,
    output_root_class: str,
    proof_image_bytes: bytes,
) -> StorageObject:
    actor_id = get_system_actor_id(session)
    storage_object = _proof_storage_object_for_asset(session, output_asset.id)
    if storage_object is None:
        storage_object = StorageObject(
            storage_path=str(output_path),
            root_class=output_root_class,
            object_type="generation-proof-image",
            media_type="image/png",
            byte_size=len(proof_image_bytes),
            sha256=_sha256_bytes(proof_image_bytes),
            created_by_actor_id=actor_id,
            current_owner_actor_id=actor_id,
            source_asset_id=output_asset.id,
        )
        session.add(storage_object)
        session.flush()
        return storage_object

    storage_object.storage_path = str(output_path)
    storage_object.root_class = output_root_class
    storage_object.media_type = "image/png"
    storage_object.byte_size = len(proof_image_bytes)
    storage_object.sha256 = _sha256_bytes(proof_image_bytes)
    storage_object.current_owner_actor_id = actor_id
    session.flush()
    return storage_object


def execute_generation_proof_image_job(
    session: Session,
    job: Job,
    payload: GenerationProofImageJobPayload,
) -> uuid.UUID:
    request_asset = _generation_request_asset(session, payload.generation_request_public_id)
    if request_asset is None:
        raise LookupError("Generation request not found.")
    if job.output_asset_id is None:
        raise LookupError("Generation proof-image job is missing its output asset.")

    output_asset = session.get(Asset, job.output_asset_id)
    if output_asset is None or output_asset.asset_type != "generation-proof-image":
        raise LookupError("Generation proof-image output asset is missing.")

    proof_image_bytes, provider_details = execute_provider_proof_image(session, payload)
    output_path = Path(payload.output_image_path)
    _write_proof_image(output_path, proof_image_bytes)
    storage_object = _sync_proof_storage_object(
        session,
        output_asset=output_asset,
        output_path=output_path,
        output_root_class=payload.output_root_class,
        proof_image_bytes=proof_image_bytes,
    )

    actor_id = get_system_actor_id(session)
    output_asset.status = "available"
    request_asset.status = "completed"
    details = {
        **provider_details,
        "byte_size": storage_object.byte_size,
        "generation_request_public_id": str(payload.generation_request_public_id),
        "job_public_id": str(job.public_id),
        "proof_asset_public_id": str(output_asset.public_id),
        "proof_image_path": str(output_path),
        "sha256": storage_object.sha256,
        "storage_object_public_id": str(storage_object.public_id),
    }
    _record_history_event(
        session,
        actor_id,
        asset_id=output_asset.id,
        details=details,
        event_type="generation.proof_image_written",
    )
    _record_history_event(
        session,
        actor_id,
        asset_id=request_asset.id,
        details=details,
        event_type="generation.completed",
    )
    if payload.character_public_id is not None:
        character_asset = get_character_asset(session, payload.character_public_id)
        if character_asset is not None:
            _record_history_event(
                session,
                actor_id,
                asset_id=character_asset.id,
                details=details,
                event_type="generation.proof_image_attached",
            )
    session.flush()
    return storage_object.id


def mark_generation_proof_image_job_failed(
    session: Session,
    job: Job,
    error_summary: str,
) -> None:
    payload = GenerationProofImageJobPayload.model_validate(job.payload)
    actor_id = get_system_actor_id(session)
    request_asset = _generation_request_asset(session, payload.generation_request_public_id)
    if request_asset is not None:
        request_asset.status = "failed"
        _record_history_event(
            session,
            actor_id,
            asset_id=request_asset.id,
            details={
                "error_summary": error_summary,
                "job_public_id": str(job.public_id),
            },
            event_type="generation.failed",
        )

    if job.output_asset_id is not None:
        output_asset = session.get(Asset, job.output_asset_id)
        if output_asset is not None:
            output_asset.status = "failed"
            _record_history_event(
                session,
                actor_id,
                asset_id=output_asset.id,
                details={
                    "error_summary": error_summary,
                    "generation_request_public_id": str(payload.generation_request_public_id),
                    "job_public_id": str(job.public_id),
                },
                event_type="generation.proof_image_failed",
            )
    session.flush()


def get_generation_proof_job(
    session: Session,
    request_public_id: uuid.UUID,
) -> Job | None:
    request_asset = _generation_request_asset(session, request_public_id)
    if request_asset is None:
        return None
    proof_asset = _proof_asset_for_request_asset_id(session, request_asset.id)
    if proof_asset is None:
        return None
    return _proof_job_for_asset(session, proof_asset.id)


def get_generation_proof_storage_object(
    session: Session,
    request_public_id: uuid.UUID,
) -> StorageObject | None:
    request_asset = _generation_request_asset(session, request_public_id)
    if request_asset is None:
        return None
    proof_asset = _proof_asset_for_request_asset_id(session, request_asset.id)
    if proof_asset is None:
        return None
    return _proof_storage_object_for_asset(session, proof_asset.id)
