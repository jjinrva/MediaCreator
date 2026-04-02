# Phase
`phase_03_preprocessing_derivatives_and_dataset_manifests`

## Scope
Backend derivative creation and manifest contracts for normalized intake assets, body/3D-prep derivatives, and LoRA dataset lineage.

## Files changed
- `apps/api/pyproject.toml`
- `apps/api/app/models/photoset_entry.py`
- `apps/api/app/services/photo_prep.py`
- `apps/api/app/services/lora_dataset.py`
- `apps/api/app/services/characters.py`
- `apps/api/app/api/routes/photosets.py`
- `apps/api/app/schemas/photosets.py`
- `apps/api/alembic/versions/0010_photoset_derivative_contract.py`
- `apps/api/tests/test_photo_derivatives_and_manifests.py`
- `apps/api/tests/test_lora_dataset_manifest_contract.py`
- `apps/api/tests/test_lora_dataset_api.py`
- `apps/worker/pyproject.toml`
- `tests/api/test_photo_derivatives_and_manifests.py`
- `tests/api/test_lora_dataset_manifest_contract.py`
- `docs/architecture/intake_derivative_contract.md`
- `docs/architecture/lora_dataset_contract.md`

## Implementation summary
- Added nullable entry-level lineage links for:
  - `body_derivative_storage_object_id`
  - `lora_derivative_storage_object_id`
- Kept originals, normalized derivatives, and thumbnails intact while writing:
  - `body-alpha.png` for `body_only` and `both`
  - `lora-normalized.png` for `lora_only` and `both`
- Bound body derivatives to background-removal metadata and bound LoRA derivatives to conservative normalization metadata instead of inferring downstream behavior from filenames.
- Registered two explicit manifests per photoset:
  - `photoset-derivative-manifest`
  - `photoset-lora-dataset-manifest`
- Added caption-seed data to the LoRA seed manifest so later dataset construction does not guess prompt text from bucket membership.
- Extended photoset artifact routing/schema so persisted entries can expose optional `body` and `lora` artifact URLs and storage-object IDs.
- Changed the character LoRA dataset builder to use only `lora_only` and `both` entries and to copy persisted LoRA derivatives instead of normalized intake files.
- Updated the LoRA dataset contract docs to reflect the stricter LoRA-qualified subset and source-derivative lineage.

## Dependency notes
- Installed and validated `rembg[cpu]` for real background removal.
- Verified the runtime dependency path by successfully running `rembg.remove(...)` on `male_body_front.png`, which downloaded `~/.u2net/u2net.onnx` and returned output bytes.

## Verification hooks added
- `apps/api/tests/test_photo_derivatives_and_manifests.py`
- `apps/api/tests/test_lora_dataset_manifest_contract.py`
- root-level wrappers under `tests/api/` to match the pack’s exact verification commands

## Known limitations
- The body derivative uses `rembg`’s CPU model and writes truthful metadata, but the UI still does not expose these manifest files directly; later phases can consume them from storage/lineage.
- Phase 03 does not yet create a saved 3D artifact or a saved LoRA artifact; it only makes their downstream inputs explicit and auditable.

## Status
PASS
