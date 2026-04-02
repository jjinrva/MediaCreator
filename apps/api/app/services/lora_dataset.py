from __future__ import annotations

import hashlib
import json
import re
import shutil
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import cast

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.models.asset import Asset
from app.models.history_event import HistoryEvent
from app.models.photoset_entry import PhotosetEntry
from app.models.storage_object import StorageObject
from app.services.characters import get_character_asset, get_character_payload
from app.services.jobs import get_system_actor_id
from app.services.storage_service import resolve_storage_layout

DATASET_VERSION = "dataset-v1"
PROMPT_CONTRACT_VERSION = "prompt-contract-v1"


@dataclass(frozen=True)
class PromptContract:
    expansion_string: str
    handle: str
    visible_tags: list[str]


def _photoset_entry_query() -> Select[tuple[PhotosetEntry]]:
    return select(PhotosetEntry).order_by(PhotosetEntry.ordinal.asc())


def _storage_object_query() -> Select[tuple[StorageObject]]:
    return select(StorageObject).order_by(StorageObject.created_at.asc())


def _slugify(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return normalized or "character"


def _source_photoset(session: Session, character_asset: Asset) -> Asset:
    if character_asset.source_asset_id is None:
        raise LookupError("Character has no source photoset.")

    photoset_asset = session.get(Asset, character_asset.source_asset_id)
    if photoset_asset is None or photoset_asset.asset_type != "photoset":
        raise LookupError("Character source photoset not found.")
    return photoset_asset


def _dataset_manifest_storage_object(
    session: Session,
    character_asset_id: uuid.UUID,
) -> StorageObject | None:
    return session.execute(
        _storage_object_query().where(
            StorageObject.source_asset_id == character_asset_id,
            StorageObject.object_type == "character-lora-dataset-manifest",
        )
    ).scalar_one_or_none()


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _prompt_contract(
    label: str,
    *,
    accepted_entry_count: int,
    character_public_id: uuid.UUID,
    framing_labels: list[str],
) -> PromptContract:
    handle = f"@character_{_slugify(f'{label}-{str(character_public_id)[:8]}')}"
    visible_tags = [
        handle.removeprefix("@"),
        "single-person",
        "character-reference",
        f"accepted-{accepted_entry_count}-image-set",
    ]
    for framing_label in sorted(set(framing_labels)):
        visible_tags.append(f"framing-{framing_label}")

    framing_expansions = [
        tag.replace("framing-", "").replace("-", " ")
        for tag in visible_tags
        if tag.startswith("framing-")
    ]
    expansion_string = ", ".join(
        [
            handle.removeprefix("@"),
            label,
            "single person",
            "character reference",
            *framing_expansions,
        ]
    )
    return PromptContract(
        expansion_string=expansion_string,
        handle=handle,
        visible_tags=visible_tags,
    )


def _dataset_root(character_public_id: uuid.UUID) -> Path:
    layout = resolve_storage_layout()
    if not layout.nas_available:
        raise RuntimeError("LoRA dataset creation requires NAS-backed storage.")

    dataset_root = layout.loras_root / "datasets" / str(character_public_id) / DATASET_VERSION
    dataset_root.mkdir(parents=True, exist_ok=True)
    return dataset_root


def _accepted_entry_payloads(
    session: Session,
    character_public_id: uuid.UUID,
) -> tuple[dict[str, object], list[dict[str, object]]]:
    character_payload = get_character_payload(session, character_public_id, api_base_url="")
    if character_payload is None:
        raise LookupError("Character not found.")
    accepted_entries = cast(list[dict[str, object]], character_payload["accepted_entries"])
    return character_payload, accepted_entries


def _accepted_photoset_entries(
    session: Session,
    character_asset: Asset,
    *,
    accepted_entry_public_ids: set[str],
) -> list[PhotosetEntry]:
    photoset_asset = _source_photoset(session, character_asset)
    photoset_entries = list(
        session.scalars(
            _photoset_entry_query().where(PhotosetEntry.photoset_asset_id == photoset_asset.id)
        ).all()
    )
    return [
        entry
        for entry in photoset_entries
        if str(entry.public_id) in accepted_entry_public_ids
    ]


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


def build_character_lora_dataset(session: Session, character_public_id: uuid.UUID) -> StorageObject:
    character_asset = get_character_asset(session, character_public_id)
    if character_asset is None:
        raise LookupError("Character not found.")

    character_payload, accepted_entries_payload = _accepted_entry_payloads(
        session,
        character_public_id,
    )
    if not accepted_entries_payload:
        raise ValueError("Character has no accepted images for dataset creation.")

    accepted_entry_public_ids = {
        str(entry_payload["public_id"]) for entry_payload in accepted_entries_payload
    }
    accepted_entries = _accepted_photoset_entries(
        session,
        character_asset,
        accepted_entry_public_ids=accepted_entry_public_ids,
    )
    if not accepted_entries:
        raise ValueError("Character has no strict accepted entries for dataset creation.")

    label = str(character_payload["label"] or f"Character {str(character_public_id)[:8]}")
    framing_labels = [
        str(entry_payload["framing_label"]) for entry_payload in accepted_entries_payload
    ]
    prompt_contract = _prompt_contract(
        label,
        accepted_entry_count=len(accepted_entries_payload),
        character_public_id=character_public_id,
        framing_labels=framing_labels,
    )

    dataset_root = _dataset_root(character_public_id)
    images_root = dataset_root / "images"
    captions_root = dataset_root / "captions"
    images_root.mkdir(parents=True, exist_ok=True)
    captions_root.mkdir(parents=True, exist_ok=True)

    manifest_entries: list[dict[str, object]] = []
    for index, entry in enumerate(accepted_entries, start=1):
        normalized_storage_object = session.get(StorageObject, entry.normalized_storage_object_id)
        if normalized_storage_object is None:
            raise LookupError("Normalized storage object not found for accepted entry.")

        source_path = Path(normalized_storage_object.storage_path)
        image_filename = f"{index:03d}{source_path.suffix.lower() or '.png'}"
        caption_filename = f"{index:03d}.txt"
        target_image_path = images_root / image_filename
        target_caption_path = captions_root / caption_filename

        shutil.copy2(source_path, target_image_path)
        caption_text = ", ".join(
            [
                prompt_contract.handle.removeprefix("@"),
                label,
                "single person",
                f"framing {entry.framing_label or 'unknown'}",
                "prepared reference",
            ]
        )
        target_caption_path.write_text(caption_text, encoding="utf-8")

        manifest_entries.append(
            {
                "caption_file": str(target_caption_path.relative_to(dataset_root)),
                "caption_text": caption_text,
                "image_file": str(target_image_path.relative_to(dataset_root)),
                "original_filename": entry.original_filename,
                "source_entry_public_id": str(entry.public_id),
                "source_photo_asset_id": str(entry.photo_asset_id),
            }
        )

    manifest = {
        "ai_toolkit_compatible": True,
        "character_public_id": str(character_public_id),
        "dataset_version": DATASET_VERSION,
        "entry_count": len(manifest_entries),
        "prompt_contract": {
            "expansion_string": prompt_contract.expansion_string,
            "handle": prompt_contract.handle,
            "version": PROMPT_CONTRACT_VERSION,
            "visible_tags": prompt_contract.visible_tags,
        },
        "source_asset_public_id": str(character_payload["originating_photoset_public_id"]),
        "entries": manifest_entries,
    }
    manifest_path = dataset_root / "dataset_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    actor_id = get_system_actor_id(session)
    existing_storage_object = _dataset_manifest_storage_object(session, character_asset.id)
    if existing_storage_object is None:
        storage_object = StorageObject(
            storage_path=str(manifest_path),
            root_class="nas",
            object_type="character-lora-dataset-manifest",
            media_type="application/json",
            byte_size=manifest_path.stat().st_size,
            sha256=_sha256(manifest_path),
            created_by_actor_id=actor_id,
            current_owner_actor_id=actor_id,
            source_asset_id=character_asset.id,
        )
        session.add(storage_object)
        session.flush()
        event_type = "lora_dataset.built"
    else:
        existing_storage_object.storage_path = str(manifest_path)
        existing_storage_object.root_class = "nas"
        existing_storage_object.media_type = "application/json"
        existing_storage_object.byte_size = manifest_path.stat().st_size
        existing_storage_object.sha256 = _sha256(manifest_path)
        existing_storage_object.current_owner_actor_id = actor_id
        session.flush()
        storage_object = existing_storage_object
        event_type = "lora_dataset.updated"

    _record_history_event(
        session,
        actor_id,
        asset_id=character_asset.id,
        details={
            "dataset_root": str(dataset_root),
            "dataset_version": DATASET_VERSION,
            "entry_count": len(manifest_entries),
            "manifest_storage_object_public_id": str(storage_object.public_id),
            "prompt_expansion": prompt_contract.expansion_string,
            "prompt_handle": prompt_contract.handle,
        },
        event_type=event_type,
    )
    return storage_object


def get_character_lora_dataset_payload(
    session: Session,
    character_public_id: uuid.UUID,
    *,
    api_base_url: str,
) -> dict[str, object] | None:
    character_asset = get_character_asset(session, character_public_id)
    if character_asset is None:
        return None

    character_payload, accepted_entries_payload = _accepted_entry_payloads(
        session,
        character_public_id,
    )
    label = str(character_payload["label"] or f"Character {str(character_public_id)[:8]}")
    framing_labels = [
        str(entry_payload["framing_label"]) for entry_payload in accepted_entries_payload
    ]
    prompt_contract = _prompt_contract(
        label,
        accepted_entry_count=len(accepted_entries_payload),
        character_public_id=character_public_id,
        framing_labels=framing_labels,
    )
    manifest_storage_object = _dataset_manifest_storage_object(session, character_asset.id)
    manifest_path = (
        Path(manifest_storage_object.storage_path)
        if manifest_storage_object is not None
        else None
    )

    status = "available" if manifest_path is not None and manifest_path.exists() else "not-ready"
    detail = (
        "LoRA dataset manifest is available and the prompt expansion contract is ready to audit."
        if status == "available"
        else "No LoRA dataset has been built yet. The prompt expansion contract is still visible."
    )

    return {
        "character_public_id": character_public_id,
        "dataset": {
            "dataset_version": DATASET_VERSION,
            "detail": detail,
            "entry_count": len(accepted_entries_payload),
            "manifest_storage_object_public_id": (
                manifest_storage_object.public_id if manifest_storage_object is not None else None
            ),
            "manifest_url": (
                f"{api_base_url}/api/v1/lora-datasets/characters/{character_public_id}/manifest.json"
                if manifest_path is not None and manifest_path.exists()
                else None
            ),
            "prompt_contract_version": PROMPT_CONTRACT_VERSION,
            "prompt_expansion": prompt_contract.expansion_string,
            "prompt_handle": prompt_contract.handle,
            "status": status,
            "visible_tags": prompt_contract.visible_tags,
        },
    }


def get_character_lora_dataset_manifest_storage_object(
    session: Session,
    character_public_id: uuid.UUID,
) -> StorageObject | None:
    character_asset = get_character_asset(session, character_public_id)
    if character_asset is None:
        return None
    return _dataset_manifest_storage_object(session, character_asset.id)
