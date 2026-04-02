from __future__ import annotations

import uuid
from typing import cast

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.models.asset import Asset
from app.models.history_event import HistoryEvent
from app.models.photoset_entry import PhotosetEntry
from app.services.body_parameters import initialize_body_parameter_rows
from app.services.facial_parameters import initialize_facial_parameter_rows
from app.services.jobs import get_system_actor_id
from app.services.photo_prep import (
    get_photoset_asset,
    get_photoset_payload,
    is_bucket_accepted_for_character_use,
    is_bucket_body_qualified,
    is_bucket_lora_qualified,
    is_qc_status_accepted_for_character_use,
)
from app.services.pose_state import initialize_pose_state_rows


def _asset_query() -> Select[tuple[Asset]]:
    return select(Asset).order_by(Asset.created_at.asc())


def _history_query() -> Select[tuple[HistoryEvent]]:
    return select(HistoryEvent).order_by(HistoryEvent.created_at.asc())


def _photoset_entry_query() -> Select[tuple[PhotosetEntry]]:
    return select(PhotosetEntry).order_by(PhotosetEntry.ordinal.asc())


def _history_event(
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


def _photoset_created_event(session: Session, photoset_asset_id: uuid.UUID) -> HistoryEvent | None:
    return session.execute(
        _history_query().where(
            HistoryEvent.asset_id == photoset_asset_id,
            HistoryEvent.event_type == "photoset.created",
        )
    ).scalar_one_or_none()


def _character_created_event(
    session: Session,
    character_asset_id: uuid.UUID,
) -> HistoryEvent | None:
    return session.execute(
        _history_query().where(
            HistoryEvent.asset_id == character_asset_id,
            HistoryEvent.event_type == "character.created",
        )
    ).scalar_one_or_none()


def _label_from_event(event: HistoryEvent | None) -> str | None:
    if event is None:
        return None

    label = event.details.get("character_label")
    if isinstance(label, str) and label.strip():
        return label
    return None


def get_character_asset(session: Session, public_id: uuid.UUID) -> Asset | None:
    return session.execute(
        _asset_query().where(Asset.public_id == public_id, Asset.asset_type == "character")
    ).scalar_one_or_none()


def _character_asset_for_photoset(session: Session, photoset_asset_id: uuid.UUID) -> Asset | None:
    return session.execute(
        _asset_query().where(
            Asset.asset_type == "character",
            Asset.source_asset_id == photoset_asset_id,
        )
    ).scalar_one_or_none()


def create_character_from_photoset(
    session: Session,
    photoset_public_id: uuid.UUID,
) -> tuple[Asset, bool]:
    photoset_asset = get_photoset_asset(session, photoset_public_id)
    if photoset_asset is None:
        raise LookupError("Photoset not found.")
    if photoset_asset.status != "prepared":
        raise ValueError("Photoset is not ready for character creation.")

    existing_character = _character_asset_for_photoset(session, photoset_asset.id)
    if existing_character is not None:
        return existing_character, False

    photoset_entries = session.scalars(
        _photoset_entry_query().where(PhotosetEntry.photoset_asset_id == photoset_asset.id)
    ).all()
    if not photoset_entries:
        raise ValueError("Photoset has no prepared entries.")

    accepted_entries = [
        entry
        for entry in photoset_entries
        if (
            is_bucket_accepted_for_character_use(entry.bucket)
            if entry.bucket
            else is_qc_status_accepted_for_character_use(entry.qc_status)
        )
    ]
    if not accepted_entries:
        raise ValueError("Photoset has no accepted entries for character creation.")

    body_entries = [
        entry
        for entry in accepted_entries
        if entry.bucket and is_bucket_body_qualified(entry.bucket)
    ]
    lora_entries = [
        entry
        for entry in accepted_entries
        if entry.bucket and is_bucket_lora_qualified(entry.bucket)
    ]

    actor_id = get_system_actor_id(session)
    accepted_entry_public_ids = [str(entry.public_id) for entry in accepted_entries]
    accepted_photo_asset_ids = [str(entry.photo_asset_id) for entry in accepted_entries]
    body_entry_public_ids = [str(entry.public_id) for entry in body_entries]
    body_photo_asset_ids = [str(entry.photo_asset_id) for entry in body_entries]
    lora_entry_public_ids = [str(entry.public_id) for entry in lora_entries]
    lora_photo_asset_ids = [str(entry.photo_asset_id) for entry in lora_entries]
    photoset_created_event = _photoset_created_event(session, photoset_asset.id)
    character_label = _label_from_event(photoset_created_event)

    character_asset = Asset(
        asset_type="character",
        status="base-created",
        source_asset_id=photoset_asset.id,
        created_by_actor_id=actor_id,
        current_owner_actor_id=actor_id,
    )
    session.add(character_asset)
    session.flush()
    initialize_body_parameter_rows(session, character_asset.id)
    initialize_facial_parameter_rows(session, character_asset.id)
    initialize_pose_state_rows(session, character_asset.id)

    _history_event(
        session,
        actor_id,
        asset_id=character_asset.id,
        details={
            "accepted_entry_count": len(accepted_entries),
            "accepted_entry_public_ids": accepted_entry_public_ids,
            "accepted_body_entry_count": len(body_entries),
            "accepted_body_entry_public_ids": body_entry_public_ids,
            "accepted_lora_entry_count": len(lora_entries),
            "accepted_lora_entry_public_ids": lora_entry_public_ids,
            "body_parameter_profile": "body-v1",
            "character_label": character_label,
            "photoset_public_id": str(photoset_asset.public_id),
            "status": character_asset.status,
        },
        event_type="character.created",
    )
    _history_event(
        session,
        actor_id,
        asset_id=character_asset.id,
        details={
            "accepted_entry_public_ids": accepted_entry_public_ids,
            "accepted_photo_asset_ids": accepted_photo_asset_ids,
            "body_entry_public_ids": body_entry_public_ids,
            "body_photo_asset_ids": body_photo_asset_ids,
            "lora_entry_public_ids": lora_entry_public_ids,
            "lora_photo_asset_ids": lora_photo_asset_ids,
            "photoset_public_id": str(photoset_asset.public_id),
            "source_asset_public_id": str(photoset_asset.public_id),
        },
        event_type="character.photoset_linked",
    )
    session.flush()
    return character_asset, True


def get_character_payload(
    session: Session,
    character_public_id: uuid.UUID,
    *,
    api_base_url: str,
) -> dict[str, object] | None:
    character_asset = get_character_asset(session, character_public_id)
    if character_asset is None:
        return None
    if character_asset.source_asset_id is None:
        raise LookupError("Character has no source photoset.")

    photoset_asset = session.get(Asset, character_asset.source_asset_id)
    if photoset_asset is None or photoset_asset.asset_type != "photoset":
        raise LookupError("Character source photoset not found.")

    photoset_payload = get_photoset_payload(
        session,
        photoset_asset.public_id,
        api_base_url=api_base_url,
    )
    if photoset_payload is None:
        raise LookupError("Character source photoset payload not found.")

    created_event = _character_created_event(session, character_asset.id)
    accepted_entry_ids = set()
    if created_event is not None:
        accepted_entry_public_ids = cast(
            list[object],
            created_event.details.get("accepted_entry_public_ids", []),
        )
        accepted_entry_ids = {
            entry_public_id
            for entry_public_id in accepted_entry_public_ids
            if isinstance(entry_public_id, str)
        }

    photoset_entries = cast(list[dict[str, object]], photoset_payload["entries"])
    accepted_entries: list[dict[str, object]] = []
    for entry in photoset_entries:
        accepted_for_character_use = bool(entry.get("accepted_for_character_use"))
        if accepted_entry_ids and str(entry["public_id"]) not in accepted_entry_ids:
            continue
        if not accepted_entry_ids and not accepted_for_character_use:
            continue

        qc_metrics = cast(dict[str, object], entry["qc_metrics"])
        accepted_entries.append(
            {
                "public_id": entry["public_id"],
                "photo_asset_public_id": entry["photo_asset_public_id"],
                "original_filename": entry["original_filename"],
                "bucket": entry["bucket"],
                "qc_status": entry["qc_status"],
                "reason_codes": entry["reason_codes"],
                "reason_messages": entry["reason_messages"],
                "framing_label": qc_metrics["framing_label"],
                "artifact_urls": entry["artifact_urls"],
            }
        )

    history_events = session.scalars(
        _history_query().where(HistoryEvent.asset_id == character_asset.id)
    ).all()

    return {
        "public_id": character_asset.public_id,
        "asset_type": character_asset.asset_type,
        "status": character_asset.status,
        "created_at": character_asset.created_at,
        "label": _label_from_event(created_event) or _label_from_event(
            _photoset_created_event(session, photoset_asset.id)
        ),
        "originating_photoset_public_id": photoset_asset.public_id,
        "accepted_entry_count": len(accepted_entries),
        "accepted_entries": accepted_entries,
        "history": [
            {
                "public_id": event.public_id,
                "event_type": event.event_type,
                "created_at": event.created_at,
                "details": event.details,
            }
            for event in history_events
        ],
    }
