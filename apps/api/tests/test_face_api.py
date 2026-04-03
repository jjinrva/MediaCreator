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
from app.models.facial_parameters import FacialParameter
from app.models.history_event import HistoryEvent
from tests.db_test_utils import migrated_database
from tests.photoset_test_utils import upload_photoset_and_complete_ingest
from tests.test_characters_api import _build_qc_report, _patch_deterministic_qc


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


def test_facial_parameter_catalog_and_updates_persist(
    monkeypatch: MonkeyPatch,
) -> None:
    _patch_deterministic_qc(
        monkeypatch,
        [
            _build_qc_report("pass"),
            _build_qc_report(
                "warn",
                framing_label="head-closeup",
                reasons=["Portrait crop is LoRA-only."],
            ),
        ],
    )
    with migrated_database("face_api") as database_url:
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
                    _, photoset_payload = upload_photoset_and_complete_ingest(
                        client,
                        session_factory,
                        data={"character_label": "Phase 16 facial subject"},
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

                    get_response = client.get(f"/api/v1/face/characters/{character_public_id}")
                    assert get_response.status_code == 200
                    get_payload = get_response.json()
                    assert len(get_payload["catalog"]) == 6
                    assert get_payload["current_values"]["jaw_open"] == 0
                    assert get_payload["current_values"]["neutral_expression_blend"] == 1
                    assert get_payload["catalog"][0]["shape_key_name"] == "JawOpen"

                    update_response = client.put(
                        f"/api/v1/face/characters/{character_public_id}",
                        json={
                            "parameter_key": "jaw_open",
                            "numeric_value": 0.15,
                        },
                    )
                    assert update_response.status_code == 200
                    update_payload = update_response.json()
                    assert update_payload["current_values"]["jaw_open"] == 0.15

                with session_factory() as session:
                    jaw_open_row = session.scalar(
                        select(FacialParameter).where(FacialParameter.parameter_key == "jaw_open")
                    )
                    history_events = session.scalars(
                        select(HistoryEvent)
                        .where(HistoryEvent.event_type == "face.parameter_updated")
                        .order_by(HistoryEvent.created_at.asc())
                    ).all()

                    assert jaw_open_row is not None
                    assert jaw_open_row.numeric_value == 0.15
                    assert len(history_events) == 1
                    assert history_events[0].details["parameter_key"] == "jaw_open"
                    assert history_events[0].details["shape_key_name"] == "JawOpen"
                    assert history_events[0].details["previous_value"] == 0
                    assert history_events[0].details["numeric_value"] == 0.15
            finally:
                app.dependency_overrides.clear()
                engine.dispose()
