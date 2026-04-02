# Phase 09 verification

## Scope verified

- The canonical route `/studio/characters/new` renders inside the studio shell.
- The ingest page supports drag-and-drop and click-to-select through `react-dropzone`.
- Local thumbnails render from object URLs and can be removed before submit.
- Thumbnail QC badges stay neutral and do not claim a pass result before backend QC exists.
- The page keeps the Phase 08 capture guidance visible beside the ingest workflow.
- The page shows no fake previously created characters or demo uploads.
- Web linting, type-checking, and the broader web regression target all pass from the final tree.

## Commands run

- `PATH="/opt/MediaCreator/infra/bin:$PATH" pnpm --dir /opt/MediaCreator/apps/web exec vitest run tests/unit/ui-primitives.test.tsx tests/unit/character-import.test.tsx`
- `PATH="/opt/MediaCreator/infra/bin:$PATH" PLAYWRIGHT_BROWSERS_PATH="/opt/MediaCreator/infra/playwright" pnpm --dir /opt/MediaCreator/apps/web exec playwright test tests/e2e/studio.spec.ts tests/e2e/character-ingest.spec.ts`
- `make lint`
- `make typecheck`
- `make test-web`

## Files changed in the phase

- `README.md`
- `PLANS.md`
- `docs/phase_reports/phase_09.md`
- `docs/verification/phase_09_verify.md`
- `apps/web/app/globals.css`
- `apps/web/app/studio/characters/new/page.tsx`
- `apps/web/components/character-import/CaptureGuideSidebar.tsx`
- `apps/web/components/character-import/CharacterImportIngest.tsx`
- `apps/web/components/ui/StudioFrame.tsx`
- `apps/web/package.json`
- `apps/web/tests/e2e/character-ingest.spec.ts`
- `apps/web/tests/e2e/studio.spec.ts`
- `apps/web/tests/unit/character-import.test.tsx`
- `pnpm-lock.yaml`

## Results

- PASS: the focused unit test proved local file selection creates thumbnails, shows neutral `QC pending backend upload` badges, and supports removal before any upload occurs.
- PASS: the focused Playwright flow used real local PNG files in a drag-and-drop interaction, verified thumbnail rendering, removed one image before submit, and confirmed the page still shows no fake previously created characters.
- PASS: the route keeps the capture-guide panel visible beside the ingest workflow without forcing the user to leave the page.
- PASS: the page remains truthful about the current phase boundary by staging `FormData` locally and not pretending the backend upload/QC pipeline already exists.
- PASS: `make lint`, `make typecheck`, and `make test-web` all completed successfully from the final tree.
- NOT APPLICABLE: no backend domain changed in Phase 09, so there was no targeted backend test to run in this phase.

## PASS/FAIL decision

PASS

## Remaining risks

- Backend upload, normalization, QC scoring, and persistent reload behavior remain deferred to Phase 10.
- The current route prevents fake QC state, but it still depends on later backend phases to replace the neutral badges with stored results.
- The drag-and-drop proof currently uses PNG fixtures; broader file-type validation still depends on the backend ingest rules added later.
