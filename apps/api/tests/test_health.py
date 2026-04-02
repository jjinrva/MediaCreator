from pathlib import Path

from _pytest.monkeypatch import MonkeyPatch
from fastapi.testclient import TestClient

from app.main import app


def test_health_endpoint_returns_storage_mode_and_single_user_status(
    monkeypatch: MonkeyPatch, tmp_path: Path
) -> None:
    nas_root = tmp_path / "nas"
    nas_root.mkdir()

    monkeypatch.setenv("MEDIACREATOR_STORAGE_NAS_ROOT", str(nas_root))
    monkeypatch.setenv("MEDIACREATOR_STORAGE_SCRATCH_ROOT", str(tmp_path / "scratch"))
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "application": "MediaCreator",
        "service": "api",
        "status": "ok",
        "mode": "single-user",
        "phase": "03",
        "storage_mode": "nas-ready",
        "nas_available": True,
    }
