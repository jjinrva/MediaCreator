# Generation capability

## Provider model

- ComfyUI is a separate local service.
- MediaCreator only reports generation as ready after capability detection passes.
- Workflow JSON lives in the repository under `workflows/comfyui/`.

## Status values

- `unavailable`
  The ComfyUI base URL is missing, or the capability contract is not configured enough to attempt readiness.
- `partially-configured`
  The base URL is configured, but the service is unreachable or required workflow/model checks still fail.
- `ready`
  The base URL responds, required workflow JSON files exist, model roots are NAS-backed, and at least one checkpoint plus one VAE file are present.

## Stable workflow filenames

- `text_to_image_v1.json`
- `character_refine_img2img_v1.json`

## NAS-backed model roots

- checkpoints: `MEDIACREATOR_STORAGE_CHECKPOINTS_ROOT`
- LoRAs: `MEDIACREATOR_STORAGE_LORAS_ROOT`
- embeddings: `MEDIACREATOR_STORAGE_EMBEDDINGS_ROOT`
- VAEs: `MEDIACREATOR_STORAGE_VAES_ROOT`

## API surface

- `GET /api/v1/system/status`

This route reports storage mode, NAS availability, and the current ComfyUI capability result without claiming that final generation is available before detection passes.
