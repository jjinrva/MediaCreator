# Phase
`phase_03_preprocessing_derivatives_and_dataset_manifests`

## Scope verified
- normalized derivatives exist alongside preserved originals
- body derivatives exist only for `body_only` and `both`
- LoRA derivatives and manifests include only `lora_only` and `both`
- rejected inputs do not leak into the LoRA manifest
- lineage links persist through storage-object rows and manifest records
- repo lint and typecheck pass after the derivative/manifest changes

## Commands run
- `cd /opt/MediaCreator && apps/api/.venv/bin/pytest -q tests/api/test_photo_derivatives_and_manifests.py`
- `cd /opt/MediaCreator && apps/api/.venv/bin/pytest -q tests/api/test_lora_dataset_manifest_contract.py`
- `make -C /opt/MediaCreator lint`
- `make -C /opt/MediaCreator typecheck`

## Artifact checks
- `tests/api/test_photo_derivatives_and_manifests.py` proved these written-path patterns existed under the temp NAS root:
  - `.../photos/uploaded/<photoset>/<photo>/original.png`
  - `.../photos/prepared/<photoset>/<photo>/normalized.png`
  - `.../photos/prepared/<photoset>/<photo>/thumbnail.png`
  - `.../photos/prepared/<photoset>/<photo>/body-alpha.png` only for `body_only` and `both`
  - `.../photos/prepared/<photoset>/<photo>/lora-normalized.png` only for `lora_only` and `both`
- the same test proved original bytes still matched the uploaded source bytes for all four buckets
- the photoset derivative manifest existed at:
  - `.../photos/prepared/manifests/<photoset>/photoset_derivatives.json`
- the photoset LoRA seed manifest existed at:
  - `.../models/loras/manifests/<photoset>/dataset_manifest.json`
- manifest metadata checks proved:
  - `photoset-derivatives-v1` recorded `alpha_present: true` for body derivatives
  - `lora-dataset-seed-v1` contained only `both` and `lora_only`
  - rejected entries were absent from the LoRA seed manifest
- `tests/api/test_lora_dataset_manifest_contract.py` proved the character-scoped dataset manifest copied only LoRA-qualified derivatives and recorded:
  - `bucket`
  - `source_derivative_path`
  - `source_derivative_storage_object_public_id`
  - copied `image_file` and `caption_file`

## Results
- `pytest -q tests/api/test_photo_derivatives_and_manifests.py`: `1 passed`
- `pytest -q tests/api/test_lora_dataset_manifest_contract.py`: `1 passed`
- `make -C /opt/MediaCreator lint`: passed
- `make -C /opt/MediaCreator typecheck`: passed

## PASS/FAIL/BLOCKED decision
PASS

## Remaining risks
- This phase proves explicit derivative and manifest lineage, but it does not yet prove the body derivatives are consumed by saved 3D generation; that belongs to Phase 04.
- The LoRA seed manifest is now explicit and bounded, but actual trainer execution and saved proof-image truth remain later phases.
