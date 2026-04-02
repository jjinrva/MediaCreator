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
from app.models.pose_state import PoseState
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


def test_pose_parameter_updates_persist_and_write_history(
    monkeypatch: MonkeyPatch,
) -> None:
    with migrated_database("pose_api") as database_url:
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
                    photoset_response = client.post(
                        "/api/v1/photosets",
                        data={"character_label": "Phase 15 pose subject"},
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
                    assert photoset_response.status_code == 201

                    character_response = client.post(
                        "/api/v1/characters",
                        json={"photoset_public_id": photoset_response.json()["public_id"]},
                    )
                    assert character_response.status_code == 201
                    character_public_id = character_response.json()["public_id"]

                    update_response = client.put(
                        f"/api/v1/pose/characters/{character_public_id}",
                        json={
                            "parameter_key": "upper_arm_l_pitch_deg",
                            "numeric_value": 10,
                        },
                    )
                    assert update_response.status_code == 200
                    payload = update_response.json()
                    assert payload["current_values"]["upper_arm_l_pitch_deg"] == 10

                with session_factory() as session:
                    left_arm_row = session.scalar(
                        select(PoseState).where(
                            PoseState.parameter_key == "upper_arm_l_pitch_deg"
                        )
                    )
                    history_events = session.scalars(
                        select(HistoryEvent)
                        .where(HistoryEvent.event_type == "pose.parameter_updated")
                        .order_by(HistoryEvent.created_at.asc())
                    ).all()

                    assert left_arm_row is not None
                    assert left_arm_row.numeric_value == 10
                    assert len(history_events) == 1
                    assert history_events[0].details["parameter_key"] == "upper_arm_l_pitch_deg"
                    assert history_events[0].details["bone_name"] == "upper_arm.L"
                    assert history_events[0].details["previous_value"] == 0
                    assert history_events[0].details["numeric_value"] == 10
            finally:
                app.dependency_overrides.clear()
                engine.dispose()
