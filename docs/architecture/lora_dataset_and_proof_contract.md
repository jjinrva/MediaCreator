# LoRA Dataset And Proof Contract

## Dataset selection
- The saved LoRA dataset may include only `lora_only` and `both` photoset entries.
- `body_only` and `rejected` entries are excluded even if they belong to the saved character.
- Each dataset version writes:
  - copied image files
  - copied caption files
  - `dataset_manifest.json`
  - source derivative lineage for every included entry

## Registry truth gates
- A `current` LoRA registry row requires a real artifact file on disk.
- If the file is missing later, the training payload reports that row as `artifact-missing`.
- Active LoRA resolution returns `None` when the registry row exists but the file does not.
- Generation workspace local-LoRA options are filtered to entries whose backing artifact file exists.

## Proof-image gate
- Proof-image success is allowed only when both of these are true:
  - AI Toolkit can produce a real local LoRA artifact
  - generation capability is ready to produce a real image artifact
- If either dependency is missing, the app may still stage requests truthfully, but it must not claim:
  - trained/current success without a real LoRA file
  - proof-image success without a saved image artifact

## Current runtime blocker shape
- This environment is currently blocked for a real proof-image run because:
  - AI Toolkit is not installed
  - ComfyUI generation is not ready
  - checkpoint and VAE roots are empty
