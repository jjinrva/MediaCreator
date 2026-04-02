import os
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
from app.models.asset import Asset
from app.models.history_event import HistoryEvent
from app.models.photoset_entry import PhotosetEntry
from app.services import photo_prep
from tests.db_test_utils import migrated_database


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


def _upload_image_bytes(
    color: tuple[int, int, int],
    *,
    size: tuple[int, int] = (640, 960),
    noise: bool = False,
) -> bytes:
    buffer = BytesIO()
    if noise:
        image = Image.frombytes("RGB", size, os.urandom(size[0] * size[1] * 3))
    else:
        image = Image.new("RGB", size, color=color)
    image.save(buffer, format="PNG")
    return buffer.getvalue()


class _StubLandmarker:
    def close(self) -> None:
        return None


def _build_qc_report(
    bucket: Literal["lora_only", "body_only", "both", "rejected"],
    *,
    blur_score: float = 140,
    exposure_score: float = 98,
    framing_label: str = "full-body",
    face_detected: bool = True,
    body_detected: bool = True,
    reason_codes: list[str] | None = None,
    reason_messages: list[str] | None = None,
) -> photo_prep.PhotoQcReport:
    status: Literal["pass", "warn", "fail"]
    if bucket == "rejected":
        status = "fail"
    elif reason_codes:
        status = "warn"
    else:
        status = "pass"

    occlusion_label = "clear"
    if not face_detected and body_detected:
        occlusion_label = "face_not_visible"
    elif face_detected and not body_detected:
        occlusion_label = "body_not_visible"
    elif not face_detected and not body_detected:
        occlusion_label = "unknown"

    return photo_prep.PhotoQcReport(
        framing_label=framing_label,
        metrics={
            "has_person": face_detected or body_detected,
            "face_detected": face_detected,
            "body_detected": body_detected,
            "body_landmarks_detected": body_detected,
            "blur_score": blur_score,
            "exposure_score": exposure_score,
            "framing_label": framing_label,
            "occlusion_label": occlusion_label,
            "resolution_ok": True,
        },
        reasons=reason_messages or [],
        status=status,
        bucket=bucket,
        usable_for_lora=bucket in {"lora_only", "both"},
        usable_for_body=bucket in {"body_only", "both"},
        reason_codes=reason_codes or [],
        reason_messages=reason_messages or [],
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

    def _fake_qc_report(
        image: object,
        face_landmarker: object,
        pose_landmarker: object,
    ) -> photo_prep.PhotoQcReport:
        return queued_reports.pop(0)

    monkeypatch.setattr(photo_prep, "_qc_report", _fake_qc_report)


def _configure_storage(monkeypatch: MonkeyPatch, temp_path: Path) -> None:
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
    monkeypatch.setenv("MEDIACREATOR_STORAGE_SCRATCH_ROOT", str(scratch_root))


def test_label_validation_duplicate_labels_and_reloadable_buckets(
    monkeypatch: MonkeyPatch,
) -> None:
    _patch_deterministic_qc(
        monkeypatch,
        [
            _build_qc_report(
                "lora_only",
                framing_label="head-closeup",
                body_detected=False,
                reason_codes=["body_evidence_missing"],
                reason_messages=["Body evidence is too weak for body modeling."],
            ),
            _build_qc_report(
                "body_only",
                face_detected=False,
                reason_codes=["face_required_for_lora"],
                reason_messages=["Face evidence was not detected for LoRA training."],
            ),
            _build_qc_report("both"),
            _build_qc_report(
                "rejected",
                face_detected=False,
                body_detected=False,
                reason_codes=["no_person_detected"],
                reason_messages=["No person was detected in the image."],
            ),
        ],
    )

    with migrated_database("photosets_phase01_classification") as database_url:
        engine, session_factory = _session_factory(database_url)
        app.dependency_overrides[get_db_session] = _override_db_session(session_factory)

        with TemporaryDirectory() as temp_dir:
            _configure_storage(monkeypatch, Path(temp_dir))

            try:
                with TestClient(app) as client:
                    empty_label_response = client.post(
                        "/api/v1/photosets",
                        data={"character_label": "   "},
                        files=[
                            (
                                "photos",
                                ("empty.png", _upload_image_bytes((60, 60, 60)), "image/png"),
                            )
                        ],
                    )
                    assert empty_label_response.status_code == 400
                    assert empty_label_response.json()["detail"] == "Character label is required."

                    upload_response = client.post(
                        "/api/v1/photosets",
                        data={"character_label": "  Casey  "},
                        files=[
                            (
                                "photos",
                                ("lora.png", _upload_image_bytes((180, 120, 110)), "image/png"),
                            ),
                            (
                                "photos",
                                ("body.png", _upload_image_bytes((120, 160, 180)), "image/png"),
                            ),
                            (
                                "photos",
                                ("both.png", _upload_image_bytes((90, 120, 180)), "image/png"),
                            ),
                            (
                                "photos",
                                ("reject.png", _upload_image_bytes((20, 20, 20)), "image/png"),
                            ),
                        ],
                    )

                    assert upload_response.status_code == 201
                    payload = upload_response.json()
                    assert payload["character_label"] == "Casey"
                    assert payload["bucket_counts"] == {
                        "lora_only": 1,
                        "body_only": 1,
                        "both": 1,
                        "rejected": 1,
                    }
                    assert payload["accepted_entry_count"] == 3
                    assert payload["rejected_entry_count"] == 1
                    assert [entry["bucket"] for entry in payload["entries"]] == [
                        "lora_only",
                        "body_only",
                        "both",
                        "rejected",
                    ]
                    assert [
                        entry["accepted_for_character_use"] for entry in payload["entries"]
                    ] == [True, True, True, False]
                    assert payload["entries"][1]["qc_metrics"]["face_detected"] is False
                    assert payload["entries"][1]["qc_metrics"]["body_detected"] is True
                    assert payload["entries"][1]["bucket"] == "body_only"
                    assert payload["entries"][1]["reason_codes"] == ["face_required_for_lora"]
                    assert payload["entries"][3]["reason_codes"] == ["no_person_detected"]

                    detail_response = client.get(f"/api/v1/photosets/{payload['public_id']}")
                    assert detail_response.status_code == 200
                    assert detail_response.json() == payload

                    _patch_deterministic_qc(monkeypatch, [_build_qc_report("both")])
                    duplicate_label_response = client.post(
                        "/api/v1/photosets",
                        data={"character_label": "Casey"},
                        files=[
                            (
                                "photos",
                                (
                                    "duplicate.png",
                                    _upload_image_bytes((200, 150, 140)),
                                    "image/png",
                                ),
                            )
                        ],
                    )
                    assert duplicate_label_response.status_code == 201
                    assert duplicate_label_response.json()["character_label"] == "Casey"

                    with session_factory() as session:
                        photosets = session.scalars(
                            select(Asset)
                            .where(Asset.asset_type == "photoset")
                            .order_by(Asset.created_at.asc())
                        ).all()
                        first_photoset_entries = session.scalars(
                            select(PhotosetEntry)
                            .where(PhotosetEntry.photoset_asset_id == photosets[0].id)
                            .order_by(PhotosetEntry.ordinal.asc())
                        ).all()
                        created_events = session.scalars(
                            select(HistoryEvent)
                            .where(HistoryEvent.event_type == "photoset.created")
                            .order_by(HistoryEvent.created_at.asc())
                        ).all()

                        assert len(photosets) == 2
                        assert [entry.bucket for entry in first_photoset_entries] == [
                            "lora_only",
                            "body_only",
                            "both",
                            "rejected",
                        ]
                        assert [event.details["character_label"] for event in created_events] == [
                            "Casey",
                            "Casey",
                        ]
            finally:
                app.dependency_overrides.clear()
                engine.dispose()


def test_multifile_upload_and_bounded_ingest_validation(
    monkeypatch: MonkeyPatch,
) -> None:
    monkeypatch.setattr(photo_prep, "MAX_UPLOAD_FILE_COUNT", 2)
    monkeypatch.setattr(photo_prep, "MAX_UPLOAD_FILE_SIZE_BYTES", 1024)
    _patch_deterministic_qc(
        monkeypatch,
        [
            _build_qc_report("both"),
            _build_qc_report("both"),
        ],
    )

    with migrated_database("photosets_phase01_limits") as database_url:
        engine, session_factory = _session_factory(database_url)
        app.dependency_overrides[get_db_session] = _override_db_session(session_factory)

        with TemporaryDirectory() as temp_dir:
            _configure_storage(monkeypatch, Path(temp_dir))

            try:
                with TestClient(app) as client:
                    success_response = client.post(
                        "/api/v1/photosets",
                        data={"character_label": "Bounded ingest"},
                        files=[
                            (
                                "photos",
                                (
                                    "first.png",
                                    _upload_image_bytes((30, 40, 50), size=(16, 16)),
                                    "image/png",
                                ),
                            ),
                            (
                                "photos",
                                (
                                    "second.png",
                                    _upload_image_bytes((60, 70, 80), size=(16, 16)),
                                    "image/png",
                                ),
                            ),
                        ],
                    )
                    assert success_response.status_code == 201
                    assert success_response.json()["entry_count"] == 2

                    too_many_response = client.post(
                        "/api/v1/photosets",
                        data={"character_label": "Too many"},
                        files=[
                            (
                                "photos",
                                (
                                    "a.png",
                                    _upload_image_bytes((1, 1, 1), size=(16, 16)),
                                    "image/png",
                                ),
                            ),
                            (
                                "photos",
                                (
                                    "b.png",
                                    _upload_image_bytes((2, 2, 2), size=(16, 16)),
                                    "image/png",
                                ),
                            ),
                            (
                                "photos",
                                (
                                    "c.png",
                                    _upload_image_bytes((3, 3, 3), size=(16, 16)),
                                    "image/png",
                                ),
                            ),
                        ],
                    )
                    assert too_many_response.status_code == 400
                    assert "at most 2 files" in too_many_response.json()["detail"]

                    oversized_response = client.post(
                        "/api/v1/photosets",
                        data={"character_label": "Too large"},
                        files=[
                            (
                                "photos",
                                (
                                    "huge.png",
                                    _upload_image_bytes((0, 0, 0), size=(256, 256), noise=True),
                                    "image/png",
                                ),
                            )
                        ],
                    )
                    assert oversized_response.status_code == 400
                    assert "upload limit" in oversized_response.json()["detail"]
            finally:
                app.dependency_overrides.clear()
                engine.dispose()
