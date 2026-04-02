# Phase 03 report

## Status

PASS

## What changed

- Extended `.env.example` with the fixed storage-root contract for NAS-backed canonical assets and local scratch.
- Added `apps/api/app/services/storage_service.py` to centralize storage-path resolution and lazy directory creation.
- Updated the API health response so it reports whether storage is in `nas-ready` or `degraded-local-only` mode.
- Added targeted backend tests for storage resolution and directory creation.
- Added `docs/architecture/storage_layout.md` plus `storage/README.md` to freeze the storage contract and the future `storage_manifest` concept.
- Updated `README.md` to make the NAS mount and local scratch requirements explicit.
- Removed phase-stale UI/API wording so the app stays truthful as later phases continue.

## Exact commands run

- `make test-api`
- `make lint`
- `make typecheck`
- `make test-web`
- `cd /opt/MediaCreator/apps/api && .venv/bin/python - <<'PY' ... ensure_storage_directories(resolve_storage_layout(...)) ... PY`
- `cd /opt/MediaCreator/apps/api && .venv/bin/python - <<'PY' ... resolve_storage_layout({...custom paths...}) ... PY`
- `rg -n "MEDIACREATOR_STORAGE_(NAS_ROOT|SCRATCH_ROOT|MODELS_ROOT|LORAS_ROOT|CHECKPOINTS_ROOT|UPLOADED_PHOTOS_ROOT|PREPARED_IMAGES_ROOT|CHARACTER_ASSETS_ROOT|WARDROBE_ROOT|EXPORTS_ROOT|RENDERS_ROOT)" /opt/MediaCreator/.env.example /opt/MediaCreator/README.md /opt/MediaCreator/docs/architecture/storage_layout.md /opt/MediaCreator/docs/architecture/local_runtime.md`
- `rg -n "MEDIACREATOR_STORAGE_(NAS_ROOT|SCRATCH_ROOT|MODELS_ROOT|LORAS_ROOT|CHECKPOINTS_ROOT|UPLOADED_PHOTOS_ROOT|PREPARED_IMAGES_ROOT|CHARACTER_ASSETS_ROOT|WARDROBE_ROOT|EXPORTS_ROOT|RENDERS_ROOT)" /opt/MediaCreator/apps/api/app/services/storage_service.py`
- `rg -n "/mnt/nas/mediacreator|/var/tmp/mediacreator/scratch|models/loras|photos/uploaded|photos/prepared|characters|wardrobe|exports|renders" /opt/MediaCreator/apps/api/app/services/storage_service.py /opt/MediaCreator/.env.example /opt/MediaCreator/README.md /opt/MediaCreator/docs/architecture/storage_layout.md /opt/MediaCreator/storage/README.md`

## Tests that passed

- `make test-api`
- `make test-web`
- `make lint`
- `make typecheck`

## Remaining risks

- NAS availability is environment-dependent by design; without the mount, the app only reports degraded local-only storage status.
- The storage-manifest concept is documented, but the database table does not exist yet.
- No application routes persist assets yet; this phase only establishes the contract and resolver.

## Next phase may start

Yes. Phase 03 verification passed, so Phase 04 may start.
