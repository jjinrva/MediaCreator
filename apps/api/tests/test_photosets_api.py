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
from app.models.storage_object import StorageObject
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


def _upload_image_bytes(color: tuple[int, int, int]) -> bytes:
    buffer = BytesIO()
    Image.new("RGB", (640, 960), color=color).save(buffer, format="PNG")
    return buffer.getvalue()


class _StubLandmarker:
    def close(self) -> None:
        return None


def _build_qc_report(
    status: Literal["pass", "warn", "fail"],
    *,
    blur_score: float = 140,
    exposure_score: float = 98,
    framing_label: str = "full-body",
    reasons: list[str] | None = None,
) -> photo_prep.PhotoQcReport:
    bucket: Literal["lora_only", "body_only", "both", "rejected"]
    if status == "fail":
        bucket = "rejected"
        usable_for_lora = False
        usable_for_body = False
        face_detected = False
        body_detected = False
        occlusion_label = "unknown"
    elif framing_label == "head-closeup":
        bucket = "lora_only"
        usable_for_lora = True
        usable_for_body = False
        face_detected = True
        body_detected = False
        occlusion_label = "body_not_visible"
    else:
        bucket = "both"
        usable_for_lora = True
        usable_for_body = True
        face_detected = True
        body_detected = True
        occlusion_label = "clear"

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
        reasons=reasons or [],
        status=status,
        bucket=bucket,
        usable_for_lora=usable_for_lora,
        usable_for_body=usable_for_body,
        reason_codes=[] if status == "pass" else [bucket],
        reason_messages=reasons or [],
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
        image: Image.Image,
        face_landmarker: object,
        pose_landmarker: object,
    ) -> photo_prep.PhotoQcReport:
        return queued_reports.pop(0)

    monkeypatch.setattr(photo_prep, "_qc_report", _fake_qc_report)


def test_photoset_upload_persists_derivatives_and_stable_qc_payload(
    monkeypatch: MonkeyPatch,
) -> None:
    _patch_deterministic_qc(
        monkeypatch,
        [
            _build_qc_report("pass"),
            _build_qc_report(
                "fail",
                blur_score=55,
                framing_label="head-closeup",
                reasons=["Image appears too blurry."],
            ),
        ],
    )

    with migrated_database("photosets_api") as database_url:
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
            monkeypatch.setenv("MEDIACREATOR_STORAGE_SCRATCH_ROOT", str(scratch_root))

            try:
                with TestClient(app) as client:
                    upload_response = client.post(
                        "/api/v1/photosets",
                        data={"character_label": "Phase 10 upload"},
                        files=[
                            (
                                "photos",
                                ("first.png", _upload_image_bytes((180, 120, 110)), "image/png"),
                            ),
                            (
                                "photos",
                                ("second.png", _upload_image_bytes((120, 160, 180)), "image/png"),
                            ),
                        ],
                    )

                    assert upload_response.status_code == 201
                    payload = upload_response.json()
                    assert payload["asset_type"] == "photoset"
                    assert payload["accepted_entry_count"] == 1
                    assert payload["entry_count"] == 2
                    assert payload["rejected_entry_count"] == 1
                    assert len(payload["entries"]) == 2
                    assert [entry["qc_status"] for entry in payload["entries"]] == ["pass", "fail"]
                    assert [
                        entry["accepted_for_character_use"] for entry in payload["entries"]
                    ] == [True, False]

                    photoset_public_id = payload["public_id"]
                    first_entry = payload["entries"][0]
                    second_entry = payload["entries"][1]
                    assert first_entry["qc_status"] == "pass"
                    assert first_entry["accepted_for_character_use"] is True
                    assert set(first_entry["qc_metrics"]) >= {
                        "has_person",
                        "face_detected",
                        "body_detected",
                        "body_landmarks_detected",
                        "blur_score",
                        "exposure_score",
                        "framing_label",
                        "occlusion_label",
                        "resolution_ok",
                    }
                    assert second_entry["qc_status"] == "fail"
                    assert second_entry["accepted_for_character_use"] is False
                    assert second_entry["qc_reasons"] == ["Image appears too blurry."]

                    detail_response = client.get(f"/api/v1/photosets/{photoset_public_id}")
                    assert detail_response.status_code == 200
                    assert detail_response.json() == payload

                    thumbnail_response = client.get(first_entry["artifact_urls"]["thumbnail"])
                    assert thumbnail_response.status_code == 200
                    assert thumbnail_response.headers["content-type"] == "image/png"

                with session_factory() as session:
                    photoset_assets = session.scalars(
                        select(Asset).where(Asset.asset_type == "photoset")
                    ).all()
                    photo_assets = session.scalars(
                        select(Asset).where(Asset.asset_type == "photo")
                    ).all()
                    entries = session.scalars(
                        select(PhotosetEntry).order_by(PhotosetEntry.ordinal.asc())
                    ).all()
                    storage_objects = session.scalars(
                        select(StorageObject).order_by(StorageObject.created_at.asc())
                    ).all()
                    history_events = session.scalars(
                        select(HistoryEvent).order_by(HistoryEvent.created_at.asc())
                    ).all()

                    assert len(photoset_assets) == 1
                    assert len(photo_assets) == 2
                    assert len(entries) == 2
                    assert len(storage_objects) == 6
                    assert [entry.qc_status for entry in entries] == ["pass", "fail"]
                    event_types = [event.event_type for event in history_events]
                    assert event_types.count("photoset.created") == 1
                    assert event_types.count("photo.prepared") == 2
                    assert event_types.count("photoset.prepared") == 1
                    assert "job.completed" in event_types

                    for storage_object in storage_objects:
                        assert Path(storage_object.storage_path).exists()
            finally:
                app.dependency_overrides.clear()
                engine.dispose()
