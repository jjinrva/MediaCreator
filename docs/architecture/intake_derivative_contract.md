# Intake Derivative Contract

Phase 03 defines the first explicit derivative and manifest contract between intake QC and downstream body/LoRA work.

## Per-entry derivative rules

Each photoset entry preserves the uploaded original and always keeps the normalized derivative and thumbnail.

Additional derivatives are bucket-bound:

- `body_only` and `both` entries get `body-alpha.png`
- `lora_only` and `both` entries get `lora-normalized.png`
- `rejected` entries do not get body or LoRA derivatives

The `photoset_entries` table persists nullable storage-object links for the body and LoRA derivatives so later phases do not infer paths from filenames.

## Photoset derivative manifest

Each ingested photoset writes `photoset_derivatives.json` with version `photoset-derivatives-v1`.

Per-entry fields include:

- source entry/public IDs
- source photo asset ID
- bucket
- reason codes and reason messages
- absolute storage paths for original, normalized, thumbnail, and optional body/LoRA derivatives
- derivative metadata for background removal and conservative LoRA normalization

The manifest is also registered as a `storage_objects` row with object type `photoset-derivative-manifest`.

## LoRA dataset seed manifest

Each ingested photoset also writes `dataset_manifest.json` with version `lora-dataset-seed-v1`.

This manifest contains only `lora_only` and `both` entries and records:

- source entry/public IDs
- bucket
- LoRA derivative path and storage-object public ID
- reason codes and reason messages
- caption-seed text/tags with version `caption-seed-v1`

This keeps later dataset construction truthful: body-only and rejected entries are visible in the photoset manifest but never leak into the LoRA seed manifest.

## Character dataset build contract

When a character dataset is built later, the dataset service copies the persisted LoRA derivatives instead of guessing from normalized images.

The character-scoped dataset manifest keeps:

- source derivative path
- source derivative storage-object public ID
- source entry/public IDs
- source bucket
- copied dataset image and caption files

That keeps the saved dataset lineage explicit from intake through AI Toolkit-compatible training inputs.
