import os
from pathlib import Path
from typing import Mapping

from pydantic import BaseModel


class StorageLayout(BaseModel):
    nas_root: Path
    models_root: Path
    loras_root: Path
    checkpoints_root: Path
    embeddings_root: Path
    vaes_root: Path
    uploaded_photos_root: Path
    prepared_images_root: Path
    character_assets_root: Path
    wardrobe_root: Path
    exports_root: Path
    renders_root: Path
    scratch_root: Path
    nas_available: bool
    storage_mode: str

    def canonical_roots(self) -> list[Path]:
        return [
            self.models_root,
            self.loras_root,
            self.checkpoints_root,
            self.embeddings_root,
            self.vaes_root,
            self.uploaded_photos_root,
            self.prepared_images_root,
            self.character_assets_root,
            self.wardrobe_root,
            self.exports_root,
            self.renders_root,
        ]


def _path_from_env(env: Mapping[str, str], key: str, default: Path) -> Path:
    return Path(env.get(key, str(default)))


def resolve_storage_layout(env: Mapping[str, str] | None = None) -> StorageLayout:
    resolved_env = env if env is not None else os.environ

    nas_root = _path_from_env(
        resolved_env, "MEDIACREATOR_STORAGE_NAS_ROOT", Path("/mnt/nas/mediacreator")
    )
    scratch_root = _path_from_env(
        resolved_env,
        "MEDIACREATOR_STORAGE_SCRATCH_ROOT",
        Path("/var/tmp/mediacreator/scratch"),
    )
    layout = StorageLayout(
        nas_root=nas_root,
        models_root=_path_from_env(
            resolved_env, "MEDIACREATOR_STORAGE_MODELS_ROOT", nas_root / "models"
        ),
        loras_root=_path_from_env(
            resolved_env, "MEDIACREATOR_STORAGE_LORAS_ROOT", nas_root / "models" / "loras"
        ),
        checkpoints_root=_path_from_env(
            resolved_env,
            "MEDIACREATOR_STORAGE_CHECKPOINTS_ROOT",
            nas_root / "models" / "checkpoints",
        ),
        embeddings_root=_path_from_env(
            resolved_env,
            "MEDIACREATOR_STORAGE_EMBEDDINGS_ROOT",
            nas_root / "models" / "embeddings",
        ),
        vaes_root=_path_from_env(
            resolved_env,
            "MEDIACREATOR_STORAGE_VAES_ROOT",
            nas_root / "models" / "vaes",
        ),
        uploaded_photos_root=_path_from_env(
            resolved_env,
            "MEDIACREATOR_STORAGE_UPLOADED_PHOTOS_ROOT",
            nas_root / "photos" / "uploaded",
        ),
        prepared_images_root=_path_from_env(
            resolved_env,
            "MEDIACREATOR_STORAGE_PREPARED_IMAGES_ROOT",
            nas_root / "photos" / "prepared",
        ),
        character_assets_root=_path_from_env(
            resolved_env,
            "MEDIACREATOR_STORAGE_CHARACTER_ASSETS_ROOT",
            nas_root / "characters",
        ),
        wardrobe_root=_path_from_env(
            resolved_env, "MEDIACREATOR_STORAGE_WARDROBE_ROOT", nas_root / "wardrobe"
        ),
        exports_root=_path_from_env(
            resolved_env, "MEDIACREATOR_STORAGE_EXPORTS_ROOT", nas_root / "exports"
        ),
        renders_root=_path_from_env(
            resolved_env, "MEDIACREATOR_STORAGE_RENDERS_ROOT", nas_root / "renders"
        ),
        scratch_root=scratch_root,
        nas_available=nas_root.exists(),
        storage_mode="nas-ready" if nas_root.exists() else "degraded-local-only",
    )
    return layout


def ensure_storage_directories(layout: StorageLayout) -> list[Path]:
    created_paths: list[Path] = []

    layout.scratch_root.mkdir(parents=True, exist_ok=True)
    created_paths.append(layout.scratch_root)

    if not layout.nas_available:
        return created_paths

    for path in layout.canonical_roots():
        path.mkdir(parents=True, exist_ok=True)
        created_paths.append(path)

    return created_paths
