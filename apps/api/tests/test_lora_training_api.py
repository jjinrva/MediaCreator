import uuid
from collections.abc import Callable, Generator
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import cast

from _pytest.monkeypatch import MonkeyPatch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.session import get_db_session
from app.main import app
from app.models.models_registry import ModelRegistry
from app.services.generation_provider import resolve_generation_lora_activation
from app.services.lora_training import (
    get_character_lora_training_payload,
    register_lora_model,
    resolve_active_lora_artifact,
)
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


def _configure_storage(monkeypatch: MonkeyPatch, temp_path: Path) -> Path:
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
    return nas_root


def _create_character_and_dataset(client: TestClient) -> str:
    photoset_response = client.post(
        "/api/v1/photosets",
        data={"character_label": "Phase 21 LoRA subject"},
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
    character_public_id = str(create_response.json()["public_id"])

    dataset_response = client.post(f"/api/v1/lora-datasets/characters/{character_public_id}")
    assert dataset_response.status_code == 200
    assert dataset_response.json()["dataset"]["status"] == "available"
    return character_public_id


def test_lora_training_route_reports_truthful_disabled_state_when_ai_toolkit_is_missing(
    monkeypatch: MonkeyPatch,
) -> None:
    with migrated_database("lora_training_missing") as database_url:
        engine, session_factory = _session_factory(database_url)
        app.dependency_overrides[get_db_session] = _override_db_session(session_factory)

        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            _configure_storage(monkeypatch, temp_path)
            monkeypatch.setattr(
                "app.services.lora_training._resolve_ai_toolkit_bin",
                lambda *_: None,
            )

            try:
                with TestClient(app) as client:
                    character_public_id = _create_character_and_dataset(client)

                    response = client.get(f"/api/v1/lora/characters/{character_public_id}")
                    assert response.status_code == 200
                    payload = response.json()
                    assert payload["capability"]["status"] == "unavailable"
                    assert "ai_toolkit_missing" in payload["capability"]["missing_requirements"]
                    assert payload["training_job"]["status"] == "not-queued"
                    assert payload["active_model"] is None
                    assert payload["registry"] == []

                    training_response = client.post(
                        f"/api/v1/lora/characters/{character_public_id}"
                    )
                    assert training_response.status_code == 400
                    assert "unavailable" in training_response.json()["detail"]
            finally:
                app.dependency_overrides.clear()
                engine.dispose()


def test_lora_registry_tracks_statuses_and_resolves_active_generation_model(
    monkeypatch: MonkeyPatch,
) -> None:
    with migrated_database("lora_training_registry") as database_url:
        engine, session_factory = _session_factory(database_url)
        app.dependency_overrides[get_db_session] = _override_db_session(session_factory)

        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            nas_root = _configure_storage(monkeypatch, temp_path)
            monkeypatch.setattr(
                "app.services.lora_training._resolve_ai_toolkit_bin",
                lambda *_: None,
            )

            try:
                with TestClient(app) as client:
                    character_public_id = uuid.UUID(_create_character_and_dataset(client))

                    old_output_path = (
                        nas_root
                        / "models"
                        / "loras"
                        / "trained"
                        / str(character_public_id)
                        / "old-current.safetensors"
                    )
                    old_output_path.parent.mkdir(parents=True, exist_ok=True)
                    old_output_path.write_bytes(b"old-current")

                    current_output_path = old_output_path.with_name("current.safetensors")
                    current_output_path.write_bytes(b"current-model")

                with session_factory() as session:
                    with session.begin():
                        register_lora_model(
                            session,
                            character_public_id,
                            details={"job_public_id": str(uuid.uuid4()), "job_status": "completed"},
                            model_name=old_output_path.name,
                            prompt_handle="@character_phase21_old",
                            status="current",
                            storage_path=old_output_path,
                            toolkit_name="ai-toolkit",
                        )
                        register_lora_model(
                            session,
                            character_public_id,
                            details={"job_public_id": str(uuid.uuid4()), "job_status": "working"},
                            model_name="working-run",
                            prompt_handle="@character_phase21_working",
                            status="working",
                            storage_path=None,
                            toolkit_name="ai-toolkit",
                        )
                        register_lora_model(
                            session,
                            character_public_id,
                            details={
                                "error_summary": "toolkit crashed",
                                "job_public_id": str(uuid.uuid4()),
                                "job_status": "failed",
                            },
                            model_name="failed-run",
                            prompt_handle="@character_phase21_failed",
                            status="failed",
                            storage_path=None,
                            toolkit_name="ai-toolkit",
                        )
                        current_entry = register_lora_model(
                            session,
                            character_public_id,
                            details={"job_public_id": str(uuid.uuid4()), "job_status": "completed"},
                            model_name=current_output_path.name,
                            prompt_handle="@character_phase21_current",
                            status="current",
                            storage_path=current_output_path,
                            toolkit_name="ai-toolkit",
                        )

                    payload = get_character_lora_training_payload(session, character_public_id)
                    assert payload is not None
                    assert payload["active_model"] is not None
                    active_model = cast(dict[str, object], payload["active_model"])
                    assert active_model["model_name"] == current_output_path.name

                    active_artifact = resolve_active_lora_artifact(session, character_public_id)
                    assert active_artifact is not None
                    assert active_artifact["storage_path"] == str(current_output_path)

                    activation = resolve_generation_lora_activation(session, character_public_id)
                    assert activation is not None
                    assert activation.loader == "comfyui-lora-loader"
                    assert activation.model_name == current_output_path.name
                    assert activation.prompt_handle == "@character_phase21_current"
                    assert activation.storage_path == str(current_output_path)

                    registry_rows = session.query(ModelRegistry).all()
                    assert len(registry_rows) == 4
                    statuses = sorted(row.status for row in registry_rows)
                    assert statuses == ["archived", "current", "failed", "working"]
                    assert current_entry.status == "current"
            finally:
                app.dependency_overrides.clear()
                engine.dispose()
