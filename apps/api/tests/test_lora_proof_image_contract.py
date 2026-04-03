import json
import uuid
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Literal

from _pytest.monkeypatch import MonkeyPatch
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.db.session import get_db_session
from app.main import app
from app.models.asset import Asset
from app.models.job import Job
from app.models.storage_object import StorageObject
from app.services.jobs import run_worker_once
from app.services.lora_training import register_lora_model
from tests.db_test_utils import migrated_database
from tests.test_lora_training_api import (
    _configure_storage,
    _create_character_and_dataset,
    _override_db_session,
    _session_factory,
)

PNG_BYTES = (
    b"\x89PNG\r\n\x1a\n"
    b"\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f"
    b"\x15\xc4\x89\x00\x00\x00\rIDATx\x9cc\xf8\xcf\xc0\xf0\x1f\x00\x05\x00\x01"
    b"\xff\x89\x99=\x1d\x00\x00\x00\x00IEND\xaeB`\x82"
)


def _write_validated_generation_workflows(workflows_root: Path) -> None:
    workflows_root.mkdir(parents=True, exist_ok=True)
    contracts = {
        "text_to_image_v1.json": {
            "workflow_id": "text_to_image_v1",
            "version": 2,
            "purpose": "Validated text-to-image proof-image contract.",
            "provider": "comfyui",
            "target_kind": "image",
            "nodes": [
                {"id": "1", "class_type": "CheckpointLoaderSimple"},
                {"id": "2", "class_type": "CLIPTextEncode"},
                {"id": "3", "class_type": "KSampler"},
                {"id": "4", "class_type": "VAEDecode"},
                {"id": "5", "class_type": "SaveImage"},
            ],
            "prompt_api": {
                "1": {
                    "class_type": "CheckpointLoaderSimple",
                    "inputs": {"ckpt_name": "{{checkpoint_name}}"},
                },
                "2": {
                    "class_type": "CLIPTextEncode",
                    "inputs": {"text": "{{prompt}}"},
                },
                "3": {"class_type": "KSampler", "inputs": {"seed": 1}},
                "4": {"class_type": "VAEDecode", "inputs": {"vae_name": "{{vae_name}}"}},
                "5": {
                    "class_type": "SaveImage",
                    "inputs": {"filename_prefix": "{{filename_prefix}}"},
                },
            },
        },
        "character_refine_img2img_v1.json": {
            "workflow_id": "character_refine_img2img_v1",
            "version": 2,
            "purpose": "Validated character refinement proof-image contract.",
            "provider": "comfyui",
            "target_kind": "image",
            "nodes": [
                {"id": "1", "class_type": "LoadImage"},
                {"id": "2", "class_type": "KSampler"},
                {"id": "3", "class_type": "VAEDecode"},
                {"id": "4", "class_type": "SaveImage"},
            ],
            "prompt_api": {
                "1": {"class_type": "LoadImage", "inputs": {"image": "reference.png"}},
                "2": {"class_type": "KSampler", "inputs": {"seed": 2}},
                "3": {"class_type": "VAEDecode", "inputs": {"vae_name": "{{vae_name}}"}},
                "4": {
                    "class_type": "SaveImage",
                    "inputs": {"filename_prefix": "{{filename_prefix}}"},
                },
            },
        },
    }
    for filename, payload in contracts.items():
        (workflows_root / filename).write_text(json.dumps(payload), encoding="utf-8")


class _FakeUrlopenResponse:
    def __init__(self, body: bytes) -> None:
        self._body = body

    def __enter__(self) -> "_FakeUrlopenResponse":
        return self

    def __exit__(self, *_args: object) -> Literal[False]:
        return False

    def read(self) -> bytes:
        return self._body


def _fake_comfyui_urlopen(request: object, timeout: float = 0.0) -> _FakeUrlopenResponse:
    del timeout
    request_url = getattr(request, "full_url", str(request))
    if request_url.endswith("/prompt"):
        return _FakeUrlopenResponse(
            json.dumps({"prompt_id": "proof-prompt-1"}).encode("utf-8")
        )
    if "/history/" in request_url:
        return _FakeUrlopenResponse(
            json.dumps(
                {
                    "proof-prompt-1": {
                        "outputs": {
                            "5": {
                                "images": [
                                    {
                                        "filename": "proof.png",
                                        "subfolder": "mediacreator",
                                        "type": "output",
                                    }
                                ]
                            }
                        }
                    }
                }
            ).encode("utf-8")
        )
    if "/view?" in request_url:
        return _FakeUrlopenResponse(PNG_BYTES)
    raise AssertionError(f"Unexpected ComfyUI request: {request_url}")


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
                    character_public_id = uuid.UUID(
                        _create_character_and_dataset(client, session_factory)
                    )

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
                    assert generation_payload["proof_image_job"]["status"] == "not-queued"
                    assert generation_payload["proof_image_artifact"] is None
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


def test_ready_generation_runtime_writes_a_real_saved_proof_image_and_lineage(
    monkeypatch: MonkeyPatch,
) -> None:
    with migrated_database("phase05_generation_proof_ready") as database_url:
        engine, session_factory = _session_factory(database_url)
        app.dependency_overrides[get_db_session] = _override_db_session(session_factory)

        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            nas_root = _configure_storage(monkeypatch, temp_path)
            workflows_root = temp_path / "workflows" / "comfyui"
            _write_validated_generation_workflows(workflows_root)
            checkpoints_root = nas_root / "models" / "checkpoints"
            vaes_root = nas_root / "models" / "vaes"
            checkpoints_root.mkdir(parents=True, exist_ok=True)
            vaes_root.mkdir(parents=True, exist_ok=True)
            (checkpoints_root / "sdxl-base.safetensors").write_text(
                "checkpoint",
                encoding="utf-8",
            )
            (vaes_root / "sdxl.vae.pt").write_text("vae", encoding="utf-8")
            monkeypatch.setenv("MEDIACREATOR_COMFYUI_BASE_URL", "http://comfyui.test:8188")
            monkeypatch.setenv("MEDIACREATOR_COMFYUI_WORKFLOWS_ROOT", str(workflows_root))
            monkeypatch.setenv(
                "MEDIACREATOR_STORAGE_CHECKPOINTS_ROOT",
                str(checkpoints_root),
            )
            monkeypatch.setenv("MEDIACREATOR_STORAGE_VAES_ROOT", str(vaes_root))
            monkeypatch.setattr(
                "app.services.generation_provider.ping_comfyui_service",
                lambda _base_url: True,
            )
            monkeypatch.setattr(
                "app.services.generation_execution.urlopen",
                _fake_comfyui_urlopen,
            )

            try:
                with TestClient(app) as client:
                    character_public_id = uuid.UUID(
                        _create_character_and_dataset(client, session_factory)
                    )

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
                    assert generation_payload["status"] == "queued"
                    assert generation_payload["provider_status"] == "ready"
                    assert generation_payload["proof_image_job"]["status"] == "queued"
                    assert generation_payload["proof_image_artifact"] is None
                    request_public_id = uuid.UUID(generation_payload["public_id"])

                worker_result = run_worker_once(session_factory)
                assert worker_result == "completed"

                with TestClient(app) as client:
                    proof_response = client.get(
                        f"/api/v1/generation/requests/{request_public_id}/proof-image"
                    )
                    assert proof_response.status_code == 200
                    assert proof_response.content == PNG_BYTES

                with session_factory() as session:
                    character_asset = session.scalar(
                        select(Asset).where(Asset.public_id == character_public_id)
                    )
                    request_asset = session.scalar(
                        select(Asset).where(Asset.public_id == request_public_id)
                    )
                    assert character_asset is not None
                    assert request_asset is not None
                    assert request_asset.asset_type == "generation-request"
                    assert request_asset.status == "completed"
                    assert request_asset.source_asset_id == character_asset.id

                    proof_asset = session.scalar(
                        select(Asset).where(
                            Asset.asset_type == "generation-proof-image",
                            Asset.source_asset_id == request_asset.id,
                        )
                    )
                    assert proof_asset is not None
                    assert proof_asset.parent_asset_id == character_asset.id
                    assert proof_asset.status == "available"

                    proof_job = session.scalar(
                        select(Job).where(
                            Job.job_type == "generation-proof-image",
                            Job.output_asset_id == proof_asset.id,
                        )
                    )
                    assert proof_job is not None
                    assert proof_job.status == "completed"
                    assert proof_job.output_storage_object_id is not None

                    proof_storage = session.scalar(
                        select(StorageObject).where(StorageObject.source_asset_id == proof_asset.id)
                    )
                    assert proof_storage is not None
                    assert proof_storage.id == proof_job.output_storage_object_id
                    assert proof_storage.object_type == "generation-proof-image"
                    assert proof_storage.byte_size == len(PNG_BYTES)
                    assert Path(proof_storage.storage_path).exists()
                    assert Path(proof_storage.storage_path).read_bytes() == PNG_BYTES
            finally:
                app.dependency_overrides.clear()
                engine.dispose()
