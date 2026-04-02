from __future__ import annotations

import hashlib
import io
import mimetypes
import urllib.request
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from PIL import Image, ImageOps, UnidentifiedImageError
from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.models.asset import Asset
from app.models.history_event import HistoryEvent
from app.models.photoset_entry import PhotosetEntry
from app.models.storage_object import StorageObject
from app.services.jobs import get_system_actor_id
from app.services.storage_service import StorageLayout, resolve_storage_layout

FACE_LANDMARKER_URL = (
    "https://storage.googleapis.com/mediapipe-models/face_landmarker/"
    "face_landmarker/float16/latest/face_landmarker.task"
)
POSE_LANDMARKER_URL = (
    "https://storage.googleapis.com/mediapipe-models/pose_landmarker/"
    "pose_landmarker_lite/float16/latest/pose_landmarker_lite.task"
)
ACCEPTED_QC_STATUSES = {"pass", "warn"}


@dataclass(frozen=True)
class IncomingPhotoUpload:
    content: bytes
    filename: str
    media_type: str | None


@dataclass(frozen=True)
class PhotoQcReport:
    framing_label: str
    metrics: dict[str, object]
    reasons: list[str]
    status: Literal["pass", "warn", "fail"]


@dataclass(frozen=True)
class PhotoStorageRoots:
    media_pipe_root: Path
    prepared_root: Path
    root_class: str
    uploaded_root: Path


def is_qc_status_accepted_for_character_use(qc_status: str) -> bool:
    return qc_status in ACCEPTED_QC_STATUSES


def _asset_query() -> Select[tuple[Asset]]:
    return select(Asset).order_by(Asset.created_at.asc())


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


def _write_bytes(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _storage_object(
    session: Session,
    actor_id: uuid.UUID,
    *,
    asset_id: uuid.UUID,
    byte_size: int,
    media_type: str,
    object_type: str,
    payload: bytes,
    root_class: str,
    storage_path: Path,
) -> StorageObject:
    storage_object = StorageObject(
        storage_path=str(storage_path),
        root_class=root_class,
        object_type=object_type,
        media_type=media_type,
        byte_size=byte_size,
        sha256=_sha256(payload),
        created_by_actor_id=actor_id,
        current_owner_actor_id=actor_id,
        source_asset_id=asset_id,
    )
    session.add(storage_object)
    session.flush()
    return storage_object


def _resolve_photo_roots(layout: StorageLayout) -> PhotoStorageRoots:
    if layout.nas_available:
        uploaded_root = layout.uploaded_photos_root
        prepared_root = layout.prepared_images_root
        root_class = "nas"
    else:
        uploaded_root = layout.scratch_root / "photos" / "uploaded"
        prepared_root = layout.scratch_root / "photos" / "prepared"
        root_class = "scratch"

    uploaded_root.mkdir(parents=True, exist_ok=True)
    prepared_root.mkdir(parents=True, exist_ok=True)
    media_pipe_root = layout.scratch_root / "mediapipe_models"
    media_pipe_root.mkdir(parents=True, exist_ok=True)

    return PhotoStorageRoots(
        media_pipe_root=media_pipe_root,
        prepared_root=prepared_root,
        root_class=root_class,
        uploaded_root=uploaded_root,
    )


def _download_model_if_needed(url: str, destination: Path) -> Path:
    if destination.exists():
        return destination

    destination.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(url, destination)
    return destination


def _create_face_landmarker(model_path: Path) -> vision.FaceLandmarker:
    options = vision.FaceLandmarkerOptions(
        base_options=python.BaseOptions(model_asset_path=str(model_path)),
        running_mode=vision.RunningMode.IMAGE,
    )
    return vision.FaceLandmarker.create_from_options(options)


def _create_pose_landmarker(model_path: Path) -> vision.PoseLandmarker:
    options = vision.PoseLandmarkerOptions(
        base_options=python.BaseOptions(model_asset_path=str(model_path)),
        running_mode=vision.RunningMode.IMAGE,
    )
    return vision.PoseLandmarker.create_from_options(options)


def _normalized_image(payload: bytes) -> Image.Image:
    with Image.open(io.BytesIO(payload)) as loaded_image:
        normalized = ImageOps.exif_transpose(loaded_image).convert("RGB")
    return normalized


def _png_bytes(image: Image.Image) -> bytes:
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def _thumbnail_bytes(image: Image.Image) -> bytes:
    contained = ImageOps.contain(image, (256, 256))
    canvas = Image.new("RGB", (256, 256), color=(20, 24, 32))
    offset = ((256 - contained.width) // 2, (256 - contained.height) // 2)
    canvas.paste(contained, offset)
    return _png_bytes(canvas)


def _mp_image(image: Image.Image) -> mp.Image:
    image_array = np.asarray(image, dtype=np.uint8)
    return mp.Image(image_format=mp.ImageFormat.SRGB, data=image_array)


def _framing_label(
    *,
    body_detected: bool,
    face_detected: bool,
    pose_result: vision.PoseLandmarkerResult,
) -> str:
    if body_detected and pose_result.pose_landmarks:
        y_values = [landmark.y for landmark in pose_result.pose_landmarks[0]]
        min_y = min(y_values)
        max_y = max(y_values)

        if min_y <= 0.18 and max_y >= 0.88:
            return "full-body"
        if max_y >= 0.7:
            return "mid-body"
        return "close-body"

    if face_detected:
        return "head-closeup"

    return "unknown"


def _qc_report(
    image: Image.Image,
    face_landmarker: vision.FaceLandmarker,
    pose_landmarker: vision.PoseLandmarker,
) -> PhotoQcReport:
    mp_image = _mp_image(image)
    face_result = face_landmarker.detect(mp_image)
    pose_result = pose_landmarker.detect(mp_image)

    face_detected = bool(face_result.face_landmarks)
    body_detected = bool(pose_result.pose_landmarks)

    grayscale = cv2.cvtColor(np.asarray(image, dtype=np.uint8), cv2.COLOR_RGB2GRAY)
    blur_score = float(cv2.Laplacian(grayscale, cv2.CV_64F).var())
    exposure_score = float(grayscale.mean())
    framing_label = _framing_label(
        body_detected=body_detected,
        face_detected=face_detected,
        pose_result=pose_result,
    )

    reasons: list[str] = []
    failed = False

    if not face_detected and not body_detected:
        reasons.append("Neither face nor body landmarks were detected.")
        failed = True
    elif not face_detected:
        reasons.append("Face landmarks were not detected.")
    elif not body_detected:
        reasons.append("Body landmarks were not detected.")

    if blur_score < 70:
        reasons.append("Image appears too blurry.")
        failed = True
    elif blur_score < 120:
        reasons.append("Image sharpness is borderline.")

    if exposure_score < 45 or exposure_score > 210:
        reasons.append("Exposure is outside the safe range.")
        failed = True
    elif exposure_score < 70 or exposure_score > 180:
        reasons.append("Exposure is usable but not ideal.")

    if failed:
        status: Literal["pass", "warn", "fail"] = "fail"
    elif reasons:
        status = "warn"
    else:
        status = "pass"

    return PhotoQcReport(
        framing_label=framing_label,
        metrics={
            "face_detected": face_detected,
            "body_landmarks_detected": body_detected,
            "blur_score": round(blur_score, 2),
            "exposure_score": round(exposure_score, 2),
            "framing_label": framing_label,
        },
        reasons=reasons,
        status=status,
    )


def _media_type_for_filename(filename: str, fallback: str | None) -> str:
    guessed_media_type, _ = mimetypes.guess_type(filename)
    return fallback or guessed_media_type or "application/octet-stream"


def _extension_for_filename(filename: str, media_type: str) -> str:
    suffix = Path(filename).suffix.lower()

    if suffix:
        return suffix
    if media_type == "image/jpeg":
        return ".jpg"
    if media_type == "image/png":
        return ".png"
    if media_type == "image/webp":
        return ".webp"
    return ".bin"


def ingest_photoset(
    session: Session,
    uploads: list[IncomingPhotoUpload],
    *,
    character_label: str | None = None,
) -> Asset:
    if not uploads:
        raise ValueError("At least one photo is required.")

    actor_id = get_system_actor_id(session)
    roots = _resolve_photo_roots(resolve_storage_layout())
    face_model_path = _download_model_if_needed(
        FACE_LANDMARKER_URL, roots.media_pipe_root / "face_landmarker.task"
    )
    pose_model_path = _download_model_if_needed(
        POSE_LANDMARKER_URL, roots.media_pipe_root / "pose_landmarker_lite.task"
    )
    face_landmarker = _create_face_landmarker(face_model_path)
    pose_landmarker = _create_pose_landmarker(pose_model_path)

    try:
        photoset_asset = Asset(
            asset_type="photoset",
            status="prepared",
            created_by_actor_id=actor_id,
            current_owner_actor_id=actor_id,
        )
        session.add(photoset_asset)
        session.flush()
        _history_event(
            session,
            actor_id,
            asset_id=photoset_asset.id,
            details={
                "character_label": character_label,
                "entry_count": len(uploads),
                "status": "prepared",
            },
            event_type="photoset.created",
        )

        for ordinal, upload in enumerate(uploads):
            media_type = _media_type_for_filename(upload.filename, upload.media_type)
            file_extension = _extension_for_filename(upload.filename, media_type)

            photo_asset = Asset(
                asset_type="photo",
                status="draft",
                parent_asset_id=photoset_asset.id,
                source_asset_id=photoset_asset.id,
                created_by_actor_id=actor_id,
                current_owner_actor_id=actor_id,
            )
            session.add(photo_asset)
            session.flush()

            photo_root = Path(str(photoset_asset.public_id)) / str(photo_asset.public_id)
            original_path = roots.uploaded_root / photo_root / f"original{file_extension}"
            normalized_path = roots.prepared_root / photo_root / "normalized.png"
            thumbnail_path = roots.prepared_root / photo_root / "thumbnail.png"

            _write_bytes(original_path, upload.content)
            original_storage_object = _storage_object(
                session,
                actor_id,
                asset_id=photo_asset.id,
                byte_size=len(upload.content),
                media_type=media_type,
                object_type="uploaded-photo-original",
                payload=upload.content,
                root_class=roots.root_class,
                storage_path=original_path,
            )

            try:
                normalized_image = _normalized_image(upload.content)
            except UnidentifiedImageError as exc:  # pragma: no cover - exercised via API
                raise ValueError(f"Unsupported image upload: {upload.filename}") from exc

            normalized_bytes = _png_bytes(normalized_image)
            thumbnail_bytes = _thumbnail_bytes(normalized_image)
            qc_report = _qc_report(normalized_image, face_landmarker, pose_landmarker)

            _write_bytes(normalized_path, normalized_bytes)
            _write_bytes(thumbnail_path, thumbnail_bytes)

            normalized_storage_object = _storage_object(
                session,
                actor_id,
                asset_id=photo_asset.id,
                byte_size=len(normalized_bytes),
                media_type="image/png",
                object_type="uploaded-photo-normalized",
                payload=normalized_bytes,
                root_class=roots.root_class,
                storage_path=normalized_path,
            )
            thumbnail_storage_object = _storage_object(
                session,
                actor_id,
                asset_id=photo_asset.id,
                byte_size=len(thumbnail_bytes),
                media_type="image/png",
                object_type="uploaded-photo-thumbnail",
                payload=thumbnail_bytes,
                root_class=roots.root_class,
                storage_path=thumbnail_path,
            )

            photo_asset.status = qc_report.status
            session.add(
                PhotosetEntry(
                    photoset_asset_id=photoset_asset.id,
                    photo_asset_id=photo_asset.id,
                    ordinal=ordinal,
                    original_filename=upload.filename,
                    qc_status=qc_report.status,
                    qc_metrics=qc_report.metrics,
                    qc_reasons=qc_report.reasons,
                    framing_label=qc_report.framing_label,
                    original_storage_object_id=original_storage_object.id,
                    normalized_storage_object_id=normalized_storage_object.id,
                    thumbnail_storage_object_id=thumbnail_storage_object.id,
                )
            )
            _history_event(
                session,
                actor_id,
                asset_id=photo_asset.id,
                details={
                    "framing_label": qc_report.framing_label,
                    "qc_reasons": qc_report.reasons,
                    "qc_status": qc_report.status,
                },
                event_type="photo.prepared",
            )

        session.flush()
        return photoset_asset
    finally:
        face_landmarker.close()
        pose_landmarker.close()


def _photoset_entry_query() -> Select[tuple[PhotosetEntry]]:
    return select(PhotosetEntry).order_by(PhotosetEntry.ordinal.asc())


def get_photoset_asset(session: Session, public_id: uuid.UUID) -> Asset | None:
    return session.execute(
        _asset_query().where(Asset.public_id == public_id, Asset.asset_type == "photoset")
    ).scalar_one_or_none()


def _storage_object_by_id(session: Session, storage_object_id: uuid.UUID) -> StorageObject:
    storage_object = session.get(StorageObject, storage_object_id)
    if storage_object is None:
        raise LookupError("Storage object not found.")
    return storage_object


def _photo_asset_by_id(session: Session, asset_id: uuid.UUID) -> Asset:
    photo_asset = session.get(Asset, asset_id)
    if photo_asset is None:
        raise LookupError("Photo asset not found.")
    return photo_asset


def _artifact_url(
    api_base_url: str,
    *,
    entry_public_id: uuid.UUID,
    photoset_public_id: uuid.UUID,
    variant: str,
) -> str:
    return (
        f"{api_base_url}/api/v1/photosets/{photoset_public_id}/entries/"
        f"{entry_public_id}/artifacts/{variant}"
    )


def serialize_photoset(
    session: Session,
    photoset_asset: Asset,
    *,
    api_base_url: str,
) -> dict[str, object]:
    entries = session.execute(
        _photoset_entry_query().where(PhotosetEntry.photoset_asset_id == photoset_asset.id)
    ).scalars().all()

    serialized_entries: list[dict[str, object]] = []
    accepted_entry_count = 0

    for entry in entries:
        photo_asset = _photo_asset_by_id(session, entry.photo_asset_id)
        original_storage_object = _storage_object_by_id(session, entry.original_storage_object_id)
        normalized_storage_object = _storage_object_by_id(
            session, entry.normalized_storage_object_id
        )
        thumbnail_storage_object = _storage_object_by_id(session, entry.thumbnail_storage_object_id)
        accepted_for_character_use = is_qc_status_accepted_for_character_use(entry.qc_status)
        if accepted_for_character_use:
            accepted_entry_count += 1

        serialized_entries.append(
            {
                "accepted_for_character_use": accepted_for_character_use,
                "public_id": entry.public_id,
                "photo_asset_public_id": photo_asset.public_id,
                "original_filename": entry.original_filename,
                "qc_status": entry.qc_status,
                "qc_reasons": entry.qc_reasons,
                "qc_metrics": entry.qc_metrics,
                "original_storage_object_public_id": original_storage_object.public_id,
                "normalized_storage_object_public_id": normalized_storage_object.public_id,
                "thumbnail_storage_object_public_id": thumbnail_storage_object.public_id,
                "artifact_urls": {
                    "original": _artifact_url(
                        api_base_url,
                        entry_public_id=entry.public_id,
                        photoset_public_id=photoset_asset.public_id,
                        variant="original",
                    ),
                    "normalized": _artifact_url(
                        api_base_url,
                        entry_public_id=entry.public_id,
                        photoset_public_id=photoset_asset.public_id,
                        variant="normalized",
                    ),
                    "thumbnail": _artifact_url(
                        api_base_url,
                        entry_public_id=entry.public_id,
                        photoset_public_id=photoset_asset.public_id,
                        variant="thumbnail",
                    ),
                },
            }
        )

    return {
        "accepted_entry_count": accepted_entry_count,
        "asset_type": photoset_asset.asset_type,
        "entry_count": len(serialized_entries),
        "entries": serialized_entries,
        "public_id": photoset_asset.public_id,
        "rejected_entry_count": len(serialized_entries) - accepted_entry_count,
        "status": photoset_asset.status,
    }


def get_photoset_payload(
    session: Session,
    photoset_public_id: uuid.UUID,
    *,
    api_base_url: str,
) -> dict[str, object] | None:
    photoset_asset = get_photoset_asset(session, photoset_public_id)

    if photoset_asset is None:
        return None

    return serialize_photoset(session, photoset_asset, api_base_url=api_base_url)


def get_artifact_storage_object(
    session: Session,
    photoset_public_id: uuid.UUID,
    entry_public_id: uuid.UUID,
    variant: Literal["original", "normalized", "thumbnail"],
) -> StorageObject | None:
    photoset_asset = get_photoset_asset(session, photoset_public_id)

    if photoset_asset is None:
        return None

    entry = session.execute(
        _photoset_entry_query().where(
            PhotosetEntry.photoset_asset_id == photoset_asset.id,
            PhotosetEntry.public_id == entry_public_id,
        )
    ).scalar_one_or_none()

    if entry is None:
        return None

    storage_object_id = {
        "original": entry.original_storage_object_id,
        "normalized": entry.normalized_storage_object_id,
        "thumbnail": entry.thumbnail_storage_object_id,
    }[variant]

    return _storage_object_by_id(session, storage_object_id)
