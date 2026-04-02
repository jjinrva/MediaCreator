# Character Outputs Contract

Phase 18 extends the durable outputs contract for character detail pages.

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
- high-detail reconstruction detail level
- high-detail strategy
- detail-prep artifact status
- reconstruction job status
- current texture fidelity
- base texture artifact status
- refined texture artifact status

If no GLB artifact exists yet, the API returns truthful `not-ready` states and the file routes return `404`.

## Preview rules

- The web preview uses `<model-viewer>`.
- The preview container is sized for full-body framing.
- If a preview GLB becomes available later, the page uses the API-provided URL directly.
- If no preview exists, the page shows a truthful placeholder instead of a fake model.

## High-detail reconstruction rules

- The high-detail path never replaces the riggable base with an uncontrolled mesh.
- The current detail level is reported truthfully as `not-started`, `riggable-base-only`, or `riggable-base-plus-detail-prep`.
- A detail-prep artifact is only written when the current capture set qualifies.
- The detail-prep artifact is a staged contract for later refinement work, not a claim that a refined mesh already exists.

## Texture/material rules

- Texture artifacts are stored separately from GLB geometry artifacts.
- The current texture fidelity is reported truthfully as `untextured`, `base-textured`, or `refined-textured`.
- Phase 19 guarantees only the `base-textured` path and does not claim a refined texture solve yet.
