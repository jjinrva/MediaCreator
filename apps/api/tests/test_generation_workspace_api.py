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
from app.services.lora_training import register_lora_model
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
        data={"character_label": "Generation test character"},
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


def test_generation_workspace_expands_prompts_and_stores_local_lora_links(
    monkeypatch: MonkeyPatch,
) -> None:
    with migrated_database("generation_workspace_api") as database_url:
        engine, session_factory = _session_factory(database_url)
        app.dependency_overrides[get_db_session] = _override_db_session(session_factory)

        with TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            _configure_storage(monkeypatch, temp_root)

            try:
                with TestClient(app) as client:
                    character_public_id = _create_character(client)

                    with session_factory() as session:
                        with session.begin():
                            local_lora_path = (
                                temp_root
                                / "nas"
                                / "models"
                                / "loras"
                                / "trained"
                                / character_public_id
                                / "current.safetensors"
                            )
                            local_lora_path.parent.mkdir(parents=True, exist_ok=True)
                            local_lora_path.write_bytes(b"phase-25-local-lora")
                            registry_entry = register_lora_model(
                                session,
                                uuid.UUID(character_public_id),
                                details={"source": "test"},
                                model_name="phase-25-local.safetensors",
                                prompt_handle="@phase25_local",
                                status="current",
                                storage_path=local_lora_path,
                                toolkit_name="ai-toolkit",
                            )
                            local_lora_public_id = str(registry_entry.public_id)

                    workspace_response = client.get("/api/v1/generation")
                    assert workspace_response.status_code == 200
                    workspace_payload = workspace_response.json()
                    character_recipe = next(
                        item
                        for item in workspace_payload["characters"]
                        if item["public_id"] == character_public_id
                    )
                    assert character_recipe["prompt_handle"].startswith("@character_")
                    assert (
                        workspace_payload["local_loras"][0]["registry_public_id"]
                        == local_lora_public_id
                    )

                    raw_prompt = f"{character_recipe['prompt_handle']} standing on a bridge"
                    expand_response = client.post(
                        "/api/v1/generation/expand",
                        json={"prompt_text": raw_prompt},
                    )
                    assert expand_response.status_code == 200
                    expansion_payload = expand_response.json()
                    assert expansion_payload["matched_handles"] == [
                        character_recipe["prompt_handle"]
                    ]
                    assert "Generation test character" in expansion_payload["expanded_prompt"]

                    create_response = client.post(
                        "/api/v1/generation/requests",
                        json={
                            "local_lora_registry_public_id": local_lora_public_id,
                            "prompt_text": raw_prompt,
                            "target_kind": "image",
                        },
                    )
                    assert create_response.status_code == 201
                    request_payload = create_response.json()
                    assert (
                        request_payload["expanded_prompt"]
                        == expansion_payload["expanded_prompt"]
                    )
                    assert (
                        request_payload["local_lora"]["registry_public_id"]
                        == local_lora_public_id
                    )
                    assert request_payload["workflow_id"] == "text_to_image_v1"

                with session_factory() as session:
                    request_asset = session.scalar(
                        select(Asset).where(
                            Asset.public_id == uuid.UUID(request_payload["public_id"])
                        )
                    )
                    assert request_asset is not None
                    assert request_asset.asset_type == "generation-request"

                    history_event = session.scalar(
                        select(HistoryEvent).where(
                            HistoryEvent.asset_id == request_asset.id,
                            HistoryEvent.event_type == "generation.requested",
                        )
                    )
                    assert history_event is not None
                    assert history_event.details["raw_prompt"] == raw_prompt
                    assert (
                        history_event.details["expanded_prompt"]
                        == expansion_payload["expanded_prompt"]
                    )
                    local_lora = history_event.details["local_lora"]
                    assert isinstance(local_lora, dict)
                    assert local_lora["registry_public_id"] == local_lora_public_id
            finally:
                app.dependency_overrides.clear()
                engine.dispose()
