import uuid
from pathlib import Path
from tempfile import TemporaryDirectory

from _pytest.monkeypatch import MonkeyPatch
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.db.session import get_db_session
from app.main import app
from app.models.asset import Asset
from app.models.history_event import HistoryEvent
from tests.db_test_utils import migrated_database
from tests.photoset_test_utils import upload_photoset_and_complete_ingest
from tests.test_characters_api import (
    _build_qc_report,
    _override_db_session,
    _patch_deterministic_qc,
    _sample_image_bytes,
    _session_factory,
)


def _configure_storage(monkeypatch: MonkeyPatch, *, nas_root: Path, scratch_root: Path) -> None:
    monkeypatch.setenv("MEDIACREATOR_STORAGE_NAS_ROOT", str(nas_root))
    monkeypatch.setenv(
        "MEDIACREATOR_STORAGE_UPLOADED_PHOTOS_ROOT",
        str(nas_root / "photos" / "uploaded"),
    )
    monkeypatch.setenv(
        "MEDIACREATOR_STORAGE_PREPARED_IMAGES_ROOT",
        str(nas_root / "photos" / "prepared"),
    )
    monkeypatch.setenv("MEDIACREATOR_STORAGE_SCRATCH_ROOT", str(scratch_root))


def test_character_creation_is_acceptance_gated_and_preserves_bucket_lineage(
    monkeypatch: MonkeyPatch,
) -> None:
    _patch_deterministic_qc(
        monkeypatch,
        [
            _build_qc_report("pass"),
            _build_qc_report(
                "warn",
                blur_score=95,
                framing_label="head-closeup",
                reasons=["Portrait crop is LoRA-only."],
            ),
            _build_qc_report(
                "fail",
                blur_score=42,
                framing_label="head-closeup",
                reasons=["Image appears too blurry."],
            ),
            _build_qc_report(
                "warn",
                blur_score=90,
                framing_label="full-body",
                reasons=["Body evidence is strong enough without a face."],
            ),
        ],
    )

    with migrated_database("phase04_character_creation_contract") as database_url:
        engine, session_factory = _session_factory(database_url)
        app.dependency_overrides[get_db_session] = _override_db_session(session_factory)

        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            nas_root = temp_path / "nas"
            scratch_root = temp_path / "scratch"
            nas_root.mkdir()
            scratch_root.mkdir()
            _configure_storage(monkeypatch, nas_root=nas_root, scratch_root=scratch_root)

            try:
                with TestClient(app) as client:
                    _, first_photoset_payload = upload_photoset_and_complete_ingest(
                        client,
                        session_factory,
                        data={"character_label": "Repeat label"},
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
                            (
                                "photos",
                                (
                                    "reject.png",
                                    _sample_image_bytes("female_body_front.png"),
                                    "image/png",
                                ),
                            ),
                        ],
                    )

                    first_character = client.post(
                        "/api/v1/characters",
                        json={"photoset_public_id": first_photoset_payload["public_id"]},
                    )
                    assert first_character.status_code == 201
                    first_character_payload = first_character.json()

                    assert first_character_payload["label"] == "Repeat label"
                    assert first_character_payload["accepted_entry_count"] == 2
                    assert [
                        entry["bucket"] for entry in first_character_payload["accepted_entries"]
                    ] == ["both", "lora_only"]
                    assert {
                        entry["public_id"] for entry in first_character_payload["accepted_entries"]
                    } == {
                        entry["public_id"]
                        for entry in first_photoset_payload["entries"]
                        if entry["accepted_for_character_use"]
                    }
                    assert all(
                        entry["bucket"] != "rejected"
                        for entry in first_character_payload["accepted_entries"]
                    )

                    _, second_photoset_payload = upload_photoset_and_complete_ingest(
                        client,
                        session_factory,
                        data={"character_label": "Repeat label"},
                        files=[
                            (
                                "photos",
                                (
                                    "male_body_left.png",
                                    _sample_image_bytes("male_body_left.png"),
                                    "image/png",
                                ),
                            )
                        ],
                    )

                    second_character = client.post(
                        "/api/v1/characters",
                        json={"photoset_public_id": second_photoset_payload["public_id"]},
                    )
                    assert second_character.status_code == 201
                    second_character_payload = second_character.json()

                    assert second_character_payload["label"] == "Repeat label"
                    assert (
                        second_character_payload["public_id"]
                        != first_character_payload["public_id"]
                    )

                with session_factory() as session:
                    first_character_asset = session.scalar(
                        select(Asset).where(
                            Asset.public_id == uuid.UUID(first_character_payload["public_id"])
                        )
                    )
                    assert first_character_asset is not None

                    history_events = session.scalars(
                        select(HistoryEvent)
                        .where(HistoryEvent.asset_id == first_character_asset.id)
                        .order_by(HistoryEvent.created_at.asc())
                    ).all()
                    assert [event.event_type for event in history_events] == [
                        "character.created",
                        "character.photoset_linked",
                    ]
                    assert history_events[0].details["accepted_entry_count"] == 2
                    assert history_events[0].details["accepted_body_entry_count"] == 1
                    assert history_events[0].details["accepted_lora_entry_count"] == 2
                    assert history_events[1].details["body_entry_public_ids"] == [
                        first_character_payload["accepted_entries"][0]["public_id"]
                    ]
                    assert history_events[1].details["lora_entry_public_ids"] == [
                        entry["public_id"] for entry in first_character_payload["accepted_entries"]
                    ]
            finally:
                app.dependency_overrides.clear()
                engine.dispose()


def test_character_creation_fails_when_all_images_are_rejected(
    monkeypatch: MonkeyPatch,
) -> None:
    _patch_deterministic_qc(
        monkeypatch,
        [
            _build_qc_report(
                "fail",
                blur_score=40,
                framing_label="head-closeup",
                reasons=["Image appears too blurry."],
            ),
            _build_qc_report(
                "fail",
                blur_score=38,
                framing_label="head-closeup",
                reasons=["Exposure is outside the safe range."],
            ),
        ],
    )

    with migrated_database("phase04_character_creation_rejected") as database_url:
        engine, session_factory = _session_factory(database_url)
        app.dependency_overrides[get_db_session] = _override_db_session(session_factory)

        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            nas_root = temp_path / "nas"
            scratch_root = temp_path / "scratch"
            nas_root.mkdir()
            scratch_root.mkdir()
            _configure_storage(monkeypatch, nas_root=nas_root, scratch_root=scratch_root)

            try:
                with TestClient(app) as client:
                    _, photoset_payload = upload_photoset_and_complete_ingest(
                        client,
                        session_factory,
                        data={"character_label": "Rejected character"},
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
                    assert photoset_payload["accepted_entry_count"] == 0

                    create_response = client.post(
                        "/api/v1/characters",
                        json={"photoset_public_id": photoset_payload["public_id"]},
                    )

                    assert create_response.status_code == 400
                    assert create_response.json() == {
                        "detail": "Photoset has no accepted entries for character creation."
                    }
            finally:
                app.dependency_overrides.clear()
                engine.dispose()
