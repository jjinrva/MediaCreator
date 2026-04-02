from pathlib import Path

from app.services.storage_service import ensure_storage_directories, resolve_storage_layout


def test_storage_service_creates_canonical_paths_when_nas_root_exists(tmp_path: Path) -> None:
    nas_root = tmp_path / "nas"
    scratch_root = tmp_path / "scratch"
    nas_root.mkdir()

    layout = resolve_storage_layout(
        {
            "MEDIACREATOR_STORAGE_NAS_ROOT": str(nas_root),
            "MEDIACREATOR_STORAGE_SCRATCH_ROOT": str(scratch_root),
        }
    )
    created = ensure_storage_directories(layout)

    assert layout.storage_mode == "nas-ready"
    assert layout.nas_available is True
    assert scratch_root in created
    assert layout.embeddings_root == nas_root / "models" / "embeddings"
    assert layout.vaes_root == nas_root / "models" / "vaes"
    for path in layout.canonical_roots():
        assert path.exists()
        assert path.is_dir()
        assert nas_root in path.parents


def test_storage_service_degrades_to_local_only_when_nas_root_is_missing(tmp_path: Path) -> None:
    nas_root = tmp_path / "missing-nas"
    scratch_root = tmp_path / "scratch"

    layout = resolve_storage_layout(
        {
            "MEDIACREATOR_STORAGE_NAS_ROOT": str(nas_root),
            "MEDIACREATOR_STORAGE_SCRATCH_ROOT": str(scratch_root),
        }
    )
    created = ensure_storage_directories(layout)

    assert layout.storage_mode == "degraded-local-only"
    assert layout.nas_available is False
    assert created == [scratch_root]
    assert scratch_root.exists()
    assert layout.embeddings_root == nas_root / "models" / "embeddings"
    assert layout.vaes_root == nas_root / "models" / "vaes"
    for path in layout.canonical_roots():
        assert not path.exists()
