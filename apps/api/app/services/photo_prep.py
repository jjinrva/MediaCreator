from __future__ import annotations

import hashlib
import io
import json
import mimetypes
import shutil
import urllib.request
import uuid
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal, cast

import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from PIL import Image, ImageEnhance, ImageOps, UnidentifiedImageError
from rembg import remove
from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.models.asset import Asset
from app.models.history_event import HistoryEvent
from app.models.job import Job
from app.models.photoset_entry import PhotosetEntry
from app.models.storage_object import StorageObject
from app.services.jobs import (
    PhotosetIngestJobPayload,
    advance_job_progress,
    complete_job,
    enqueue_job,
    fail_job,
    get_system_actor_id,
    update_job_payload,
)
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
ALLOWED_IMAGE_MEDIA_TYPES = frozenset({"image/jpeg", "image/png", "image/webp"})
MAX_UPLOAD_FILE_COUNT = 5000
MAX_UPLOAD_FILE_SIZE_BYTES = 20 * 1024 * 1024
UPLOAD_WRITE_CHUNK_SIZE_BYTES = 1024 * 1024
MIN_IMAGE_WIDTH = 512
MIN_IMAGE_HEIGHT = 512
MIN_BLUR_FOR_LORA = 120.0
MIN_BLUR_FOR_BODY = 55.0
MIN_EXPOSURE_FOR_LORA = 70.0
MAX_EXPOSURE_FOR_LORA = 180.0
MIN_EXPOSURE_FOR_BODY = 45.0
MAX_EXPOSURE_FOR_BODY = 210.0
PHOTOSET_DERIVATIVE_MANIFEST_VERSION = "photoset-derivatives-v1"
LORA_DATASET_SEED_MANIFEST_VERSION = "lora-dataset-seed-v1"
LORA_CAPTION_SEED_VERSION = "caption-seed-v1"
BODY_SEGMENTATION_PROVIDER = "rembg"
BODY_SEGMENTATION_MODEL = "u2net"


def _default_bucket_counts() -> dict[str, int]:
    return {
        "lora_only": 0,
        "body_only": 0,
        "both": 0,
        "rejected": 0,
    }


@dataclass(frozen=True)
class IncomingPhotoUpload:
    byte_size: int
    filename: str
    media_type: str | None
    staged_path: Path


@dataclass(frozen=True)
class PhotoQcReport:
    framing_label: str
    metrics: dict[str, object]
    reasons: list[str]
    status: Literal["pass", "warn", "fail"]
    bucket: Literal["lora_only", "body_only", "both", "rejected"] = "rejected"
    usable_for_lora: bool = False
    usable_for_body: bool = False
    reason_codes: list[str] = field(default_factory=list)
    reason_messages: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class PhotosetIngestResult:
    ingest_job: Job
    photoset_asset: Asset


@dataclass(frozen=True)
class PhotoStorageRoots:
    media_pipe_root: Path
    prepared_root: Path
    root_class: str
    uploaded_root: Path


def is_qc_status_accepted_for_character_use(qc_status: str) -> bool:
    return qc_status in ACCEPTED_QC_STATUSES


def is_bucket_accepted_for_character_use(bucket: str) -> bool:
    return bucket in {"lora_only", "body_only", "both"}


def is_bucket_body_qualified(bucket: str) -> bool:
    return bucket in {"body_only", "both"}


def is_bucket_lora_qualified(bucket: str) -> bool:
    return bucket in {"lora_only", "both"}


def resolve_upload_media_type(filename: str, fallback: str | None) -> str:
    return _media_type_for_filename(filename, fallback)


def extension_for_upload_filename(filename: str, media_type: str) -> str:
    return _extension_for_filename(filename, media_type)


def create_upload_staging_root() -> Path:
    staging_root = resolve_storage_layout().scratch_root / "photoset-staging" / str(uuid.uuid4())
    staging_root.mkdir(parents=True, exist_ok=True)
    return staging_root


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


def _has_transparency(image: Image.Image) -> bool:
    if image.mode != "RGBA":
        return False
    alpha_channel = image.getchannel("A")
    extrema = alpha_channel.getextrema()
    if not isinstance(extrema, tuple):
        return False
    alpha_min, alpha_max = cast(tuple[int, int], extrema)
    return alpha_min < 255 or alpha_max < 255


def _body_derivative_artifact(image: Image.Image) -> tuple[bytes, dict[str, object]]:
    background_removed_bytes = remove(_png_bytes(image.convert("RGBA")))
    with Image.open(io.BytesIO(background_removed_bytes)) as loaded_image:
        alpha_masked_image = loaded_image.convert("RGBA")

    metadata = {
        "alpha_present": _has_transparency(alpha_masked_image),
        "height": alpha_masked_image.height,
        "mode": alpha_masked_image.mode,
        "provider": BODY_SEGMENTATION_PROVIDER,
        "segmentation_model": BODY_SEGMENTATION_MODEL,
        "width": alpha_masked_image.width,
    }
    return _png_bytes(alpha_masked_image), metadata


def _lora_derivative_artifact(image: Image.Image) -> tuple[bytes, dict[str, object]]:
    image_array = np.asarray(image.convert("RGB"), dtype=np.float32)
    channel_means = image_array.mean(axis=(0, 1))
    target_mean = float(channel_means.mean())
    white_balance_gains = np.clip(target_mean / np.maximum(channel_means, 1.0), 0.92, 1.08)
    white_balanced = np.clip(image_array * white_balance_gains.reshape(1, 1, 3), 0, 255).astype(
        np.uint8
    )

    balanced_image = Image.fromarray(white_balanced, mode="RGB")
    mean_luminance = float(white_balanced.mean())
    brightness_gain = min(1.05, max(0.95, 112.0 / max(mean_luminance, 1.0)))
    lora_image = ImageEnhance.Brightness(balanced_image).enhance(brightness_gain)
    contrast_gain = 1.04
    lora_image = ImageEnhance.Contrast(lora_image).enhance(contrast_gain)

    metadata = {
        "brightness_gain": round(brightness_gain, 4),
        "contrast_gain": round(contrast_gain, 4),
        "height": lora_image.height,
        "white_balance_gains": [round(float(gain), 4) for gain in white_balance_gains],
        "width": lora_image.width,
    }
    return _png_bytes(lora_image), metadata


def _manifest_root(
    layout: StorageLayout,
    *,
    manifest_kind: Literal["photoset", "lora"],
) -> tuple[Path, str]:
    if layout.nas_available:
        root = (
            layout.prepared_images_root / "manifests"
            if manifest_kind == "photoset"
            else layout.loras_root / "manifests"
        )
        root_class = "nas"
    else:
        root = (
            layout.scratch_root / "photos" / "prepared" / "manifests"
            if manifest_kind == "photoset"
            else layout.scratch_root / "loras" / "manifests"
        )
        root_class = "scratch"

    root.mkdir(parents=True, exist_ok=True)
    return root, root_class


def _persist_manifest_storage_object(
    session: Session,
    actor_id: uuid.UUID,
    *,
    manifest: dict[str, object],
    object_type: str,
    photoset_asset_id: uuid.UUID,
    root_class: str,
    storage_path: Path,
) -> StorageObject:
    payload = json.dumps(manifest, indent=2, sort_keys=True).encode("utf-8")
    _write_bytes(storage_path, payload)
    return _storage_object(
        session,
        actor_id,
        asset_id=photoset_asset_id,
        byte_size=len(payload),
        media_type="application/json",
        object_type=object_type,
        payload=payload,
        root_class=root_class,
        storage_path=storage_path,
    )


def _lora_caption_seed(
    character_label: str,
    *,
    bucket: str,
    framing_label: str,
    usable_for_body: bool,
) -> dict[str, object]:
    tags = [
        character_label,
        "single person",
        f"bucket {bucket.replace('_', ' ')}",
        framing_label.replace("-", " "),
    ]
    if usable_for_body:
        tags.append("body reference")

    return {
        "seed_text": ", ".join(tags),
        "tags": tags,
        "version": LORA_CAPTION_SEED_VERSION,
    }


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


def _occlusion_label(*, face_detected: bool, body_detected: bool) -> str:
    if face_detected and body_detected:
        return "clear"
    if body_detected:
        return "face_not_visible"
    if face_detected:
        return "body_not_visible"
    return "unknown"


def _qc_metrics(
    *,
    body_detected: bool,
    blur_score: float,
    exposure_score: float,
    face_detected: bool,
    framing_label: str,
    occlusion_label: str,
    resolution_ok: bool,
) -> dict[str, object]:
    person_detected = face_detected or body_detected
    blur_ok_for_lora = blur_score >= MIN_BLUR_FOR_LORA
    blur_ok_for_body = blur_score >= MIN_BLUR_FOR_BODY
    exposure_ok_for_lora = MIN_EXPOSURE_FOR_LORA <= exposure_score <= MAX_EXPOSURE_FOR_LORA
    exposure_ok_for_body = MIN_EXPOSURE_FOR_BODY <= exposure_score <= MAX_EXPOSURE_FOR_BODY

    return {
        "has_person": person_detected,
        "person_detected": person_detected,
        "face_detected": face_detected,
        "body_detected": body_detected,
        "body_landmarks_detected": body_detected,
        "blur_score": round(blur_score, 2),
        "blur_ok_for_lora": blur_ok_for_lora,
        "blur_ok_for_body": blur_ok_for_body,
        "exposure_score": round(exposure_score, 2),
        "exposure_ok_for_lora": exposure_ok_for_lora,
        "exposure_ok_for_body": exposure_ok_for_body,
        "framing_label": framing_label,
        "occlusion_label": occlusion_label,
        "resolution_ok": resolution_ok,
    }


def _normalized_character_label(character_label: str | None) -> str:
    if character_label is None:
        raise ValueError("Character label is required.")
    normalized = character_label.strip()
    if not normalized:
        raise ValueError("Character label is required.")
    return normalized


def _job_progress_percent(*, processed_files: int, total_files: int, stage_offset: int) -> int:
    if total_files <= 0:
        return 0
    base = int((processed_files / total_files) * 80)
    return min(99, base + stage_offset)


def _status_from_bucket(
    *,
    bucket: Literal["lora_only", "body_only", "both", "rejected"],
    reason_codes: list[str],
) -> Literal["pass", "warn", "fail"]:
    if bucket == "rejected":
        return "fail"
    if reason_codes:
        return "warn"
    return "pass"


def _coerce_qc_report(report: PhotoQcReport) -> PhotoQcReport:
    reason_messages = report.reason_messages or report.reasons
    reason_codes = list(report.reason_codes)
    bucket = report.bucket
    usable_for_lora = report.usable_for_lora
    usable_for_body = report.usable_for_body

    if not reason_codes and bucket == "rejected" and report.status in ACCEPTED_QC_STATUSES:
        metrics = report.metrics
        face_detected = bool(metrics.get("face_detected"))
        body_detected = bool(
            metrics.get("body_detected", metrics.get("body_landmarks_detected", False))
        )
        if face_detected and body_detected:
            bucket = "both"
            usable_for_lora = True
            usable_for_body = True
        elif face_detected:
            bucket = "lora_only"
            usable_for_lora = True
        elif body_detected:
            bucket = "body_only"
            usable_for_body = True

    return PhotoQcReport(
        framing_label=report.framing_label,
        metrics=report.metrics,
        reasons=reason_messages,
        status=report.status,
        bucket=bucket,
        usable_for_lora=usable_for_lora,
        usable_for_body=usable_for_body,
        reason_codes=reason_codes,
        reason_messages=reason_messages,
    )


def _qc_report_from_signals(
    *,
    face_detected: bool,
    body_detected: bool,
    blur_score: float,
    exposure_score: float,
    framing_label: str,
    resolution_ok: bool,
) -> PhotoQcReport:
    occlusion_label = _occlusion_label(face_detected=face_detected, body_detected=body_detected)
    metrics = _qc_metrics(
        body_detected=body_detected,
        blur_score=blur_score,
        exposure_score=exposure_score,
        face_detected=face_detected,
        framing_label=framing_label,
        occlusion_label=occlusion_label,
        resolution_ok=resolution_ok,
    )
    person_detected = bool(metrics["person_detected"])

    if not person_detected:
        return PhotoQcReport(
            framing_label=framing_label,
            metrics=metrics,
            reasons=["No person was detected in the image."],
            status="fail",
            bucket="rejected",
            usable_for_lora=False,
            usable_for_body=False,
            reason_codes=["no_person_detected"],
            reason_messages=["No person was detected in the image."],
        )

    lora_failures: list[tuple[str, str]] = []
    body_failures: list[tuple[str, str]] = []
    warning_messages: list[str] = []
    warning_codes: list[str] = []

    if not resolution_ok:
        lora_failures.append(
            ("resolution_too_low_for_lora", "Image resolution is too low for LoRA training.")
        )
        body_failures.append(
            ("resolution_too_low_for_body", "Image resolution is too low for body modeling.")
        )

    if not face_detected:
        lora_failures.append(
            ("face_required_for_lora", "Face evidence was not detected for LoRA training.")
        )

    if not body_detected:
        body_failures.append(
            ("body_evidence_missing", "Body evidence is too weak for body modeling.")
        )

    if not bool(metrics["blur_ok_for_lora"]):
        lora_failures.append(
            ("blur_below_lora_threshold", "Image is too blurry for LoRA training.")
        )
    elif blur_score < (MIN_BLUR_FOR_LORA + 25):
        warning_codes.append("lora_blur_borderline")
        warning_messages.append("Image sharpness is borderline for LoRA training.")

    if not bool(metrics["blur_ok_for_body"]):
        body_failures.append(
            ("blur_below_body_threshold", "Image is too blurry for body modeling.")
        )
    elif blur_score < (MIN_BLUR_FOR_BODY + 15):
        warning_codes.append("body_blur_borderline")
        warning_messages.append(
            "Image sharpness is borderline but still acceptable for body modeling."
        )

    if not bool(metrics["exposure_ok_for_lora"]):
        lora_failures.append(
            ("exposure_out_of_lora_range", "Exposure is outside the LoRA training range.")
        )
    elif (
        exposure_score < (MIN_EXPOSURE_FOR_LORA + 10)
        or exposure_score > (MAX_EXPOSURE_FOR_LORA - 10)
    ):
        warning_codes.append("lora_exposure_borderline")
        warning_messages.append("Exposure is borderline for LoRA training.")

    if not bool(metrics["exposure_ok_for_body"]):
        body_failures.append(
            ("exposure_out_of_body_range", "Exposure is outside the body modeling range.")
        )
    elif (
        exposure_score < (MIN_EXPOSURE_FOR_BODY + 10)
        or exposure_score > (MAX_EXPOSURE_FOR_BODY - 10)
    ):
        warning_codes.append("body_exposure_borderline")
        warning_messages.append(
            "Exposure is borderline but still acceptable for body modeling."
        )

    if body_detected and framing_label == "head-closeup":
        body_failures.append(
            ("body_framing_insufficient", "Framing is too tight for body modeling.")
        )

    usable_for_lora = not lora_failures
    usable_for_body = not body_failures

    if usable_for_lora and usable_for_body:
        bucket: Literal["lora_only", "body_only", "both", "rejected"] = "both"
        reason_codes = warning_codes
        reason_messages = warning_messages
    elif usable_for_lora:
        bucket = "lora_only"
        reason_codes = [code for code, _ in body_failures] + warning_codes
        reason_messages = [message for _, message in body_failures] + warning_messages
    elif usable_for_body:
        bucket = "body_only"
        reason_codes = [code for code, _ in lora_failures] + warning_codes
        reason_messages = [message for _, message in lora_failures] + warning_messages
    else:
        bucket = "rejected"
        reason_codes = [code for code, _ in lora_failures + body_failures] + warning_codes
        reason_messages = [
            message for _, message in lora_failures + body_failures
        ] + warning_messages

    return PhotoQcReport(
        framing_label=framing_label,
        metrics=metrics,
        reasons=reason_messages,
        status=_status_from_bucket(bucket=bucket, reason_codes=reason_codes),
        bucket=bucket,
        usable_for_lora=usable_for_lora,
        usable_for_body=usable_for_body,
        reason_codes=reason_codes,
        reason_messages=reason_messages,
    )


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
    resolution_ok = image.width >= MIN_IMAGE_WIDTH and image.height >= MIN_IMAGE_HEIGHT
    return _qc_report_from_signals(
        face_detected=face_detected,
        body_detected=body_detected,
        blur_score=blur_score,
        exposure_score=exposure_score,
        framing_label=framing_label,
        resolution_ok=resolution_ok,
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
) -> PhotosetIngestResult:
    if not uploads:
        raise ValueError("At least one photo is required.")
    if len(uploads) > MAX_UPLOAD_FILE_COUNT:
        raise ValueError(f"A photoset may contain at most {MAX_UPLOAD_FILE_COUNT} files.")

    normalized_label = _normalized_character_label(character_label)
    actor_id = get_system_actor_id(session)
    photoset_asset = Asset(
        asset_type="photoset",
        status="queued",
        created_by_actor_id=actor_id,
        current_owner_actor_id=actor_id,
    )
    session.add(photoset_asset)
    session.flush()
    ingest_job = enqueue_job(
        session,
        actor_id,
        {
            "kind": "photoset-ingest",
            "character_label": normalized_label,
            "staged_uploads": [
                {
                    "byte_size": upload.byte_size,
                    "filename": upload.filename,
                    "media_type": _media_type_for_filename(upload.filename, upload.media_type),
                    "staged_path": str(upload.staged_path),
                }
                for upload in uploads
            ],
            "total_files": len(uploads),
            "processed_files": 0,
            "bucket_counts": _default_bucket_counts(),
            "photoset_public_id": photoset_asset.public_id,
        },
        output_asset_id=photoset_asset.id,
    )
    _history_event(
        session,
        actor_id,
        asset_id=photoset_asset.id,
        details={
            "character_label": normalized_label,
            "entry_count": len(uploads),
            "ingest_job_public_id": str(ingest_job.public_id),
            "status": "queued",
        },
        event_type="photoset.created",
    )
    return PhotosetIngestResult(
        ingest_job=ingest_job,
        photoset_asset=photoset_asset,
    )


def _cleanup_staged_uploads(uploads: Sequence[IncomingPhotoUpload]) -> None:
    for staged_root in {upload.staged_path.parent for upload in uploads}:
        shutil.rmtree(staged_root, ignore_errors=True)


def _uploads_from_job_payload(payload: PhotosetIngestJobPayload) -> list[IncomingPhotoUpload]:
    return [
        IncomingPhotoUpload(
            byte_size=staged_upload.byte_size,
            filename=staged_upload.filename,
            media_type=staged_upload.media_type,
            staged_path=Path(staged_upload.staged_path),
        )
        for staged_upload in payload.staged_uploads
    ]


def _run_photoset_ingest_pipeline(
    session: Session,
    *,
    photoset_asset: Asset,
    ingest_job: Job,
    normalized_label: str,
    uploads: Sequence[IncomingPhotoUpload],
) -> None:
    actor_id = get_system_actor_id(session)
    layout = resolve_storage_layout()
    roots = _resolve_photo_roots(layout)
    face_model_path = _download_model_if_needed(
        FACE_LANDMARKER_URL, roots.media_pipe_root / "face_landmarker.task"
    )
    pose_model_path = _download_model_if_needed(
        POSE_LANDMARKER_URL, roots.media_pipe_root / "pose_landmarker_lite.task"
    )
    face_landmarker = _create_face_landmarker(face_model_path)
    pose_landmarker = _create_pose_landmarker(pose_model_path)
    bucket_counts = _default_bucket_counts()
    derivative_manifest_entries: list[dict[str, object]] = []
    lora_manifest_entries: list[dict[str, object]] = []

    try:
        photoset_asset.status = "ingesting"
        session.flush()
        advance_job_progress(
            session,
            actor_id,
            ingest_job,
            step_name="upload_received",
            progress_percent=12,
        )
        update_job_payload(
            session,
            ingest_job,
            processed_files=0,
            bucket_counts=dict(bucket_counts),
        )

        for ordinal, upload in enumerate(uploads):
            media_type = _media_type_for_filename(upload.filename, upload.media_type)
            file_extension = _extension_for_filename(upload.filename, media_type)
            original_bytes = upload.staged_path.read_bytes()
            processed_files = ordinal + 1

            advance_job_progress(
                session,
                actor_id,
                ingest_job,
                step_name="normalizing",
                progress_percent=_job_progress_percent(
                    processed_files=ordinal,
                    total_files=len(uploads),
                    stage_offset=15,
                ),
            )

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
            body_derivative_path = roots.prepared_root / photo_root / "body-alpha.png"
            lora_derivative_path = roots.prepared_root / photo_root / "lora-normalized.png"

            _write_bytes(original_path, original_bytes)
            original_storage_object = _storage_object(
                session,
                actor_id,
                asset_id=photo_asset.id,
                byte_size=upload.byte_size,
                media_type=media_type,
                object_type="uploaded-photo-original",
                payload=original_bytes,
                root_class=roots.root_class,
                storage_path=original_path,
            )

            try:
                normalized_image = _normalized_image(original_bytes)
            except UnidentifiedImageError as exc:  # pragma: no cover - exercised via API
                raise ValueError(f"Unsupported image upload: {upload.filename}") from exc

            advance_job_progress(
                session,
                actor_id,
                ingest_job,
                step_name="person_check",
                progress_percent=_job_progress_percent(
                    processed_files=ordinal,
                    total_files=len(uploads),
                    stage_offset=20,
                ),
            )

            normalized_bytes = _png_bytes(normalized_image)
            thumbnail_bytes = _thumbnail_bytes(normalized_image)
            advance_job_progress(
                session,
                actor_id,
                ingest_job,
                step_name="qc_metrics",
                progress_percent=_job_progress_percent(
                    processed_files=ordinal,
                    total_files=len(uploads),
                    stage_offset=25,
                ),
            )
            qc_report = _coerce_qc_report(
                _qc_report(normalized_image, face_landmarker, pose_landmarker)
            )
            photoset_asset.status = "classifying"
            session.flush()
            advance_job_progress(
                session,
                actor_id,
                ingest_job,
                step_name="classification",
                progress_percent=_job_progress_percent(
                    processed_files=ordinal,
                    total_files=len(uploads),
                    stage_offset=30,
                ),
            )

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
            body_derivative_storage_object: StorageObject | None = None
            body_derivative_metadata: dict[str, object] | None = None
            if qc_report.bucket in {"body_only", "both"}:
                body_derivative_bytes, body_derivative_metadata = _body_derivative_artifact(
                    normalized_image
                )
                _write_bytes(body_derivative_path, body_derivative_bytes)
                body_derivative_storage_object = _storage_object(
                    session,
                    actor_id,
                    asset_id=photo_asset.id,
                    byte_size=len(body_derivative_bytes),
                    media_type="image/png",
                    object_type="uploaded-photo-body-derivative",
                    payload=body_derivative_bytes,
                    root_class=roots.root_class,
                    storage_path=body_derivative_path,
                )

            lora_derivative_storage_object: StorageObject | None = None
            lora_derivative_metadata: dict[str, object] | None = None
            if qc_report.bucket in {"lora_only", "both"}:
                lora_derivative_bytes, lora_derivative_metadata = _lora_derivative_artifact(
                    normalized_image
                )
                _write_bytes(lora_derivative_path, lora_derivative_bytes)
                lora_derivative_storage_object = _storage_object(
                    session,
                    actor_id,
                    asset_id=photo_asset.id,
                    byte_size=len(lora_derivative_bytes),
                    media_type="image/png",
                    object_type="uploaded-photo-lora-derivative",
                    payload=lora_derivative_bytes,
                    root_class=roots.root_class,
                    storage_path=lora_derivative_path,
                )

            advance_job_progress(
                session,
                actor_id,
                ingest_job,
                step_name="derivative_write",
                progress_percent=_job_progress_percent(
                    processed_files=ordinal,
                    total_files=len(uploads),
                    stage_offset=35,
                ),
            )

            photo_asset.status = qc_report.status
            bucket_counts[qc_report.bucket] += 1
            update_job_payload(
                session,
                ingest_job,
                processed_files=processed_files,
                bucket_counts=dict(bucket_counts),
            )
            photoset_entry = PhotosetEntry(
                photoset_asset_id=photoset_asset.id,
                photo_asset_id=photo_asset.id,
                ordinal=ordinal,
                original_filename=upload.filename,
                bucket=qc_report.bucket,
                qc_status=qc_report.status,
                qc_metrics=qc_report.metrics,
                qc_reasons=qc_report.reason_messages,
                usable_for_lora=qc_report.usable_for_lora,
                usable_for_body=qc_report.usable_for_body,
                reason_codes=qc_report.reason_codes,
                reason_messages=qc_report.reason_messages,
                framing_label=qc_report.framing_label,
                original_storage_object_id=original_storage_object.id,
                normalized_storage_object_id=normalized_storage_object.id,
                thumbnail_storage_object_id=thumbnail_storage_object.id,
                body_derivative_storage_object_id=(
                    body_derivative_storage_object.id
                    if body_derivative_storage_object is not None
                    else None
                ),
                lora_derivative_storage_object_id=(
                    lora_derivative_storage_object.id
                    if lora_derivative_storage_object is not None
                    else None
                ),
            )
            session.add(photoset_entry)
            session.flush()

            derivative_manifest_entries.append(
                {
                    "bucket": qc_report.bucket,
                    "entry_public_id": str(photoset_entry.public_id),
                    "framing_label": qc_report.framing_label,
                    "original_filename": upload.filename,
                    "photo_asset_public_id": str(photo_asset.public_id),
                    "qc_status": qc_report.status,
                    "reason_codes": qc_report.reason_codes,
                    "reason_messages": qc_report.reason_messages,
                    "source_photo_asset_id": str(photo_asset.id),
                    "storage": {
                        "body_derivative": (
                            {
                                "metadata": body_derivative_metadata,
                                "path": str(body_derivative_path),
                                "storage_object_public_id": str(
                                    body_derivative_storage_object.public_id
                                ),
                            }
                            if body_derivative_storage_object is not None
                            else None
                        ),
                        "lora_derivative": (
                            {
                                "metadata": lora_derivative_metadata,
                                "path": str(lora_derivative_path),
                                "storage_object_public_id": str(
                                    lora_derivative_storage_object.public_id
                                ),
                            }
                            if lora_derivative_storage_object is not None
                            else None
                        ),
                        "normalized": {
                            "path": str(normalized_path),
                            "storage_object_public_id": str(normalized_storage_object.public_id),
                        },
                        "original": {
                            "path": str(original_path),
                            "storage_object_public_id": str(original_storage_object.public_id),
                        },
                        "thumbnail": {
                            "path": str(thumbnail_path),
                            "storage_object_public_id": str(thumbnail_storage_object.public_id),
                        },
                    },
                    "usable_for_body": qc_report.usable_for_body,
                    "usable_for_lora": qc_report.usable_for_lora,
                }
            )
            if lora_derivative_storage_object is not None:
                lora_manifest_entries.append(
                    {
                        "bucket": qc_report.bucket,
                        "caption_seed": _lora_caption_seed(
                            normalized_label,
                            bucket=qc_report.bucket,
                            framing_label=qc_report.framing_label,
                            usable_for_body=qc_report.usable_for_body,
                        ),
                        "entry_public_id": str(photoset_entry.public_id),
                        "framing_label": qc_report.framing_label,
                        "lora_derivative_path": str(lora_derivative_path),
                        "lora_derivative_storage_object_public_id": str(
                            lora_derivative_storage_object.public_id
                        ),
                        "original_filename": upload.filename,
                        "photo_asset_public_id": str(photo_asset.public_id),
                        "reason_codes": qc_report.reason_codes,
                        "reason_messages": qc_report.reason_messages,
                    }
                )
            _history_event(
                session,
                actor_id,
                asset_id=photo_asset.id,
                details={
                    "bucket": qc_report.bucket,
                    "framing_label": qc_report.framing_label,
                    "qc_reasons": qc_report.reason_messages,
                    "reason_codes": qc_report.reason_codes,
                    "qc_status": qc_report.status,
                },
                event_type="photo.prepared",
            )

        photoset_manifest_root, photoset_manifest_root_class = _manifest_root(
            layout,
            manifest_kind="photoset",
        )
        photoset_manifest_path = (
            photoset_manifest_root / str(photoset_asset.public_id) / "photoset_derivatives.json"
        )
        photoset_manifest_storage_object = _persist_manifest_storage_object(
            session,
            actor_id,
            manifest={
                "character_label": normalized_label,
                "entry_count": len(derivative_manifest_entries),
                "entries": derivative_manifest_entries,
                "photoset_public_id": str(photoset_asset.public_id),
                "version": PHOTOSET_DERIVATIVE_MANIFEST_VERSION,
            },
            object_type="photoset-derivative-manifest",
            photoset_asset_id=photoset_asset.id,
            root_class=photoset_manifest_root_class,
            storage_path=photoset_manifest_path,
        )
        _history_event(
            session,
            actor_id,
            asset_id=photoset_asset.id,
            details={
                "entry_count": len(derivative_manifest_entries),
                "manifest_path": str(photoset_manifest_path),
                "manifest_storage_object_public_id": str(
                    photoset_manifest_storage_object.public_id
                ),
                "version": PHOTOSET_DERIVATIVE_MANIFEST_VERSION,
            },
            event_type="photoset.derivatives_manifested",
        )

        lora_manifest_root, lora_manifest_root_class = _manifest_root(
            layout,
            manifest_kind="lora",
        )
        lora_manifest_path = (
            lora_manifest_root / str(photoset_asset.public_id) / "dataset_manifest.json"
        )
        lora_manifest_storage_object = _persist_manifest_storage_object(
            session,
            actor_id,
            manifest={
                "character_label": normalized_label,
                "entry_count": len(lora_manifest_entries),
                "entries": lora_manifest_entries,
                "photoset_public_id": str(photoset_asset.public_id),
                "version": LORA_DATASET_SEED_MANIFEST_VERSION,
            },
            object_type="photoset-lora-dataset-manifest",
            photoset_asset_id=photoset_asset.id,
            root_class=lora_manifest_root_class,
            storage_path=lora_manifest_path,
        )
        _history_event(
            session,
            actor_id,
            asset_id=photoset_asset.id,
            details={
                "entry_count": len(lora_manifest_entries),
                "manifest_path": str(lora_manifest_path),
                "manifest_storage_object_public_id": str(lora_manifest_storage_object.public_id),
                "version": LORA_DATASET_SEED_MANIFEST_VERSION,
            },
            event_type="photoset.lora_manifested",
        )

        persisted_entries = session.execute(
            _photoset_entry_query().where(PhotosetEntry.photoset_asset_id == photoset_asset.id)
        ).scalars().all()
        if len(persisted_entries) != len(uploads):
            raise RuntimeError("Photoset ingest cannot complete before all entries are persisted.")

        photoset_asset.status = "prepared"
        session.flush()
        advance_job_progress(
            session,
            actor_id,
            ingest_job,
            step_name="complete",
            progress_percent=99,
        )
        complete_job(
            session,
            actor_id,
            ingest_job,
            output_asset_id=photoset_asset.id,
        )
        _history_event(
            session,
            actor_id,
            asset_id=photoset_asset.id,
            details={
                "accepted_entry_count": sum(
                    count for bucket, count in bucket_counts.items() if bucket != "rejected"
                ),
                "bucket_counts": dict(bucket_counts),
                "character_label": normalized_label,
                "ingest_job_public_id": str(ingest_job.public_id),
                "status": "prepared",
            },
            event_type="photoset.prepared",
        )
    finally:
        face_landmarker.close()
        pose_landmarker.close()


def execute_photoset_ingest_job(
    session: Session,
    job: Job,
    payload: PhotosetIngestJobPayload,
) -> None:
    actor_id = get_system_actor_id(session)
    photoset_asset = get_photoset_asset(session, payload.photoset_public_id)
    uploads = _uploads_from_job_payload(payload)

    try:
        if photoset_asset is None:
            raise LookupError("Photoset not found for queued ingest job.")
        _run_photoset_ingest_pipeline(
            session,
            photoset_asset=photoset_asset,
            ingest_job=job,
            normalized_label=payload.character_label,
            uploads=uploads,
        )
    except Exception as exc:
        if photoset_asset is not None:
            photoset_asset.status = "failed"
            session.flush()
        fail_job(session, actor_id, job, str(exc))
    finally:
        _cleanup_staged_uploads(uploads)


def _photoset_entry_query() -> Select[tuple[PhotosetEntry]]:
    return select(PhotosetEntry).order_by(PhotosetEntry.ordinal.asc())


def _photoset_history_query() -> Select[tuple[HistoryEvent]]:
    return select(HistoryEvent).order_by(HistoryEvent.created_at.asc())


def _job_query() -> Select[tuple[Job]]:
    return select(Job).order_by(Job.created_at.asc())


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


def _photoset_character_label(session: Session, photoset_asset_id: uuid.UUID) -> str | None:
    created_event = session.execute(
        _photoset_history_query().where(
            HistoryEvent.asset_id == photoset_asset_id,
            HistoryEvent.event_type == "photoset.created",
        )
    ).scalar_one_or_none()
    if created_event is None:
        return None
    character_label = created_event.details.get("character_label")
    if isinstance(character_label, str) and character_label.strip():
        return character_label
    return None


def _latest_photoset_ingest_job(session: Session, photoset_asset_id: uuid.UUID) -> Job | None:
    return session.execute(
        _job_query().where(
            Job.output_asset_id == photoset_asset_id,
            Job.job_type == "photoset-ingest",
        )
    ).scalar_one_or_none()


def _serialized_bucket_counts(entries: Sequence[PhotosetEntry]) -> dict[str, int]:
    bucket_counts = _default_bucket_counts()
    for entry in entries:
        if entry.bucket in bucket_counts:
            bucket_counts[entry.bucket] += 1
            continue
        if is_qc_status_accepted_for_character_use(entry.qc_status):
            bucket_counts["both"] += 1
        else:
            bucket_counts["rejected"] += 1
    return bucket_counts


def _accepted_for_character_use(entry: PhotosetEntry) -> bool:
    if entry.bucket:
        return is_bucket_accepted_for_character_use(entry.bucket)
    return is_qc_status_accepted_for_character_use(entry.qc_status)


def _serialized_ingest_job(job: Job | None) -> dict[str, object] | None:
    if job is None:
        return None
    total_files = job.payload.get("total_files")
    processed_files = job.payload.get("processed_files")
    bucket_counts = job.payload.get("bucket_counts")
    return {
        "job_public_id": job.public_id,
        "status": job.status,
        "step_name": job.step_name,
        "progress_percent": job.progress_percent,
        "total_files": total_files if isinstance(total_files, int) else None,
        "processed_files": processed_files if isinstance(processed_files, int) else None,
        "bucket_counts": bucket_counts if isinstance(bucket_counts, dict) else None,
    }


def _artifact_url(
    api_base_url: str,
    *,
    entry_public_id: uuid.UUID,
    photoset_public_id: uuid.UUID,
    variant: Literal["body", "lora", "normalized", "original", "thumbnail"],
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
    bucket_counts = _serialized_bucket_counts(entries)

    for entry in entries:
        photo_asset = _photo_asset_by_id(session, entry.photo_asset_id)
        original_storage_object = _storage_object_by_id(session, entry.original_storage_object_id)
        normalized_storage_object = _storage_object_by_id(
            session, entry.normalized_storage_object_id
        )
        thumbnail_storage_object = _storage_object_by_id(session, entry.thumbnail_storage_object_id)
        body_derivative_storage_object = (
            _storage_object_by_id(session, entry.body_derivative_storage_object_id)
            if entry.body_derivative_storage_object_id is not None
            else None
        )
        lora_derivative_storage_object = (
            _storage_object_by_id(session, entry.lora_derivative_storage_object_id)
            if entry.lora_derivative_storage_object_id is not None
            else None
        )
        accepted_for_character_use = _accepted_for_character_use(entry)
        if accepted_for_character_use:
            accepted_entry_count += 1

        serialized_entries.append(
            {
                "accepted_for_character_use": accepted_for_character_use,
                "public_id": entry.public_id,
                "photo_asset_public_id": photo_asset.public_id,
                "original_filename": entry.original_filename,
                "bucket": entry.bucket or ("both" if accepted_for_character_use else "rejected"),
                "qc_status": entry.qc_status,
                "qc_reasons": entry.qc_reasons,
                "reason_codes": entry.reason_codes,
                "reason_messages": entry.reason_messages,
                "qc_metrics": entry.qc_metrics,
                "usable_for_lora": entry.usable_for_lora,
                "usable_for_body": entry.usable_for_body,
                "original_storage_object_public_id": original_storage_object.public_id,
                "normalized_storage_object_public_id": normalized_storage_object.public_id,
                "thumbnail_storage_object_public_id": thumbnail_storage_object.public_id,
                "body_derivative_storage_object_public_id": (
                    body_derivative_storage_object.public_id
                    if body_derivative_storage_object is not None
                    else None
                ),
                "lora_derivative_storage_object_public_id": (
                    lora_derivative_storage_object.public_id
                    if lora_derivative_storage_object is not None
                    else None
                ),
                "artifact_urls": {
                    "body": (
                        _artifact_url(
                            api_base_url,
                            entry_public_id=entry.public_id,
                            photoset_public_id=photoset_asset.public_id,
                            variant="body",
                        )
                        if body_derivative_storage_object is not None
                        else None
                    ),
                    "lora": (
                        _artifact_url(
                            api_base_url,
                            entry_public_id=entry.public_id,
                            photoset_public_id=photoset_asset.public_id,
                            variant="lora",
                        )
                        if lora_derivative_storage_object is not None
                        else None
                    ),
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
        "bucket_counts": bucket_counts,
        "character_label": _photoset_character_label(session, photoset_asset.id),
        "entry_count": len(serialized_entries),
        "entries": serialized_entries,
        "ingest_job": _serialized_ingest_job(
            _latest_photoset_ingest_job(session, photoset_asset.id)
        ),
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
    variant: Literal["body", "lora", "normalized", "original", "thumbnail"],
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
        "body": entry.body_derivative_storage_object_id,
        "lora": entry.lora_derivative_storage_object_id,
        "original": entry.original_storage_object_id,
        "normalized": entry.normalized_storage_object_id,
        "thumbnail": entry.thumbnail_storage_object_id,
    }[variant]

    if storage_object_id is None:
        return None

    return _storage_object_by_id(session, storage_object_id)
