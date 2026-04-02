import json
from pathlib import Path

from _pytest.monkeypatch import MonkeyPatch
from fastapi.testclient import TestClient

from app.main import app
from app.services.generation_provider import REQUIRED_WORKFLOW_FILES, get_generation_capability


def _configure_generation_env(monkeypatch: MonkeyPatch, tmp_path: Path) -> Path:
    nas_root = tmp_path / "nas"
    workflows_root = tmp_path / "workflows" / "comfyui"
    checkpoints_root = nas_root / "models" / "checkpoints"
    loras_root = nas_root / "models" / "loras"
    embeddings_root = nas_root / "models" / "embeddings"
    vaes_root = nas_root / "models" / "vaes"

    for path in (
        nas_root,
        workflows_root,
        checkpoints_root,
        loras_root,
        embeddings_root,
        vaes_root,
    ):
        path.mkdir(parents=True, exist_ok=True)

    monkeypatch.setenv("MEDIACREATOR_STORAGE_NAS_ROOT", str(nas_root))
    monkeypatch.setenv("MEDIACREATOR_STORAGE_SCRATCH_ROOT", str(tmp_path / "scratch"))
    monkeypatch.setenv("MEDIACREATOR_STORAGE_CHECKPOINTS_ROOT", str(checkpoints_root))
    monkeypatch.setenv("MEDIACREATOR_STORAGE_LORAS_ROOT", str(loras_root))
    monkeypatch.setenv("MEDIACREATOR_STORAGE_EMBEDDINGS_ROOT", str(embeddings_root))
    monkeypatch.setenv("MEDIACREATOR_STORAGE_VAES_ROOT", str(vaes_root))
    monkeypatch.setenv("MEDIACREATOR_COMFYUI_WORKFLOWS_ROOT", str(workflows_root))
    monkeypatch.setenv("MEDIACREATOR_COMFYUI_BASE_URL", "http://127.0.0.1:8188")
    return workflows_root


def _write_required_workflows(workflows_root: Path) -> None:
    for workflow_name in REQUIRED_WORKFLOW_FILES:
        workflow_path = workflows_root / workflow_name
        workflow_path.write_text(
            json.dumps(
                {
                    "workflow_id": workflow_name.removesuffix(".json"),
                    "version": 1,
                    "purpose": "Phase 06 capability contract placeholder",
                    "nodes": [],
                }
            ),
            encoding="utf-8",
        )


def test_system_status_reports_unavailable_when_comfyui_is_absent(
    monkeypatch: MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("MEDIACREATOR_STORAGE_NAS_ROOT", str(tmp_path / "missing-nas"))
    monkeypatch.setenv("MEDIACREATOR_STORAGE_SCRATCH_ROOT", str(tmp_path / "scratch"))
    monkeypatch.delenv("MEDIACREATOR_COMFYUI_BASE_URL", raising=False)
    monkeypatch.setenv(
        "MEDIACREATOR_COMFYUI_WORKFLOWS_ROOT",
        str(tmp_path / "missing-workflows"),
    )
    client = TestClient(app)

    response = client.get("/api/v1/system/status")

    assert response.status_code == 200
    payload = response.json()
    assert payload["generation"]["status"] == "unavailable"
    assert payload["generation"]["comfyui_base_url"] is None
    assert payload["generation"]["comfyui_service_reachable"] is False
    assert "comfyui_base_url_missing" in payload["generation"]["missing_requirements"]
    assert "workflows_root_missing" in payload["generation"]["missing_requirements"]
    assert payload["generation"]["status"] != "ready"


def test_system_status_validates_workflows_and_nas_model_roots(
    monkeypatch: MonkeyPatch, tmp_path: Path
) -> None:
    workflows_root = _configure_generation_env(monkeypatch, tmp_path)
    _write_required_workflows(workflows_root)
    checkpoints_root = tmp_path / "nas" / "models" / "checkpoints"
    vaes_root = tmp_path / "nas" / "models" / "vaes"
    (checkpoints_root / "sdxl-base.safetensors").write_text("checkpoint", encoding="utf-8")
    (vaes_root / "sdxl.vae.pt").write_text("vae", encoding="utf-8")
    monkeypatch.setattr(
        "app.services.generation_provider.ping_comfyui_service",
        lambda _base_url: True,
    )
    client = TestClient(app)

    response = client.get("/api/v1/system/status")

    assert response.status_code == 200
    payload = response.json()
    assert payload["generation"]["status"] == "ready"
    assert payload["generation"]["model_roots_on_nas"] is True
    assert payload["generation"]["missing_workflow_files"] == []
    assert payload["generation"]["checkpoint_files_detected"] == ["sdxl-base.safetensors"]
    assert payload["generation"]["vae_files_detected"] == ["sdxl.vae.pt"]
    assert payload["generation"]["checkpoints_root"] == str(checkpoints_root)
    assert payload["generation"]["vaes_root"] == str(vaes_root)
    assert payload["generation"]["embeddings_root"] == str(
        tmp_path / "nas" / "models" / "embeddings"
    )
    assert payload["generation"]["workflows_root"] == str(workflows_root)


def test_generation_capability_reports_partial_state_when_service_is_unreachable(
    monkeypatch: MonkeyPatch, tmp_path: Path
) -> None:
    workflows_root = _configure_generation_env(monkeypatch, tmp_path)
    _write_required_workflows(workflows_root)
    checkpoints_root = tmp_path / "nas" / "models" / "checkpoints"
    vaes_root = tmp_path / "nas" / "models" / "vaes"
    (checkpoints_root / "sdxl-base.safetensors").write_text("checkpoint", encoding="utf-8")
    (vaes_root / "sdxl.vae.pt").write_text("vae", encoding="utf-8")

    capability = get_generation_capability(service_ping=lambda _base_url: False)

    assert capability.status == "partially-configured"
    assert capability.comfyui_service_reachable is False
    assert capability.model_roots_on_nas is True
    assert capability.missing_requirements == ["comfyui_service_unreachable"]
