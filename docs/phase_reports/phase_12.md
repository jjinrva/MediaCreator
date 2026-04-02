# Phase 12 report

## Status

PASS

## What changed

- Rebuilt `/studio/characters/[publicId]` into the fixed Phase 12 layout with these sections only: Overview, Body, Pose, History, and Outputs.
- Added the `GlbPreview` component under `apps/web/components/glb-preview` using the `<model-viewer>` stack, with a full-body-sized viewport and a truthful placeholder path when no GLB exists.
- Added the FastAPI export scaffold routes under `GET /api/v1/exports/characters/{character_public_id}` plus stable preview/final GLB file endpoints.
- Added the export scaffold service and schema so the UI loads preview status, final-export status, and export-job status entirely from the API.
- Kept the Outputs section truthful by reporting `not-ready` until a real `character-preview-glb` or `character-export-glb` storage object exists.
- Added focused backend, unit, and Playwright coverage for the new output scaffold and the restricted character-detail layout.
- Added `@google/model-viewer` to the web app dependency graph and documented the Phase 12 outputs contract in `docs/architecture/character_outputs.md`.
- Fixed follow-up verification issues before final PASS:
  - tightened the placeholder text selectors in the new GLB unit and Playwright coverage because the truthful placeholder detail string appears in more than one node
  - added explicit missing-file checks on the preview and final GLB file routes so missing artifacts return `404` instead of pretending the file exists

## Exact commands run

- `PATH="/opt/MediaCreator/infra/bin:$PATH" pnpm --dir /opt/MediaCreator/apps/web add @google/model-viewer`
- `cd /opt/MediaCreator/apps/api && .venv/bin/pytest tests/test_exports_api.py tests/test_characters_api.py -q`
- `PATH="/opt/MediaCreator/infra/bin:$PATH" pnpm --dir /opt/MediaCreator/apps/web exec vitest run tests/unit/character-import.test.tsx tests/unit/glb-preview.test.tsx`
- `PATH="/opt/MediaCreator/infra/bin:$PATH" PLAYWRIGHT_BROWSERS_PATH="/opt/MediaCreator/infra/playwright" pnpm --dir /opt/MediaCreator/apps/web exec playwright test tests/e2e/character-creation.spec.ts`
- `make lint`
- `make typecheck`
- `make test-api`
- `make test-web`

## Tests that passed

- `cd /opt/MediaCreator/apps/api && .venv/bin/pytest tests/test_exports_api.py tests/test_characters_api.py -q`
- `PATH="/opt/MediaCreator/infra/bin:$PATH" pnpm --dir /opt/MediaCreator/apps/web exec vitest run tests/unit/character-import.test.tsx tests/unit/glb-preview.test.tsx`
- `PATH="/opt/MediaCreator/infra/bin:$PATH" PLAYWRIGHT_BROWSERS_PATH="/opt/MediaCreator/infra/playwright" pnpm --dir /opt/MediaCreator/apps/web exec playwright test tests/e2e/character-creation.spec.ts`
- `make lint`
- `make typecheck`
- `make test-api`
- `make test-web`

## Remaining risks

- The Outputs section is truthful but still placeholder-backed until a later Blender phase writes real GLB storage objects for preview or export.
- The `<model-viewer>` path is now wired, but framing refinement and meaningful camera defaults still depend on later Blender export work.
- Body and Pose are intentionally empty-state sections in this phase, so future numeric controls must reuse the same route layout instead of inventing a second editor surface.

## Next phase may start

Yes. Phase 12 verification passed, so Phase 13 may start.
