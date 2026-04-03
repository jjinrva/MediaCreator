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
from app.models.storage_object import StorageObject
from app.services.jobs import run_worker_once
from tests.db_test_utils import migrated_database
from tests.photoset_test_utils import upload_photoset_and_complete_ingest

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


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


def test_preview_export_generates_base_texture_artifact_and_embeds_texture_data(
    monkeypatch: MonkeyPatch,
) -> None:
    with migrated_database("texture_pipeline_api") as database_url:
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
            monkeypatch.setenv(
                "MEDIACREATOR_STORAGE_CHARACTER_ASSETS_ROOT",
                str(nas_root / "characters"),
            )
            monkeypatch.setenv("MEDIACREATOR_STORAGE_SCRATCH_ROOT", str(scratch_root))

            try:
                with TestClient(app) as client:
                    _, photoset_payload = upload_photoset_and_complete_ingest(
                        client,
                        session_factory,
                        data={"character_label": "Phase 19 textured preview subject"},
                        files=[
                            (
                                "photos",
                                (
                                    "male_head_front.png",
                                    _sample_image_bytes("male_head_front.png"),
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

                    create_response = client.post(
                        "/api/v1/characters",
                        json={"photoset_public_id": photoset_payload["public_id"]},
                    )
                    assert create_response.status_code == 201
                    character_public_id = create_response.json()["public_id"]

                    export_response = client.post(
                        f"/api/v1/exports/characters/{character_public_id}/preview"
                    )
                    assert export_response.status_code == 202
                    assert export_response.json()["status"] == "queued"

                assert run_worker_once(session_factory) == "completed"

                with TestClient(app) as client:
                    payload = client.get(
                        f"/api/v1/exports/characters/{character_public_id}"
                    ).json()
                    assert (
                        payload["texture_material"]["current_texture_fidelity"]
                        == "base-textured"
                    )
                    assert (
                        payload["texture_material"]["base_texture_artifact"]["status"]
                        == "available"
                    )
                    assert payload["preview_glb"]["status"] == "available"

                    preview_response = client.get(
                        f"/api/v1/exports/characters/{character_public_id}/preview.glb"
                    )
                    assert preview_response.status_code == 200
                    assert PNG_SIGNATURE in preview_response.content

                    base_texture_response = client.get(
                        f"/api/v1/exports/characters/{character_public_id}/textures/base-color.png"
                    )
                    assert base_texture_response.status_code == 200
                    assert base_texture_response.headers["content-type"].startswith("image/png")

                with session_factory() as session:
                    base_texture_storage = session.scalar(
                        select(StorageObject).where(
                            StorageObject.object_type == "character-base-color-texture"
                        )
                    )
                    history_events = session.scalars(
                        select(HistoryEvent)
                        .where(
                            HistoryEvent.event_type.in_(
                                ["texture.generated", "export.preview_generated"]
                            )
                        )
                        .order_by(HistoryEvent.created_at.asc())
                    ).all()

                    assert base_texture_storage is not None
                    assert Path(base_texture_storage.storage_path).exists()
                    assert len(history_events) == 2
                    assert {event.event_type for event in history_events} == {
                        "texture.generated",
                        "export.preview_generated",
                    }
            finally:
                app.dependency_overrides.clear()
                engine.dispose()
