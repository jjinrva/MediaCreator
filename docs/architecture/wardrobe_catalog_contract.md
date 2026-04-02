# Wardrobe Catalog Contract

Phase 22 introduces the first reusable closet catalog.

## Asset model

- The reusable base garment is stored as one `wardrobe-item` asset.
- Color, material, and fitting data are stored as separate child assets:
  - `wardrobe-color-variant`
  - `wardrobe-material-variant`
  - `wardrobe-fitting-profile`
- Photo-source items use a separate `wardrobe-source-photo` asset plus a NAS-backed storage object.
- Prompt-backed items use a separate `wardrobe-prompt-request` asset plus a NAS-backed JSON manifest.

## Truthful AI path

- The AI wardrobe path uses the existing ComfyUI capability check.
- If ComfyUI is not ready, the app still stores the prompt-backed closet item but marks it as staged instead of claiming a generated garment image exists.
- The closet catalog always exposes the current generation capability state next to the creation forms.

## Catalog payload

- `GET /api/v1/wardrobe` returns:
  - the current AI wardrobe generation capability summary
  - a list of real wardrobe items only
  - explicit `material`, `base_color`, and `fitting_status`
  - source photo URLs when a photo-backed item exists
  - prompt text when an AI prompt-backed item exists

## Create routes

- `POST /api/v1/wardrobe/from-photo` stores one source garment photo and creates the base wardrobe item plus its child metadata assets.
- `POST /api/v1/wardrobe/from-prompt` stores one prompt manifest and creates the base wardrobe item plus its child metadata assets.
