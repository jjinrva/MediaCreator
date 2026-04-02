from collections.abc import Callable, Generator
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory

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


def test_photoset_upload_persists_derivatives_and_stable_qc_payload(
    monkeypatch: MonkeyPatch,
) -> None:
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
                    assert payload["entry_count"] == 2
                    assert len(payload["entries"]) == 2

                    photoset_public_id = payload["public_id"]
                    first_entry = payload["entries"][0]
                    assert first_entry["qc_status"] in {"pass", "warn", "fail"}
                    assert set(first_entry["qc_metrics"]) == {
                        "face_detected",
                        "body_landmarks_detected",
                        "blur_score",
                        "exposure_score",
                        "framing_label",
                    }

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
                    assert [event.event_type for event in history_events] == [
                        "photoset.created",
                        "photo.prepared",
                        "photo.prepared",
                    ]

                    for storage_object in storage_objects:
                        assert Path(storage_object.storage_path).exists()
            finally:
                app.dependency_overrides.clear()
                engine.dispose()
