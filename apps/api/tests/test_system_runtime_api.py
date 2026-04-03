import json
from collections.abc import Callable, Generator
from pathlib import Path
from tempfile import TemporaryDirectory

from _pytest.monkeypatch import MonkeyPatch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.session import get_db_session
from app.main import app
from app.services.jobs import upsert_service_heartbeat
from tests.db_test_utils import migrated_database
from tests.photoset_test_utils import upload_photoset_and_complete_ingest


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


def _configure_runtime(monkeypatch: MonkeyPatch, temp_path: Path) -> Path:
    nas_root = temp_path / "nas"
    scratch_root = temp_path / "scratch"
    workflows_root = temp_path / "workflows" / "comfyui"
    blender_bin = temp_path / "blender" / "blender"
    report_path = temp_path / "reports" / "final_verify_matrix.json"

    for path in (
        nas_root,
        scratch_root,
        workflows_root,
        nas_root / "models" / "checkpoints",
        nas_root / "models" / "loras",
        nas_root / "models" / "embeddings",
        nas_root / "models" / "vaes",
        nas_root / "photos" / "uploaded",
        nas_root / "photos" / "prepared",
        temp_path / "reports",
        blender_bin.parent,
    ):
        path.mkdir(parents=True, exist_ok=True)

    blender_bin.write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")
    report_path.write_text(
        json.dumps(
            {
                "generated_at": "2026-04-02T03:00:00Z",
                "overall_status": "pending",
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setenv("MEDIACREATOR_BLENDER_BIN", str(blender_bin))
    monkeypatch.setenv("MEDIACREATOR_COMFYUI_WORKFLOWS_ROOT", str(workflows_root))
    monkeypatch.setenv("MEDIACREATOR_DIAGNOSTICS_REPORT_PATH", str(report_path))
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
    monkeypatch.setenv(
        "MEDIACREATOR_STORAGE_CHECKPOINTS_ROOT",
        str(nas_root / "models" / "checkpoints"),
    )
    monkeypatch.setenv(
        "MEDIACREATOR_STORAGE_LORAS_ROOT",
        str(nas_root / "models" / "loras"),
    )
    monkeypatch.setenv(
        "MEDIACREATOR_STORAGE_EMBEDDINGS_ROOT",
        str(nas_root / "models" / "embeddings"),
    )
    monkeypatch.setenv(
        "MEDIACREATOR_STORAGE_VAES_ROOT",
        str(nas_root / "models" / "vaes"),
    )
    monkeypatch.delenv("MEDIACREATOR_COMFYUI_BASE_URL", raising=False)
    monkeypatch.delenv("MEDIACREATOR_AI_TOOLKIT_BIN", raising=False)
    return nas_root


def _create_character(
    client: TestClient,
    session_factory: sessionmaker[Session],
) -> str:
    _, photoset_payload = upload_photoset_and_complete_ingest(
        client,
        session_factory,
        data={"character_label": "Diagnostics character"},
        files=[
            (
                "photos",
                (
                    "male_head_front.png",
                    _sample_image_bytes("male_head_front.png"),
                    "image/png",
                ),
            )
        ],
    )

    create_response = client.post(
        "/api/v1/characters",
        json={"photoset_public_id": photoset_payload["public_id"]},
    )
    assert create_response.status_code == 201
    return str(create_response.json()["public_id"])


def test_system_status_and_diagnostics_routes_report_truthful_runtime_state(
    monkeypatch: MonkeyPatch,
) -> None:
    with migrated_database("system_runtime_api") as database_url:
        engine, session_factory = _session_factory(database_url)
        app.dependency_overrides[get_db_session] = _override_db_session(session_factory)

        with TemporaryDirectory() as temp_dir:
            nas_root = _configure_runtime(monkeypatch, Path(temp_dir))

            try:
                with TestClient(app) as client:
                    _create_character(client, session_factory)
                    with session_factory() as session, session.begin():
                        upsert_service_heartbeat(
                            session,
                            service_name="worker",
                            detail="polling",
                        )

                    status_response = client.get("/api/v1/system/status")
                    assert status_response.status_code == 200
                    status_payload = status_response.json()

                    assert status_payload["mode"] == "single-user"
                    assert status_payload["nas_available"] is True
                    assert status_payload["storage_mode"] == "nas-ready"
                    assert status_payload["blender"]["status"] == "ready"
                    assert status_payload["ai_toolkit"]["status"] == "unavailable"
                    assert status_payload["generation"]["status"] == "unavailable"
                    assert status_payload["worker"]["service_name"] == "worker"
                    assert status_payload["worker"]["status"] == "ready"
                    assert status_payload["storage_paths"]["nas_root"] == str(nas_root)
                    assert status_payload["storage_paths"]["checkpoints_root"] == str(
                        nas_root / "models" / "checkpoints"
                    )

                    diagnostics_response = client.get("/api/v1/system/diagnostics")
                    assert diagnostics_response.status_code == 200
                    diagnostics_payload = diagnostics_response.json()
                    checks = {
                        check["check_id"]: check for check in diagnostics_payload["checks"]
                    }

                    assert checks["ingest_pipeline"]["status"] == "pass"
                    assert checks["body_edit_persistence"]["status"] == "pass"
                    assert checks["pose_persistence"]["status"] == "pass"
                    assert checks["worker_heartbeat"]["status"] == "pass"
                    assert checks["glb_preview"]["status"] == "fail"
                    assert checks["export_availability"]["status"] == "fail"
                    assert checks["lora_training_capability"]["status"] == "fail"
                    assert checks["generation_workflow_availability"]["status"] == "fail"
                    assert diagnostics_payload["report_summary"] == {
                        "generated_at": "2026-04-02T03:00:00Z",
                        "human_report_path": str(
                            Path(temp_dir) / "reports" / "final_verify_matrix.md"
                        ),
                        "machine_report_path": str(
                            Path(temp_dir) / "reports" / "final_verify_matrix.json"
                        ),
                        "overall_status": "pending",
                    }
            finally:
                app.dependency_overrides.clear()
                engine.dispose()
