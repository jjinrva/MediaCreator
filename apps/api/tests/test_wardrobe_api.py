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


def _configure_storage(monkeypatch: MonkeyPatch, temp_path: Path) -> None:
    nas_root = temp_path / "nas"
    scratch_root = temp_path / "scratch"
    nas_root.mkdir()
    scratch_root.mkdir()

    monkeypatch.setenv("MEDIACREATOR_STORAGE_NAS_ROOT", str(nas_root))
    monkeypatch.setenv("MEDIACREATOR_STORAGE_SCRATCH_ROOT", str(scratch_root))
    monkeypatch.setenv("MEDIACREATOR_STORAGE_WARDROBE_ROOT", str(nas_root / "wardrobe"))
    monkeypatch.setenv(
        "MEDIACREATOR_STORAGE_UPLOADED_PHOTOS_ROOT",
        str(nas_root / "photos" / "uploaded"),
    )
    monkeypatch.setenv(
        "MEDIACREATOR_STORAGE_PREPARED_IMAGES_ROOT",
        str(nas_root / "photos" / "prepared"),
    )
    monkeypatch.delenv("MEDIACREATOR_COMFYUI_BASE_URL", raising=False)
    monkeypatch.setenv(
        "MEDIACREATOR_COMFYUI_WORKFLOWS_ROOT",
        str(temp_path / "missing-workflows"),
    )


def test_wardrobe_catalog_supports_photo_and_prompt_paths_with_persistent_metadata(
    monkeypatch: MonkeyPatch,
) -> None:
    with migrated_database("wardrobe_api") as database_url:
        engine, session_factory = _session_factory(database_url)
        app.dependency_overrides[get_db_session] = _override_db_session(session_factory)

        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            _configure_storage(monkeypatch, temp_path)

            try:
                with TestClient(app) as client:
                    photo_response = client.post(
                        "/api/v1/wardrobe/from-photo",
                        data={
                            "label": "Black tank top",
                            "garment_type": "tank top",
                            "material": "cotton",
                            "base_color": "black",
                        },
                        files=[
                            (
                                "photo",
                                (
                                    "male_body_front.png",
                                    _sample_image_bytes("male_body_front.png"),
                                    "image/png",
                                ),
                            )
                        ],
                    )
                    assert photo_response.status_code == 201
                    photo_payload = photo_response.json()
                    assert photo_payload["items"][0]["creation_path"] == "photo"
                    assert photo_payload["items"][0]["label"] == "Black tank top"
                    assert photo_payload["items"][0]["material"] == "cotton"
                    assert photo_payload["items"][0]["base_color"] == "black"
                    photo_public_id = photo_payload["items"][0]["public_id"]

                    source_response = client.get(
                        f"/api/v1/wardrobe/{photo_public_id}/source-photo"
                    )
                    assert source_response.status_code == 200
                    assert source_response.headers["content-type"] == "image/png"

                    prompt_response = client.post(
                        "/api/v1/wardrobe/from-prompt",
                        json={
                            "label": "Prompt leather jacket",
                            "garment_type": "jacket",
                            "material": "leather",
                            "base_color": "brown",
                            "prompt_text": "brown leather jacket with silver zipper",
                        },
                    )
                    assert prompt_response.status_code == 201
                    prompt_payload = prompt_response.json()
                    assert prompt_payload["generation_capability"]["status"] == "unavailable"
                    assert len(prompt_payload["items"]) == 2

                    prompt_item = next(
                        item
                        for item in prompt_payload["items"]
                        if item["creation_path"] == "ai-prompt"
                    )
                    assert prompt_item["label"] == "Prompt leather jacket"
                    assert prompt_item["material"] == "leather"
                    assert prompt_item["base_color"] == "brown"
                    assert (
                        prompt_item["prompt_text"] == "brown leather jacket with silver zipper"
                    )

                    catalog_response = client.get("/api/v1/wardrobe")
                    assert catalog_response.status_code == 200
                    catalog_payload = catalog_response.json()
                    assert len(catalog_payload["items"]) == 2
                    assert [item["label"] for item in catalog_payload["items"]] == [
                        "Black tank top",
                        "Prompt leather jacket",
                    ]
                    assert catalog_payload["items"][0]["material"] == "cotton"
                    assert catalog_payload["items"][1]["material"] == "leather"

                with session_factory() as session:
                    wardrobe_assets = session.scalars(
                        select(Asset).where(Asset.asset_type == "wardrobe-item")
                    ).all()
                    color_assets = session.scalars(
                        select(Asset).where(Asset.asset_type == "wardrobe-color-variant")
                    ).all()
                    material_assets = session.scalars(
                        select(Asset).where(Asset.asset_type == "wardrobe-material-variant")
                    ).all()
                    fitting_assets = session.scalars(
                        select(Asset).where(Asset.asset_type == "wardrobe-fitting-profile")
                    ).all()
                    created_events = session.scalars(
                        select(HistoryEvent).where(
                            HistoryEvent.event_type.in_(
                                ("wardrobe.created_from_photo", "wardrobe.created_from_prompt")
                            )
                        )
                    ).all()
                    photo_storage = session.scalar(
                        select(StorageObject).where(
                            StorageObject.object_type == "wardrobe-photo-source"
                        )
                    )
                    prompt_storage = session.scalar(
                        select(StorageObject).where(
                            StorageObject.object_type == "wardrobe-ai-prompt-manifest"
                        )
                    )

                    assert len(wardrobe_assets) == 2
                    assert len(color_assets) == 2
                    assert len(material_assets) == 2
                    assert len(fitting_assets) == 2
                    assert len(created_events) == 2
                    assert photo_storage is not None
                    assert prompt_storage is not None
                    assert Path(photo_storage.storage_path).exists()
                    assert Path(prompt_storage.storage_path).exists()
            finally:
                app.dependency_overrides.clear()
                engine.dispose()
