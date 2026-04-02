import json
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


def test_lora_dataset_route_writes_dataset_files_manifest_and_prompt_contract(
    monkeypatch: MonkeyPatch,
) -> None:
    with migrated_database("lora_dataset_api") as database_url:
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
            monkeypatch.setenv(
                "MEDIACREATOR_STORAGE_LORAS_ROOT",
                str(nas_root / "models" / "loras"),
            )
            monkeypatch.setenv("MEDIACREATOR_STORAGE_SCRATCH_ROOT", str(scratch_root))

            try:
                with TestClient(app) as client:
                    photoset_response = client.post(
                        "/api/v1/photosets",
                        data={"character_label": "Phase 20 dataset subject"},
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

                    create_response = client.post(
                        "/api/v1/characters",
                        json={"photoset_public_id": photoset_response.json()["public_id"]},
                    )
                    assert create_response.status_code == 201
                    character_public_id = create_response.json()["public_id"]

                    dataset_response = client.post(
                        f"/api/v1/lora-datasets/characters/{character_public_id}"
                    )
                    assert dataset_response.status_code == 200
                    payload = dataset_response.json()
                    assert payload["dataset"]["status"] == "available"
                    assert payload["dataset"]["entry_count"] == 2
                    assert payload["dataset"]["prompt_handle"].startswith("@character_")
                    assert payload["dataset"]["prompt_expansion"]

                    manifest_response = client.get(
                        f"/api/v1/lora-datasets/characters/{character_public_id}/manifest.json"
                    )
                    assert manifest_response.status_code == 200
                    manifest = manifest_response.json()
                    assert manifest["dataset_version"] == "dataset-v1"
                    assert manifest["entry_count"] == 2
                    assert manifest["prompt_contract"]["version"] == "prompt-contract-v1"
                    assert (
                        manifest["prompt_contract"]["handle"]
                        == payload["dataset"]["prompt_handle"]
                    )
                    assert manifest["entries"][0]["image_file"].endswith(".png")
                    assert manifest["entries"][0]["caption_file"].endswith(".txt")

                with session_factory() as session:
                    manifest_storage = session.scalar(
                        select(StorageObject).where(
                            StorageObject.object_type == "character-lora-dataset-manifest"
                        )
                    )
                    history_event = session.scalar(
                        select(HistoryEvent).where(HistoryEvent.event_type == "lora_dataset.built")
                    )

                    assert manifest_storage is not None
                    manifest_file = Path(manifest_storage.storage_path)
                    assert manifest_file.exists()
                    manifest_json = json.loads(manifest_file.read_text(encoding="utf-8"))
                    dataset_root = manifest_file.parent
                    for entry in manifest_json["entries"]:
                        assert (dataset_root / entry["image_file"]).exists()
                        assert (dataset_root / entry["caption_file"]).exists()
                    assert history_event is not None
            finally:
                app.dependency_overrides.clear()
                engine.dispose()
