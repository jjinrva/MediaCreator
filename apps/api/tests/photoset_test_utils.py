from collections.abc import Sequence
from typing import Any, cast

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from app.services.jobs import run_worker_once


def queue_photoset_upload(
    client: TestClient,
    *,
    data: dict[str, str],
    files: Sequence[tuple[str, tuple[str, bytes, str]]],
) -> dict[str, Any]:
    response = client.post("/api/v1/photosets", data=data, files=list(files))
    assert response.status_code == 202
    payload = cast(dict[str, Any], response.json())
    ingest_job = payload["ingest_job"]
    assert ingest_job["job_public_id"] is not None
    assert ingest_job["status"] != "completed"
    return payload


def complete_photoset_ingest(
    client: TestClient,
    session_factory: sessionmaker[Session],
    *,
    queued_payload: dict[str, Any],
) -> dict[str, Any]:
    assert run_worker_once(session_factory) == "completed"
    detail_response = client.get(f"/api/v1/photosets/{queued_payload['public_id']}")
    assert detail_response.status_code == 200
    return cast(dict[str, Any], detail_response.json())


def upload_photoset_and_complete_ingest(
    client: TestClient,
    session_factory: sessionmaker[Session],
    *,
    data: dict[str, str],
    files: Sequence[tuple[str, tuple[str, bytes, str]]],
) -> tuple[dict[str, Any], dict[str, Any]]:
    queued_payload = queue_photoset_upload(client, data=data, files=files)
    final_payload = complete_photoset_ingest(
        client,
        session_factory,
        queued_payload=queued_payload,
    )
    return queued_payload, final_payload
