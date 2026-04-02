import uuid
from collections.abc import Callable, Generator
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Literal

from _pytest.monkeypatch import MonkeyPatch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.session import get_db_session
from app.main import app
from app.models.asset import Asset
from app.models.history_event import HistoryEvent
from app.services import photo_prep
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


class _StubLandmarker:
    def close(self) -> None:
        return None


def _build_qc_report(
    status: Literal["pass", "warn", "fail"],
    *,
    blur_score: float = 140,
    exposure_score: float = 98,
    framing_label: str = "full-body",
    reasons: list[str] | None = None,
) -> photo_prep.PhotoQcReport:
    return photo_prep.PhotoQcReport(
        framing_label=framing_label,
        metrics={
            "face_detected": True,
            "body_landmarks_detected": True,
            "blur_score": blur_score,
            "exposure_score": exposure_score,
            "framing_label": framing_label,
        },
        reasons=reasons or [],
        status=status,
    )


def _patch_deterministic_qc(
    monkeypatch: MonkeyPatch,
    reports: list[photo_prep.PhotoQcReport],
) -> None:
    queued_reports = list(reports)

    monkeypatch.setattr(
        photo_prep,
        "_download_model_if_needed",
        lambda url, destination: destination,
    )
    monkeypatch.setattr(photo_prep, "_create_face_landmarker", lambda model_path: _StubLandmarker())
    monkeypatch.setattr(photo_prep, "_create_pose_landmarker", lambda model_path: _StubLandmarker())

    def _fake_qc_report(
        image: object,
        face_landmarker: object,
        pose_landmarker: object,
    ) -> photo_prep.PhotoQcReport:
        return queued_reports.pop(0)

    monkeypatch.setattr(photo_prep, "_qc_report", _fake_qc_report)


def test_character_creation_registers_lineage_history_and_detail_payload(
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
                reasons=["Image sharpness is borderline."],
            ),
            _build_qc_report(
                "fail",
                blur_score=45,
                framing_label="head-closeup",
                reasons=["Image appears too blurry."],
            ),
        ],
    )

    with migrated_database("characters_api") as database_url:
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
            monkeypatch.setenv("MEDIACREATOR_STORAGE_SCRATCH_ROOT", str(scratch_root))

            try:
                with TestClient(app) as client:
                    photoset_response = client.post(
                        "/api/v1/photosets",
                        data={"character_label": "Phase 11 browser subject"},
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
                                    "female_body_front.png",
                                    _sample_image_bytes("female_body_front.png"),
                                    "image/png",
                                ),
                            ),
                        ],
                    )

                    assert photoset_response.status_code == 201
                    photoset_payload = photoset_response.json()
                    accepted_entries = [
                        entry
                        for entry in photoset_payload["entries"]
                        if entry["accepted_for_character_use"]
                    ]

                    create_response = client.post(
                        "/api/v1/characters",
                        json={"photoset_public_id": photoset_payload["public_id"]},
                    )
                    assert create_response.status_code == 201
                    character_payload = create_response.json()

                    assert character_payload["asset_type"] == "character"
                    assert character_payload["status"] == "base-created"
                    assert character_payload["label"] == "Phase 11 browser subject"
                    assert (
                        character_payload["originating_photoset_public_id"]
                        == photoset_payload["public_id"]
                    )
                    assert (
                        character_payload["accepted_entry_count"]
                        == photoset_payload["accepted_entry_count"]
                    )
                    assert len(character_payload["accepted_entries"]) == 2
                    assert [
                        entry["qc_status"] for entry in character_payload["accepted_entries"]
                    ] == ["pass", "warn"]
                    assert [
                        entry["public_id"] for entry in character_payload["accepted_entries"]
                    ] == [entry["public_id"] for entry in accepted_entries]
                    assert [event["event_type"] for event in character_payload["history"]] == [
                        "character.created",
                        "character.photoset_linked",
                    ]

                    detail_response = client.get(
                        f"/api/v1/characters/{character_payload['public_id']}"
                    )
                    assert detail_response.status_code == 200
                    assert detail_response.json() == character_payload

                    duplicate_response = client.post(
                        "/api/v1/characters",
                        json={"photoset_public_id": photoset_payload["public_id"]},
                    )
                    assert duplicate_response.status_code == 200
                    assert duplicate_response.json()["public_id"] == character_payload["public_id"]

                with session_factory() as session:
                    photoset_asset = session.scalar(
                        select(Asset).where(
                            Asset.public_id == uuid.UUID(photoset_payload["public_id"])
                        )
                    )
                    character_assets = session.scalars(
                        select(Asset).where(Asset.asset_type == "character")
                    ).all()
                    history_events = session.scalars(
                        select(HistoryEvent)
                        .join(Asset, HistoryEvent.asset_id == Asset.id)
                        .where(Asset.asset_type == "character")
                        .order_by(HistoryEvent.created_at.asc())
                    ).all()

                    assert photoset_asset is not None
                    assert len(character_assets) == 1
                    assert character_assets[0].source_asset_id == photoset_asset.id
                    assert [event.event_type for event in history_events] == [
                        "character.created",
                        "character.photoset_linked",
                    ]
                    assert (
                        history_events[0].details["photoset_public_id"]
                        == photoset_payload["public_id"]
                    )
                    assert (
                        history_events[0].details["accepted_entry_count"]
                        == photoset_payload["accepted_entry_count"]
                    )
                    assert history_events[0].details["accepted_entry_public_ids"] == [
                        entry["public_id"] for entry in accepted_entries
                    ]
            finally:
                app.dependency_overrides.clear()
                engine.dispose()


def test_character_creation_rejects_photoset_with_zero_accepted_entries(
    monkeypatch: MonkeyPatch,
) -> None:
    _patch_deterministic_qc(
        monkeypatch,
        [
            _build_qc_report(
                "fail",
                blur_score=45,
                framing_label="head-closeup",
                reasons=["Image appears too blurry."],
            ),
            _build_qc_report(
                "fail",
                blur_score=40,
                framing_label="head-closeup",
                reasons=["Exposure is outside the safe range."],
            ),
        ],
    )

    with migrated_database("characters_api_zero_accepted") as database_url:
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
            monkeypatch.setenv("MEDIACREATOR_STORAGE_SCRATCH_ROOT", str(scratch_root))

            try:
                with TestClient(app) as client:
                    photoset_response = client.post(
                        "/api/v1/photosets",
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
                    assert photoset_response.json()["accepted_entry_count"] == 0

                    create_response = client.post(
                        "/api/v1/characters",
                        json={"photoset_public_id": photoset_response.json()["public_id"]},
                    )

                    assert create_response.status_code == 400
                    assert create_response.json() == {
                        "detail": "Photoset has no accepted entries for character creation."
                    }

                with session_factory() as session:
                    character_assets = session.scalars(
                        select(Asset).where(Asset.asset_type == "character")
                    ).all()
                    assert character_assets == []
            finally:
                app.dependency_overrides.clear()
                engine.dispose()
