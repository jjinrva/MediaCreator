import json
from collections.abc import Callable, Generator
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Literal

from _pytest.monkeypatch import MonkeyPatch
from fastapi.testclient import TestClient
from PIL import Image
from sqlalchemy import create_engine, select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.session import get_db_session
from app.main import app
from app.models.history_event import HistoryEvent
from app.models.photoset_entry import PhotosetEntry
from app.models.storage_object import StorageObject
from app.services import photo_prep
from tests.db_test_utils import migrated_database
from tests.photoset_test_utils import upload_photoset_and_complete_ingest


def _session_factory(database_url: str) -> tuple[Engine, sessionmaker[Session]]:
    engine = create_engine(database_url, pool_pre_ping=True)
    return engine, sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def _override_db_session(
    session_factory: sessionmaker[Session],
) -> Callable[[], Generator[Session, None, None]]:
    def _dependency() -> Generator[Session, None, None]:
        session = session_factory()
        try:
            yield session
        finally:
            session.close()

    return _dependency


def _sample_image_bytes(filename: str) -> bytes:
    repo_root = Path(__file__).resolve().parents[3]
    return (repo_root / "docs" / "capture_guides" / "assets" / filename).read_bytes()


class _StubLandmarker:
    def close(self) -> None:
        return None


def _build_qc_report(
    bucket: Literal["lora_only", "body_only", "both", "rejected"],
    *,
    framing_label: str = "full-body",
    reason_codes: list[str] | None = None,
    reason_messages: list[str] | None = None,
) -> photo_prep.PhotoQcReport:
    if bucket == "rejected":
        usable_for_lora = False
        usable_for_body = False
        face_detected = False
        body_detected = False
        status: Literal["pass", "warn", "fail"] = "fail"
    elif bucket == "lora_only":
        usable_for_lora = True
        usable_for_body = False
        face_detected = True
        body_detected = False
        status = "warn" if reason_codes else "pass"
    elif bucket == "body_only":
        usable_for_lora = False
        usable_for_body = True
        face_detected = False
        body_detected = True
        status = "warn" if reason_codes else "pass"
    else:
        usable_for_lora = True
        usable_for_body = True
        face_detected = True
        body_detected = True
        status = "warn" if reason_codes else "pass"

    messages = reason_messages or []
    codes = reason_codes or []
    return photo_prep.PhotoQcReport(
        framing_label=framing_label,
        metrics={
            "has_person": face_detected or body_detected,
            "person_detected": face_detected or body_detected,
            "face_detected": face_detected,
            "body_detected": body_detected,
            "body_landmarks_detected": body_detected,
            "blur_score": 145.0,
            "blur_ok_for_lora": 145.0 >= photo_prep.MIN_BLUR_FOR_LORA,
            "blur_ok_for_body": 145.0 >= photo_prep.MIN_BLUR_FOR_BODY,
            "exposure_score": 100.0,
            "exposure_ok_for_lora": (
                photo_prep.MIN_EXPOSURE_FOR_LORA <= 100.0 <= photo_prep.MAX_EXPOSURE_FOR_LORA
            ),
            "exposure_ok_for_body": (
                photo_prep.MIN_EXPOSURE_FOR_BODY <= 100.0 <= photo_prep.MAX_EXPOSURE_FOR_BODY
            ),
            "framing_label": framing_label,
            "occlusion_label": "clear" if face_detected and body_detected else "face_not_visible",
            "resolution_ok": True,
        },
        reasons=messages,
        status=status,
        bucket=bucket,
        usable_for_lora=usable_for_lora,
        usable_for_body=usable_for_body,
        reason_codes=codes,
        reason_messages=messages,
    )


def _patch_deterministic_qc(
    monkeypatch: MonkeyPatch,
    reports: list[photo_prep.PhotoQcReport],
) -> None:
    queued_reports = list(reports)

    monkeypatch.setattr(
        photo_prep,
        "_download_model_if_needed",
        lambda url, destination: destination,
    )
    monkeypatch.setattr(photo_prep, "_create_face_landmarker", lambda model_path: _StubLandmarker())
    monkeypatch.setattr(photo_prep, "_create_pose_landmarker", lambda model_path: _StubLandmarker())
    monkeypatch.setattr(
        photo_prep,
        "_qc_report",
        lambda image, face_landmarker, pose_landmarker: queued_reports.pop(0),
    )


def _png_bytes(mode: str, size: tuple[int, int], color: tuple[int, ...]) -> bytes:
    buffer = BytesIO()
    Image.new(mode, size, color=color).save(buffer, format="PNG")
    return buffer.getvalue()


def _patch_derivative_artifacts(monkeypatch: MonkeyPatch) -> None:
    def _fake_body_derivative(image: Image.Image) -> tuple[bytes, dict[str, object]]:
        return (
            _png_bytes("RGBA", image.size, (90, 160, 210, 180)),
            {
                "alpha_present": True,
                "height": image.height,
                "mode": "RGBA",
                "provider": "rembg",
                "segmentation_model": "stub-u2net",
                "width": image.width,
            },
        )

    def _fake_lora_derivative(image: Image.Image) -> tuple[bytes, dict[str, object]]:
        return (
            _png_bytes("RGB", image.size, (140, 150, 160)),
            {
                "brightness_gain": 1.01,
                "contrast_gain": 1.04,
                "height": image.height,
                "white_balance_gains": [1.0, 1.01, 0.99],
                "width": image.width,
            },
        )

    monkeypatch.setattr(photo_prep, "_body_derivative_artifact", _fake_body_derivative)
    monkeypatch.setattr(photo_prep, "_lora_derivative_artifact", _fake_lora_derivative)


def test_ingest_writes_bucket_bound_derivatives_and_explicit_manifests(
    monkeypatch: MonkeyPatch,
) -> None:
    _patch_deterministic_qc(
        monkeypatch,
        [
            _build_qc_report(
                "body_only",
                reason_codes=["face_required_for_lora"],
                reason_messages=["Face evidence was not detected for LoRA training."],
            ),
            _build_qc_report("both"),
            _build_qc_report("lora_only", framing_label="head-closeup"),
            _build_qc_report(
                "rejected",
                framing_label="unknown",
                reason_codes=["no_person_detected"],
                reason_messages=["No person was detected in the image."],
            ),
        ],
    )
    _patch_derivative_artifacts(monkeypatch)

    with migrated_database("photo_derivatives") as database_url:
        engine, session_factory = _session_factory(database_url)
        app.dependency_overrides[get_db_session] = _override_db_session(session_factory)

        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            nas_root = temp_path / "nas"
            scratch_root = temp_path / "scratch"
            nas_root.mkdir()
            scratch_root.mkdir()

            monkeypatch.setenv("MEDIACREATOR_STORAGE_NAS_ROOT", str(nas_root))
            monkeypatch.setenv(
                "MEDIACREATOR_STORAGE_UPLOADED_PHOTOS_ROOT",
                str(nas_root / "photos" / "uploaded"),
            )
            monkeypatch.setenv(
                "MEDIACREATOR_STORAGE_PREPARED_IMAGES_ROOT",
                str(nas_root / "photos" / "prepared"),
            )
            monkeypatch.setenv(
                "MEDIACREATOR_STORAGE_LORAS_ROOT",
                str(nas_root / "models" / "loras"),
            )
            monkeypatch.setenv("MEDIACREATOR_STORAGE_SCRATCH_ROOT", str(scratch_root))

            upload_map = {
                "body.png": _sample_image_bytes("male_body_front.png"),
                "both.png": _sample_image_bytes("female_body_front.png"),
                "lora.png": _sample_image_bytes("female_head_front.png"),
                "reject.png": _sample_image_bytes("male_head_front.png"),
            }

            try:
                with TestClient(app) as client:
                    _, payload = upload_photoset_and_complete_ingest(
                        client,
                        session_factory,
                        data={"character_label": "Derivative Subject"},
                        files=[
                            ("photos", ("body.png", upload_map["body.png"], "image/png")),
                            ("photos", ("both.png", upload_map["both.png"], "image/png")),
                            ("photos", ("lora.png", upload_map["lora.png"], "image/png")),
                            ("photos", ("reject.png", upload_map["reject.png"], "image/png")),
                        ],
                    )
                    assert payload["bucket_counts"] == {
                        "body_only": 1,
                        "both": 1,
                        "lora_only": 1,
                        "rejected": 1,
                    }

                    entries_by_bucket = {entry["bucket"]: entry for entry in payload["entries"]}
                    assert entries_by_bucket["body_only"]["artifact_urls"]["body"] is not None
                    assert entries_by_bucket["body_only"]["artifact_urls"]["lora"] is None
                    assert entries_by_bucket["both"]["artifact_urls"]["body"] is not None
                    assert entries_by_bucket["both"]["artifact_urls"]["lora"] is not None
                    assert entries_by_bucket["lora_only"]["artifact_urls"]["body"] is None
                    assert entries_by_bucket["lora_only"]["artifact_urls"]["lora"] is not None
                    assert entries_by_bucket["rejected"]["artifact_urls"]["body"] is None
                    assert entries_by_bucket["rejected"]["artifact_urls"]["lora"] is None

                with session_factory() as session:
                    entries = session.scalars(
                        select(PhotosetEntry).order_by(PhotosetEntry.ordinal.asc())
                    ).all()
                    assert [entry.bucket for entry in entries] == [
                        "body_only",
                        "both",
                        "lora_only",
                        "rejected",
                    ]

                    original_paths_by_bucket: dict[str, Path] = {}
                    for entry in entries:
                        original_storage = session.get(
                            StorageObject, entry.original_storage_object_id
                        )
                        normalized_storage = session.get(
                            StorageObject, entry.normalized_storage_object_id
                        )
                        thumbnail_storage = session.get(
                            StorageObject, entry.thumbnail_storage_object_id
                        )
                        assert original_storage is not None
                        assert normalized_storage is not None
                        assert thumbnail_storage is not None
                        original_path = Path(original_storage.storage_path)
                        normalized_path = Path(normalized_storage.storage_path)
                        thumbnail_path = Path(thumbnail_storage.storage_path)
                        assert original_path.exists()
                        assert normalized_path.exists()
                        assert thumbnail_path.exists()
                        original_paths_by_bucket[entry.bucket] = original_path

                        if entry.bucket in {"body_only", "both"}:
                            assert entry.body_derivative_storage_object_id is not None
                            body_storage = session.get(
                                StorageObject, entry.body_derivative_storage_object_id
                            )
                            assert body_storage is not None
                            assert Path(body_storage.storage_path).exists()
                        else:
                            assert entry.body_derivative_storage_object_id is None

                        if entry.bucket in {"lora_only", "both"}:
                            assert entry.lora_derivative_storage_object_id is not None
                            lora_storage = session.get(
                                StorageObject, entry.lora_derivative_storage_object_id
                            )
                            assert lora_storage is not None
                            assert Path(lora_storage.storage_path).exists()
                        else:
                            assert entry.lora_derivative_storage_object_id is None

                    assert (
                        original_paths_by_bucket["body_only"].read_bytes()
                        == upload_map["body.png"]
                    )
                    assert original_paths_by_bucket["both"].read_bytes() == upload_map["both.png"]
                    assert (
                        original_paths_by_bucket["lora_only"].read_bytes()
                        == upload_map["lora.png"]
                    )
                    assert (
                        original_paths_by_bucket["rejected"].read_bytes()
                        == upload_map["reject.png"]
                    )

                    derivative_manifest_storage = session.scalar(
                        select(StorageObject).where(
                            StorageObject.object_type == "photoset-derivative-manifest"
                        )
                    )
                    lora_manifest_storage = session.scalar(
                        select(StorageObject).where(
                            StorageObject.object_type == "photoset-lora-dataset-manifest"
                        )
                    )
                    derivatives_history = session.scalar(
                        select(HistoryEvent).where(
                            HistoryEvent.event_type == "photoset.derivatives_manifested"
                        )
                    )
                    lora_history = session.scalar(
                        select(HistoryEvent).where(
                            HistoryEvent.event_type == "photoset.lora_manifested"
                        )
                    )

                    assert derivative_manifest_storage is not None
                    assert lora_manifest_storage is not None
                    assert derivatives_history is not None
                    assert lora_history is not None

                    derivative_manifest = json.loads(
                        Path(derivative_manifest_storage.storage_path).read_text(encoding="utf-8")
                    )
                    lora_manifest = json.loads(
                        Path(lora_manifest_storage.storage_path).read_text(encoding="utf-8")
                    )

                    assert derivative_manifest["version"] == "photoset-derivatives-v1"
                    assert derivative_manifest["entry_count"] == 4
                    manifest_entries_by_bucket = {
                        entry["bucket"]: entry for entry in derivative_manifest["entries"]
                    }
                    assert (
                        manifest_entries_by_bucket["body_only"]["storage"]["body_derivative"][
                            "metadata"
                        ]["alpha_present"]
                        is True
                    )
                    assert (
                        manifest_entries_by_bucket["lora_only"]["storage"]["body_derivative"]
                        is None
                    )
                    assert (
                        manifest_entries_by_bucket["lora_only"]["storage"]["lora_derivative"][
                            "path"
                        ].endswith("lora-normalized.png")
                    )

                    assert lora_manifest["version"] == "lora-dataset-seed-v1"
                    assert lora_manifest["entry_count"] == 2
                    assert {entry["bucket"] for entry in lora_manifest["entries"]} == {
                        "both",
                        "lora_only",
                    }
                    assert all(
                        entry["caption_seed"]["version"] == "caption-seed-v1"
                        for entry in lora_manifest["entries"]
                    )
            finally:
                app.dependency_overrides.clear()
                engine.dispose()
