# Phase 13 report

## Status

PASS

## What changed

- Added the canonical body parameter model in `apps/api/app/models/body_parameters.py`, including the frozen eight-parameter catalog and the persisted `body_parameters` table.
- Added Alembic migration `0004_body_parameter_foundation.py` so new databases create the `body_parameters` table with one unique row per character and parameter key.
- Added the read API at `GET /api/v1/body/characters/{character_public_id}` to return the parameter catalog plus the current character values.
- Updated character creation so new characters initialize the Phase 13 default numeric body rows immediately.
- Replaced the Body-section placeholder on `/studio/characters/[publicId]` with an API-backed read-only parameter catalog and current-value readout.
- Added the frozen parameter contract doc at `docs/architecture/body_parameter_contract.md`.
- Added focused backend, unit, and Playwright coverage for the new catalog rows, API contract, and body readout.

## Exact commands run

- `cd /opt/MediaCreator/apps/api && .venv/bin/pytest tests/test_body_api.py tests/test_characters_api.py -q`
- `PATH="/opt/MediaCreator/infra/bin:$PATH" pnpm --dir /opt/MediaCreator/apps/web exec vitest run tests/unit/body-parameter-readout.test.tsx`
- `PATH="/opt/MediaCreator/infra/bin:$PATH" PLAYWRIGHT_BROWSERS_PATH="/opt/MediaCreator/infra/playwright" pnpm --dir /opt/MediaCreator/apps/web exec playwright test tests/e2e/character-creation.spec.ts`
- `test -f /opt/MediaCreator/docs/architecture/body_parameter_contract.md && rg -n "height_scale|shoulder_width|chest_volume|waist_width|hip_width|upper_arm_volume|thigh_volume|calf_volume" /opt/MediaCreator/docs/architecture/body_parameter_contract.md`
- `make lint`
- `make typecheck`
- `make test-api`
- `make test-web`

## Tests that passed

- `cd /opt/MediaCreator/apps/api && .venv/bin/pytest tests/test_body_api.py tests/test_characters_api.py -q`
- `PATH="/opt/MediaCreator/infra/bin:$PATH" pnpm --dir /opt/MediaCreator/apps/web exec vitest run tests/unit/body-parameter-readout.test.tsx`
- `PATH="/opt/MediaCreator/infra/bin:$PATH" PLAYWRIGHT_BROWSERS_PATH="/opt/MediaCreator/infra/playwright" pnpm --dir /opt/MediaCreator/apps/web exec playwright test tests/e2e/character-creation.spec.ts`
- `test -f /opt/MediaCreator/docs/architecture/body_parameter_contract.md && rg -n "height_scale|shoulder_width|chest_volume|waist_width|hip_width|upper_arm_volume|thigh_volume|calf_volume" /opt/MediaCreator/docs/architecture/body_parameter_contract.md`
- `make lint`
- `make typecheck`
- `make test-api`
- `make test-web`

## Remaining risks

- Phase 13 exposes the canonical read contract only; editing and history-backed writes still belong to Phase 14.
- Existing characters created before Phase 13 can still fall back to default catalog values on read if they do not already have persisted rows.
- The parameter names are frozen now, so later Blender and natural-language phases must map onto this contract rather than rename the stored keys.

## Next phase may start

Yes. Phase 13 verification passed, so Phase 14 may start.
