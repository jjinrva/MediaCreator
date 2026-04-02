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
from app.models.body_parameters import BodyParameter
from app.models.history_event import HistoryEvent
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


def test_body_parameter_catalog_and_default_rows_are_available_for_a_character(
    monkeypatch: MonkeyPatch,
) -> None:
    with migrated_database("body_api") as database_url:
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
                        data={"character_label": "Phase 13 body subject"},
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

                    body_response = client.get(
                        f"/api/v1/body/characters/{character_public_id}"
                    )
                    assert body_response.status_code == 200
                    payload = body_response.json()
                    assert payload["character_public_id"] == character_public_id
                    assert len(payload["catalog"]) == 8
                    assert [entry["key"] for entry in payload["catalog"]] == [
                        "height_scale",
                        "shoulder_width",
                        "chest_volume",
                        "waist_width",
                        "hip_width",
                        "upper_arm_volume",
                        "thigh_volume",
                        "calf_volume",
                    ]
                    assert payload["current_values"] == {
                        "height_scale": 1.0,
                        "shoulder_width": 1.0,
                        "chest_volume": 1.0,
                        "waist_width": 1.0,
                        "hip_width": 1.0,
                        "upper_arm_volume": 1.0,
                        "thigh_volume": 1.0,
                        "calf_volume": 1.0,
                    }

                with session_factory() as session:
                    stored_rows = session.scalars(
                        select(BodyParameter).order_by(BodyParameter.created_at.asc())
                    ).all()
                    assert len(stored_rows) == 8
                    assert {row.parameter_key for row in stored_rows} == {
                        "height_scale",
                        "shoulder_width",
                        "chest_volume",
                        "waist_width",
                        "hip_width",
                        "upper_arm_volume",
                        "thigh_volume",
                        "calf_volume",
                    }
            finally:
                app.dependency_overrides.clear()
                engine.dispose()


def test_body_parameter_updates_persist_and_write_history(
    monkeypatch: MonkeyPatch,
) -> None:
    with migrated_database("body_api_update") as database_url:
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
                        data={"character_label": "Phase 14 body subject"},
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
                        f"/api/v1/body/characters/{character_public_id}",
                        json={
                            "parameter_key": "shoulder_width",
                            "numeric_value": 1.09,
                        },
                    )
                    assert update_response.status_code == 200
                    payload = update_response.json()
                    assert payload["current_values"]["shoulder_width"] == 1.09

                with session_factory() as session:
                    shoulder_width_row = session.scalar(
                        select(BodyParameter).where(
                            BodyParameter.parameter_key == "shoulder_width"
                        )
                    )
                    history_events = session.scalars(
                        select(HistoryEvent)
                        .where(HistoryEvent.event_type == "body.parameter_updated")
                        .order_by(HistoryEvent.created_at.asc())
                    ).all()

                    assert shoulder_width_row is not None
                    assert shoulder_width_row.numeric_value == 1.09
                    assert len(history_events) == 1
                    assert history_events[0].details["parameter_key"] == "shoulder_width"
                    assert history_events[0].details["previous_value"] == 1.0
                    assert history_events[0].details["numeric_value"] == 1.09
            finally:
                app.dependency_overrides.clear()
                engine.dispose()
