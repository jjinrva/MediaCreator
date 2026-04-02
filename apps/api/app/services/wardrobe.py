from __future__ import annotations

import hashlib
import json
import mimetypes
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import cast

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.models.asset import Asset
from app.models.history_event import HistoryEvent
from app.models.storage_object import StorageObject
from app.services.generation_provider import get_generation_capability
from app.services.jobs import get_system_actor_id
from app.services.storage_service import resolve_storage_layout


@dataclass(frozen=True)
class IncomingWardrobePhotoUpload:
    content: bytes
    filename: str
    media_type: str | None


def _asset_query() -> Select[tuple[Asset]]:
    return select(Asset).order_by(Asset.created_at.asc())


def _history_query() -> Select[tuple[HistoryEvent]]:
    return select(HistoryEvent).order_by(HistoryEvent.created_at.asc())


def _storage_object_query() -> Select[tuple[StorageObject]]:
    return select(StorageObject).order_by(StorageObject.created_at.asc())


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


def _sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _ensure_wardrobe_root() -> Path:
    layout = resolve_storage_layout()
    if not layout.nas_available:
        raise RuntimeError("Wardrobe creation requires NAS-backed storage.")
    layout.wardrobe_root.mkdir(parents=True, exist_ok=True)
    return layout.wardrobe_root


def _create_asset(
    session: Session,
    actor_id: uuid.UUID,
    *,
    asset_type: str,
    status: str,
    parent_asset_id: uuid.UUID | None = None,
    source_asset_id: uuid.UUID | None = None,
) -> Asset:
    asset = Asset(
        asset_type=asset_type,
        status=status,
        parent_asset_id=parent_asset_id,
        source_asset_id=source_asset_id,
        created_by_actor_id=actor_id,
        current_owner_actor_id=actor_id,
    )
    session.add(asset)
    session.flush()
    return asset


def _create_variant_asset(
    session: Session,
    actor_id: uuid.UUID,
    *,
    parent_asset_id: uuid.UUID,
    source_asset_id: uuid.UUID,
    asset_type: str,
    event_type: str,
    status: str,
    details: dict[str, object],
) -> Asset:
    asset = _create_asset(
        session,
        actor_id,
        asset_type=asset_type,
        status=status,
        parent_asset_id=parent_asset_id,
        source_asset_id=source_asset_id,
    )
    _record_history_event(
        session,
        actor_id,
        asset_id=asset.id,
        details=details,
        event_type=event_type,
    )
    return asset


def _store_storage_object(
    session: Session,
    actor_id: uuid.UUID,
    *,
    source_asset_id: uuid.UUID,
    object_type: str,
    media_type: str,
    path: Path,
    content: bytes,
) -> StorageObject:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    storage_object = StorageObject(
        storage_path=str(path),
        root_class="nas",
        object_type=object_type,
        media_type=media_type,
        byte_size=len(content),
        sha256=_sha256_bytes(content),
        created_by_actor_id=actor_id,
        current_owner_actor_id=actor_id,
        source_asset_id=source_asset_id,
    )
    session.add(storage_object)
    session.flush()
    return storage_object


def _creation_event(asset_history: list[HistoryEvent]) -> HistoryEvent:
    for event in asset_history:
        if event.event_type in {"wardrobe.created_from_photo", "wardrobe.created_from_prompt"}:
            return event
    raise LookupError("Wardrobe creation event not found.")


def _asset_history(session: Session, asset_id: uuid.UUID) -> list[HistoryEvent]:
    return list(session.scalars(_history_query().where(HistoryEvent.asset_id == asset_id)).all())


def _child_asset(
    session: Session,
    parent_asset_id: uuid.UUID,
    *,
    asset_type: str,
) -> Asset | None:
    return session.execute(
        _asset_query().where(
            Asset.parent_asset_id == parent_asset_id,
            Asset.asset_type == asset_type,
        )
    ).scalar_one_or_none()


def _child_value(
    session: Session,
    parent_asset_id: uuid.UUID,
    *,
    asset_type: str,
    detail_key: str,
) -> str | None:
    asset = _child_asset(session, parent_asset_id, asset_type=asset_type)
    if asset is None:
        return None
    history = _asset_history(session, asset.id)
    if not history:
        return None
    detail_value = history[0].details.get(detail_key)
    return detail_value if isinstance(detail_value, str) else None


def _wardrobe_source_photo_storage_object(
    session: Session,
    wardrobe_asset: Asset,
) -> StorageObject | None:
    if wardrobe_asset.source_asset_id is None:
        return None

    source_asset = session.get(Asset, wardrobe_asset.source_asset_id)
    if source_asset is None or source_asset.asset_type != "wardrobe-source-photo":
        return None

    return session.execute(
        _storage_object_query().where(
            StorageObject.source_asset_id == source_asset.id,
            StorageObject.object_type == "wardrobe-photo-source",
        )
    ).scalar_one_or_none()


def _source_photo_url(api_base_url: str, wardrobe_public_id: uuid.UUID) -> str:
    base_url = api_base_url.rstrip("/")
    return f"{base_url}/api/v1/wardrobe/{wardrobe_public_id}/source-photo"


def _wardrobe_item_payload(
    session: Session,
    wardrobe_asset: Asset,
    *,
    api_base_url: str,
) -> dict[str, object]:
    history = _asset_history(session, wardrobe_asset.id)
    creation_event = _creation_event(history)
    details = creation_event.details
    source_photo_storage_object = _wardrobe_source_photo_storage_object(session, wardrobe_asset)
    prompt_text = details.get("prompt_text")
    label = details.get("label")
    garment_type = details.get("garment_type")
    creation_path = details.get("creation_path")
    source_photo_url = None
    if source_photo_storage_object is not None:
        source_photo_url = _source_photo_url(api_base_url, wardrobe_asset.public_id)

    return {
        "public_id": wardrobe_asset.public_id,
        "status": wardrobe_asset.status,
        "label": (
            label
            if isinstance(label, str)
            else f"Wardrobe {str(wardrobe_asset.public_id)[:8]}"
        ),
        "garment_type": garment_type if isinstance(garment_type, str) else "unspecified",
        "creation_path": creation_path if isinstance(creation_path, str) else "unknown",
        "base_color": _child_value(
            session,
            wardrobe_asset.id,
            asset_type="wardrobe-color-variant",
            detail_key="base_color",
        )
        or "",
        "material": _child_value(
            session,
            wardrobe_asset.id,
            asset_type="wardrobe-material-variant",
            detail_key="material_label",
        )
        or "",
        "fitting_status": _child_value(
            session,
            wardrobe_asset.id,
            asset_type="wardrobe-fitting-profile",
            detail_key="fitting_status",
        )
        or "unassigned",
        "prompt_text": prompt_text if isinstance(prompt_text, str) else None,
        "source_photo_url": source_photo_url,
        "history": [
            {
                "created_at": event.created_at,
                "details": event.details,
                "event_type": event.event_type,
                "public_id": event.public_id,
            }
            for event in history
        ],
    }


def get_wardrobe_generation_summary() -> dict[str, object]:
    capability = get_generation_capability()
    detail = (
        "ComfyUI is ready for wardrobe prompt generation."
        if capability.status == "ready"
        else (
            "ComfyUI is not ready, so AI wardrobe items are stored as prompt-backed "
            "catalog records without claiming a generated garment image."
        )
    )
    return {
        "detail": detail,
        "missing_requirements": capability.missing_requirements,
        "status": capability.status,
    }


def create_wardrobe_from_photo(
    session: Session,
    upload: IncomingWardrobePhotoUpload,
    *,
    base_color: str,
    garment_type: str,
    label: str,
    material_label: str,
) -> Asset:
    wardrobe_root = _ensure_wardrobe_root()
    actor_id = get_system_actor_id(session)
    safe_filename = Path(upload.filename).name or "wardrobe-source.png"
    media_type = (
        upload.media_type
        or mimetypes.guess_type(safe_filename)[0]
        or "application/octet-stream"
    )

    source_asset = _create_asset(
        session,
        actor_id,
        asset_type="wardrobe-source-photo",
        status="stored",
    )
    wardrobe_asset = _create_asset(
        session,
        actor_id,
        asset_type="wardrobe-item",
        status="photo-ingested",
        source_asset_id=source_asset.id,
    )
    storage_object = _store_storage_object(
        session,
        actor_id,
        source_asset_id=source_asset.id,
        object_type="wardrobe-photo-source",
        media_type=media_type,
        path=wardrobe_root / "photo-ingest" / str(wardrobe_asset.public_id) / safe_filename,
        content=upload.content,
    )

    color_asset = _create_variant_asset(
        session,
        actor_id,
        parent_asset_id=wardrobe_asset.id,
        source_asset_id=wardrobe_asset.id,
        asset_type="wardrobe-color-variant",
        event_type="wardrobe.color_variant.created",
        status="current",
        details={"base_color": base_color},
    )
    material_asset = _create_variant_asset(
        session,
        actor_id,
        parent_asset_id=wardrobe_asset.id,
        source_asset_id=wardrobe_asset.id,
        asset_type="wardrobe-material-variant",
        event_type="wardrobe.material_variant.created",
        status="current",
        details={"material_label": material_label},
    )
    fitting_asset = _create_variant_asset(
        session,
        actor_id,
        parent_asset_id=wardrobe_asset.id,
        source_asset_id=wardrobe_asset.id,
        asset_type="wardrobe-fitting-profile",
        event_type="wardrobe.fitting_profile.created",
        status="unassigned",
        details={"fitting_status": "unassigned"},
    )
    _record_history_event(
        session,
        actor_id,
        asset_id=wardrobe_asset.id,
        details={
            "base_color": base_color,
            "color_variant_public_id": str(color_asset.public_id),
            "creation_path": "photo",
            "fitting_profile_public_id": str(fitting_asset.public_id),
            "garment_type": garment_type,
            "label": label,
            "material": material_label,
            "material_variant_public_id": str(material_asset.public_id),
            "source_filename": safe_filename,
            "source_photo_storage_object_public_id": str(storage_object.public_id),
        },
        event_type="wardrobe.created_from_photo",
    )
    return wardrobe_asset


def create_wardrobe_from_prompt(
    session: Session,
    *,
    base_color: str,
    garment_type: str,
    label: str,
    material_label: str,
    prompt_text: str,
) -> Asset:
    wardrobe_root = _ensure_wardrobe_root()
    actor_id = get_system_actor_id(session)
    generation_summary = get_wardrobe_generation_summary()
    capability_status = str(generation_summary["status"])

    source_asset = _create_asset(
        session,
        actor_id,
        asset_type="wardrobe-prompt-request",
        status="captured",
    )
    wardrobe_asset = _create_asset(
        session,
        actor_id,
        asset_type="wardrobe-item",
        status="ai-generation-ready" if capability_status == "ready" else "ai-prompt-staged",
        source_asset_id=source_asset.id,
    )
    prompt_manifest = {
        "base_color": base_color,
        "capability_status": capability_status,
        "garment_type": garment_type,
        "label": label,
        "material": material_label,
        "missing_requirements": cast(list[str], generation_summary["missing_requirements"]),
        "prompt_text": prompt_text,
    }
    prompt_storage = _store_storage_object(
        session,
        actor_id,
        source_asset_id=source_asset.id,
        object_type="wardrobe-ai-prompt-manifest",
        media_type="application/json",
        path=wardrobe_root / "ai-prompts" / str(wardrobe_asset.public_id) / "request.json",
        content=json.dumps(prompt_manifest, indent=2).encode("utf-8"),
    )

    color_asset = _create_variant_asset(
        session,
        actor_id,
        parent_asset_id=wardrobe_asset.id,
        source_asset_id=wardrobe_asset.id,
        asset_type="wardrobe-color-variant",
        event_type="wardrobe.color_variant.created",
        status="current",
        details={"base_color": base_color},
    )
    material_asset = _create_variant_asset(
        session,
        actor_id,
        parent_asset_id=wardrobe_asset.id,
        source_asset_id=wardrobe_asset.id,
        asset_type="wardrobe-material-variant",
        event_type="wardrobe.material_variant.created",
        status="current",
        details={"material_label": material_label},
    )
    fitting_asset = _create_variant_asset(
        session,
        actor_id,
        parent_asset_id=wardrobe_asset.id,
        source_asset_id=wardrobe_asset.id,
        asset_type="wardrobe-fitting-profile",
        event_type="wardrobe.fitting_profile.created",
        status="unassigned",
        details={"fitting_status": "unassigned"},
    )
    _record_history_event(
        session,
        actor_id,
        asset_id=wardrobe_asset.id,
        details={
            "base_color": base_color,
            "color_variant_public_id": str(color_asset.public_id),
            "creation_path": "ai-prompt",
            "fitting_profile_public_id": str(fitting_asset.public_id),
            "garment_type": garment_type,
            "generation_capability_status": capability_status,
            "generation_missing_requirements": cast(
                list[str], generation_summary["missing_requirements"]
            ),
            "label": label,
            "material": material_label,
            "material_variant_public_id": str(material_asset.public_id),
            "prompt_manifest_storage_object_public_id": str(prompt_storage.public_id),
            "prompt_text": prompt_text,
        },
        event_type="wardrobe.created_from_prompt",
    )
    return wardrobe_asset


def get_wardrobe_asset(session: Session, public_id: uuid.UUID) -> Asset | None:
    return session.execute(
        _asset_query().where(
            Asset.public_id == public_id,
            Asset.asset_type == "wardrobe-item",
        )
    ).scalar_one_or_none()


def get_wardrobe_source_photo_storage_object(
    session: Session,
    wardrobe_public_id: uuid.UUID,
) -> StorageObject | None:
    wardrobe_asset = get_wardrobe_asset(session, wardrobe_public_id)
    if wardrobe_asset is None:
        return None
    return _wardrobe_source_photo_storage_object(session, wardrobe_asset)


def get_wardrobe_catalog_payload(
    session: Session,
    *,
    api_base_url: str,
) -> dict[str, object]:
    wardrobe_assets = list(
        session.scalars(_asset_query().where(Asset.asset_type == "wardrobe-item")).all()
    )
    return {
        "generation_capability": get_wardrobe_generation_summary(),
        "items": [
            _wardrobe_item_payload(
                session,
                wardrobe_asset,
                api_base_url=api_base_url,
            )
            for wardrobe_asset in wardrobe_assets
        ],
    }
