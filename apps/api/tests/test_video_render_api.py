import uuid
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
from app.models.asset import Asset
from app.models.history_event import HistoryEvent
from app.models.job import Job
from app.models.storage_object import StorageObject
from app.services.jobs import run_worker_once
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


def _configure_storage(monkeypatch: MonkeyPatch, temp_path: Path) -> None:
    nas_root = temp_path / "nas"
    scratch_root = temp_path / "scratch"
    nas_root.mkdir()
    scratch_root.mkdir()

    monkeypatch.setenv("MEDIACREATOR_BLENDER_BIN", "/opt/blender-4.5-lts/blender")
    monkeypatch.setenv("MEDIACREATOR_STORAGE_NAS_ROOT", str(nas_root))
    monkeypatch.setenv("MEDIACREATOR_STORAGE_SCRATCH_ROOT", str(scratch_root))
    monkeypatch.setenv(
        "MEDIACREATOR_STORAGE_UPLOADED_PHOTOS_ROOT",
        str(nas_root / "photos" / "uploaded"),
    )
    monkeypatch.setenv(
        "MEDIACREATOR_STORAGE_PREPARED_IMAGES_ROOT",
        str(nas_root / "photos" / "prepared"),
    )


def _create_character(
    client: TestClient,
    session_factory: sessionmaker[Session],
) -> str:
    _, photoset_payload = upload_photoset_and_complete_ingest(
        client,
        session_factory,
        data={"character_label": "Video render test character"},
        files=[
            (
                "photos",
                (
                    "male_head_front.png",
                    _sample_image_bytes("male_head_front.png"),
                    "image/png",
                ),
            )
        ],
    )

    create_response = client.post(
        "/api/v1/characters",
        json={"photoset_public_id": photoset_payload["public_id"]},
    )
    assert create_response.status_code == 201
    return str(create_response.json()["public_id"])


def test_video_render_creates_a_real_mp4_with_character_and_motion_lineage(
    monkeypatch: MonkeyPatch,
) -> None:
    with migrated_database("video_render_api") as database_url:
        engine, session_factory = _session_factory(database_url)
        app.dependency_overrides[get_db_session] = _override_db_session(session_factory)

        with TemporaryDirectory() as temp_dir:
            _configure_storage(monkeypatch, Path(temp_dir))

            try:
                with TestClient(app) as client:
                    character_public_id = _create_character(client, session_factory)

                    motion_response = client.get("/api/v1/motion")
                    assert motion_response.status_code == 200
                    jump_clip = next(
                        clip
                        for clip in motion_response.json()["motion_library"]
                        if clip["slug"] == "jump"
                    )

                    assign_response = client.put(
                        f"/api/v1/motion/characters/{character_public_id}",
                        json={"motion_public_id": jump_clip["public_id"]},
                    )
                    assert assign_response.status_code == 200

                    render_response = client.post(
                        f"/api/v1/video/characters/{character_public_id}/render",
                        json={"width": 320, "height": 320, "duration_seconds": 1.1},
                    )
                    assert render_response.status_code == 202
                    queued_payload = render_response.json()
                    assert queued_payload["status"] == "queued"
                    assert queued_payload["step_name"] == "queued"
                    assert queued_payload["progress_percent"] == 0

                    render_payload = client.get("/api/v1/video").json()
                    rendered_character = next(
                        item
                        for item in render_payload["characters"]
                        if item["public_id"] == character_public_id
                    )
                    assert rendered_character["render_job"]["status"] == "queued"
                    assert (
                        rendered_character["render_job"]["job_public_id"]
                        == queued_payload["job_public_id"]
                    )
                    latest_video = rendered_character["latest_video"]
                    assert latest_video is not None
                    assert latest_video["motion_name"] == "Jump"
                    assert latest_video["job_public_id"] is not None
                    assert latest_video["url"] is None

                assert run_worker_once(session_factory) == "completed"

                with TestClient(app) as client:
                    render_payload = client.get("/api/v1/video").json()
                    rendered_character = next(
                        item
                        for item in render_payload["characters"]
                        if item["public_id"] == character_public_id
                    )
                    latest_video = rendered_character["latest_video"]
                    assert latest_video is not None
                    assert latest_video["url"] is not None

                    video_response = client.get(
                        f"/api/v1/video/assets/{latest_video['public_id']}.mp4"
                    )
                    assert video_response.status_code == 200
                    assert video_response.headers["content-type"].startswith("video/mp4")
                    assert len(video_response.content) > 0

                with session_factory() as session:
                    character_asset = session.scalar(
                        select(Asset).where(Asset.public_id == uuid.UUID(character_public_id))
                    )
                    motion_asset = session.scalar(
                        select(Asset).where(Asset.public_id == uuid.UUID(jump_clip["public_id"]))
                    )
                    video_asset = session.scalar(
                        select(Asset).where(Asset.public_id == uuid.UUID(latest_video["public_id"]))
                    )
                    job = session.scalar(
                        select(Job).where(Job.public_id == uuid.UUID(latest_video["job_public_id"]))
                    )
                    assert character_asset is not None
                    assert motion_asset is not None
                    assert video_asset is not None
                    assert job is not None

                    storage_object = session.scalar(
                        select(StorageObject).where(StorageObject.source_asset_id == video_asset.id)
                    )
                    history_types = list(
                        session.scalars(
                            select(HistoryEvent.event_type)
                            .where(
                                HistoryEvent.asset_id == character_asset.id,
                                HistoryEvent.event_type.like("video.%"),
                            )
                            .order_by(HistoryEvent.created_at.asc())
                        ).all()
                    )

                    assert video_asset.parent_asset_id == character_asset.id
                    assert video_asset.source_asset_id == motion_asset.id
                    assert video_asset.status == "available"
                    assert job.job_type == "character-motion-video-render"
                    assert job.status == "completed"
                    assert job.step_name == "completed"
                    assert storage_object is not None
                    assert Path(storage_object.storage_path).exists()
                    assert storage_object.byte_size is not None
                    assert storage_object.byte_size > 0
                    assert history_types == [
                        "video.render_requested",
                        "video.render_completed",
                        "video.output_registered",
                    ]
            finally:
                app.dependency_overrides.clear()
                engine.dispose()
