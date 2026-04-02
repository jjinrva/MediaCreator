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
from app.models.history_event import HistoryEvent
from app.services.blender_runtime import build_preview_export_job_payload
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


def _configure_storage(monkeypatch: MonkeyPatch, temp_path: Path) -> None:
    nas_root = temp_path / "nas"
    scratch_root = temp_path / "scratch"
    nas_root.mkdir()
    scratch_root.mkdir()

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


def _create_character(client: TestClient) -> str:
    photoset_response = client.post(
        "/api/v1/photosets",
        data={"character_label": "Motion test character"},
        files=[
            (
                "photos",
                (
                    "male_body_front.png",
                    _sample_image_bytes("male_body_front.png"),
                    "image/png",
                ),
            )
        ],
    )
    assert photoset_response.status_code == 201

    create_response = client.post(
        "/api/v1/characters",
        json={"photoset_public_id": photoset_response.json()["public_id"]},
    )
    assert create_response.status_code == 201
    return str(create_response.json()["public_id"])


def test_motion_library_lists_seeded_actions_assigns_characters_and_updates_preview_payload(
    monkeypatch: MonkeyPatch,
) -> None:
    with migrated_database("motion_library_api") as database_url:
        engine, session_factory = _session_factory(database_url)
        app.dependency_overrides[get_db_session] = _override_db_session(session_factory)

        with TemporaryDirectory() as temp_dir:
            _configure_storage(monkeypatch, Path(temp_dir))

            try:
                with TestClient(app) as client:
                    character_public_id = _create_character(client)

                    motion_response = client.get("/api/v1/motion")
                    assert motion_response.status_code == 200
                    motion_payload = motion_response.json()
                    assert [clip["name"] for clip in motion_payload["motion_library"]] == [
                        "Idle",
                        "Walk",
                        "Jump",
                        "Sit",
                        "Turn",
                    ]
                    walk_clip = next(
                        clip for clip in motion_payload["motion_library"] if clip["slug"] == "walk"
                    )
                    assert Path(walk_clip["action_payload_path"]).exists()

                    assign_response = client.put(
                        f"/api/v1/motion/characters/{character_public_id}",
                        json={"motion_public_id": walk_clip["public_id"]},
                    )
                    assert assign_response.status_code == 200
                    assign_payload = assign_response.json()
                    assigned_character = next(
                        item
                        for item in assign_payload["characters"]
                        if item["public_id"] == character_public_id
                    )
                    assert assigned_character["current_motion"]["motion_name"] == "Walk"

                with session_factory() as session:
                    preview_payload = build_preview_export_job_payload(
                        session,
                        uuid.UUID(character_public_id),
                    )
                    history_event = session.scalar(
                        select(HistoryEvent).where(
                            HistoryEvent.event_type == "character.motion_assigned"
                        )
                    )

                    assert preview_payload["motion_clip_name"] == "Walk"
                    assert str(preview_payload["motion_payload_path"]).endswith("walk.json")
                    assert history_event is not None
            finally:
                app.dependency_overrides.clear()
                engine.dispose()
