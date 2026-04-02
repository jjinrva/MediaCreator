# Phase 09 report

## Status

PASS

## What changed

- Added the canonical character-creation route at `/studio/characters/new` using the existing studio shell and truthful Phase 09 status messaging.
- Added a client-side ingest workflow with `react-dropzone` for drag-and-drop plus click-to-select, local object-URL thumbnails, per-image removal, and a truthful local `FormData` staging step.
- Kept every thumbnail QC badge neutral with `QC pending backend upload` so the UI does not pretend the backend preparation pipeline has already run.
- Added an inline capture-guide sidebar beside the ingest workflow by reusing the Phase 08 guidance constants instead of creating a second instruction source.
- Added adjacent shared tooltip triggers for every field on the page: the character label textbox and the photoset file field.
- Extended the studio navigation so the new canonical route is reachable from the shell without introducing a second creation path.
- Added focused unit coverage for local thumbnail/removal behavior and a focused Playwright drag-and-drop flow that uses real local PNG files.
- Fixed follow-up verification issues before final PASS:
  - corrected the relative import path from the new route into the shared component tree
  - tightened the Playwright QC-badge assertion so it only counts thumbnail-card badges instead of the page-level status text
  - fixed the Playwright helper typing so `make typecheck` passes from the final tree

## Exact commands run

- `PATH="/opt/MediaCreator/infra/bin:$PATH" pnpm install`
- `PATH="/opt/MediaCreator/infra/bin:$PATH" pnpm --dir /opt/MediaCreator/apps/web exec vitest run tests/unit/ui-primitives.test.tsx tests/unit/character-import.test.tsx`
- `PATH="/opt/MediaCreator/infra/bin:$PATH" PLAYWRIGHT_BROWSERS_PATH="/opt/MediaCreator/infra/playwright" pnpm --dir /opt/MediaCreator/apps/web exec playwright test tests/e2e/studio.spec.ts tests/e2e/character-ingest.spec.ts`
- `make lint`
- `make typecheck`
- `make test-web`

## Tests that passed

- `PATH="/opt/MediaCreator/infra/bin:$PATH" pnpm --dir /opt/MediaCreator/apps/web exec vitest run tests/unit/ui-primitives.test.tsx tests/unit/character-import.test.tsx`
- `PATH="/opt/MediaCreator/infra/bin:$PATH" PLAYWRIGHT_BROWSERS_PATH="/opt/MediaCreator/infra/playwright" pnpm --dir /opt/MediaCreator/apps/web exec playwright test tests/e2e/studio.spec.ts tests/e2e/character-ingest.spec.ts`
- `make lint`
- `make typecheck`
- `make test-web`

## Remaining risks

- Phase 09 stages files only in the browser; the FastAPI upload endpoint, QC metrics, and persistent reload behavior are intentionally deferred to Phase 10.
- The current thumbnail cards show filename and size only; artifact history, lineage, and prepared derivative metadata do not exist yet.
- The local `FormData` staging step proves the chosen upload shape without sending a backend mutation yet, so later phases must preserve that contract when the API route lands.

## Next phase may start

Yes. Phase 09 verification passed, so Phase 10 may start.
