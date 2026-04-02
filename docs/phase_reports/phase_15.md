# Phase 15 report

## Status

PASS

## What changed

- Added the canonical pose-state model and migration so each character now stores one numeric row per limb pose parameter in a dedicated `pose_state` table.
- Added the pose API at `GET /api/v1/pose/characters/{character_public_id}` and `PUT /api/v1/pose/characters/{character_public_id}` with backend-provided catalog metadata, range validation, and history writes on committed changes.
- Initialized pose rows during character creation so the detail route always has stable left-arm, right-arm, left-leg, and right-leg controls.
- Added the `PoseParameterEditor` client component that renders backend-defined sliders and tooltips, saves on `onValueCommit`, reconciles from the API response, and refreshes the route so the preview scaffold and history stay aligned.
- Updated the character detail page so the Pose section is API-backed, reload-safe, and truthfully reflects persisted pose values.
- Added focused backend, unit, and Playwright coverage for pose persistence, reload stability, and history evidence.
- Tightened the Playwright history assertions to expect the real Phase 15 outcome: four `pose.parameter_updated` events after the four committed limb changes.
- Documented the canonical pose contract in `docs/architecture/pose_parameter_contract.md`.

## Exact commands run

- `cd /opt/MediaCreator/apps/api && .venv/bin/pytest tests/test_pose_api.py -q`
- `PATH="/opt/MediaCreator/infra/bin:$PATH" pnpm --dir /opt/MediaCreator/apps/web exec vitest run tests/unit/pose-parameter-editor.test.tsx`
- `PATH="/opt/MediaCreator/infra/bin:$PATH" PLAYWRIGHT_BROWSERS_PATH="/opt/MediaCreator/infra/playwright" pnpm --dir /opt/MediaCreator/apps/web exec playwright test tests/e2e/character-creation.spec.ts`
- `make lint`
- `make typecheck`

## Tests that passed

- `cd /opt/MediaCreator/apps/api && .venv/bin/pytest tests/test_pose_api.py -q`
- `PATH="/opt/MediaCreator/infra/bin:$PATH" pnpm --dir /opt/MediaCreator/apps/web exec vitest run tests/unit/pose-parameter-editor.test.tsx`
- `PATH="/opt/MediaCreator/infra/bin:$PATH" PLAYWRIGHT_BROWSERS_PATH="/opt/MediaCreator/infra/playwright" pnpm --dir /opt/MediaCreator/apps/web exec playwright test tests/e2e/character-creation.spec.ts`
- `make lint`
- `make typecheck`

## Remaining risks

- Each pose commit still refreshes the full detail route so History and the preview scaffold stay truthful; later Blender-backed preview phases may want a narrower refresh path.
- Phase 15 stores canonical pose intent only. It does not yet deform a GLB or drive Blender rig output.
- The pose catalog currently covers limb pitch only, with face and expression controls deferred to Phase 16.

## Next phase may start

Yes. Phase 15 verification passed, so Phase 16 may start.
