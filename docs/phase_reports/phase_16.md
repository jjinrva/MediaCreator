# Phase 16 report

## Status

PASS

## What changed

- Added the canonical facial-parameter model and migration so each character now stores persisted face controls in a dedicated `facial_parameters` table.
- Added the face API at `GET /api/v1/face/characters/{character_public_id}` and `PUT /api/v1/face/characters/{character_public_id}` with backend-provided catalog metadata, range validation, and `face.parameter_updated` history writes.
- Initialized facial rows during character creation so the detail route always has a truthful minimal face-control surface.
- Added the `FaceParameterEditor` client component that renders backend-defined sliders and tooltips, saves on `onValueCommit`, reconciles from the API response, and refreshes the route so History stays aligned with saved state.
- Updated the character detail page to add the Face section alongside the existing Body and Pose editors.
- Added focused backend, unit, and Playwright coverage for the facial catalog, persisted updates, reload stability, and history evidence.
- Documented the frozen face contract and its Blender mapping intent in `docs/architecture/face_parameter_contract.md`.

## Exact commands run

- `cd /opt/MediaCreator/apps/api && .venv/bin/pytest tests/test_face_api.py -q`
- `PATH="/opt/MediaCreator/infra/bin:$PATH" pnpm --dir /opt/MediaCreator/apps/web exec vitest run tests/unit/face-parameter-editor.test.tsx`
- `PATH="/opt/MediaCreator/infra/bin:$PATH" PLAYWRIGHT_BROWSERS_PATH="/opt/MediaCreator/infra/playwright" pnpm --dir /opt/MediaCreator/apps/web exec playwright test tests/e2e/character-creation.spec.ts`
- `make lint`
- `make typecheck`

## Tests that passed

- `cd /opt/MediaCreator/apps/api && .venv/bin/pytest tests/test_face_api.py -q`
- `PATH="/opt/MediaCreator/infra/bin:$PATH" pnpm --dir /opt/MediaCreator/apps/web exec vitest run tests/unit/face-parameter-editor.test.tsx`
- `PATH="/opt/MediaCreator/infra/bin:$PATH" PLAYWRIGHT_BROWSERS_PATH="/opt/MediaCreator/infra/playwright" pnpm --dir /opt/MediaCreator/apps/web exec playwright test tests/e2e/character-creation.spec.ts`
- `make lint`
- `make typecheck`

## Remaining risks

- The current face editor persists numeric scaffolding only; no live Blender facial deformation ships in Phase 16.
- The UI refreshes the full detail route after each committed facial change so History remains exact.
- The minimal catalog is intentionally small and symmetric; richer left/right brow, eyelid, and phoneme controls remain later-phase work.

## Next phase may start

Yes. Phase 16 verification passed, so Phase 17 may start.
