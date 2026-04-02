from __future__ import annotations

import os
import uuid
from typing import cast

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.models.asset import Asset
from app.services.body_parameters import get_character_body_parameter_payload
from app.services.characters import get_character_payload
from app.services.exports import get_character_export_payload
from app.services.generation_provider import get_generation_capability
from app.services.jobs import (
    DEFAULT_WORKER_HEARTBEAT_STALE_AFTER_SECONDS,
    WORKER_SERVICE_NAME,
    get_service_heartbeat_payload,
)
from app.services.lora_training import get_character_lora_training_payload
from app.services.pose_state import get_character_pose_state_payload
from app.services.system_runtime import read_diagnostics_report_summary

INTERNAL_API_BASE_URL = os.environ.get(
    "MEDIACREATOR_INTERNAL_API_BASE_URL", "http://127.0.0.1:8010"
)


def _asset_query() -> Select[tuple[Asset]]:
    return select(Asset).order_by(Asset.created_at.desc())


def _latest_character_public_id(session: Session) -> uuid.UUID | None:
    character_asset = session.scalars(
        _asset_query().where(Asset.asset_type == "character")
    ).first()
    if character_asset is None:
        return None
    return character_asset.public_id


def _check_payload(
    *,
    check_id: str,
    detail: str,
    label: str,
    status: str,
) -> dict[str, str]:
    return {
        "check_id": check_id,
        "detail": detail,
        "label": label,
        "status": status,
    }


def get_live_diagnostics_payload(session: Session) -> dict[str, object]:
    character_public_id = _latest_character_public_id(session)
    checks: list[dict[str, str]] = []
    worker_heartbeat = get_service_heartbeat_payload(
        session,
        WORKER_SERVICE_NAME,
        stale_after_seconds=DEFAULT_WORKER_HEARTBEAT_STALE_AFTER_SECONDS,
    )

    checks.append(
        _check_payload(
            check_id="worker_heartbeat",
            detail=str(worker_heartbeat["detail"]),
            label="Worker heartbeat",
            status="pass" if worker_heartbeat["status"] == "ready" else "fail",
        )
    )

    if character_public_id is None:
        checks.extend(
            [
                _check_payload(
                    check_id="ingest_pipeline",
                    detail=(
                        "No character exists yet, so the ingest pipeline has not been "
                        "exercised in this runtime."
                    ),
                    label="Ingest pipeline",
                    status="not-run",
                ),
                _check_payload(
                    check_id="body_edit_persistence",
                    detail="No character exists yet, so body persistence cannot be checked.",
                    label="Body edit persistence",
                    status="not-run",
                ),
                _check_payload(
                    check_id="pose_persistence",
                    detail="No character exists yet, so pose persistence cannot be checked.",
                    label="Pose persistence",
                    status="not-run",
                ),
                _check_payload(
                    check_id="glb_preview",
                    detail=(
                        "No character exists yet, so GLB preview availability cannot be "
                        "checked."
                    ),
                    label="GLB preview",
                    status="not-run",
                ),
                _check_payload(
                    check_id="export_availability",
                    detail="No character exists yet, so export availability cannot be checked.",
                    label="Export availability",
                    status="not-run",
                ),
                _check_payload(
                    check_id="lora_training_capability",
                    detail=(
                        "No character exists yet, so character-scoped LoRA training capability "
                        "cannot be checked."
                    ),
                    label="LoRA training capability",
                    status="not-run",
                ),
            ]
        )
    else:
        character_payload = get_character_payload(session, character_public_id, api_base_url="")
        accepted_entry_count = 0
        if character_payload is not None:
            accepted_entry_value = character_payload.get("accepted_entry_count")
            if isinstance(accepted_entry_value, int):
                accepted_entry_count = accepted_entry_value
        checks.append(
            _check_payload(
                check_id="ingest_pipeline",
                detail=(
                    f"Latest character has {accepted_entry_count} accepted reference image(s)."
                    if accepted_entry_count > 0
                    else "Latest character has no accepted reference images."
                ),
                label="Ingest pipeline",
                status="pass" if accepted_entry_count > 0 else "fail",
            )
        )

        body_payload = get_character_body_parameter_payload(session, character_public_id)
        checks.append(
            _check_payload(
                check_id="body_edit_persistence",
                detail=(
                    "Body parameter values are readable from the API."
                    if body_payload is not None
                    else "Body parameter values are missing for the latest character."
                ),
                label="Body edit persistence",
                status="pass" if body_payload is not None else "fail",
            )
        )

        pose_payload = get_character_pose_state_payload(session, character_public_id)
        checks.append(
            _check_payload(
                check_id="pose_persistence",
                detail=(
                    "Pose parameter values are readable from the API."
                    if pose_payload is not None
                    else "Pose parameter values are missing for the latest character."
                ),
                label="Pose persistence",
                status="pass" if pose_payload is not None else "fail",
            )
        )

        export_payload = get_character_export_payload(
            session,
            character_public_id,
            api_base_url=INTERNAL_API_BASE_URL,
        )
        preview_status = "not-ready"
        export_available = False
        if export_payload is not None:
            preview_glb = cast(dict[str, object], export_payload["preview_glb"])
            preview_status_value = preview_glb.get("status")
            if isinstance(preview_status_value, str):
                preview_status = preview_status_value
            export_available = preview_status == "available"
            if not export_available:
                texture_material = cast(dict[str, object], export_payload["texture_material"])
                base_texture_artifact = cast(
                    dict[str, object],
                    texture_material["base_texture_artifact"],
                )
                base_texture_status = base_texture_artifact.get("status")
                export_available = (
                    isinstance(base_texture_status, str) and base_texture_status == "available"
                )
        checks.append(
            _check_payload(
                check_id="glb_preview",
                detail=f"Preview GLB status is '{preview_status}'.",
                label="GLB preview",
                status="pass" if preview_status == "available" else "fail",
            )
        )
        checks.append(
            _check_payload(
                check_id="export_availability",
                detail=(
                    "At least one persisted export artifact is available."
                    if export_available
                    else "No persisted export artifact is currently available."
                ),
                label="Export availability",
                status="pass" if export_available else "fail",
            )
        )

        lora_payload = get_character_lora_training_payload(session, character_public_id)
        lora_status = "not-run"
        lora_detail = "No character-scoped LoRA capability payload was available."
        if lora_payload is not None:
            capability = cast(dict[str, object], lora_payload["capability"])
            capability_status = capability.get("status")
            capability_detail = capability.get("detail")
            lora_status = (
                "pass"
                if isinstance(capability_status, str) and capability_status == "ready"
                else "fail"
            )
            if isinstance(capability_detail, str):
                lora_detail = capability_detail
        checks.append(
            _check_payload(
                check_id="lora_training_capability",
                detail=lora_detail,
                label="LoRA training capability",
                status=lora_status,
            )
        )

    generation_capability = get_generation_capability()
    checks.append(
        _check_payload(
            check_id="generation_workflow_availability",
            detail=(
                "Generation capability is ready."
                if generation_capability.status == "ready"
                else (
                    "Generation capability is not ready: "
                    + ", ".join(generation_capability.missing_requirements)
                )
            ),
            label="Generation workflow availability",
            status="pass" if generation_capability.status == "ready" else "fail",
        )
    )

    return {
        "checks": checks,
        "report_summary": read_diagnostics_report_summary(),
    }
