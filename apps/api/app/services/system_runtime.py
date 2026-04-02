from __future__ import annotations

import json
import os
from pathlib import Path
from typing import cast

from app.services.generation_provider import get_generation_capability
from app.services.lora_training import get_lora_training_capability
from app.services.storage_service import resolve_storage_layout
from app.services.video_render import DEFAULT_BLENDER_BIN

REPO_ROOT = Path(__file__).resolve().parents[4]


def _diagnostics_report_path() -> Path:
    configured = os.getenv("MEDIACREATOR_DIAGNOSTICS_REPORT_PATH")
    if configured:
        return Path(configured)
    return REPO_ROOT / "docs" / "verification" / "final_verify_matrix.json"


def _diagnostics_report_markdown_path(report_path: Path) -> Path:
    configured = os.getenv("MEDIACREATOR_DIAGNOSTICS_REPORT_MARKDOWN_PATH")
    if configured:
        return Path(configured)
    return report_path.with_suffix(".md")


def get_blender_capability() -> dict[str, object]:
    configured = Path(os.getenv("MEDIACREATOR_BLENDER_BIN", str(DEFAULT_BLENDER_BIN)))
    if configured.exists():
        return {
            "blender_bin": str(configured),
            "detail": "Blender 4.5 LTS is available for preview/video render jobs.",
            "status": "ready",
        }
    return {
        "blender_bin": str(configured),
        "detail": "Blender 4.5 LTS is missing, so preview and video render jobs cannot run.",
        "status": "missing",
    }


def get_storage_paths_payload() -> dict[str, str]:
    layout = resolve_storage_layout()
    return {
        "character_assets_root": str(layout.character_assets_root),
        "checkpoints_root": str(layout.checkpoints_root),
        "embeddings_root": str(layout.embeddings_root),
        "exports_root": str(layout.exports_root),
        "loras_root": str(layout.loras_root),
        "models_root": str(layout.models_root),
        "nas_root": str(layout.nas_root),
        "prepared_images_root": str(layout.prepared_images_root),
        "renders_root": str(layout.renders_root),
        "scratch_root": str(layout.scratch_root),
        "uploaded_photos_root": str(layout.uploaded_photos_root),
        "vaes_root": str(layout.vaes_root),
        "wardrobe_root": str(layout.wardrobe_root),
    }


def get_system_settings_payload() -> dict[str, object]:
    storage_layout = resolve_storage_layout()
    generation_capability = get_generation_capability()
    ai_toolkit = get_lora_training_capability()

    return {
        "application": "MediaCreator",
        "service": "api",
        "mode": "single-user",
        "storage_mode": storage_layout.storage_mode,
        "nas_available": storage_layout.nas_available,
        "generation": generation_capability,
        "blender": get_blender_capability(),
        "ai_toolkit": ai_toolkit,
        "storage_paths": get_storage_paths_payload(),
    }


def read_diagnostics_report_summary() -> dict[str, object] | None:
    report_path = _diagnostics_report_path()
    if not report_path.exists():
        return None

    loaded = json.loads(report_path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        return None

    report_payload = cast(dict[str, object], loaded)
    generated_at = report_payload.get("generated_at")
    overall_status = report_payload.get("overall_status")
    return {
        "generated_at": generated_at if isinstance(generated_at, str) else None,
        "human_report_path": str(_diagnostics_report_markdown_path(report_path)),
        "machine_report_path": str(report_path),
        "overall_status": overall_status if isinstance(overall_status, str) else None,
    }
