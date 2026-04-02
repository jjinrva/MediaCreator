# Phase 11 report

## Status

PASS

## What changed

- Added `POST /api/v1/characters` and `GET /api/v1/characters/{character_public_id}` on FastAPI.
- Added a dedicated character-registry service that creates a `character` asset from a persisted photoset, points `source_asset_id` back to the originating photoset, and records one stable public ID per source photoset.
- Made character creation idempotent by source photoset so accidental double-submit returns the existing character instead of duplicating the registry row.
- Added character history events for both registry creation and photoset linking, with accepted entry public IDs captured in the event details.
- Added the API-backed detail route at `/studio/characters/[publicId]` and updated `/studio/characters/new` so the browser can create a base character and redirect there.
- Added frontend coverage for the new create action and browser coverage for create, redirect, and reload.
- Added `docs/architecture/character_registry.md` and updated `README.md` with the new API and route contract.
- Fixed one follow-up verification issue before final PASS:
  - corrected the dynamic route import path under `apps/web/app/studio/characters/[publicId]/page.tsx` after Playwright exposed the broken module resolution

## Exact commands run

- `cd /opt/MediaCreator/apps/api && .venv/bin/pytest tests/test_characters_api.py -q`
- `PATH="/opt/MediaCreator/infra/bin:$PATH" pnpm --dir /opt/MediaCreator/apps/web exec vitest run tests/unit/character-import.test.tsx`
- `PATH="/opt/MediaCreator/infra/bin:$PATH" PLAYWRIGHT_BROWSERS_PATH="/opt/MediaCreator/infra/playwright" pnpm --dir /opt/MediaCreator/apps/web exec playwright test tests/e2e/character-creation.spec.ts`
- `make lint`
- `make typecheck`
- `make test-api`
- `make test-web`

## Tests that passed

- `cd /opt/MediaCreator/apps/api && .venv/bin/pytest tests/test_characters_api.py -q`
- `PATH="/opt/MediaCreator/infra/bin:$PATH" pnpm --dir /opt/MediaCreator/apps/web exec vitest run tests/unit/character-import.test.tsx`
- `PATH="/opt/MediaCreator/infra/bin:$PATH" PLAYWRIGHT_BROWSERS_PATH="/opt/MediaCreator/infra/playwright" pnpm --dir /opt/MediaCreator/apps/web exec playwright test tests/e2e/character-creation.spec.ts`
- `make lint`
- `make typecheck`
- `make test-api`
- `make test-web`

## Remaining risks

- Phase 11 stores the accepted prepared-reference set in character history details rather than a dedicated join table, so later phases must keep extending that same contract instead of inventing a parallel source-link model.
- The detail route currently focuses on registry truth, accepted references, and history only; GLB preview and export sections still belong to Phase 12.
- Character labels still originate from the photoset upload event, so a later rename workflow will need its own explicit mutation path rather than overloading creation.

## Next phase may start

Yes. Phase 11 verification passed, so Phase 12 may start.
