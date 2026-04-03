from pathlib import Path
from tempfile import TemporaryDirectory

from _pytest.monkeypatch import MonkeyPatch
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.db.session import get_db_session
from app.main import app
from app.models.job import Job
from app.models.storage_object import StorageObject
from app.services.jobs import run_worker_once
from tests.db_test_utils import migrated_database
from tests.photoset_test_utils import upload_photoset_and_complete_ingest
from tests.test_characters_api import (
    _build_qc_report,
    _override_db_session,
    _patch_deterministic_qc,
    _sample_image_bytes,
    _session_factory,
)


def _configure_runtime(monkeypatch: MonkeyPatch, *, nas_root: Path, scratch_root: Path) -> None:
    monkeypatch.setenv("MEDIACREATOR_BLENDER_BIN", "/opt/blender-4.5-lts/blender")
    monkeypatch.setenv("MEDIACREATOR_STORAGE_NAS_ROOT", str(nas_root))
    monkeypatch.setenv(
        "MEDIACREATOR_STORAGE_UPLOADED_PHOTOS_ROOT",
        str(nas_root / "photos" / "uploaded"),
    )
    monkeypatch.setenv(
        "MEDIACREATOR_STORAGE_PREPARED_IMAGES_ROOT",
        str(nas_root / "photos" / "prepared"),
    )
    monkeypatch.setenv("MEDIACREATOR_STORAGE_EXPORTS_ROOT", str(nas_root / "exports"))
    monkeypatch.setenv("MEDIACREATOR_STORAGE_SCRATCH_ROOT", str(scratch_root))


def test_saved_base_glb_is_queued_then_registered_from_a_real_artifact(
    monkeypatch: MonkeyPatch,
) -> None:
    _patch_deterministic_qc(
        monkeypatch,
        [
            _build_qc_report("pass"),
            _build_qc_report(
                "warn",
                blur_score=92,
                framing_label="head-closeup",
                reasons=["Portrait crop is LoRA-only."],
            ),
        ],
    )

    with migrated_database("phase04_saved_glb_contract") as database_url:
        engine, session_factory = _session_factory(database_url)
        app.dependency_overrides[get_db_session] = _override_db_session(session_factory)

        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            nas_root = temp_path / "nas"
            scratch_root = temp_path / "scratch"
            nas_root.mkdir()
            scratch_root.mkdir()
            _configure_runtime(monkeypatch, nas_root=nas_root, scratch_root=scratch_root)

            try:
                with TestClient(app) as client:
                    _, photoset_payload = upload_photoset_and_complete_ingest(
                        client,
                        session_factory,
                        data={"character_label": "Phase 04 saved GLB"},
                        files=[
                            (
                                "photos",
                                (
                                    "male_body_front.png",
                                    _sample_image_bytes("male_body_front.png"),
                                    "image/png",
                                ),
                            ),
                            (
                                "photos",
                                (
                                    "female_head_front.png",
                                    _sample_image_bytes("female_head_front.png"),
                                    "image/png",
                                ),
                            ),
                        ],
                    )

                    character_response = client.post(
                        "/api/v1/characters",
                        json={"photoset_public_id": photoset_payload["public_id"]},
                    )
                    assert character_response.status_code == 201
                    character_public_id = character_response.json()["public_id"]

                    before_queue = client.get(f"/api/v1/exports/characters/{character_public_id}")
                    assert before_queue.status_code == 200
                    assert before_queue.json()["preview_glb"]["status"] == "not-ready"
                    assert before_queue.json()["export_job"]["status"] == "not-queued"

                    queued_response = client.post(
                        f"/api/v1/exports/characters/{character_public_id}/preview"
                    )
                    assert queued_response.status_code == 202
                    queued_payload = queued_response.json()
                    assert queued_payload["status"] == "queued"
                    assert queued_payload["step_name"] == "queued"
                    assert queued_payload["progress_percent"] == 0

                    after_queue = client.get(f"/api/v1/exports/characters/{character_public_id}")
                    assert after_queue.status_code == 200
                    assert after_queue.json()["preview_glb"]["status"] == "not-ready"
                    assert after_queue.json()["export_job"]["status"] == "queued"

                with session_factory() as session:
                    queued_job = session.scalar(
                        select(Job).where(Job.job_type == "blender-preview-export")
                    )
                    assert queued_job is not None
                    assert queued_job.output_asset_id is not None
                    assert queued_job.output_storage_object_id is None

                assert run_worker_once(session_factory) == "completed"

                with TestClient(app) as client:
                    completed_payload = client.get(
                        f"/api/v1/exports/characters/{character_public_id}"
                    ).json()
                    assert completed_payload["preview_glb"]["status"] == "available"
                    assert completed_payload["preview_glb"]["url"] is not None
                    assert completed_payload["export_job"]["status"] == "completed"
                    assert completed_payload["export_job"]["progress_percent"] == 100

                    preview_response = client.get(
                        f"/api/v1/exports/characters/{character_public_id}/preview.glb"
                    )
                    assert preview_response.status_code == 200
                    assert preview_response.headers["content-type"] == "model/gltf-binary"
                    assert len(preview_response.content) > 0

                with session_factory() as session:
                    preview_storage = session.scalar(
                        select(StorageObject).where(
                            StorageObject.object_type == "character-preview-glb"
                        )
                    )
                    completed_job = session.scalar(
                        select(Job).where(Job.job_type == "blender-preview-export")
                    )
                    assert preview_storage is not None
                    assert Path(preview_storage.storage_path).exists()
                    assert completed_job is not None
                    assert completed_job.status == "completed"
                    assert completed_job.output_storage_object_id == preview_storage.id
            finally:
                app.dependency_overrides.clear()
                engine.dispose()


def test_high_detail_path_uses_body_qualified_threshold_for_detail_prep(
    monkeypatch: MonkeyPatch,
) -> None:
    _patch_deterministic_qc(
        monkeypatch,
        [
            _build_qc_report("pass"),
            _build_qc_report(
                "warn",
                blur_score=88,
                reasons=["Body evidence is acceptable."],
            ),
            _build_qc_report(
                "warn",
                blur_score=96,
                framing_label="head-closeup",
                reasons=["Portrait crop is LoRA-only."],
            ),
        ],
    )

    with migrated_database("phase04_detail_threshold") as database_url:
        engine, session_factory = _session_factory(database_url)
        app.dependency_overrides[get_db_session] = _override_db_session(session_factory)

        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            nas_root = temp_path / "nas"
            scratch_root = temp_path / "scratch"
            nas_root.mkdir()
            scratch_root.mkdir()
            _configure_runtime(monkeypatch, nas_root=nas_root, scratch_root=scratch_root)

            try:
                with TestClient(app) as client:
                    _, photoset_payload = upload_photoset_and_complete_ingest(
                        client,
                        session_factory,
                        data={"character_label": "Phase 04 threshold subject"},
                        files=[
                            (
                                "photos",
                                (
                                    "male_body_front.png",
                                    _sample_image_bytes("male_body_front.png"),
                                    "image/png",
                                ),
                            ),
                            (
                                "photos",
                                (
                                    "male_body_left.png",
                                    _sample_image_bytes("male_body_left.png"),
                                    "image/png",
                                ),
                            ),
                            (
                                "photos",
                                (
                                    "male_head_front.png",
                                    _sample_image_bytes("male_head_front.png"),
                                    "image/png",
                                ),
                            ),
                        ],
                    )

                    character_response = client.post(
                        "/api/v1/characters",
                        json={"photoset_public_id": photoset_payload["public_id"]},
                    )
                    assert character_response.status_code == 201
                    character_public_id = character_response.json()["public_id"]

                    queued_response = client.post(
                        f"/api/v1/exports/characters/{character_public_id}/reconstruction"
                    )
                    assert queued_response.status_code == 202
                    queued_payload = queued_response.json()
                    assert queued_payload["status"] == "queued"
                    assert queued_payload["progress_percent"] == 0

                with session_factory() as session:
                    reconstruction_job = session.scalar(
                        select(Job).where(Job.job_type == "high-detail-reconstruction")
                    )
                    assert reconstruction_job is not None
                    assert reconstruction_job.payload["accepted_entry_count"] == 3
                    assert reconstruction_job.payload["body_qualified_entry_count"] == 2

                assert run_worker_once(session_factory) == "completed"

                with TestClient(app) as client:
                    exports_payload = client.get(
                        f"/api/v1/exports/characters/{character_public_id}"
                    ).json()
                    assert exports_payload["reconstruction"]["detail_level"] == "riggable-base-only"
                    assert exports_payload["reconstruction"]["strategy"] == "smplx-stage1-only"
                    assert exports_payload["reconstruction"]["detail_prep_artifact"]["status"] == (
                        "not-ready"
                    )
                    assert exports_payload["reconstruction"]["reconstruction_job"]["status"] == (
                        "completed"
                    )
                    assert "Current body-qualified inputs: 2" in exports_payload["reconstruction"][
                        "detail"
                    ]
                    assert exports_payload["reconstruction"]["riggable_base_glb"]["status"] == (
                        "available"
                    )

                with session_factory() as session:
                    detail_prep_storage = session.scalar(
                        select(StorageObject).where(
                            StorageObject.object_type == "character-detail-prep-manifest"
                        )
                    )
                    reconstruction_job = session.scalar(
                        select(Job).where(Job.job_type == "high-detail-reconstruction")
                    )
                    assert detail_prep_storage is None
                    assert reconstruction_job is not None
                    assert reconstruction_job.output_storage_object_id is not None
            finally:
                app.dependency_overrides.clear()
                engine.dispose()
