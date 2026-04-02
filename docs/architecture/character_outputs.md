# Character Outputs Contract

Phase 12 establishes the first durable outputs contract for character detail pages.

## Detail route layout

The character detail page at `/studio/characters/[publicId]` now exposes these sections only:

- Overview
- Body
- Pose
- History
- Outputs

Wardrobe, scenes, and composer controls do not appear before their phases land.

## Export scaffold API

Phase 12 adds:

- `GET /api/v1/exports/characters/{character_public_id}`
- `GET /api/v1/exports/characters/{character_public_id}/preview.glb`
- `GET /api/v1/exports/characters/{character_public_id}/final.glb`

The scaffold route returns:

- preview GLB status
- final GLB export status
- export job status

If no GLB artifact exists yet, the API returns truthful `not-ready` states and the file routes return `404`.

## Preview rules

- The web preview uses `<model-viewer>`.
- The preview container is sized for full-body framing.
- If a preview GLB becomes available later, the page uses the API-provided URL directly.
- If no preview exists, the page shows a truthful placeholder instead of a fake model.
