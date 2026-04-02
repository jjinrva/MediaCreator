from __future__ import annotations

import hashlib
import uuid
from pathlib import Path

from PIL import Image, ImageOps
from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.models.asset import Asset
from app.models.history_event import HistoryEvent
from app.models.photoset_entry import PhotosetEntry
from app.models.storage_object import StorageObject
from app.services.characters import get_character_asset
from app.services.jobs import get_system_actor_id
from app.services.storage_service import resolve_storage_layout


def _photoset_entry_query() -> Select[tuple[PhotosetEntry]]:
    return select(PhotosetEntry).order_by(PhotosetEntry.ordinal.asc())


def _storage_object_query() -> Select[tuple[StorageObject]]:
    return select(StorageObject).order_by(StorageObject.created_at.asc())


def _source_photoset(session: Session, character_asset: Asset) -> Asset:
    if character_asset.source_asset_id is None:
        raise LookupError("Character has no source photoset.")

    photoset_asset = session.get(Asset, character_asset.source_asset_id)
    if photoset_asset is None or photoset_asset.asset_type != "photoset":
        raise LookupError("Character source photoset not found.")
    return photoset_asset


def _capture_entries(session: Session, photoset_asset_id: uuid.UUID) -> list[PhotosetEntry]:
    return list(
        session.scalars(
            _photoset_entry_query().where(PhotosetEntry.photoset_asset_id == photoset_asset_id)
        ).all()
    )


def _normalized_capture_paths(session: Session, photoset_asset_id: uuid.UUID) -> list[Path]:
    paths: list[Path] = []
    for entry in _capture_entries(session, photoset_asset_id):
        storage_object = session.get(StorageObject, entry.normalized_storage_object_id)
        if storage_object is None:
            raise LookupError("Normalized storage object not found for photoset entry.")
        paths.append(Path(storage_object.storage_path))
    return paths


def _texture_root(character_public_id: uuid.UUID) -> tuple[Path, str]:
    layout = resolve_storage_layout()
    if layout.nas_available:
        root = layout.character_assets_root / str(character_public_id) / "textures"
        root_class = "nas"
    else:
        root = layout.scratch_root / "characters" / str(character_public_id) / "textures"
        root_class = "scratch"

    root.mkdir(parents=True, exist_ok=True)
    return root, root_class


def _texture_storage_object(
    session: Session,
    *,
    character_asset_id: uuid.UUID,
    object_type: str,
) -> StorageObject | None:
    return session.execute(
        _storage_object_query().where(
            StorageObject.source_asset_id == character_asset_id,
            StorageObject.object_type == object_type,
        )
    ).scalar_one_or_none()


def _base_color_texture_image(source_paths: list[Path]) -> Image.Image:
    if not source_paths:
        raise ValueError("Character has no prepared photos for the texture pipeline.")

    canvas = Image.new("RGB", (1024, 1024), color=(88, 78, 70))
    cells = [(0, 0), (512, 0), (0, 512), (512, 512)]
    selected_paths = source_paths[:4]

    for index, origin in enumerate(cells):
        source_path = selected_paths[index % len(selected_paths)]
        with Image.open(source_path) as source_image:
            fitted = ImageOps.fit(
                ImageOps.exif_transpose(source_image).convert("RGB"),
                (512, 512),
                method=Image.Resampling.LANCZOS,
            )
        canvas.paste(fitted, origin)

    return canvas


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


def ensure_character_base_texture(
    session: Session,
    character_public_id: uuid.UUID,
) -> StorageObject:
    character_asset = get_character_asset(session, character_public_id)
    if character_asset is None:
        raise LookupError("Character not found.")

    photoset_asset = _source_photoset(session, character_asset)
    capture_paths = _normalized_capture_paths(session, photoset_asset.id)
    texture_root, root_class = _texture_root(character_public_id)
    texture_path = texture_root / "base-color.png"

    texture_image = _base_color_texture_image(capture_paths)
    texture_image.save(texture_path, format="PNG")

    actor_id = get_system_actor_id(session)
    existing_storage_object = _texture_storage_object(
        session,
        character_asset_id=character_asset.id,
        object_type="character-base-color-texture",
    )

    if existing_storage_object is None:
        storage_object = StorageObject(
            storage_path=str(texture_path),
            root_class=root_class,
            object_type="character-base-color-texture",
            media_type="image/png",
            byte_size=texture_path.stat().st_size,
            sha256=_sha256(texture_path),
            created_by_actor_id=actor_id,
            current_owner_actor_id=actor_id,
            source_asset_id=character_asset.id,
        )
        session.add(storage_object)
        session.flush()
        event_type = "texture.generated"
    else:
        existing_storage_object.storage_path = str(texture_path)
        existing_storage_object.root_class = root_class
        existing_storage_object.media_type = "image/png"
        existing_storage_object.byte_size = texture_path.stat().st_size
        existing_storage_object.sha256 = _sha256(texture_path)
        existing_storage_object.current_owner_actor_id = actor_id
        session.flush()
        storage_object = existing_storage_object
        event_type = "texture.updated"

    _record_history_event(
        session,
        actor_id,
        asset_id=character_asset.id,
        details={
            "capture_count": len(capture_paths),
            "storage_object_public_id": str(storage_object.public_id),
            "storage_path": str(texture_path),
            "texture_fidelity": "base-textured",
        },
        event_type=event_type,
    )
    return storage_object


def get_character_base_texture_storage_object(
    session: Session,
    character_public_id: uuid.UUID,
) -> StorageObject | None:
    character_asset = get_character_asset(session, character_public_id)
    if character_asset is None:
        return None
    return _texture_storage_object(
        session,
        character_asset_id=character_asset.id,
        object_type="character-base-color-texture",
    )


def get_character_refined_texture_storage_object(
    session: Session,
    character_public_id: uuid.UUID,
) -> StorageObject | None:
    character_asset = get_character_asset(session, character_public_id)
    if character_asset is None:
        return None
    return _texture_storage_object(
        session,
        character_asset_id=character_asset.id,
        object_type="character-refined-color-texture",
    )
