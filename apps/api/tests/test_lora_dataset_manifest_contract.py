import json
from pathlib import Path
from tempfile import TemporaryDirectory

from _pytest.monkeypatch import MonkeyPatch
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.db.session import get_db_session
from app.main import app
from app.models.storage_object import StorageObject
from tests.db_test_utils import migrated_database
from tests.photoset_test_utils import upload_photoset_and_complete_ingest
from tests.test_photo_derivatives_and_manifests import (
    _build_qc_report,
    _override_db_session,
    _patch_derivative_artifacts,
    _patch_deterministic_qc,
    _sample_image_bytes,
    _session_factory,
)


def test_lora_dataset_manifest_uses_only_lora_qualified_derivatives(
    monkeypatch: MonkeyPatch,
) -> None:
    _patch_deterministic_qc(
        monkeypatch,
        [
            _build_qc_report(
                "body_only",
                reason_codes=["face_required_for_lora"],
                reason_messages=["Face evidence was not detected for LoRA training."],
            ),
            _build_qc_report("both"),
            _build_qc_report(
                "rejected",
                framing_label="unknown",
                reason_codes=["no_person_detected"],
                reason_messages=["No person was detected in the image."],
            ),
        ],
    )
    _patch_derivative_artifacts(monkeypatch)

    with migrated_database("lora_manifest_contract") as database_url:
        engine, session_factory = _session_factory(database_url)
        app.dependency_overrides[get_db_session] = _override_db_session(session_factory)

        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
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

            try:
                with TestClient(app) as client:
                    _, photoset_payload = upload_photoset_and_complete_ingest(
                        client,
                        session_factory,
                        data={"character_label": "LoRA Contract Subject"},
                        files=[
                            (
                                "photos",
                                (
                                    "body.png",
                                    _sample_image_bytes("male_body_front.png"),
                                    "image/png",
                                ),
                            ),
                            (
                                "photos",
                                (
                                    "both.png",
                                    _sample_image_bytes("female_body_front.png"),
                                    "image/png",
                                ),
                            ),
                            (
                                "photos",
                                (
                                    "reject.png",
                                    _sample_image_bytes("male_head_front.png"),
                                    "image/png",
                                ),
                            ),
                        ],
                    )

                    create_response = client.post(
                        "/api/v1/characters",
                        json={"photoset_public_id": photoset_payload["public_id"]},
                    )
                    assert create_response.status_code == 201
                    character_public_id = create_response.json()["public_id"]

                    dataset_response = client.post(
                        f"/api/v1/lora-datasets/characters/{character_public_id}"
                    )
                    assert dataset_response.status_code == 200
                    payload = dataset_response.json()
                    assert payload["dataset"]["status"] == "available"
                    assert payload["dataset"]["entry_count"] == 1

                    manifest_response = client.get(
                        f"/api/v1/lora-datasets/characters/{character_public_id}/manifest.json"
                    )
                    assert manifest_response.status_code == 200
                    manifest = manifest_response.json()
                    assert manifest["dataset_version"] == "dataset-v1"
                    assert manifest["entry_count"] == 1
                    assert manifest["entries"][0]["bucket"] == "both"
                    assert manifest["entries"][0]["source_derivative_path"].endswith(
                        "lora-normalized.png"
                    )
                    assert manifest["entries"][0]["reason_codes"] == []

                with session_factory() as session:
                    manifest_storage = session.scalar(
                        select(StorageObject).where(
                            StorageObject.object_type == "character-lora-dataset-manifest"
                        )
                    )
                    assert manifest_storage is not None
                    manifest_file = Path(manifest_storage.storage_path)
                    assert manifest_file.exists()
                    manifest_json = json.loads(manifest_file.read_text(encoding="utf-8"))
                    dataset_root = manifest_file.parent
                    assert len(manifest_json["entries"]) == 1
                    entry = manifest_json["entries"][0]
                    assert (dataset_root / entry["image_file"]).exists()
                    assert (dataset_root / entry["caption_file"]).exists()
                    assert entry["bucket"] == "both"
                    assert entry["source_derivative_path"].endswith("lora-normalized.png")
            finally:
                app.dependency_overrides.clear()
                engine.dispose()
