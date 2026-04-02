# Storage layout

## Purpose

MediaCreator stores metadata in PostgreSQL, but large binaries live on the filesystem.

- Canonical, long-lived assets live on the NAS
- Short-lived working files and caches live on local NVMe scratch
- PostgreSQL stores metadata, lineage, and later storage-manifest rows, not large binaries

## Fixed roots

### NAS-backed canonical roots

- `MEDIACREATOR_STORAGE_NAS_ROOT`
- `MEDIACREATOR_STORAGE_MODELS_ROOT`
- `MEDIACREATOR_STORAGE_LORAS_ROOT`
- `MEDIACREATOR_STORAGE_CHECKPOINTS_ROOT`
- `MEDIACREATOR_STORAGE_EMBEDDINGS_ROOT`
- `MEDIACREATOR_STORAGE_VAES_ROOT`
- `MEDIACREATOR_STORAGE_UPLOADED_PHOTOS_ROOT`
- `MEDIACREATOR_STORAGE_PREPARED_IMAGES_ROOT`
- `MEDIACREATOR_STORAGE_CHARACTER_ASSETS_ROOT`
- `MEDIACREATOR_STORAGE_WARDROBE_ROOT`
- `MEDIACREATOR_STORAGE_EXPORTS_ROOT`
- `MEDIACREATOR_STORAGE_RENDERS_ROOT`

### Local scratch root

- `MEDIACREATOR_STORAGE_SCRATCH_ROOT`

## What lives where

### NAS

- Stable model files and checkpoints
- LoRA artifacts
- Embeddings
- VAEs
- User-uploaded photos and prepared derivatives
- Character assets
- Wardrobe assets
- Exports
- Final renders

### Local scratch

- Temporary working directories
- Short-lived caches
- Active job scratch data
- Retry-safe transient files that can be recreated

## Degraded mode

If the NAS root is missing, MediaCreator must not pretend canonical storage is available.

- the backend reports `degraded-local-only`
- local scratch still initializes
- canonical NAS subdirectories are not created until the NAS root exists

## Storage manifest concept

The storage-manifest table is introduced later, but the concept is fixed now. Each stored artifact will later need metadata that includes:

- artifact type
- canonical path
- root class (`nas` or `scratch`)
- lineage reference
- history reference
- content metadata
- availability status

## Fixed folder names

The following leaf folder names are part of the contract and should not drift:

- `models`
- `loras`
- `checkpoints`
- `embeddings`
- `vaes`
- `uploaded`
- `prepared`
- `characters`
- `wardrobe`
- `exports`
- `renders`
