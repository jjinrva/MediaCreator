import uuid
from collections.abc import Callable, Generator
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Literal

from _pytest.monkeypatch import MonkeyPatch
from fastapi.testclient import TestClient
from PIL import Image
from sqlalchemy import select
from sqlalchemy.engine import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.session import get_db_session
from app.main import app
from app.models.photoset_entry import PhotosetEntry
from app.services import photo_prep
from app.services.jobs import complete_job, run_worker_once
from tests.db_test_utils import migrated_database
from tests.photoset_test_utils import queue_photoset_upload


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
    bucket: Literal["lora_only", "body_only", "both", "rejected"],
    *,
    face_detected: bool = True,
    body_detected: bool = True,
    reason_codes: list[str] | None = None,
    reason_messages: list[str] | None = None,
) -> photo_prep.PhotoQcReport:
    return photo_prep.PhotoQcReport(
        framing_label="full-body",
        metrics={
            "has_person": face_detected or body_detected,
            "person_detected": face_detected or body_detected,
            "face_detected": face_detected,
            "body_detected": body_detected,
            "body_landmarks_detected": body_detected,
            "blur_score": 160.0,
            "blur_ok_for_lora": 160.0 >= photo_prep.MIN_BLUR_FOR_LORA,
            "blur_ok_for_body": 160.0 >= photo_prep.MIN_BLUR_FOR_BODY,
            "exposure_score": 100.0,
            "exposure_ok_for_lora": (
                photo_prep.MIN_EXPOSURE_FOR_LORA <= 100.0 <= photo_prep.MAX_EXPOSURE_FOR_LORA
            ),
            "exposure_ok_for_body": (
                photo_prep.MIN_EXPOSURE_FOR_BODY <= 100.0 <= photo_prep.MAX_EXPOSURE_FOR_BODY
            ),
            "framing_label": "full-body",
            "occlusion_label": "clear" if face_detected and body_detected else "face_not_visible",
            "resolution_ok": True,
        },
        reasons=reason_messages or [],
        status="fail" if bucket == "rejected" else "warn" if reason_codes else "pass",
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


def _stages_appear_in_order(stage_names: list[str], required_stages: list[str]) -> bool:
    required_index = 0
    for stage_name in stage_names:
        if stage_name == required_stages[required_index]:
            required_index += 1
            if required_index == len(required_stages):
                return True
    return False


def test_ingest_job_records_ordered_stage_progress_and_completion_gate(
    monkeypatch: MonkeyPatch,
) -> None:
    _patch_deterministic_qc(
        monkeypatch,
        [
            _build_qc_report("both"),
            _build_qc_report(
                "body_only",
                face_detected=False,
                reason_codes=["face_required_for_lora"],
                reason_messages=["Face evidence was not detected for LoRA training."],
            ),
        ],
    )

    completion_snapshot: dict[str, int] = {}
    original_complete_job = complete_job

    def _wrapped_complete_job(
        session: Session,
        actor_id: uuid.UUID,
        job: object,
        output_asset_id: uuid.UUID | None = None,
        output_storage_object_id: uuid.UUID | None = None,
    ) -> object:
        completion_snapshot["entry_count_at_complete"] = len(
            session.scalars(select(PhotosetEntry)).all()
        )
        completion_snapshot["processed_files_at_complete"] = int(
            getattr(job, "payload", {}).get("processed_files", -1)
        )
        return original_complete_job(
            session,
            actor_id,
            job,  # type: ignore[arg-type]
            output_asset_id=output_asset_id,
            output_storage_object_id=output_storage_object_id,
        )

    monkeypatch.setattr(photo_prep, "complete_job", _wrapped_complete_job)

    with migrated_database("photosets_phase01_job_progress") as database_url:
        engine, session_factory = _session_factory(database_url)
        app.dependency_overrides[get_db_session] = _override_db_session(session_factory)

        with TemporaryDirectory() as temp_dir:
            _configure_storage(monkeypatch, Path(temp_dir))

            try:
                with TestClient(app) as client:
                    queued_payload = queue_photoset_upload(
                        client,
                        data={"character_label": "Progress subject"},
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
                    assert queued_payload["ingest_job"]["status"] == "queued"
                    assert queued_payload["ingest_job"]["processed_files"] == 0
                    assert queued_payload["ingest_job"]["bucket_counts"] == {
                        "lora_only": 0,
                        "body_only": 0,
                        "both": 0,
                        "rejected": 0,
                    }

                    job_response = client.get(
                        f"/api/v1/jobs/{queued_payload['ingest_job']['job_public_id']}"
                    )
                    assert job_response.status_code == 200
                    assert job_response.json()["status"] == "queued"

                    assert run_worker_once(session_factory) == "completed"

                    detail_response = client.get(f"/api/v1/photosets/{queued_payload['public_id']}")
                    assert detail_response.status_code == 200
                    payload = detail_response.json()
                    assert payload["ingest_job"]["processed_files"] == 2
                    assert payload["ingest_job"]["bucket_counts"] == {
                        "lora_only": 0,
                        "body_only": 1,
                        "both": 1,
                        "rejected": 0,
                    }

                    job_response = client.get(
                        f"/api/v1/jobs/{payload['ingest_job']['job_public_id']}"
                    )
                    assert job_response.status_code == 200
                    job_payload = job_response.json()
                    assert job_payload["status"] == "completed"
                    assert job_payload["step_name"] == "completed"
                    assert job_payload["progress"]["total_files"] == 2
                    assert job_payload["progress"]["processed_files"] == 2
                    assert job_payload["progress"]["bucket_counts"] == {
                        "lora_only": 0,
                        "body_only": 1,
                        "both": 1,
                        "rejected": 0,
                    }

                    stage_names = [
                        stage["step_name"]
                        for stage in job_payload["stage_history"]
                        if stage["step_name"] is not None
                    ]
                    assert _stages_appear_in_order(
                        stage_names,
                        [
                            "queued",
                            "upload_received",
                            "normalizing",
                            "person_check",
                            "qc_metrics",
                            "classification",
                            "derivative_write",
                            "complete",
                            "completed",
                        ],
                    )
            finally:
                app.dependency_overrides.clear()
                engine.dispose()

    assert completion_snapshot == {
        "entry_count_at_complete": 2,
        "processed_files_at_complete": 2,
    }
