import uuid
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import cast

import pytest
from _pytest.monkeypatch import MonkeyPatch
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.main import app
from app.services.lora_training import (
    get_character_lora_training_payload,
    register_lora_model,
    resolve_active_lora_artifact,
)
from app.services.prompt_expansion import get_generation_workspace_payload
from tests import test_lora_training_api as _lora_training_api
from tests.db_test_utils import migrated_database
from tests.test_lora_training_api import (
    _configure_storage,
    _create_character_and_dataset,
    _override_db_session,
    _session_factory,
)

test_lora_training_route_reports_truthful_disabled_state_when_ai_toolkit_is_missing = (
    _lora_training_api.test_lora_training_route_reports_truthful_disabled_state_when_ai_toolkit_is_missing
)


def test_current_lora_registry_entries_require_real_artifacts_for_activation(
    monkeypatch: MonkeyPatch,
) -> None:
    with migrated_database("phase05_lora_current_artifact_truth") as database_url:
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
                from fastapi.testclient import TestClient

                with TestClient(app) as client:
                    character_public_id = uuid.UUID(
                        _create_character_and_dataset(client, session_factory)
                    )

                with session_factory() as session:
                    _assert_missing_artifact_is_rejected(
                        session,
                        character_public_id=character_public_id,
                        nas_root=nas_root,
                    )
                    _assert_deleted_artifact_is_not_reported_as_active(
                        session,
                        character_public_id=character_public_id,
                        nas_root=nas_root,
                    )
            finally:
                app.dependency_overrides.clear()
                engine.dispose()


def _assert_missing_artifact_is_rejected(
    session: Session,
    *,
    character_public_id: uuid.UUID,
    nas_root: Path,
) -> None:
    missing_output_path = (
        nas_root
        / "models"
        / "loras"
        / "trained"
        / str(character_public_id)
        / "missing-current.safetensors"
    )
    with session.begin():
        with pytest.raises(ValueError, match="real artifact file"):
            register_lora_model(
                session,
                character_public_id,
                details={"job_public_id": str(uuid.uuid4()), "job_status": "completed"},
                model_name=missing_output_path.name,
                prompt_handle="@character_phase05_missing",
                status="current",
                storage_path=missing_output_path,
                toolkit_name="ai-toolkit",
            )


def _assert_deleted_artifact_is_not_reported_as_active(
    session: Session,
    *,
    character_public_id: uuid.UUID,
    nas_root: Path,
) -> None:
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

    assert resolve_active_lora_artifact(session, character_public_id) is not None

    output_path.unlink()

    payload = get_character_lora_training_payload(session, character_public_id)
    assert payload is not None
    assert payload["active_model"] is None

    registry_entries = cast(list[dict[str, object]], payload["registry"])
    current_payload = next(
        entry for entry in registry_entries if entry["public_id"] == current_entry.public_id
    )
    assert current_payload["status"] == "artifact-missing"

    workspace = get_generation_workspace_payload(session)
    assert workspace["local_loras"] == []
