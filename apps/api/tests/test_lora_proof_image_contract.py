import uuid
from pathlib import Path
from tempfile import TemporaryDirectory

from _pytest.monkeypatch import MonkeyPatch
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.db.session import get_db_session
from app.main import app
from app.models.asset import Asset
from app.models.storage_object import StorageObject
from app.services.lora_training import register_lora_model
from tests.db_test_utils import migrated_database
from tests.test_lora_training_api import (
    _configure_storage,
    _create_character_and_dataset,
    _override_db_session,
    _session_factory,
)


def test_lora_proof_generation_stays_truthful_when_runtime_dependencies_are_missing(
    monkeypatch: MonkeyPatch,
) -> None:
    with migrated_database("phase05_lora_proof_blocked") as database_url:
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

                with session_factory() as session:
                    output_path = (
                        nas_root
                        / "models"
                        / "loras"
                        / "trained"
                        / str(character_public_id)
                        / "current.safetensors"
                    )
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    output_path.write_bytes(b"trained-lora")

                    with session.begin():
                        current_entry = register_lora_model(
                            session,
                            character_public_id,
                            details={"job_public_id": str(uuid.uuid4()), "job_status": "completed"},
                            model_name=output_path.name,
                            prompt_handle="@character_phase05_current",
                            status="current",
                            storage_path=output_path,
                            toolkit_name="ai-toolkit",
                        )

                with TestClient(app) as client:
                    lora_payload = client.get(
                        f"/api/v1/lora/characters/{character_public_id}"
                    ).json()
                    assert lora_payload["capability"]["status"] == "unavailable"
                    assert lora_payload["active_model"] is not None

                    workspace_payload = client.get("/api/v1/generation").json()
                    assert workspace_payload["generation_capability"]["status"] == "unavailable"
                    assert workspace_payload["local_loras"] == [
                        {
                            "character_public_id": str(character_public_id),
                            "model_name": output_path.name,
                            "owner_label": "Phase 21 LoRA subject",
                            "prompt_handle": "@character_phase05_current",
                            "registry_public_id": str(current_entry.public_id),
                            "source": "local",
                            "status": "current",
                            "storage_path": str(output_path),
                            "toolkit_name": "ai-toolkit",
                        }
                    ]

                    generation_response = client.post(
                        "/api/v1/generation/requests",
                        json={
                            "external_lora_registry_public_id": None,
                            "local_lora_registry_public_id": str(current_entry.public_id),
                            "prompt_text": "@character_phase05_current studio portrait",
                            "target_kind": "image",
                        },
                    )
                    assert generation_response.status_code == 201
                    generation_payload = generation_response.json()
                    assert generation_payload["status"] == "staged"
                    assert generation_payload["provider_status"] == "unavailable"
                    assert generation_payload["local_lora"]["registry_public_id"] == str(
                        current_entry.public_id
                    )

                with session_factory() as session:
                    request_assets = session.scalars(
                        select(Asset).where(Asset.asset_type == "generation-request")
                    ).all()
                    proof_storage = session.scalars(
                        select(StorageObject).where(
                            StorageObject.source_asset_id.in_(
                                [asset.id for asset in request_assets]
                            )
                        )
                    ).all()

                    assert len(request_assets) == 1
                    assert proof_storage == []
            finally:
                app.dependency_overrides.clear()
                engine.dispose()
