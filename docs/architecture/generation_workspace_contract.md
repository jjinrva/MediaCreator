# Generation Workspace Contract

Phase 25 adds one separate prompt workspace at `/studio/generate`.

## Workspace scope

- The workspace is separate from the core 3D character editing routes.
- Users can stage image or video generation requests.
- `@character` handles expand visibly into the stored prompt recipe.
- Local LoRAs are only selectable through the internal model registry.
- Optional external Civitai imports must be written into the internal registry before they can be selected.

## API

- `GET /api/v1/generation` returns:
  - character prompt recipes
  - generation capability summary
  - Civitai import capability summary
  - local and external registry-backed LoRA options
  - recent stored generation requests
  - the versioned workflow contract paths
- `POST /api/v1/generation/expand` resolves `@character` handles into the visible expanded prompt.
- `POST /api/v1/generation/requests` stores one generation request asset plus its expanded prompt and linked model references.
- `GET /api/v1/generation/external-loras/search` and `POST /api/v1/generation/external-loras/import` exist only for the opt-in Civitai path.

## Storage and lineage

- Each stored request creates one `generation-request` asset.
- The request history writes `generation.requested` with:
  - raw prompt
  - expanded prompt
  - matched handles
  - selected local/external LoRA references
  - provider status
  - workflow contract ID and path
- Imported external LoRAs create:
  - one `external-lora` asset
  - one NAS-backed storage object
  - one `models_registry` row with `toolkit_name = "civitai"`

## Truthfulness limits

- Phase 25 does not claim final generated media exists.
- It does claim the request workspace, prompt expansion, workflow contract selection, and model-reference storage are all explicit and reloadable.
