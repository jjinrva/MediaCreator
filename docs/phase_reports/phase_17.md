# Phase 17 report

## Status

PASS

## What changed

- Added the Blender runtime service so preview exports run through a versioned background payload with character identity, numeric body values, numeric pose values, and explicit output targets.
- Added the Blender-side Rigify proxy export script and workflow contract under `scripts/blender` and `workflows/blender` so the app has a stable GLB export baseline.
- Extended the export service and preview route so `POST /api/v1/exports/characters/{character_public_id}/preview` produces a real GLB, a completed job record, storage metadata, and history evidence.
- Updated the character detail page and `GlbPreview` component so the UI truthfully exposes preview generation and shows the Blender export result rather than placeholder state.
- Added focused backend, unit, and Playwright coverage for background export execution, file output existence, truthful preview rendering, and persisted history events.
- Moved untyped third-party import allowances into package-level mypy config so the required strict `make typecheck` gate passes without stale inline ignores.

## Exact commands run

- `cd /opt/MediaCreator/apps/api && .venv/bin/pytest tests/test_blender_export_api.py -q`
- `PATH="/opt/MediaCreator/infra/bin:$PATH" pnpm --dir /opt/MediaCreator/apps/web exec vitest run tests/unit/glb-preview.test.tsx`
- `PATH="/opt/MediaCreator/infra/bin:$PATH" PLAYWRIGHT_BROWSERS_PATH="/opt/MediaCreator/infra/playwright" pnpm --dir /opt/MediaCreator/apps/web exec playwright test tests/e2e/character-creation.spec.ts`
- `make lint`
- `make typecheck`

## Tests that passed

- `cd /opt/MediaCreator/apps/api && .venv/bin/pytest tests/test_blender_export_api.py -q`
- `PATH="/opt/MediaCreator/infra/bin:$PATH" pnpm --dir /opt/MediaCreator/apps/web exec vitest run tests/unit/glb-preview.test.tsx`
- `PATH="/opt/MediaCreator/infra/bin:$PATH" PLAYWRIGHT_BROWSERS_PATH="/opt/MediaCreator/infra/playwright" pnpm --dir /opt/MediaCreator/apps/web exec playwright test tests/e2e/character-creation.spec.ts`
- `make lint`
- `make typecheck`

## Remaining risks

- The current Blender path exports a stable preview GLB baseline; richer Rigify controls, animation export breadth, and higher-fidelity mesh refinement remain later-phase work.
- The export job is synchronous in the tested preview flow even though it writes durable job/history state.
- The typecheck fix intentionally centralizes third-party untyped import handling in `pyproject.toml`; future new binary dependencies should follow that same pattern.

## Next phase may start

Yes. Phase 17 verification passed, so Phase 18 may start.
