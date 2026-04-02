# Phase 12 verification

## Scope verified

- Fixed five-section character detail layout on `/studio/characters/[publicId]`
- Export scaffold API under `/api/v1/exports/characters/{character_public_id}`
- Truthful GLB placeholder behavior when no preview artifact exists
- History section showing only real events
- Required lint, type-check, API regression, and web regression gates

## Commands run

- `PATH="/opt/MediaCreator/infra/bin:$PATH" pnpm --dir /opt/MediaCreator/apps/web add @google/model-viewer`
- `cd /opt/MediaCreator/apps/api && .venv/bin/pytest tests/test_exports_api.py tests/test_characters_api.py -q`
- `PATH="/opt/MediaCreator/infra/bin:$PATH" pnpm --dir /opt/MediaCreator/apps/web exec vitest run tests/unit/character-import.test.tsx tests/unit/glb-preview.test.tsx`
- `PATH="/opt/MediaCreator/infra/bin:$PATH" PLAYWRIGHT_BROWSERS_PATH="/opt/MediaCreator/infra/playwright" pnpm --dir /opt/MediaCreator/apps/web exec playwright test tests/e2e/character-creation.spec.ts`
- `make lint`
- `make typecheck`
- `make test-api`
- `make test-web`

## Files changed in the phase

- `PLANS.md`
- `README.md`
- `apps/api/app/api/router.py`
- `apps/api/app/api/routes/exports.py`
- `apps/api/app/schemas/exports.py`
- `apps/api/app/services/exports.py`
- `apps/api/tests/test_exports_api.py`
- `apps/web/app/globals.css`
- `apps/web/app/studio/characters/[publicId]/page.tsx`
- `apps/web/components/glb-preview/GlbPreview.tsx`
- `apps/web/package.json`
- `apps/web/tests/e2e/character-creation.spec.ts`
- `apps/web/tests/unit/glb-preview.test.tsx`
- `docs/architecture/character_outputs.md`
- `docs/phase_reports/phase_12.md`
- `docs/verification/phase_12_verify.md`
- `pnpm-lock.yaml`

## Results

- PASS: the targeted backend export test created a real character through the Phase 11 flow, loaded `/api/v1/exports/characters/{character_public_id}`, and confirmed that preview GLB, final GLB, and export job all report truthful placeholder states when no artifact exists.
- PASS: the same backend test confirmed the preview file route returns `404` instead of pretending a missing GLB file is available.
- PASS: the targeted unit tests proved the create flow still redirects correctly and that the new `GlbPreview` component renders a truthful placeholder when the preview source is absent.
- PASS: the targeted Playwright flow loaded the character detail page, confirmed the exact Phase 12 sections, verified the GLB placeholder text, and asserted that future-phase headings such as Wardrobe, Scenes, and Composer are absent.
- PASS: the Playwright flow also reloaded the detail route and confirmed the same history-plus-placeholder state survives a full refresh.
- PASS: `make lint`, `make typecheck`, `make test-api`, and `make test-web` all completed successfully from the final tree.

## PASS/FAIL decision

PASS

## Remaining risks

- No real GLB artifact exists yet, so the preview remains a truthful placeholder until later Blender export phases produce storage objects and files.
- The Outputs API contract is stable, but its `available` path has not been exercised yet because this phase intentionally does not fabricate a GLB.
- Body and Pose sections still intentionally lack numeric controls and persistence.
