from __future__ import annotations

import hashlib
import json
import uuid
from pathlib import Path
from typing import cast

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.models.asset import Asset
from app.models.history_event import HistoryEvent
from app.models.storage_object import StorageObject
from app.services.characters import get_character_asset, get_character_payload
from app.services.jobs import get_system_actor_id

REPO_ROOT = Path(__file__).resolve().parents[4]
MOTION_LIBRARY_ROOT = REPO_ROOT / "motions" / "library"
SEED_MOTION_FILES = ("idle.json", "walk.json", "jump.json", "sit.json", "turn.json")


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


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _motion_storage_object_for_path(session: Session, action_path: Path) -> StorageObject | None:
    return session.execute(
        _storage_object_query().where(
            StorageObject.object_type == "motion-action-payload",
            StorageObject.storage_path == str(action_path),
        )
    ).scalar_one_or_none()


def _motion_history(session: Session, motion_asset_id: uuid.UUID) -> list[HistoryEvent]:
    return list(
        session.scalars(
            _history_query().where(HistoryEvent.asset_id == motion_asset_id)
        ).all()
    )


def _motion_seed_details(action_path: Path) -> dict[str, object]:
    seed_payload = json.loads(action_path.read_text(encoding="utf-8"))
    return cast(dict[str, object], seed_payload)


def seed_motion_library(session: Session) -> None:
    actor_id = get_system_actor_id(session)

    for file_name in SEED_MOTION_FILES:
        action_path = MOTION_LIBRARY_ROOT / file_name
        if _motion_storage_object_for_path(session, action_path) is not None:
            continue

        seed_details = _motion_seed_details(action_path)
        motion_asset = Asset(
            asset_type="motion-clip",
            status="available",
            created_by_actor_id=actor_id,
            current_owner_actor_id=actor_id,
        )
        session.add(motion_asset)
        session.flush()

        storage_object = StorageObject(
            storage_path=str(action_path),
            root_class="repo",
            object_type="motion-action-payload",
            media_type="application/json",
            byte_size=action_path.stat().st_size,
            sha256=_sha256(action_path),
            created_by_actor_id=actor_id,
            current_owner_actor_id=actor_id,
            source_asset_id=motion_asset.id,
        )
        session.add(storage_object)
        session.flush()

        _record_history_event(
            session,
            actor_id,
            asset_id=motion_asset.id,
            details={
                "action_payload_path": str(action_path),
                "action_payload_storage_object_public_id": str(storage_object.public_id),
                "compatible_rig_class": seed_details["compatible_rig_class"],
                "duration_seconds": seed_details["duration_seconds"],
                "external_import_note": seed_details["external_import_note"],
                "name": seed_details["name"],
                "recommended_external_source": seed_details["recommended_external_source"],
                "slug": seed_details["slug"],
                "source": seed_details["source"],
            },
            event_type="motion.seeded",
        )
        session.flush()


def _motion_asset_details(session: Session, motion_asset: Asset) -> dict[str, object]:
    history = _motion_history(session, motion_asset.id)
    if not history:
        raise LookupError("Motion asset history is missing.")
    return history[0].details


def list_motion_assets_payload(session: Session) -> list[dict[str, object]]:
    seed_motion_library(session)
    motion_assets = list(
        session.scalars(_asset_query().where(Asset.asset_type == "motion-clip")).all()
    )

    payloads: list[dict[str, object]] = []
    for motion_asset in motion_assets:
        details = _motion_asset_details(session, motion_asset)
        payloads.append(
            {
                "public_id": motion_asset.public_id,
                "name": details["name"],
                "slug": details["slug"],
                "duration_seconds": details["duration_seconds"],
                "source": details["source"],
                "compatible_rig_class": details["compatible_rig_class"],
                "action_payload_path": details["action_payload_path"],
                "recommended_external_source": details["recommended_external_source"],
                "external_import_note": details["external_import_note"],
            }
        )
    return payloads


def get_motion_asset(session: Session, public_id: uuid.UUID) -> Asset | None:
    seed_motion_library(session)
    return session.execute(
        _asset_query().where(
            Asset.public_id == public_id,
            Asset.asset_type == "motion-clip",
        )
    ).scalar_one_or_none()


def _latest_motion_assignment_event(
    session: Session,
    character_asset_id: uuid.UUID,
) -> HistoryEvent | None:
    return session.execute(
        select(HistoryEvent)
        .where(
            HistoryEvent.asset_id == character_asset_id,
            HistoryEvent.event_type == "character.motion_assigned",
        )
        .order_by(HistoryEvent.created_at.desc())
        .limit(1)
    ).scalar_one_or_none()


def get_character_motion_assignment(
    session: Session,
    character_public_id: uuid.UUID,
) -> dict[str, object] | None:
    character_asset = get_character_asset(session, character_public_id)
    if character_asset is None:
        return None

    assignment_event = _latest_motion_assignment_event(session, character_asset.id)
    if assignment_event is None:
        return None
    return assignment_event.details


def assign_motion_to_character(
    session: Session,
    character_public_id: uuid.UUID,
    motion_public_id: uuid.UUID,
) -> dict[str, object]:
    seed_motion_library(session)
    character_asset = get_character_asset(session, character_public_id)
    if character_asset is None:
        raise LookupError("Character not found.")

    motion_asset = get_motion_asset(session, motion_public_id)
    if motion_asset is None:
        raise LookupError("Motion asset not found.")

    actor_id = get_system_actor_id(session)
    motion_details = _motion_asset_details(session, motion_asset)
    assignment = {
        "action_payload_path": motion_details["action_payload_path"],
        "compatible_rig_class": motion_details["compatible_rig_class"],
        "duration_seconds": motion_details["duration_seconds"],
        "motion_asset_public_id": str(motion_asset.public_id),
        "motion_name": motion_details["name"],
        "motion_slug": motion_details["slug"],
        "source": motion_details["source"],
    }
    _record_history_event(
        session,
        actor_id,
        asset_id=character_asset.id,
        details=assignment,
        event_type="character.motion_assigned",
    )
    return assignment


def _character_label(session: Session, character_asset: Asset) -> str:
    payload = get_character_payload(session, character_asset.public_id, api_base_url="")
    if payload is None:
        return f"Character {str(character_asset.public_id)[:8]}"
    label = payload.get("label")
    return (
        label
        if isinstance(label, str) and label
        else f"Character {str(character_asset.public_id)[:8]}"
    )


def list_character_motion_payloads(session: Session) -> list[dict[str, object]]:
    character_assets = list(
        session.scalars(_asset_query().where(Asset.asset_type == "character")).all()
    )
    payloads: list[dict[str, object]] = []
    for character_asset in character_assets:
        current_motion = get_character_motion_assignment(session, character_asset.public_id)
        payloads.append(
            {
                "public_id": character_asset.public_id,
                "label": _character_label(session, character_asset),
                "status": character_asset.status,
                "current_motion": current_motion,
            }
        )
    return payloads


def get_motion_screen_payload(session: Session) -> dict[str, object]:
    return {
        "characters": list_character_motion_payloads(session),
        "import_note": (
            "Local seeded Rigify-compatible actions are available now. External humanoid imports "
            "remain optional, with Mixamo documented as the recommended future source."
        ),
        "motion_library": list_motion_assets_payload(session),
    }
