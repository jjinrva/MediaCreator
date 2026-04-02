from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import uuid
from pathlib import Path
from typing import Mapping, cast

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.models.history_event import HistoryEvent
from app.models.job import Job
from app.models.models_registry import ModelRegistry
from app.models.storage_object import StorageObject
from app.services.characters import get_character_asset
from app.services.jobs import LoraTrainingJobPayload, enqueue_job, get_system_actor_id
from app.services.lora_dataset import (
    get_character_lora_dataset_manifest_storage_object,
    get_character_lora_dataset_payload,
)
from app.services.storage_service import resolve_storage_layout


def _job_query() -> Select[tuple[Job]]:
    return select(Job).order_by(Job.created_at.desc())


def _registry_query() -> Select[tuple[ModelRegistry]]:
    return select(ModelRegistry).order_by(ModelRegistry.created_at.desc())


def _storage_object_query() -> Select[tuple[StorageObject]]:
    return select(StorageObject).order_by(StorageObject.created_at.desc())


def _resolve_ai_toolkit_bin(env: Mapping[str, str] | None = None) -> Path | None:
    resolved_env = env if env is not None else os.environ
    configured = resolved_env.get("MEDIACREATOR_AI_TOOLKIT_BIN")
    if configured:
        configured_path = Path(configured)
        return configured_path if configured_path.exists() else None

    discovered = shutil.which("ai-toolkit")
    return Path(discovered) if discovered else None


def get_lora_training_capability(env: Mapping[str, str] | None = None) -> dict[str, object]:
    resolved_env = env if env is not None else os.environ
    storage_layout = resolve_storage_layout(resolved_env)
    ai_toolkit_bin = _resolve_ai_toolkit_bin(resolved_env)
    missing_requirements: list[str] = []

    if ai_toolkit_bin is None:
        missing_requirements.append("ai_toolkit_missing")
    if not storage_layout.nas_available:
        missing_requirements.append("nas_storage_missing")

    status = "ready" if not missing_requirements else "unavailable"
    detail = (
        "AI Toolkit is installed and LoRA training can run locally."
        if status == "ready"
        else (
            "LoRA training is unavailable because AI Toolkit is missing or NAS-backed "
            "storage is not ready."
        )
    )

    return {
        "ai_toolkit_bin": str(ai_toolkit_bin) if ai_toolkit_bin is not None else None,
        "detail": detail,
        "loras_root": str(storage_layout.loras_root),
        "missing_requirements": missing_requirements,
        "status": status,
    }


def _archive_current_entries(session: Session, character_asset_id: uuid.UUID) -> None:
    current_entries = session.scalars(
        _registry_query().where(
            ModelRegistry.character_asset_id == character_asset_id,
            ModelRegistry.model_type == "lora",
            ModelRegistry.status == "current",
        )
    ).all()
    for entry in current_entries:
        entry.status = "archived"


def _job_public_id(details: dict[str, object] | None) -> str | None:
    if details is None:
        return None
    job_public_id = details.get("job_public_id")
    return job_public_id if isinstance(job_public_id, str) else None


def _registry_entry_for_job(
    session: Session,
    *,
    character_asset_id: uuid.UUID,
    job_public_id: uuid.UUID,
) -> ModelRegistry | None:
    registry_entries = session.scalars(
        _registry_query().where(
            ModelRegistry.character_asset_id == character_asset_id,
            ModelRegistry.model_type == "lora",
        )
    ).all()
    for entry in registry_entries:
        if _job_public_id(entry.details) == str(job_public_id):
            return entry
    return None


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


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def register_lora_model(
    session: Session,
    character_public_id: uuid.UUID,
    *,
    details: dict[str, object] | None,
    model_name: str,
    prompt_handle: str,
    status: str,
    storage_path: Path | None,
    toolkit_name: str | None,
) -> ModelRegistry:
    character_asset = get_character_asset(session, character_public_id)
    if character_asset is None:
        raise LookupError("Character not found.")

    actor_id = get_system_actor_id(session)
    storage_object_id: uuid.UUID | None = None
    if storage_path is not None:
        storage_path.parent.mkdir(parents=True, exist_ok=True)
        storage_object = session.execute(
            _storage_object_query().where(
                StorageObject.source_asset_id == character_asset.id,
                StorageObject.object_type == "character-lora-model",
                StorageObject.storage_path == str(storage_path),
            )
        ).scalar_one_or_none()
        if storage_object is None:
            storage_object = StorageObject(
                storage_path=str(storage_path),
                root_class="nas",
                object_type="character-lora-model",
                media_type="application/octet-stream",
                byte_size=storage_path.stat().st_size if storage_path.exists() else 0,
                sha256=_sha256(storage_path) if storage_path.exists() else None,
                created_by_actor_id=actor_id,
                current_owner_actor_id=actor_id,
                source_asset_id=character_asset.id,
            )
            session.add(storage_object)
            session.flush()
        else:
            storage_object.byte_size = storage_path.stat().st_size if storage_path.exists() else 0
            storage_object.sha256 = _sha256(storage_path) if storage_path.exists() else None
            storage_object.current_owner_actor_id = actor_id
            session.flush()
        storage_object_id = storage_object.id

    if status == "current":
        _archive_current_entries(session, character_asset.id)

    registry_entry = ModelRegistry(
        character_asset_id=character_asset.id,
        model_type="lora",
        model_name=model_name,
        status=status,
        prompt_handle=prompt_handle,
        toolkit_name=toolkit_name,
        storage_object_id=storage_object_id,
        details=details or {},
    )
    session.add(registry_entry)
    session.flush()
    return registry_entry


def update_lora_registry_status_for_job(
    session: Session,
    character_public_id: uuid.UUID,
    *,
    job_public_id: uuid.UUID,
    status: str,
) -> ModelRegistry | None:
    character_asset = get_character_asset(session, character_public_id)
    if character_asset is None:
        raise LookupError("Character not found.")

    registry_entry = _registry_entry_for_job(
        session,
        character_asset_id=character_asset.id,
        job_public_id=job_public_id,
    )
    if registry_entry is None:
        return None

    registry_entry.status = status
    details = dict(registry_entry.details)
    details["job_status"] = status
    registry_entry.details = details
    session.flush()
    return registry_entry


def list_character_lora_registry(
    session: Session,
    character_public_id: uuid.UUID,
) -> list[ModelRegistry]:
    character_asset = get_character_asset(session, character_public_id)
    if character_asset is None:
        raise LookupError("Character not found.")
    return list(
        session.scalars(
            _registry_query().where(
                ModelRegistry.character_asset_id == character_asset.id,
                ModelRegistry.model_type == "lora",
            )
        ).all()
    )


def resolve_active_lora_registry_entry(
    session: Session,
    character_public_id: uuid.UUID,
) -> ModelRegistry | None:
    character_asset = get_character_asset(session, character_public_id)
    if character_asset is None:
        return None
    return session.execute(
        _registry_query().where(
            ModelRegistry.character_asset_id == character_asset.id,
            ModelRegistry.model_type == "lora",
            ModelRegistry.status == "current",
        )
    ).scalar_one_or_none()


def resolve_active_lora_artifact(
    session: Session,
    character_public_id: uuid.UUID,
) -> dict[str, object] | None:
    active_entry = resolve_active_lora_registry_entry(session, character_public_id)
    if active_entry is None or active_entry.storage_object_id is None:
        return None

    storage_object = session.get(StorageObject, active_entry.storage_object_id)
    if storage_object is None:
        return None

    return {
        "model_name": active_entry.model_name,
        "prompt_handle": active_entry.prompt_handle,
        "status": active_entry.status,
        "storage_object_public_id": storage_object.public_id,
        "storage_path": storage_object.storage_path,
    }


def build_lora_training_job_payload(
    session: Session,
    character_public_id: uuid.UUID,
) -> dict[str, object]:
    capability = get_lora_training_capability()
    if capability["status"] != "ready":
        raise RuntimeError(str(capability["detail"]))

    manifest_storage_object = get_character_lora_dataset_manifest_storage_object(
        session,
        character_public_id,
    )
    if manifest_storage_object is None or not Path(manifest_storage_object.storage_path).exists():
        raise ValueError("LoRA dataset manifest is missing.")

    dataset_payload = get_character_lora_dataset_payload(
        session,
        character_public_id,
        api_base_url="",
    )
    if dataset_payload is None:
        raise LookupError("Character not found.")
    dataset = cast(dict[str, object], dataset_payload["dataset"])

    storage_layout = resolve_storage_layout()
    output_root = storage_layout.loras_root / "trained" / str(character_public_id)
    output_root.mkdir(parents=True, exist_ok=True)
    scratch_root = storage_layout.scratch_root / "ai_toolkit"
    scratch_root.mkdir(parents=True, exist_ok=True)

    payload = LoraTrainingJobPayload(
        character_public_id=character_public_id,
        ai_toolkit_bin=str(capability["ai_toolkit_bin"]),
        dataset_manifest_path=manifest_storage_object.storage_path,
        output_lora_path=str(output_root / "current.safetensors"),
        prompt_handle=str(dataset["prompt_handle"]),
        training_config_path=str(scratch_root / f"{character_public_id}-ai-toolkit.json"),
    )
    return payload.model_dump(mode="json")


def create_lora_training_registry_entry(
    session: Session,
    *,
    character_public_id: uuid.UUID,
    job_public_id: uuid.UUID,
    prompt_handle: str,
) -> ModelRegistry:
    return register_lora_model(
        session,
        character_public_id,
        details={
            "job_public_id": str(job_public_id),
            "job_status": "working",
        },
        model_name=f"ai-toolkit-{str(job_public_id)[:8]}",
        prompt_handle=prompt_handle,
        status="working",
        storage_path=None,
        toolkit_name="ai-toolkit",
    )


def queue_lora_training(session: Session, character_public_id: uuid.UUID) -> Job:
    character_asset = get_character_asset(session, character_public_id)
    if character_asset is None:
        raise LookupError("Character not found.")
    payload = build_lora_training_job_payload(session, character_public_id)
    actor_id = get_system_actor_id(session)
    job = enqueue_job(
        session,
        actor_id,
        payload,
        output_asset_id=character_asset.id,
    )
    create_lora_training_registry_entry(
        session,
        character_public_id=character_public_id,
        job_public_id=job.public_id,
        prompt_handle=str(payload["prompt_handle"]),
    )
    return job


def execute_lora_training_job(
    session: Session,
    job: Job,
    payload: LoraTrainingJobPayload,
) -> uuid.UUID:
    config_path = Path(payload.training_config_path)
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(
        json.dumps(
            {
                "dataset_manifest_path": payload.dataset_manifest_path,
                "output_lora_path": payload.output_lora_path,
                "prompt_handle": payload.prompt_handle,
                "trainer": "ai-toolkit",
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    subprocess.run(
        [payload.ai_toolkit_bin, "--config", str(config_path)],
        check=True,
        cwd=str(config_path.parent),
    )

    output_path = Path(payload.output_lora_path)
    if not output_path.exists():
        raise FileNotFoundError(f"AI Toolkit did not produce '{output_path}'.")

    update_lora_registry_status_for_job(
        session,
        payload.character_public_id,
        job_public_id=job.public_id,
        status="archived",
    )

    registry_entry = register_lora_model(
        session,
        payload.character_public_id,
        details={
            "job_public_id": str(job.public_id),
            "job_status": "completed",
        },
        model_name=output_path.name,
        prompt_handle=payload.prompt_handle,
        status="current",
        storage_path=output_path,
        toolkit_name="ai-toolkit",
    )
    actor_id = get_system_actor_id(session)
    character_asset = get_character_asset(session, payload.character_public_id)
    assert character_asset is not None
    _record_history_event(
        session,
        actor_id,
        asset_id=character_asset.id,
        details={
            "job_public_id": str(job.public_id),
            "model_name": registry_entry.model_name,
            "model_registry_public_id": str(registry_entry.public_id),
            "prompt_handle": registry_entry.prompt_handle,
        },
        event_type="lora_training.completed",
    )

    assert registry_entry.storage_object_id is not None
    return registry_entry.storage_object_id


def mark_lora_training_job_failed(
    session: Session,
    *,
    character_public_id: uuid.UUID,
    job_public_id: uuid.UUID,
    error_summary: str,
) -> ModelRegistry | None:
    registry_entry = update_lora_registry_status_for_job(
        session,
        character_public_id,
        job_public_id=job_public_id,
        status="failed",
    )
    if registry_entry is None:
        return None

    details = dict(registry_entry.details)
    details["error_summary"] = error_summary
    registry_entry.details = details
    actor_id = get_system_actor_id(session)
    character_asset = get_character_asset(session, character_public_id)
    assert character_asset is not None
    _record_history_event(
        session,
        actor_id,
        asset_id=character_asset.id,
        details={
            "error_summary": error_summary,
            "job_public_id": str(job_public_id),
            "model_registry_public_id": str(registry_entry.public_id),
        },
        event_type="lora_training.failed",
    )
    session.flush()
    return registry_entry


def _job_payload(job: Job | None) -> dict[str, object]:
    if job is None:
        return {"status": "not-queued", "detail": "No LoRA training job has been queued yet."}
    if job.status == "completed":
        return {"status": job.status, "detail": "Latest LoRA training job completed successfully."}
    if job.status == "failed":
        return {
            "status": job.status,
            "detail": job.error_summary or "Latest LoRA training job failed.",
        }
    return {"status": job.status, "detail": f"Latest LoRA training job is {job.status}."}


def get_character_lora_training_payload(
    session: Session,
    character_public_id: uuid.UUID,
) -> dict[str, object] | None:
    character_asset = get_character_asset(session, character_public_id)
    if character_asset is None:
        return None

    capability = get_lora_training_capability()
    registry_entries = list_character_lora_registry(session, character_public_id)
    active_model = resolve_active_lora_artifact(session, character_public_id)
    latest_job = session.execute(
        _job_query().where(
            Job.output_asset_id == character_asset.id,
            Job.job_type == "lora-train-ai-toolkit",
        )
    ).scalar_one_or_none()

    registry_payload: list[dict[str, object]] = []
    for entry in registry_entries:
        storage_object_public_id = None
        if entry.storage_object_id is not None:
            storage_object = session.get(StorageObject, entry.storage_object_id)
            storage_object_public_id = (
                storage_object.public_id if storage_object is not None else None
            )
        registry_payload.append(
            {
                "details": entry.details,
                "model_name": entry.model_name,
                "prompt_handle": entry.prompt_handle,
                "public_id": entry.public_id,
                "status": entry.status,
                "storage_object_public_id": storage_object_public_id,
            }
        )

    return {
        "character_public_id": character_public_id,
        "capability": capability,
        "training_job": _job_payload(latest_job),
        "active_model": active_model,
        "registry": registry_payload,
    }
