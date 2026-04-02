from collections.abc import Callable, Generator
from pathlib import Path
from tempfile import TemporaryDirectory

from _pytest.monkeypatch import MonkeyPatch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.session import get_db_session
from app.main import app
from app.models.history_event import HistoryEvent
from app.models.job import Job
from app.models.storage_object import StorageObject
from app.services.jobs import run_worker_once
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


def _sample_image_bytes(filename: str) -> bytes:
    repo_root = Path(__file__).resolve().parents[3]
    return (repo_root / "docs" / "capture_guides" / "assets" / filename).read_bytes()


def test_high_detail_reconstruction_route_writes_truthful_base_and_detail_prep_outputs(
    monkeypatch: MonkeyPatch,
) -> None:
    with migrated_database("reconstruction_api") as database_url:
        engine, session_factory = _session_factory(database_url)
        app.dependency_overrides[get_db_session] = _override_db_session(session_factory)

        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            nas_root = temp_path / "nas"
            scratch_root = temp_path / "scratch"
            nas_root.mkdir()
            scratch_root.mkdir()

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

            try:
                with TestClient(app) as client:
                    photoset_response = client.post(
                        "/api/v1/photosets",
                        data={"character_label": "Phase 18 reconstruction subject"},
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
                                    "male_body_back.png",
                                    _sample_image_bytes("male_body_back.png"),
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
                                    "male_body_right.png",
                                    _sample_image_bytes("male_body_right.png"),
                                    "image/png",
                                ),
                            ),
                            (
                                "photos",
                                (
                                    "male_body_three_quarter.png",
                                    _sample_image_bytes("male_body_three_quarter.png"),
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
                    assert photoset_response.status_code == 201

                    create_response = client.post(
                        "/api/v1/characters",
                        json={"photoset_public_id": photoset_response.json()["public_id"]},
                    )
                    assert create_response.status_code == 201
                    character_public_id = create_response.json()["public_id"]

                    reconstruction_response = client.post(
                        f"/api/v1/exports/characters/{character_public_id}/reconstruction"
                    )
                    assert reconstruction_response.status_code == 202
                    queued_payload = reconstruction_response.json()
                    assert queued_payload["status"] == "queued"
                    assert queued_payload["step_name"] == "queued"
                    assert queued_payload["progress_percent"] == 0

                    scaffold_response = client.get(
                        f"/api/v1/exports/characters/{character_public_id}"
                    )
                    assert scaffold_response.status_code == 200
                    scaffold_payload = scaffold_response.json()
                    assert (
                        scaffold_payload["reconstruction"]["reconstruction_job"]["status"]
                        == "queued"
                    )
                    assert (
                        scaffold_payload["reconstruction"]["reconstruction_job"]["job_public_id"]
                        == queued_payload["job_public_id"]
                    )
                    assert (
                        scaffold_payload["reconstruction"]["riggable_base_glb"]["status"]
                        == "not-ready"
                    )

                assert run_worker_once(session_factory) == "completed"

                with TestClient(app) as client:
                    payload = client.get(
                        f"/api/v1/exports/characters/{character_public_id}"
                    ).json()
                    assert payload["reconstruction"]["detail_level"] == (
                        "riggable-base-plus-detail-prep"
                    )
                    assert payload["reconstruction"]["strategy"] == "smplx-stage1-plus-colmap-prep"
                    assert payload["reconstruction"]["riggable_base_glb"]["status"] == "available"
                    assert (
                        payload["reconstruction"]["detail_prep_artifact"]["status"] == "available"
                    )
                    assert payload["reconstruction"]["reconstruction_job"]["status"] == "completed"

                    preview_response = client.get(
                        f"/api/v1/exports/characters/{character_public_id}/preview.glb"
                    )
                    assert preview_response.status_code == 200

                    detail_prep_response = client.get(
                        f"/api/v1/exports/characters/{character_public_id}/detail-prep.json"
                    )
                    assert detail_prep_response.status_code == 200
                    assert detail_prep_response.headers["content-type"].startswith(
                        "application/json"
                    )
                    assert "smplx-stage1-plus-colmap-prep" in detail_prep_response.text

                with session_factory() as session:
                    detail_prep_storage = session.scalar(
                        select(StorageObject).where(
                            StorageObject.object_type == "character-detail-prep-manifest"
                        )
                    )
                    reconstruction_job = session.scalar(
                        select(Job).where(Job.job_type == "high-detail-reconstruction")
                    )
                    history_events = session.scalars(
                        select(HistoryEvent)
                        .where(
                            HistoryEvent.event_type.in_(
                                [
                                    "job.completed",
                                    "reconstruction.completed",
                                    "reconstruction.detail_prep_generated",
                                ]
                            )
                        )
                        .order_by(HistoryEvent.created_at.asc())
                    ).all()

                    assert detail_prep_storage is not None
                    assert Path(detail_prep_storage.storage_path).exists()
                    assert reconstruction_job is not None
                    assert reconstruction_job.status == "completed"
                    assert reconstruction_job.step_name == "completed"
                    assert reconstruction_job.output_storage_object_id is not None
                    assert len(history_events) == 3
                    assert {event.event_type for event in history_events} == {
                        "job.completed",
                        "reconstruction.completed",
                        "reconstruction.detail_prep_generated",
                    }
            finally:
                app.dependency_overrides.clear()
                engine.dispose()
